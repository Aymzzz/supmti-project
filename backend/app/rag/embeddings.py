"""
Embedding model wrapper using sentence-transformers.
Runs locally — zero API cost.
"""

from sentence_transformers import SentenceTransformer
from typing import List
from app.config import settings


class EmbeddingModel:
    """Wrapper around sentence-transformers for generating embeddings."""

    _instance = None

    def __new__(cls):
        """Singleton pattern — only load the model once."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._model = None
        return cls._instance

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            print(f"📦 Loading embedding model: {settings.embedding_model}")
            self._model = SentenceTransformer(settings.embedding_model)
            print("✅ Embedding model loaded")
        return self._model

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        return self.model.encode(text, normalize_embeddings=True).tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return [e.tolist() for e in embeddings]

    def embed_query(self, query: str) -> List[float]:
        """Alias for embed_text — used for search queries."""
        return self.embed_text(query)


# Global instance
embedding_model = EmbeddingModel()
