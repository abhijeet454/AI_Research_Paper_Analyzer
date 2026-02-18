# rag_utils.py

import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import logging
from config import settings

logger = logging.getLogger(__name__)

class RAGVectorStore:
    def __init__(self):
        """Initializes the RAG vector store."""
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        self.d = self.embedding_model.get_sentence_embedding_dimension()
        self.documents = []  # Will store {'text': chunk, 'source': filename}
        self.index = faiss.IndexFlatL2(self.d)
        logger.info(f"Initialized FAISS index with dimension {self.d}.")

    def add_texts(self, texts: list[str], source: str):
        """Adds a list of text chunks from a specific source to the vector store."""
        valid_texts = [text for text in texts if text and not text.isspace()]
        if not valid_texts:
            logger.warning(f"add_texts called with no valid text content for source: {source}.")
            return

        logger.info(f"Encoding and adding {len(valid_texts)} new chunks from '{source}' to the index.")
        # OPTIMIZATION: encode_multi_process is faster for large numbers of chunks
        embeddings = self.embedding_model.encode(valid_texts, convert_to_numpy=True, show_progress_bar=False)
        self.index.add(embeddings.astype('float32'))
        
        for text in valid_texts:
            self.documents.append({'text': text, 'source': source})
            
        logger.info(f"Index now contains {self.index.ntotal} total vectors.")

    def query(self, query_text: str, top_k: int = settings.TOP_K) -> list[dict]:
        """Queries the vector store to find the most relevant document chunks."""
        if self.index.ntotal == 0:
            logger.warning("Query attempted on an empty index.")
            return []

        logger.info(f"Performing query for top {top_k} results.")
        query_emb = self.embedding_model.encode([query_text], convert_to_numpy=True).astype('float32')
        distances, indices = self.index.search(query_emb, top_k)
        
        # Ensure indices are within the valid range
        results = [self.documents[i] for i in indices[0] if 0 <= i < len(self.documents)]
        return results

    def clear(self):
        """Resets the vector store to its initial empty state."""
        self.documents = []
        self.index.reset() # Use reset() for a clean wipe
        logger.info("RAG vector store has been cleared.")