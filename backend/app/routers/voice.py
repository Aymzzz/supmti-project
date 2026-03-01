"""
Voice API router – handles TTS (Text-to-Speech).
STT is handled client-side via Web Speech API.
"""

from fastapi import APIRouter, Response, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from openai import AsyncOpenAI

from app.services.voice_service import voice_service
from app.config import settings

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

import io
import speech_recognition as sr

@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: str = Form("fr")
):
    """Transcribe uploaded pure WAV audio using free Google STT in memory!"""
    # Map 'fr' -> 'fr-FR', 'en' -> 'en-US', 'darija' -> 'ar-MA'
    lang_map = {
        "fr": "fr-FR",
        "en": "en-US",
        "darija": "ar-MA"
    }
    stt_lang = lang_map.get(language, "fr-FR")

    try:
        # Read the raw WAV bytes sent from the frontend AudioContext encoder
        content = await audio.read()
        
        recognizer = sr.Recognizer()
        
        # We can read the bytes straight into AudioFile, no temp files, no WinError 32 File Lock bugs!
        with sr.AudioFile(io.BytesIO(content)) as source:
            audio_data = recognizer.record(source)
            transcript = recognizer.recognize_google(audio_data, language=stt_lang)
            
        return {"transcript": transcript}
        
    except sr.UnknownValueError:
        # Could not understand the voice
        return {"transcript": ""}
    except sr.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Google Speech Recognition API error: {e}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
