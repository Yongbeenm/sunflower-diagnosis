"""Chatbot service for user conversations.

Provides a conversational AI assistant for users to ask questions
about plant diseases and get help describing symptoms.
"""

from __future__ import annotations

import logging
import uuid

from ai.config import ai_config
from ai.schemas.ai_schemas import AIChatRequest, AIChatResponse
from ai.services.ollama_service import OllamaService, get_ollama_service
from ai.services.prompt_loader import load_prompt
from ai.services.symptom_extractor import SymptomExtractor

logger = logging.getLogger(__name__)


class ConversationContext:
    """Simple in-memory conversation context storage.
    
    In production, this should be replaced with Redis or database storage.
    """
    
    def __init__(self) -> None:
        self._conversations: dict[str, list[dict[str, str]]] = {}
    
    def get_messages(self, conversation_id: str) -> list[dict[str, str]]:
        """Get message history for a conversation."""
        return self._conversations.get(conversation_id, [])
    
    def add_message(self, conversation_id: str, role: str, content: str) -> None:
        """Add a message to conversation history."""
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = []
        
        self._conversations[conversation_id].append({
            "role": role,
            "content": content,
        })
        
        # Keep only last 10 messages to avoid context overflow
        if len(self._conversations[conversation_id]) > 10:
            self._conversations[conversation_id] = self._conversations[conversation_id][-10:]
    
    def clear(self, conversation_id: str) -> None:
        """Clear a conversation."""
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]


# Global conversation context (in production, use Redis)
_conversation_context = ConversationContext()


class ChatbotService:
    """AI chatbot service for user assistance."""
    
    def __init__(
        self,
        ollama_service: OllamaService | None = None,
        symptom_extractor: SymptomExtractor | None = None,
    ) -> None:
        self.ollama = ollama_service or get_ollama_service()
        self.extractor = symptom_extractor or SymptomExtractor(ollama_service=self.ollama)
        self.context = _conversation_context
    
    async def chat(self, request: AIChatRequest) -> AIChatResponse:
        """Process a chat message from the user.
        
        Args:
            request: Chat request with message and locale
        
        Returns:
            Chat response with AI message
        """
        # Get or create conversation ID
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Load system prompt
        system_prompt = load_prompt("chatbot")
        
        # Add locale-specific instruction
        if request.locale == "km":
            system_prompt += "\n\nRespond in Khmer language (ភាសាខ្មែរ)."
        else:
            system_prompt += "\n\nRespond in English."
        
        # Get conversation history
        history = self.context.get_messages(conversation_id)
        
        # Build messages for Ollama
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": request.message})
        
        try:
            # Get AI response
            response = await self.ollama.chat(
                messages=messages,
                temperature=ai_config.AI_TEMPERATURE,
            )
            
            # Save to conversation history
            self.context.add_message(conversation_id, "user", request.message)
            self.context.add_message(conversation_id, "assistant", response)
            
            # Check if message seems to describe symptoms (heuristic)
            needs_diagnosis = await self._check_if_symptom_description(request.message)
            
            # If it looks like symptom description, extract symptoms
            extracted_symptoms = None
            if needs_diagnosis:
                try:
                    extracted = await self.extractor.extract_symptoms(
                        message=request.message,
                        locale=request.locale,
                    )
                    if extracted.confidence > 0.3:  # Only if reasonably confident
                        extracted_symptoms = extracted.model_dump()
                except Exception as e:
                    logger.warning(f"Could not extract symptoms: {e}")
            
            return AIChatResponse(
                message=response,
                conversation_id=conversation_id,
                needs_diagnosis=needs_diagnosis,
                extracted_symptoms=extracted_symptoms,
            )
        
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            
            # Return graceful error message
            error_message = (
                "សូមទោស ខ្ញុំមានបញ្ហាបច្ចេកទេស។ សូមព្យាយាមម្តងទៀត។"
                if request.locale == "km"
                else "Sorry, I'm having technical difficulties. Please try again."
            )
            
            return AIChatResponse(
                message=error_message,
                conversation_id=conversation_id,
                needs_diagnosis=False,
            )
    
    async def _check_if_symptom_description(self, message: str) -> bool:
        """Heuristic check if message describes plant symptoms.
        
        Args:
            message: User message
        
        Returns:
            True if message seems to describe symptoms
        """
        # Simple keyword-based heuristic
        symptom_keywords = [
            # English
            "leaf", "leaves", "spot", "spots", "yellow", "brown", "wilting",
            "disease", "sick", "dying", "rot", "mold", "pest", "insect",
            "stem", "root", "flower", "head", "discolor",
            # Khmer
            "ស្លឹក", "ពណ៌", "ចំណុច", "រោគ", "ស្ងួត", "រលួយ", "សត្វ",
        ]
        
        message_lower = message.lower()
        for keyword in symptom_keywords:
            if keyword in message_lower:
                return True
        
        return False
    
    def clear_conversation(self, conversation_id: str) -> None:
        """Clear a conversation history.
        
        Args:
            conversation_id: ID of conversation to clear
        """
        self.context.clear(conversation_id)


def get_chatbot_service() -> ChatbotService:
    """Get ChatbotService instance.
    
    Returns:
        ChatbotService instance
    """
    return ChatbotService()
