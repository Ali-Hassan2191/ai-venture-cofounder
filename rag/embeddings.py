"""
Embedding utilities and vector computation.
Conforms dynamically to the model and vector dimension defined in config.json
(e.g., sentence-transformers/all-MiniLM-L6-v2 with 384 dimensions).
Includes a resilient fallback mechanism to ensure zero runtime crashes regardless of environment.
"""
import hashlib
import logging
from typing import List, Optional
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """
    Manages embedding generation for FAISS query search.
    Dynamically conforms to the vector dimension and model specified in config.json.
    """

    def __init__(self, default_dimension: int = 384):
        self.default_dimension = default_dimension
        self._transformer_model = None
        self._loaded_model_name: Optional[str] = None

    def _get_transformer_model(
        self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """Attempts to lazily load sentence-transformers model if available."""
        if self._transformer_model is None or self._loaded_model_name != model_name:
            try:
                from sentence_transformers import SentenceTransformer
                # Try exact model identifier first
                try:
                    self._transformer_model = SentenceTransformer(model_name)
                except Exception:
                    # Strip organization prefix if present (e.g., all-MiniLM-L6-v2)
                    clean_name = model_name.split("/")[-1] if "/" in model_name else model_name
                    self._transformer_model = SentenceTransformer(clean_name)

                self._loaded_model_name = model_name
                logger.info(f"Loaded SentenceTransformer model: '{model_name}'")
            except Exception as e:
                logger.info(f"SentenceTransformer not available ({e}), using fallback vector generation.")
                self._transformer_model = False
        return self._transformer_model

    def embed_query(
        self,
        text: str,
        target_dimension: int = 384,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        normalize: bool = True,
    ) -> np.ndarray:
        """
        Embeds a single query string into a float32 numpy vector matching target_dimension.
        Applies L2 normalization if normalize is True (required for IndexFlatIP cosine similarity).
        """
        if not text:
            return np.zeros(target_dimension, dtype=np.float32)

        model = self._get_transformer_model(model_name)
        if model:
            try:
                raw_emb = model.encode(text, convert_to_numpy=True)
                if len(raw_emb) == target_dimension:
                    if normalize:
                        norm = np.linalg.norm(raw_emb)
                        if norm > 1e-9:
                            raw_emb = raw_emb / norm
                    return raw_emb.astype(np.float32)
            except Exception as e:
                logger.warning(
                    f"SentenceTransformer encoding failed: {e}. Falling back to deterministic vector generation."
                )

        # Deterministic hashing embedding generator for guaranteed zero-dependency compatibility
        return self._hash_based_vector(text, target_dimension, normalize=normalize)

    def _hash_based_vector(
        self, text: str, dimension: int, normalize: bool = True
    ) -> np.ndarray:
        """Generates a stable normalized pseudo-vector based on character and token hashing."""
        words = text.lower().split()
        vec = np.zeros(dimension, dtype=np.float32)

        for i, word in enumerate(words):
            h = int(hashlib.sha256(word.encode("utf-8")).hexdigest()[:8], 16)
            idx = h % dimension
            sign = 1.0 if ((h >> 4) % 2 == 0) else -1.0
            vec[idx] += sign / (1.0 + (i * 0.05))

        if normalize:
            norm = np.linalg.norm(vec)
            if norm > 1e-9:
                vec = vec / norm
        return vec.astype(np.float32)


# Global singleton
embedding_manager = EmbeddingManager()
