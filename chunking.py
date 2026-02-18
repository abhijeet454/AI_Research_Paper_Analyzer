# chunking.py

import numpy as np
from sentence_transformers import SentenceTransformer
from scipy.signal import find_peaks
import pysbd  # <-- IMPORT THE NEW LIBRARY
import logging

logger = logging.getLogger(__name__)

class SemanticChunker:
    """Splits text into chunks based on semantic similarity."""
    def __init__(self, embedding_model: SentenceTransformer):
        self.model = embedding_model
        # Initialize the sentence segmenter from pysbd
        self.segmenter = pysbd.Segmenter(language="en", clean=False)

    # The problematic _ensure_nltk_punkt method has been completely removed.

    def _calculate_distances(self, embeddings: np.ndarray) -> np.ndarray:
        """Calculates the cosine distance between consecutive sentence embeddings."""
        distances = []
        for i in range(len(embeddings) - 1):
            # Normalize embeddings to unit vectors for cosine similarity calculation
            norm_embed_i = embeddings[i] / np.linalg.norm(embeddings[i])
            norm_embed_i_plus_1 = embeddings[i+1] / np.linalg.norm(embeddings[i+1])
            dist = 1 - np.dot(norm_embed_i, norm_embed_i_plus_1)
            distances.append(dist)
        return np.array(distances)

    def chunk(self, text: str, percentile_threshold: int = 95) -> list[str]:
        """Chunks the text based on semantic breakpoints."""
        # Use the new library to split sentences
        sentences = self.segmenter.segment(text)

        if len(sentences) < 3:
            return [text]

        embeddings = self.model.encode(sentences, convert_to_numpy=True)
        distances = self._calculate_distances(embeddings)
        
        if len(distances) == 0:
            return [text]

        threshold = np.percentile(distances, percentile_threshold)
        split_points, _ = find_peaks(distances, height=threshold)

        chunks = []
        start_idx = 0
        for point in split_points:
            end_idx = point + 1
            chunks.append(" ".join(sentences[start_idx:end_idx]))
            start_idx = end_idx

        # Add the final chunk
        chunks.append(" ".join(sentences[start_idx:]))
        
        # Filter out very small chunks
        return [chunk for chunk in chunks if len(chunk.split()) > 10]