"""
Chat API router – handles text chat via REST and WebSocket (streaming).
"""

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

from app.services.chat_service import chat_service
from app.services.language_service import language_service

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message")
    session_id: Optional[str] = Field(None, description="Chat session ID")
    language: Optional[str] = Field(None, description="Language override (fr, en, darija)")


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    language: str
    sources: List[Dict] = []
    num_docs_retrieved: int = 0


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[Dict]


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, req: Request):
    """Send a message and get a response from the chatbot."""
    # Get or create session
    session = chat_service.get_or_create_session(
        session_id=request.session_id,
        language=request.language or "fr",
    )

    # Detect language if not specified
    detected_lang = request.language or language_service.detect(request.message)
    session.language = detected_lang

    # Add user message to history
    session.add_message("user", request.message)
    chat_service.persist_message(session.session_id, "user", request.message)

    # Get RAG pipeline from app state
    pipeline = req.app.state.rag_pipeline

    # Query the RAG pipeline
    result = await pipeline.query(
        question=request.message,
        conversation_history=session.get_history(),
        language=detected_lang,
    )

    # Add assistant response to history
    session.add_message("assistant", result["answer"], {
        "sources": result["sources"],
    })
    chat_service.persist_message(session.session_id, "assistant", result["answer"])

    return ChatResponse(
        answer=result["answer"],
        session_id=session.session_id,
        language=detected_lang,
        sources=result["sources"],
        num_docs_retrieved=result["num_docs_retrieved"],
    )


@router.get("/chat/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(session_id: str, limit: int = 50):
    """Fetch stored message history for a session."""
    history = chat_service.get_persisted_history(session_id=session_id, limit=limit)
    return ChatHistoryResponse(session_id=session_id, messages=history)


@router.get("/chat/sessions")
async def list_chat_sessions(limit: int = 20):
    """List available sessions (Supabase if enabled, else in-memory)."""
    return {"sessions": chat_service.list_persisted_sessions(limit=limit)}


@router.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket):
    """WebSocket endpoint for streaming chat responses."""
    await websocket.accept()

    session_id = None

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message = data.get("message", "")
            session_id = data.get("session_id", session_id)
            language = data.get("language")

            if not message:
                await websocket.send_json({"error": "Empty message"})
                continue

            # Get or create session
            session = chat_service.get_or_create_session(
                session_id=session_id,
                language=language or "fr",
            )
            session_id = session.session_id

            # Detect language
            detected_lang = language or language_service.detect(message)

            # Add user message
            session.add_message("user", message)
            chat_service.persist_message(session.session_id, "user", message)

            # Get RAG pipeline
            pipeline = websocket.app.state.rag_pipeline

            # Stream response
            full_response = ""
            await websocket.send_json({
                "type": "start",
                "session_id": session_id,
                "language": detected_lang,
            })

            async for token in pipeline.query_stream(
                question=message,
                conversation_history=session.get_history(),
                language=detected_lang,
            ):
                full_response += token
                await websocket.send_json({
                    "type": "token",
                    "content": token,
                })

            # Add to history
            session.add_message("assistant", full_response)
            chat_service.persist_message(session.session_id, "assistant", full_response)

            await websocket.send_json({
                "type": "end",
                "full_response": full_response,
            })

    except WebSocketDisconnect:
        print(f"WebSocket disconnected: session {session_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()
