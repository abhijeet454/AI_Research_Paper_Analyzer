import streamlit as st
import os
import uuid
from config import settings
from pdf_utils import extract_text_from_pdf, PDFParsingError
from llm_utils import get_llm_analysis, LLMAnalysisError # get_llm_analysis handles chunking internally
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(streamlit)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

st.set_page_config(page_title=settings.PROJECT_NAME, layout="wide")

st.markdown(f"""
    <style>
        .reportview-container .main .block-container{{
            padding-top: 2rem; padding-right: 2rem; padding-left: 2rem; padding-bottom: 2rem;
        }}
        .stButton>button {{ width: 100%; border-radius: 0.5rem; }}
        .stMultiSelect [data-baseweb="tag"] {{ background-color: #0078D4; color: white; }}
    </style>
    """, unsafe_allow_html=True)

st.title(f"🔬 {settings.PROJECT_NAME} (Enhanced with Chunking)")
st.markdown("Upload a research paper (PDF) for AI-powered analysis. Now capable of handling larger documents!")
st.markdown(f"Powered by Groq and Llama 3 (Model: `{settings.LLM_MODEL}`). Chunk size: ~{settings.CHUNK_TARGET_CHAR_COUNT} chars.")

if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}
if 'current_pdf_name' not in st.session_state:
    st.session_state.current_pdf_name = None
if 'error_message' not in st.session_state:
    st.session_state.error_message = None
if 'processing' not in st.session_state:
    st.session_state.processing = False

uploaded_file = st.file_uploader("📂 Choose a PDF research paper", type="pdf", key="pdf_uploader")

st.sidebar.header("⚙️ Analysis Configuration")
selected_analysis_types_display = st.sidebar.multiselect(
    "Select Analysis Types:",
    options=list(settings.ANALYSIS_OPTIONS.keys()),
    format_func=lambda x: settings.ANALYSIS_OPTIONS[x],
    default=["summary", "gaps"],
    key="analysis_selector"
)

st.sidebar.subheader("Advanced (Optional)")
custom_model_name = st.sidebar.text_input(
    "Override LLM Model", 
    value=settings.LLM_MODEL, 
    help=f"Default: {settings.LLM_MODEL}. Ensure the model is available on Groq.",
    key="model_override"
)
# CHUNK_TARGET_CHAR_COUNT can be made configurable here if desired

analyze_button = st.button("🚀 Analyze Paper", type="primary", disabled=st.session_state.processing, key="analyze_button")

# Placeholders for status messages and progress bar
status_placeholder_main = st.empty() # For PDF parsing status
status_placeholder_llm = st.empty()  # For LLM chunk processing status
progress_bar = st.empty()

