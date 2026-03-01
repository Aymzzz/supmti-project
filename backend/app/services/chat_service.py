"""
Chat service – manages conversation sessions and message history.
"""

from typing import Dict, List, Optional
from datetime import datetime
import uuid


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
        self._sessions[session.session_id] = session
        return session

    def delete_session(self, session_id: str) -> bool:
        """Delete a chat session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False


# Global instance
chat_service = ChatService()
