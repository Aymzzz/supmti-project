"""
Chat service – manages conversation sessions and message history.
"""

from typing import Dict, List, Optional
from datetime import datetime
import uuid

from app.services.supabase_service import supabase_chat_persistence


class ChatSession:
    """Represents a single chat conversation."""

    def __init__(self, session_id: str = None, language: str = "fr"):
        self.session_id = session_id or str(uuid.uuid4())
        self.language = language
        self.messages: List[Dict] = []
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.user_profile: Optional[Dict] = None

    def add_message(self, role: str, content: str, metadata: Dict = None):
        """Add a message to the conversation history."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        })
        self.updated_at = datetime.utcnow()

    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation history."""
        return self.messages[-limit:]

    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "language": self.language,
            "messages": self.messages,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "user_profile": self.user_profile,
        }


class ChatService:
    """Manages chat sessions (in-memory for now)."""

    def __init__(self):
        self._sessions: Dict[str, ChatSession] = {}
        self._persistence = supabase_chat_persistence

    def create_session(self, language: str = "fr") -> ChatSession:
        """Create a new chat session."""
        session = ChatSession(language=language)
        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get an existing session by ID."""
        return self._sessions.get(session_id)

    def get_or_create_session(
        self, session_id: str = None, language: str = "fr"
    ) -> ChatSession:
        """Get existing session or create a new one."""
        if session_id and session_id in self._sessions:
            return self._sessions[session_id]

        session = ChatSession(session_id=session_id, language=language)

        if self._persistence.enabled:
            try:
                self._persistence.ensure_session(session.session_id)
                persisted_history = self._persistence.get_history(session.session_id, limit=50)
                if persisted_history:
                    session.messages = persisted_history
            except Exception as exc:
                print(f"⚠️ Failed loading Supabase chat history: {exc}")

        self._sessions[session.session_id] = session
        return session

    def persist_message(self, session_id: str, role: str, content: str) -> None:
        """Persist a chat message if Supabase persistence is enabled."""
        if not self._persistence.enabled:
            return
        try:
            self._persistence.ensure_session(session_id)
            self._persistence.add_message(session_id, role, content)
        except Exception as exc:
            print(f"⚠️ Failed persisting chat message: {exc}")

    def get_persisted_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get persisted history from Supabase (falls back to in-memory)."""
        if self._persistence.enabled:
            try:
                persisted = self._persistence.get_history(session_id, limit=limit)
                if persisted:
                    return persisted
            except Exception as exc:
                print(f"⚠️ Failed loading persisted history: {exc}")

        session = self.get_session(session_id)
        if not session:
            return []
        return session.get_history(limit=limit)

    def list_persisted_sessions(self, limit: int = 20) -> List[Dict]:
        """List sessions from Supabase if enabled, otherwise from memory."""
        if self._persistence.enabled:
            try:
                return self._persistence.list_sessions(limit=limit)
            except Exception as exc:
                print(f"⚠️ Failed listing persisted sessions: {exc}")

        sessions = list(self._sessions.values())
        sessions.sort(key=lambda s: s.updated_at, reverse=True)
        return [
            {
                "id": s.session_id,
                "title": None,
                "created_at": s.created_at.isoformat(),
                "updated_at": s.updated_at.isoformat(),
            }
            for s in sessions[:limit]
        ]

    def delete_session(self, session_id: str) -> bool:
        """Delete a chat session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False


# Global instance
chat_service = ChatService()