if analyze_button and uploaded_file is not None:
    if not selected_analysis_types_display:
        st.error("⚠️ Please select at least one analysis type from the sidebar.")
    else:
        st.session_state.processing = True
        st.session_state.error_message = None
        st.session_state.analysis_results = {}
        st.session_state.current_pdf_name = uploaded_file.name
        
        # Clear previous placeholders
        status_placeholder_main.empty()
        status_placeholder_llm.empty()
        progress_bar.empty()
        
        # Re-initialize placeholders for the current run
        current_status_main = status_placeholder_main.container()
        current_status_llm = status_placeholder_llm.container() # For LLM specific messages
        current_progress_bar = progress_bar.progress(0)


        temp_file_path = os.path.join(settings.UPLOAD_DIR, f"{uuid.uuid4().hex}_{uploaded_file.name}")
        
        try:
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            logger.info(f"Uploaded file saved temporarily to: {temp_file_path}")

            current_status_main.info(f"⏳ Parsing PDF '{uploaded_file.name}'...")
            extracted_text = extract_text_from_pdf(temp_file_path)
            logger.info(f"PDF parsing successful for {uploaded_file.name}. Text length: {len(extracted_text)}")
            current_status_main.success(f"✅ PDF Parsed. Total characters: {len(extracted_text):,}")
            current_progress_bar.progress(0.1) # 10% after PDF parsing

            # LLM Analysis for each selected type using the status placeholder from llm_utils
            total_llm_analyses = len(selected_analysis_types_display)
            for i, analysis_key in enumerate(selected_analysis_types_display):
                analysis_display_name = settings.ANALYSIS_OPTIONS[analysis_key]
                current_status_main.info(f"✨ Starting '{analysis_display_name}'...")
                
                # Pass the llm_status_placeholder to the analysis function
                # It will be updated inside get_llm_analysis during chunk processing
                try:
                    # The get_llm_analysis will use its own status_placeholder for chunk progress
                    # Here we just indicate which overall analysis is running
                    analysis_result = get_llm_analysis(
                        extracted_text, 
                        analysis_key, 
                        model_name=custom_model_name or settings.LLM_MODEL,
                        streamlit_status_placeholder=current_status_llm # Pass placeholder here
                    )
                    st.session_state.analysis_results[analysis_key] = analysis_result
                    logger.info(f"Successfully completed '{analysis_display_name}' for {uploaded_file.name}.")
                except LLMAnalysisError as llm_err:
                    logger.error(f"LLM Analysis Error for {analysis_display_name}: {llm_err}", exc_info=True)
                    st.session_state.analysis_results[analysis_key] = f"❌ Error during '{analysis_display_name}': {str(llm_err)}"
                except Exception as gen_err:
                    logger.error(f"Unexpected Error for {analysis_display_name}: {gen_err}", exc_info=True)
                    st.session_state.analysis_results[analysis_key] = f"❌ Unexpected error for '{analysis_display_name}': {str(gen_err)}"
                
                current_progress_bar.progress(0.1 + (0.9 * ((i + 1) / total_llm_analyses)))
                current_status_llm.empty() # Clear LLM specific status after each analysis type

            current_status_main.success(f"✅ All analyses complete for '{uploaded_file.name}'!")
            current_progress_bar.progress(1.0)

        except PDFParsingError as pdf_err:
            logger.error(f"PDF Parsing Error: {pdf_err}", exc_info=True)
            st.session_state.error_message = f"❌ PDF Parsing Failed: {str(pdf_err)}"
            current_status_main.error(st.session_state.error_message)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)
            st.session_state.error_message = f"❌ An unexpected error occurred: {str(e)}"
            current_status_main.error(st.session_state.error_message)
        finally:
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    logger.info(f"Cleaned up temporary file: {temp_file_path}")
                except OSError as e_remove:
                    logger.error(f"Error removing temporary file {temp_file_path}: {e_remove}")
            st.session_state.processing = False
            # Clear placeholders explicitly after processing
            status_placeholder_main.empty()
            status_placeholder_llm.empty()
            progress_bar.empty()
            st.rerun() # Use st.rerun()

elif analyze_button and uploaded_file is None:
    st.warning("☝️ Please upload a PDF file first.")

if st.session_state.error_message and not st.session_state.processing:
    st.error(st.session_state.error_message)

if st.session_state.analysis_results and st.session_state.current_pdf_name:
    st.markdown("---")
    st.header(f"📊 Analysis Results for: _{st.session_state.current_pdf_name}_")
    
    for analysis_key, result_text in st.session_state.analysis_results.items():
        display_name = settings.ANALYSIS_OPTIONS.get(analysis_key, analysis_key.replace("_", " ").title())
        with st.expander(f"**{display_name}**", expanded=True):
            if isinstance(result_text, str) and "❌ Error" in result_text:
                st.error(result_text)
            else:
                st.markdown(result_text, unsafe_allow_html=True)

st.markdown("---")
st.markdown("ℹ️ **Note:** Analysis quality depends on PDF text clarity and LLM capabilities. Always critically evaluate outputs.")