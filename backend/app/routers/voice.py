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
        print(f"DEBUG STT: Received {len(content)} bytes of audio for language {stt_lang}")
        
        # Save exact received bytes to disk for inspection
        import os
        debug_path = os.path.join(os.getcwd(), "debug_stt.wav")
        with open(debug_path, "wb") as f:
            f.write(content)
            
        recognizer = sr.Recognizer()
        
        # We can read the bytes straight into AudioFile
        with sr.AudioFile(io.BytesIO(content)) as source:
            audio_data = recognizer.record(source)
            
            # Diagnostic: check audio frame data to see if it's completely silent
            frames = audio_data.frame_data
            if frames:
                # Calculate rough amplitude 
                import wave, struct
                samples = struct.unpack('<' + 'h' * (len(frames) // 2), frames)
                max_amp = max(abs(s) for s in samples) if samples else 0
                print(f"DEBUG STT: Audio loaded. Duration={len(frames)/2/source.SAMPLE_RATE:.2f}s, Max Amplitude={max_amp}")
            
            transcript = recognizer.recognize_google(audio_data, language=stt_lang)
            print(f"DEBUG STT: Google Transcript='{transcript}'")
            
        return {"transcript": transcript}
        
    except sr.UnknownValueError:
        print("DEBUG STT: sr.UnknownValueError - Google could not understand the voice")
        # Could not understand the voice
        return {"transcript": ""}
    except ValueError as e:
        print(f"DEBUG STT: ValueError (Bad Audio Format) - {e}")
        # Could be an empty file (0 bytes) from a UI race condition
        return {"transcript": ""}
    except sr.RequestError as e:
        print(f"DEBUG STT: sr.RequestError - {e}")
        raise HTTPException(status_code=500, detail=f"Google Speech Recognition API error: {e}")
    except Exception as e:
        print(f"DEBUG STT: Exception - {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
