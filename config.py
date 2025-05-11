import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "AI Research Paper Analyzer (Streamlit)"
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3-70b-8192") # Or user's llama-3.3-70b-versatile if valid

    UPLOAD_DIR: str = "temp_uploaded_pdfs"
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR, exist_ok=True) # Ensure directory exists

    ANALYSIS_OPTIONS = {
        "summary": "📄 Comprehensive Summary",
        "critical_analysis": "🧐 Critical Analysis",
        "gaps": "🔍 Research Gaps",
        "suggestions": "💡 Future Work & Suggestions"
    }

    # New settings for chunking
    # Target characters per chunk. ~4 chars/token. Aim for ~4000-5000 tokens per chunk payload.
    # If prompt is ~1000-1500 tokens, text chunk should be ~2500-3500 tokens.
    # 3000 tokens * 4 chars/token = 12000 characters per chunk.
    CHUNK_TARGET_CHAR_COUNT: int = 12000
    CHUNK_OVERLAP_CHAR_COUNT: int = 500 # Overlap to maintain context between chunks

settings = Settings()

if not settings.GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found. Please set it in your .env file.")