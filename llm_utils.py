from groq import Groq, GroqError
from config import settings
import logging
import time
import streamlit as st

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

client = Groq(api_key=settings.GROQ_API_KEY)

class LLMAnalysisError(Exception):
    """Custom exception for LLM analysis errors."""
    pass

def split_text_into_chunks(text: str, target_char_count: int = settings.CHUNK_TARGET_CHAR_COUNT, overlap_char_count: int = settings.CHUNK_OVERLAP_CHAR_COUNT) -> list[str]:
    """
    Splits text into chunks with specified target size and overlap, preferring paragraph breaks.
    
    Args:
        text: The text to split.
        target_char_count: Target size of each chunk in characters.
        overlap_char_count: Number of characters to overlap between chunks.
    
    Returns:
        List of text chunks.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + target_char_count
        if end < len(text):
            split_point = text.rfind('\n\n', start, end)
            if split_point == -1 or split_point < start:
                split_point = end
            else:
                split_point += 2  # After the '\n\n'
        else:
            split_point = len(text)
        chunk = text[start:split_point]
        chunks.append(chunk)
        start = split_point - overlap_char_count if split_point - overlap_char_count > start else split_point
    return chunks

def get_llm_analysis(paper_text: str, analysis_type: str, model_name: str = settings.LLM_MODEL, streamlit_status_placeholder=None) -> str:
    """
    Performs a specified analysis on the paper text using Groq LLM, processing in chunks if necessary.

    Args:
        paper_text: The full text of the research paper.
        analysis_type: Type of analysis ("summary", "critical_analysis", "gaps", "suggestions").
        model_name: The LLM model to use (e.g., "llama3-70b-8192").
        streamlit_status_placeholder: Optional Streamlit container for status updates.

    Returns:
        The LLM's generated analysis.

    Raises:
        LLMAnalysisError if the API call fails or returns an error.
    """
    if not paper_text.strip():
        logger.error("LLM analysis attempted on empty paper text.")
        raise LLMAnalysisError("Cannot analyze empty paper text.")

    system_prompt = (
        "You are an exceptionally intelligent and meticulous AI Research Analyzer. "
        "Your expertise lies in dissecting academic papers to provide insightful, structured, and actionable analysis. "
        "Adhere strictly to the requested format and depth for each analysis type. "
        "Ensure your language is precise, academic, and objective."
    )

    user_prompt_templates = {
        "summary": """
        **Task: Comprehensive Academic Summary**

        Based on the following excerpt from a research paper, generate a comprehensive academic summary for this part. The summary MUST cover these distinct sections:
        1.  **Primary Research Objectives:** Clearly state the main questions or goals the authors aimed to address.
        2.  **Core Methodological Approach:** Describe the key methods, experimental design, data sources, and analytical techniques employed. Be specific.
        3.  **Key Findings and Results:** Detail the most significant outcomes and data-supported discoveries. Quantify where possible.
        4.  **Principal Conclusions and Implications:** Articulate the main takeaways, the authors' interpretations, and the broader implications of the research for the field.
        5.  **Novelty/Contribution:** Briefly state what is new or innovative about this work.

        Ensure the summary is well-structured, using markdown for headings for each section.

        Research Paper Text (excerpt):
        ---
        {text}
        ---
        **Formatted Academic Summary:**
        """,
        "critical_analysis": """
        **Task: In-Depth Critical Analysis**

        Conduct a rigorous critical analysis of the provided excerpt from a research paper. Your analysis MUST be structured into the following sections, using markdown headings:
        1.  **Clarity and Definition of Research Problem/Questions:** Evaluate how clearly the research problem, questions, or hypotheses are defined and justified.
        2.  **Methodological Rigor and Appropriateness:** Assess suitability, identify flaws, limitations, biases.
        3.  **Validity and Reliability of Findings:** Critique presentation and interpretation of results.
        4.  **Significance and Contribution to the Field:** Evaluate novelty and impact.
        5.  **Overall Strengths and Weaknesses:** Summarize major strengths and weaknesses.

        Research Paper Text (excerpt):
        ---
        {text}
        ---
        **Formatted Critical Analysis:**
        """,
        "gaps": """
        **Task: Identification of Specific Research Gaps**

        Based on the provided excerpt from a research paper, identify specific, actionable research gaps for this part. Present as a numbered list with:
        a. A clear statement of the gap.
        b. A brief justification referencing specific aspects of the text.

        Research Paper Text (excerpt):
        ---
        {text}
        ---
        **Identified Research Gaps (Numbered List):**
        """,
        "suggestions": """
        **Task: Constructive Suggestions for Future Research and Enhancements**

        Drawing upon the provided excerpt from a research paper, generate suggestions:
        **I. Suggestions for Future Research Projects (Minimum 3):**
            1. Proposed Research Direction
            2. Rationale & Link to Current Paper
            3. Potential Impact & Contribution
        **II. Suggestions for Enhancing the Current Study:**
            1. Proposed Enhancement(s)
            2. Justification

        Research Paper Text (excerpt):
        ---
        {text}
        ---
        **Constructive Suggestions:**
        """
    }

    if analysis_type not in user_prompt_templates:
        logger.error(f"Invalid analysis type requested: {analysis_type}")
        raise LLMAnalysisError(f"Invalid analysis type: {analysis_type}")

    chunks = split_text_into_chunks(paper_text)
    analysis_parts = []
    max_retries = 3
    retry_delay = 5  # seconds

    for i, chunk in enumerate(chunks, 1):
        if streamlit_status_placeholder:
            streamlit_status_placeholder.info(f"Processing chunk {i} of {len(chunks)} for {settings.ANALYSIS_OPTIONS[analysis_type]}...")
        user_content = user_prompt_templates[analysis_type].format(text=chunk)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Requesting '{analysis_type}' for chunk {i} from Groq LLM (Model: {model_name}). Attempt {attempt + 1}")
                start_time = time.time()
                chat_completion = client.chat.completions.create(
                    messages=messages,
                    model=model_name,
                    temperature=0.4,
                    max_tokens=3500,
                    top_p=0.9,
                )
                end_time = time.time()
                logger.info(f"Groq API call for '{analysis_type}' chunk {i} completed in {end_time - start_time:.2f} seconds.")
                response_content = chat_completion.choices[0].message.content
                
                if not response_content.strip() and attempt == max_retries - 1:
                    raise LLMAnalysisError(f"LLM returned empty response for chunk {i} after {max_retries} attempts.")
                elif not response_content.strip():
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                
                analysis_parts.append(f"**Analysis of Chunk {i}:**\n\n{response_content}")
                break
            except GroqError as e:
                logger.error(f"Groq API error for chunk {i}, attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    analysis_parts.append(f"**Error in Chunk {i} after {max_retries} attempts:** {str(e)}")
                time.sleep(retry_delay * (attempt + 1))
    
    full_analysis = f"**Note:** The following analysis is based on processing the document in chunks due to its length.\n\n"
    full_analysis += "\n\n---\n\n".join(analysis_parts)
    return full_analysis