"""
ChromaDB vector store for document storage and retrieval.
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional
import hashlib

from app.config import settings
from app.rag.embeddings import embedding_model


class VectorStore:
    """ChromaDB-backed vector store for the RAG knowledge base."""

    def __init__(self):
        self._client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        print(f"📚 ChromaDB collection '{settings.chroma_collection_name}' "
              f"has {self._collection.count()} documents")

    @property
    def collection(self):
        return self._collection

    @property
    def count(self) -> int:
        return self._collection.count()

    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        """Add documents to the vector store."""
        if ids is None:
            ids = [
                hashlib.md5(text.encode()).hexdigest()
                for text in texts
            ]

        # Generate embeddings locally
        embeddings = embedding_model.embed_texts(texts)

        self._collection.upsert(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas or [{}] * len(texts),
            ids=ids,
        )
        print(f"✅ Added {len(texts)} documents to vector store")

    def search(
        self,
        query: str,
        top_k: int = None,
        where: Optional[Dict] = None,
    ) -> Dict:
        """Search the vector store for relevant documents."""
        if top_k is None:
            top_k = settings.top_k_results

        query_embedding = embedding_model.embed_query(query)

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        return results

    def delete_collection(self) -> None:
        """Delete and recreate the collection (for re-ingestion)."""
        self._client.delete_collection(settings.chroma_collection_name)
        self._collection = self._client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        print("🗑️ Collection reset")
