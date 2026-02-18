# preloaded_data.py

import os
import logging
from pdf_utils import extract_text_from_pdf, PDFParsingError
from chunking import SemanticChunker
from rag_utils import RAGVectorStore

logger = logging.getLogger(__name__)
DATA_DIR = "data"

def preload_data_to_store(rag_store: RAGVectorStore) -> list[str]:
    """
    Scans DATA_DIR, processes files, chunks them semantically, and adds them to the rag_store.
    Returns a list of filenames that were successfully processed.
    """
    processed_filenames = []
    if not os.path.exists(DATA_DIR):
        logger.warning(f"Preload data directory not found: '{DATA_DIR}'. Skipping preloading.")
        return []

    logger.info("--- Starting preloading process ---")
    chunker = SemanticChunker(rag_store.embedding_model)
    files_to_process = [f for f in os.listdir(DATA_DIR) if f.endswith((".pdf", ".txt", ".md"))]

    if not files_to_process:
        logger.info("No supported files (.pdf, .txt, .md) found in the 'data' directory.")
        return []

    for filename in files_to_process:
        file_path = os.path.join(DATA_DIR, filename)
        content = ""
        try:
            logger.info(f"Processing '{filename}'...")
            if filename.endswith(".pdf"):
                content = extract_text_from_pdf(file_path)
            else: # For .txt and .md
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

            if content.strip():
                chunks = chunker.chunk(content)
                if chunks:
                    rag_store.add_texts(chunks, source=filename)
                    logger.info(f"Successfully processed and chunked '{filename}' into {len(chunks)} semantic chunks.")
                    processed_filenames.append(filename)
                else:
                    logger.warning(f"Could not generate any chunks from '{filename}'. It may be too short.")
            else:
                logger.warning(f"No content extracted from '{filename}'.")

        except (PDFParsingError, Exception) as e:
            logger.error(f"Failed to process preloaded file {file_path}: {e}")
            
    logger.info(f"--- Preloading complete. Processed {len(processed_filenames)} files. ---")
    return processed_filenames