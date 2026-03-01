"""
RAG Pipeline – Orchestrates the full retrieve-augment-generate flow.
"""

from typing import List, Dict, Optional, AsyncGenerator

from app.rag.vectorstore import VectorStore
from app.rag.retriever import HybridRetriever
from app.rag.generator import LLMGenerator


class RAGPipeline:
    """
    Full RAG pipeline: Query → Retrieve → Augment → Generate
    """

    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.retriever = HybridRetriever(vector_store)
        self.generator = LLMGenerator()

    async def query(
        self,
        question: str,
        conversation_history: Optional[List[Dict]] = None,
        language: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Dict:
        """
        Process a user question through the full RAG pipeline.

        Returns:
            Dict with 'answer', 'sources', and 'language'
        """
        # 1. Retrieve relevant documents (search across all languages)
        retrieved_docs = self.retriever.retrieve(
            query=question,
            category=category,
        )

        # 2. Generate response with context
        answer = await self.generator.generate(
            query=question,
            retrieved_docs=retrieved_docs,
            conversation_history=conversation_history,
            language=language or "fr",
        )

        # 3. Extract source metadata
        sources = [
            {
                "source": doc.get("metadata", {}).get("source", ""),
                "category": doc.get("metadata", {}).get("category", ""),
                "score": doc.get("score", 0),
            }
            for doc in retrieved_docs
        ]

        return {
            "answer": answer,
            "sources": sources,
            "language": language or "auto",
            "num_docs_retrieved": len(retrieved_docs),
        }

    async def query_stream(
        self,
        question: str,
        conversation_history: Optional[List[Dict]] = None,
        language: Optional[str] = None,
        category: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream a response through the RAG pipeline.
        Yields tokens as they are generated.
        """
        # 1. Retrieve relevant documents (search all languages)
        retrieved_docs = self.retriever.retrieve(
            query=question,
            category=category,
        )

        # 2. Stream generation
        async for token in self.generator.generate_stream(
            query=question,
            retrieved_docs=retrieved_docs,
            conversation_history=conversation_history,
            language=language or "fr",
        ):
            yield token
