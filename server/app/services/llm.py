"""
Language Model service using OpenAI
"""
from typing import Optional, List, Dict, Any
from openai import OpenAI
from config.settings import get_settings
from app.utils.logger import setup_logger
from app.utils.errors import OpenAIException

logger = setup_logger(__name__)
settings = get_settings()


class LLMService:
    """Language Model service for chat interactions"""

    def __init__(self):
        """Initialize LLM service"""
        if not settings.OPENAI_API_KEY:
            raise OpenAIException("OPENAI_API_KEY not set")

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL_CHAT
        self.temperature = settings.OPENAI_TEMPERATURE
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        logger.info(f"LLMService initialized with model: {self.model}")

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Send chat request to OpenAI"""
        try:
            # Add system prompt if provided
            if system_prompt:
                messages = [
                    {"role": "system", "content": system_prompt},
                    *messages
                ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )

            return response.choices[0].message.content

        except OpenAIException:
            raise
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            raise OpenAIException(f"Chat request failed: {str(e)}")

    def completion(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Get completion for a prompt"""
        try:
            messages = [{"role": "user", "content": prompt}]
            return self.chat(messages, temperature, max_tokens)

        except Exception as e:
            logger.error(f"Error in completion: {str(e)}")
            raise OpenAIException(f"Completion request failed: {str(e)}")

    def chat_with_context(
        self,
        query: str,
        context: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """Chat with context for RAG"""
        try:
            prompt = f"""Contexto:
{context}

Pergunta:
{query}

Responda baseado no contexto fornecido acima."""

            messages = [{"role": "user", "content": prompt}]
            return self.chat(messages, system_prompt=system_prompt)

        except Exception as e:
            logger.error(f"Error in chat with context: {str(e)}")
            raise OpenAIException(f"Chat with context failed: {str(e)}")


# Global instance
_llm_service = None


def get_llm_service() -> LLMService:
    """Get or create LLM service instance"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
