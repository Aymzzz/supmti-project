"""
Voice API router – handles TTS (Text-to-Speech).
STT is handled client-side via Web Speech API.
"""

from fastapi import APIRouter, Response
from pydantic import BaseModel, Field
from typing import Optional

from app.services.voice_service import voice_service

router = APIRouter()


class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to synthesize to speech")
    language: str = Field("fr", description="Language (fr, en, darija)")


@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech audio (MP3)."""
    audio_bytes = await voice_service.text_to_speech_bytes(
        text=request.text,
        language=request.language,
    )

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline; filename=speech.mp3",
        },
    )


@router.get("/voices")
async def list_voices(language: Optional[str] = None):
    """List available TTS voices."""
    voices = await voice_service.list_voices(language_filter=language)
    return {"voices": voices[:20]}  # Limit to 20
