"""
Supabase persistence helpers for chat sessions and message history.
"""

from typing import Any, Dict, List, Optional
import importlib

from app.config import settings

supabase_module = None
create_client = None  # type: ignore

try:
    supabase_module = importlib.import_module("supabase")
    create_client = getattr(supabase_module, "create_client", None)
except Exception:
    supabase_module = None

Client = Any


class SupabaseChatPersistence:
    """Persists chat sessions/messages in Supabase when enabled."""

    def __init__(self):
        self._enabled = (
            settings.use_supabase_chat_history
            and bool(settings.supabase_url)
            and bool(settings.supabase_key)
            and create_client is not None
        )
        self._client: Optional[Client] = None

        if self._enabled:
            try:
                self._client = create_client(settings.supabase_url, settings.supabase_key)
                print("✅ Supabase chat persistence enabled")
            except Exception as exc:
                self._enabled = False
                self._client = None
                print(f"⚠️ Supabase init failed, using in-memory chat only: {exc}")

    @property
    def enabled(self) -> bool:
        return self._enabled and self._client is not None

    def ensure_session(self, session_id: str, title: Optional[str] = None) -> None:
        if not self.enabled:
            return

        existing = (
            self._client.table("chat_sessions")
            .select("id")
            .eq("id", session_id)
            .limit(1)
            .execute()
        )
        if existing.data:
            return

        payload = {"id": session_id}
        if title:
            payload["title"] = title

        self._client.table("chat_sessions").insert(payload).execute()

    def add_message(self, session_id: str, role: str, content: str) -> None:
        if not self.enabled:
            return

        self._client.table("chat_messages").insert(
            {
                "session_id": session_id,
                "role": role,
                "content": content,
            }
        ).execute()

    def get_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        if not self.enabled:
            return []

        result = (
            self._client.table("chat_messages")
            .select("role,content,created_at")
            .eq("session_id", session_id)
            .order("created_at")
            .limit(limit)
            .execute()
        )

        rows = result.data or []
        return [
            {
                "role": row.get("role", "assistant"),
                "content": row.get("content", ""),
                "timestamp": row.get("created_at", ""),
                "metadata": {},
            }
            for row in rows
        ]

    def list_sessions(self, limit: int = 20) -> List[Dict]:
        if not self.enabled:
            return []

        result = (
            self._client.table("chat_sessions")
            .select("id,title,created_at")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []


supabase_chat_persistence = SupabaseChatPersistence()
