"""
Application configuration loaded from environment variables.
"""

from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    # APIs
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openai_api_key: str = ""
    fallback_api_key: str = ""
    fallback_base_url: str = ""

    # Model Configuration
    primary_model: str = "openai/gpt-4o-mini"
    fallback_model: str = "meta-llama/llama-3.3-70b-instruct"
    # Use multilingual embedding so English questions can match French database texts
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"

    # ChromaDB (fallback/local)
    chroma_persist_dir: str = "./chroma_db"
    chroma_collection_name: str = "supmti_knowledge"

    # Supabase (Database & Vector Store)
    supabase_url: str = ""
    supabase_key: str = ""
    supabase_db_password: str = ""  # For direct Postgres connection if needed
    use_supabase_chat_history: bool = False

    # RAG
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k_results: int = 5
    temperature: float = 0.3

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = '["http://localhost:3000","http://localhost:3001"]'

    # Voice
    edge_tts_voice_fr: str = "fr-FR-DeniseNeural"
    edge_tts_voice_en: str = "en-US-JennyNeural"
    edge_tts_voice_ar: str = "ar-MA-MounaNeural"

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.cors_origins)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
