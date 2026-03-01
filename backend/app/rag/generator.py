"""
LLM response generator using OpenRouter API.
Supports streaming and conversation memory.
"""

from openai import AsyncOpenAI
from typing import List, Dict, Optional, AsyncGenerator
import json

from app.config import settings


# System prompt for the SupMTI chatbot
SYSTEM_PROMPT_TEMPLATE = """Tu es l'assistant virtuel intelligent de SupMTI (École Supérieure des Sciences et Technologies de l'Informatique et du Management), un chatbot d'orientation scolaire.

## Ton rôle :
- Aider les futurs étudiants à découvrir les filières de SupMTI
- Recommander la filière la plus adaptée selon leur profil
- Vérifier l'éligibilité des étudiants aux formations
- Répondre aux questions sur l'école (admissions, frais, campus, etc.)

## Règles strictes :
1. RÉPONDS UNIQUEMENT avec les informations fournies dans le contexte ci-dessous
2. Si tu ne trouves pas la réponse dans le contexte, dis-le honnêtement
3. Ne JAMAIS inventer d'informations sur l'école
4. Adapte ta langue à celle de l'utilisateur :
   - Si l'utilisateur parle en Darija (marocain), réponds en Darija naturel
   - Si l'utilisateur parle en Français, réponds en Français
   - Si l'utilisateur parle en Anglais, réponds en Anglais
5. Sois amical, professionnel et encourageant
6. Pour les questions d'éligibilité, sois précis et cite les critères

## Contexte de la base de connaissances :
{context}

## Historique de la conversation :
{history}
"""


class LLMGenerator:
    """Generates responses using OpenRouter API (OpenAI-compatible)."""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
        )
        self.primary_model = settings.primary_model
        self.fallback_model = settings.fallback_model

    def _build_system_prompt(
        self,
        context: str,
        history: str = "",
    ) -> str:
        """Build the system prompt with injected context."""
        return SYSTEM_PROMPT_TEMPLATE.format(
            context=context or "Aucun contexte trouvé.",
            history=history or "Pas d'historique.",
        )

    def _format_context(self, retrieved_docs: List[Dict]) -> str:
        """Format retrieved documents into a context string."""
        if not retrieved_docs:
            return "Aucun document pertinent trouvé dans la base de connaissances."

        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            source = doc.get("metadata", {}).get("source", "unknown")
            category = doc.get("metadata", {}).get("category", "")
            context_parts.append(
                f"[Source {i} | {category} | {source}]\n{doc['content']}"
            )
        return "\n\n---\n\n".join(context_parts)

    def _format_history(
        self, conversation_history: List[Dict]
    ) -> str:
        """Format conversation history for the prompt."""
        if not conversation_history:
            return ""

        history_parts = []
        for msg in conversation_history[-6:]:  # Last 6 messages
            role = "Utilisateur" if msg["role"] == "user" else "Assistant"
            history_parts.append(f"{role}: {msg['content']}")
        return "\n".join(history_parts)

    async def generate(
        self,
        query: str,
        retrieved_docs: List[Dict],
        conversation_history: Optional[List[Dict]] = None,
        language: str = "fr",
    ) -> str:
        """Generate a response using the LLM."""
        context = self._format_context(retrieved_docs)
        history = self._format_history(conversation_history or [])
        system_prompt = self._build_system_prompt(context, history)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]

        try:
            response = await self.client.chat.completions.create(
                model=self.primary_model,
                messages=messages,
                temperature=settings.temperature,
                max_tokens=1024,
            )
            return response.choices[0].message.content

        except Exception as e:
            print(f"⚠️ Primary model failed: {e}. Trying fallback...")
            try:
                response = await self.client.chat.completions.create(
                    model=self.fallback_model,
                    messages=messages,
                    temperature=settings.temperature,
                    max_tokens=1024,
                )
                return response.choices[0].message.content
            except Exception as fallback_error:
                print(f"❌ Fallback model also failed: {fallback_error}")
                return (
                    "Désolé, je rencontre des difficultés techniques. "
                    "Veuillez réessayer dans quelques instants."
                )

    async def generate_stream(
        self,
        query: str,
        retrieved_docs: List[Dict],
        conversation_history: Optional[List[Dict]] = None,
        language: str = "fr",
    ) -> AsyncGenerator[str, None]:
        """Stream a response token-by-token using the LLM."""
        context = self._format_context(retrieved_docs)
        history = self._format_history(conversation_history or [])
        system_prompt = self._build_system_prompt(context, history)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]

        try:
            stream = await self.client.chat.completions.create(
                model=self.primary_model,
                messages=messages,
                temperature=settings.temperature,
                max_tokens=1024,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            print(f"⚠️ Streaming error: {e}")
            yield (
                "Désolé, je rencontre des difficultés techniques. "
                "Veuillez réessayer."
            )
