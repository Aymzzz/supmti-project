"""
LLM response generator using OpenRouter API.
Supports streaming and conversation memory.
"""

from openai import AsyncOpenAI
from typing import List, Dict, Optional, AsyncGenerator
import json

from app.config import settings


# System prompt for the SupMTI chatbot
SYSTEM_PROMPT_TEMPLATE = """Tu es l'assistant virtuel intelligent de SupMTI (École Supérieure des Sciences et Technologies de l'Informatique et du Management), un véritable CONSEILLER D'ORIENTATION SCOLAIRE.

## Ton rôle :
- Aider les futurs étudiants à découvrir les filières de SupMTI
- Agir comme un GUIDE interactif : Si un étudiant cherche sa voie, pose-lui progressivement des questions ciblées sur ses centres d'intérêt (ex: "Préférez-vous la théorie ou la pratique ?", "Aimez-vous la programmation, construire des choses ou gérer des projets ?"). Recommande ensuite la meilleure filière.
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
        # Primary client (OpenRouter) with strict timeout and no retries to prevent long hangs
        self.primary_client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            max_retries=0,
            timeout=8.0, 
        )
        
        # Fallback client (Can be Groq, explicit OpenAI, or default OpenRouter)
        fallback_key = settings.fallback_api_key or settings.openrouter_api_key
        fallback_url = settings.fallback_base_url or settings.openrouter_base_url
        self.fallback_client = AsyncOpenAI(
            api_key=fallback_key,
            base_url=fallback_url,
            max_retries=0,
            timeout=8.0,
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

    async def translate_to_french(self, text: str) -> str:
        """Translate the user query to French to improve BM25 retrieval."""
        prompt = (
            "Traduisez le texte suivant en français. "
            "Ne renvoyez QUE la traduction, sans guillemets, sans aucun autre texte ou explication.\n\n"
            f"Texte : {text}"
        )
        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = await self.primary_client.chat.completions.create(
                model=self.primary_model,
                messages=messages,
                temperature=0.0,
                max_tokens=256,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ Translation primary failed: {e}. Trying fallback...")
            try:
                response = await self.fallback_client.chat.completions.create(
                    model=self.fallback_model,
                    messages=messages,
                    temperature=0.0,
                    max_tokens=256,
                )
                return response.choices[0].message.content.strip()
            except Exception as fallback_error:
                print(f"❌ Fallback translation also failed: {fallback_error}")
                return text  # Fallback to original text

    async def generate(
        self,
        query: str,
        retrieved_docs: List[Dict],
        conversation_history: Optional[List[Dict]] = None,
        language: str = "fr",
    ) -> str:
        """Generate a response using the LLM with tool calling support."""
        context = self._format_context(retrieved_docs)
        history = self._format_history(conversation_history or [])
        system_prompt = self._build_system_prompt(context, history)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_program_recommendations",
                    "description": "Call this to get actual program recommendations based on the user's interests.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "interests": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of the student's interests (e.g. ['math', 'AI', 'business'])"
                            }
                        },
                        "required": ["interests"]
                    }
                }
            }
        ]

        try:
            response = await self.primary_client.chat.completions.create(
                model=self.primary_model,
                messages=messages,
                temperature=settings.temperature,
                max_tokens=1024,
                tools=tools,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            
            # Check if the model wants to call the recommendation tool
            if response_message.tool_calls:
                from app.services.recommendation_service import recommendation_service
                
                messages.append(response_message)
                for tool_call in response_message.tool_calls:
                    if tool_call.function.name == "get_program_recommendations":
                        args = json.loads(tool_call.function.arguments)
                        rec_result = recommendation_service.recommend(interests=args.get("interests", []))
                        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(rec_result)
                        })
                
                # Get the final response integrating the tool result
                final_response = await self.primary_client.chat.completions.create(
                    model=self.primary_model,
                    messages=messages,
                    temperature=settings.temperature,
                    max_tokens=1024,
                )
                return final_response.choices[0].message.content

            return response_message.content

        except Exception as e:
            print(f"⚠️ Primary model failed: {e}. Trying fallback...")
            try:
                response = await self.fallback_client.chat.completions.create(
                    model=self.fallback_model,
                    messages=messages,
                    temperature=settings.temperature,
                    max_tokens=1024,
                )
                return response.choices[0].message.content
            except Exception as fallback_error:
                print(f"❌ Fallback model also failed: {fallback_error}")
                return (
                    "Désolé, je rencontre des difficultés techniques (Serveur surchargé). "
                    "Veuillez réessayer dans quelques instants."
                )

    async def generate_stream(
        self,
        query: str,
        retrieved_docs: List[Dict],
        conversation_history: Optional[List[Dict]] = None,
        language: str = "fr",
    ) -> AsyncGenerator[str, None]:
        """Stream a response token-by-token using the LLM. Supports tool calling."""
        context = self._format_context(retrieved_docs)
        history = self._format_history(conversation_history or [])
        system_prompt = self._build_system_prompt(context, history)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_program_recommendations",
                    "description": "Call this to get actual program recommendations based on the user's interests.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "interests": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of the student's interests (e.g. ['math', 'AI', 'business'])"
                            }
                        },
                        "required": ["interests"]
                    }
                }
            }
        ]

        try:
            # First, make a non-streaming call to check if the LLM wants to use a tool
            initial_response = await self.primary_client.chat.completions.create(
                model=self.primary_model,
                messages=messages,
                temperature=settings.temperature,
                max_tokens=1024,
                tools=tools,
                tool_choice="auto"
            )
            
            response_message = initial_response.choices[0].message
            
            # Check if the model wants to call the recommendation tool
            if response_message.tool_calls:
                from app.services.recommendation_service import recommendation_service
                
                messages.append(response_message)
                for tool_call in response_message.tool_calls:
                    if tool_call.function.name == "get_program_recommendations":
                        args = json.loads(tool_call.function.arguments)
                        rec_result = recommendation_service.recommend(interests=args.get("interests", []))
                        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(rec_result)
                        })
                
                # We have the tool result, now stream the final answer
                stream = await self.primary_client.chat.completions.create(
                    model=self.primary_model,
                    messages=messages,
                    temperature=settings.temperature,
                    max_tokens=1024,
                    stream=True,
                )
                
                async for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                return
            
            # If no tool calls, just stream the text directly from the initial response content if possible
            # But the best way is to re-execute as a stream since we didn't use `stream=True`
            stream = await self.primary_client.chat.completions.create(
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
            print(f"⚠️ Streaming primary error: {e}. Trying fallback stream...")
            try:
                stream = await self.fallback_client.chat.completions.create(
                    model=self.fallback_model,
                    messages=messages,
                    temperature=settings.temperature,
                    max_tokens=1024,
                    stream=True,
                )

                async for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            except Exception as fallback_error:
                print(f"❌ Fallback streaming failed: {fallback_error}")
                yield "Désolé, les serveurs d'intelligence artificielle sont actuellement surchargés. Veuillez réessayer très bientôt."
