import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # --- Project Info ---
    PROJECT_NAME: str = "FlowChat: AquaQuery Oceanographic Assistant"

    # --- API Keys & Models ---
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3-70b-8192")

    # --- File Handling ---
    UPLOAD_DIR: str = "temp_uploaded_pdfs"

    # --- RAG Configuration ---
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    TOP_K: int = 5 # Number of relevant chunks to retrieve

settings = Settings()

# --- Initial Setup ---
if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

if not settings.GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found. Please set it in your .env file or as an environment variable.")