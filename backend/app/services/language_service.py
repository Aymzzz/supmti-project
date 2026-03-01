"""
Language detection service for multilingual support.
Detects Darija, French, and English from user input.
"""

import re
from typing import Optional


# Common Darija markers (Arabic script and Latin)
DARIJA_MARKERS = [
    "كيفاش", "واش", "شنو", "فين", "علاش", "بغيت", "عندي", "ديال",
    "مزيان", "باش", "كنبغي", "شحال", "كيداير", "لاباس", "نعم",
    "بزاف", "ماشي", "هادشي", "كاين", "مكاينش", "واخا", "شوف",
    # Latinized Darija markers
    "wach", "chno", "kifach", "fin", "3lach", "bghit", "3ndi", "dyal",
    "mzyan", "bach", "kanb8i", "ch7al", "kidayr", "labas", "bzzaf",
    "machi", "hadchi", "kayn", "makaynch", "wakha", "chouf",
    "salam", "la7", "mnin", "lla", "nta", "nti", "hna", "homa",
]

# Common French markers
FRENCH_MARKERS = [
    "je", "tu", "il", "elle", "nous", "vous", "ils", "elles",
    "est", "suis", "sont", "avez", "avons", "ai", "bonjour",
    "comment", "qu'est-ce", "pourquoi", "quand", "où", "quel",
    "quelle", "quels", "quelles", "c'est", "je veux", "j'ai",
    "une", "le", "la", "les", "des", "du", "au", "aux",
    "merci", "s'il vous plaît", "étudier", "filière", "école",
    "inscription", "diplôme", "formation",
]

# English markers
ENGLISH_MARKERS = [
    "i", "you", "he", "she", "we", "they", "am", "is", "are",
    "what", "where", "when", "why", "how", "which", "who",
    "the", "and", "but", "or", "not", "can", "could", "would",
    "should", "will", "have", "has", "do", "does", "did",
    "hello", "hi", "please", "thank", "want", "need", "study",
    "program", "school", "engineering", "eligible",
]


class LanguageService:
    """Detects language from user input text."""

    def detect(self, text: str) -> str:
        """
        Detect the language of the input text.

        Returns:
            'darija', 'fr', or 'en'
        """
        if not text or not text.strip():
            return "fr"  # Default to French

        text_lower = text.lower().strip()

        # Check for Arabic script (strong indicator for Darija)
        if re.search(r'[\u0600-\u06FF]', text):
            return "darija"

        # Count marker matches for each language
        scores = {
            "darija": self._count_markers(text_lower, DARIJA_MARKERS),
            "fr": self._count_markers(text_lower, FRENCH_MARKERS),
            "en": self._count_markers(text_lower, ENGLISH_MARKERS),
        }

        # If Darija has any score, prioritize it (less common, more specific markers)
        if scores["darija"] > 0:
            return "darija"

        # Return highest scoring language
        detected = max(scores, key=scores.get)

        # If no markers matched, default to French
        if scores[detected] == 0:
            return "fr"

        return detected

    def _count_markers(self, text: str, markers: list) -> int:
        """Count how many markers appear in the text."""
        count = 0
        words = set(re.findall(r'\b\w+\b', text))
        for marker in markers:
            marker_words = set(marker.lower().split())
            if marker_words.issubset(words) or marker.lower() in text:
                count += 1
        return count

    def get_display_name(self, lang_code: str) -> str:
        """Get display name for a language code."""
        names = {
            "darija": "الدارجة المغربية",
            "fr": "Français",
            "en": "English",
        }
        return names.get(lang_code, lang_code)


# Global instance
language_service = LanguageService()
