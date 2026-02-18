# app.py

import streamlit as st
import os
import uuid
from config import settings
from pdf_utils import extract_text_from_pdf, PDFParsingError
from llm_utils import get_rag_response_stream, LLMAnalysisError
from rag_utils import RAGVectorStore
from preloaded_data import preload_data_to_store
from chunking import SemanticChunker
import logging
import time

# --- Setup & Initialization ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

st.set_page_config(page_title=settings.PROJECT_NAME, layout="wide")

# --- Session State Initialization ---
def initialize_session_state():
    """Initializes session state variables if they don't exist."""
    if 'rag_store' not in st.session_state:
        st.session_state.rag_store = RAGVectorStore()
        st.session_state.processed_files = set()
        logger.info("Initialized RAGVectorStore and processed_files in session state.")

        with st.spinner("Loading initial knowledge base..."):
            processed_filenames = preload_data_to_store(st.session_state.rag_store)
            for name in processed_filenames:
                st.session_state.processed_files.add(name)
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
        logger.info("Initialized chat_history in session state.")
    
    if 'semantic_chunker' not in st.session_state:
        st.session_state.semantic_chunker = SemanticChunker(st.session_state.rag_store.embedding_model)

initialize_session_state()

# --- UI Styles ---
st.markdown("""
    <style>
        .stChatMessage {
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        .stChatMessage[data-testid="stChatMessageContent"] {
            background-color: #f8f9fa;
        }
    </style>
""", unsafe_allow_html=True)


# --- Sidebar ---
with st.sidebar:
    st.header("📚 Document Management")
    uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in st.session_state.processed_files:
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    try:
                        temp_path = os.path.join(settings.UPLOAD_DIR, uploaded_file.name)
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getvalue())
                        
                        text = extract_text_from_pdf(temp_path)
                        chunks = st.session_state.semantic_chunker.chunk(text)
                        st.session_state.rag_store.add_texts(chunks, source=uploaded_file.name)
                        
                        st.session_state.processed_files.add(uploaded_file.name)
                        st.success(f"✅ Indexed {uploaded_file.name}")
                        os.remove(temp_path)
                    except Exception as e:
                        st.error(f"❌ Error processing {uploaded_file.name}: {e}")

    st.subheader("Indexed Documents")
    if not st.session_state.processed_files:
        st.info("Knowledge base is empty. Upload a PDF or add files to the 'data' folder.")
    else:
        for file_name in sorted(list(st.session_state.processed_files)):
            st.markdown(f"- `{file_name}`")

    if st.button("Clear All Data & Chats"):
        # Clear specific session state keys instead of wiping the whole state
        st.session_state.rag_store.clear()
        st.session_state.chat_history = []
        st.session_state.processed_files = set()
        st.rerun()

# --- Main Chat Interface ---
st.title("🌊 FlowChat: AquaQuery Oceanographic Assistant")
st.markdown("Your assistant for understanding oceanographic research. Ask questions and get cited answers.")

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("View Sources"):
                for source in message["sources"]:
                    # Use st.info or st.code for better visual separation of sources
                    st.info(f"**Source Document:** `{source['source']}`\n\n**Content:**\n\n> {source['text'].replace('$', '//$')}")

# Handle new chat input
if prompt := st.chat_input("Ask AquaQuery about your documents..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            if st.session_state.rag_store.index.ntotal == 0:
                st.warning("The knowledge base is empty. Please upload documents before asking questions.")
                st.session_state.chat_history.append({"role": "assistant", "content": "The knowledge base is empty."})
            else:
                with st.spinner("Searching documents..."):
                    retrieved_docs = st.session_state.rag_store.query(prompt, top_k=settings.TOP_K)
                    context_parts = [f"--- Excerpt from {doc['source']} ---\n{doc['text']}" for doc in retrieved_docs]
                    context = "\n\n".join(context_parts)

                if not retrieved_docs:
                    st.warning("I couldn't find relevant information in the documents for your query.")
                    st.session_state.chat_history.append({"role": "assistant", "content": "I couldn't find relevant information in the documents for your query."})
                else:
                    response_generator = get_rag_response_stream(query=prompt, context=context)
                    full_response = st.write_stream(response_generator)
                    
                    bot_message = {"role": "assistant", "content": full_response}
                    if retrieved_docs:
                        bot_message["sources"] = retrieved_docs
                    
                    if full_response:
                        st.session_state.chat_history.append(bot_message)
                        
                        # **CORRECTION**: The source display expander is removed from here.
                        # The main history display loop above will now handle rendering the sources
                        # for this new message on the next automatic re-run after the stream completes.
                        # This avoids duplicate display logic.
                        st.rerun() # Explicitly rerun to make the history loop display the new message with its sources.


        except Exception as e:
            error_message = f"An error occurred: {e}"
            st.error(error_message)
            st.session_state.chat_history.append({"role": "assistant", "content": error_message})
            logger.error(f"Error during chat response generation: {e}", exc_info=True)