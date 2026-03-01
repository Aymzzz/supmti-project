"""
Voice service – handles Text-to-Speech using Edge TTS.
STT is handled client-side via Web Speech API.
"""

import edge_tts
import tempfile
import os
from typing import Optional

from app.config import settings


class VoiceService:
    """Text-to-Speech service using Microsoft Edge TTS (free)."""

    VOICE_MAP = {
        "fr": None,      # Loaded from settings
        "en": None,
        "darija": None,   # Uses Arabic voice
    }

    def __init__(self):
        self.VOICE_MAP = {
            "fr": settings.edge_tts_voice_fr,
            "en": settings.edge_tts_voice_en,
            "darija": settings.edge_tts_voice_ar,
        }

    def get_voice(self, language: str) -> str:
        """Get the TTS voice for a given language."""
        return self.VOICE_MAP.get(language, self.VOICE_MAP["fr"])

    async def text_to_speech(
        self,
        text: str,
        language: str = "fr",
        output_path: Optional[str] = None,
    ) -> str:
        """
        Convert text to speech audio file.

        Args:
            text: Text to synthesize
            language: Language code (fr, en, darija)
            output_path: Optional path for the audio file

        Returns:
            Path to the generated audio file (MP3)
        """
        voice = self.get_voice(language)

        if output_path is None:
            # Create a temporary file
            fd, output_path = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)

        communicate = edge_tts.Communicate(text=text, voice=voice)
        await communicate.save(output_path)

        return output_path

    async def text_to_speech_bytes(
        self,
        text: str,
        language: str = "fr",
    ) -> bytes:
        """
        Convert text to speech and return audio bytes.
        Useful for streaming directly to the client.
        """
        voice = self.get_voice(language)
        communicate = edge_tts.Communicate(text=text, voice=voice)

        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]

        return audio_data

    @staticmethod
    async def list_voices(language_filter: str = None) -> list:
        """List available Edge TTS voices."""
        voices = await edge_tts.list_voices()
        if language_filter:
            voices = [
                v for v in voices
                if v["Locale"].startswith(language_filter)
            ]
        return voices


# Global instance
voice_service = VoiceService()
