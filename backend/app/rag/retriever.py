"""
Hybrid retriever combining semantic search with BM25 keyword matching.
Includes re-ranking for better accuracy.
"""

from typing import List, Dict, Optional, Tuple
from rank_bm25 import BM25Okapi
import re

from app.rag.vectorstore import VectorStore
from app.config import settings


class HybridRetriever:
    """
    Combines ChromaDB semantic search with BM25 keyword search
    for higher retrieval accuracy. Optionally re-ranks results.
    """

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    def _normalize_text(self, text: str) -> str:
        """Normalize text for BM25 tokenization."""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        return text

    def _bm25_search(
        self,
        query: str,
        documents: List[str],
        top_k: int = 5
    ) -> List[Tuple[int, float]]:
        """Perform BM25 keyword search on a list of documents."""
        tokenized_docs = [
            self._normalize_text(doc).split()
            for doc in documents
        ]
        bm25 = BM25Okapi(tokenized_docs)
        tokenized_query = self._normalize_text(query).split()
        scores = bm25.get_scores(tokenized_query)

        # Return indices and scores sorted by score
        indexed_scores = list(enumerate(scores))
        indexed_scores.sort(key=lambda x: x[1], reverse=True)
        return indexed_scores[:top_k]

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        language: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[Dict]:
        """
        Hybrid retrieval: semantic + BM25 with score fusion.

        Args:
            query: User question
            top_k: Number of results to return
            language: Filter by language (fr, en, darija)
            category: Filter by category (programs, admissions, general)

        Returns:
            List of relevant document chunks with metadata
        """
        if top_k is None:
            top_k = settings.top_k_results

        # Build metadata filter
        where = None
        if language or category:
            conditions = []
            if language:
                conditions.append({"language": language})
            if category:
                conditions.append({"category": category})

            if len(conditions) == 1:
                where = conditions[0]
            else:
                where = {"$and": conditions}

        # 1. Semantic search via ChromaDB
        semantic_results = self.vector_store.search(
            query=query,
            top_k=top_k * 2,  # Over-fetch for re-ranking
            where=where,
        )

        if not semantic_results["documents"] or not semantic_results["documents"][0]:
            return []

        documents = semantic_results["documents"][0]
        metadatas = semantic_results["metadatas"][0]
        distances = semantic_results["distances"][0]

        # 2. BM25 re-ranking on the semantic results
        bm25_scores = self._bm25_search(query, documents, top_k=len(documents))
        bm25_score_map = {idx: score for idx, score in bm25_scores}

        # 3. Score fusion (weighted combination)
        fused_results = []
        for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
            semantic_score = 1 - dist  # Convert distance to similarity
            bm25_score = bm25_score_map.get(i, 0)

            # Normalize BM25 score
            max_bm25 = max((s for _, s in bm25_scores), default=1) or 1
            normalized_bm25 = bm25_score / max_bm25

            # Weighted fusion: 60% semantic, 40% BM25
            fused_score = 0.6 * semantic_score + 0.4 * normalized_bm25

            fused_results.append({
                "content": doc,
                "metadata": meta,
                "score": round(fused_score, 4),
                "semantic_score": round(semantic_score, 4),
                "bm25_score": round(normalized_bm25, 4),
            })

        # Sort by fused score and return top_k
        fused_results.sort(key=lambda x: x["score"], reverse=True)
        return fused_results[:top_k]
