"""
SupMTI Intelligent Chatbot – FastAPI Backend
Main application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.routers import chat, voice, eligibility, recommend


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup and cleanup on shutdown."""
    # Startup: Initialize vector store
    from app.rag.vectorstore import VectorStore
    vector_store = VectorStore()
    app.state.vector_store = vector_store
    print("✅ Vector store initialized")

    # Initialize RAG pipeline
    from app.rag.pipeline import RAGPipeline
    pipeline = RAGPipeline(vector_store)
    app.state.rag_pipeline = pipeline
    print("✅ RAG pipeline ready")

    yield

    # Shutdown: cleanup
    print("👋 Shutting down SupMTI Chatbot API")


app = FastAPI(
    title="SupMTI Intelligent Chatbot API",
    description="AI-powered chatbot for student orientation at SupMTI. "
                "Supports text & voice interaction in Darija, French, and English.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(voice.router, prefix="/api/voice", tags=["Voice"])
app.include_router(eligibility.router, prefix="/api/eligibility", tags=["Eligibility"])
app.include_router(recommend.router, prefix="/api/recommend", tags=["Recommendation"])


@app.get("/")
async def root():
    return {
        "name": "SupMTI Intelligent Chatbot API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
