# llm_utils.py

from groq import Groq, GroqError
from config import settings
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    client = Groq(api_key=settings.GROQ_API_KEY)
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    client = None

class LLMAnalysisError(Exception):
    """Custom exception for LLM analysis errors."""
    pass

def get_rag_response_stream(query: str, context: str, model_name: str = settings.LLM_MODEL):
    """
    Generates a response for a RAG query using the Groq API with streaming.
    """
    if not client:
        raise LLMAnalysisError("Groq API client is not initialized. Check API key.")
    if not context.strip():
        logger.warning("RAG query attempted with empty context.")
        yield "I could not find any relevant information in the provided documents to answer this question."
        return

    # --- UPDATED ADVANCED PROMPT ---
    prompt = f"""
    You are AquaQuery, an expert AI oceanographic research assistant. Your primary goal is to provide accurate, helpful, and concise answers based *exclusively* on the provided document excerpts.

    **CRITICAL RULES:**
    1.  **Base Answers on Provided Context Only:** Do NOT use any external knowledge. If the answer is not in the context, state that clearly.
    
    2.  **Handle Greetings:** If the user's query is a simple greeting (like "hi", "hello", "how are you?") or a thank you, **ignore the context entirely** and respond with a friendly, brief greeting. Do not summarize the documents. For example, if the query is "hi", just say "Hello! How can I help you with your documents today?".

    3.  **Synthesize Information:** For all other questions, your primary task is to synthesize the provided context excerpts into a coherent answer.

    4.  **Handle Partial Information:** If you can only partially answer a real question, provide the information you have and clearly state what is missing.

    5.  **Cite Sources:** For every piece of information you provide in response to a real question, you MUST cite the source document. Use the format `(Source: filename.pdf)`. Do not add citations to greetings.

    6.  **Be Direct:** Answer the user's question directly. Avoid conversational fluff.

    **Provided Context Excerpts:**
    ---
    {context}
    ---

    **User's Question:** {query}

    **Your Answer:**
    """

    messages = [{"role": "user", "content": prompt}]
    max_retries = 2
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            logger.info(f"Requesting streaming completion from Groq for query: '{query[:50]}...'. Attempt {attempt + 1}")
            start_time = time.time()
            stream = client.chat.completions.create(
                messages=messages,
                model=model_name,
                temperature=0.1,
                max_tokens=2048,
                top_p=0.9,
                stream=True,
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
            end_time = time.time()
            logger.info(f"Groq stream completed in {end_time - start_time:.2f} seconds.")
            return

        except GroqError as e:
            logger.error(f"Groq API error on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise LLMAnalysisError(f"Groq API Error after multiple retries: {e}")
            time.sleep(retry_delay * (attempt + 1))
        except Exception as e:
            logger.error(f"An unexpected error occurred during LLM request: {e}", exc_info=True)
            raise LLMAnalysisError(f"An unexpected error occurred: {e}")