"""
Chat service that orchestrates RAG and LLM
"""
from typing import Optional, Dict, Any
from datetime import datetime
from app.services.llm import get_llm_service
from app.rag.search import get_semantic_search
from app.database.redis import get_redis_cache
from config.prompts import SYSTEM_PROMPT_CHAT
from config.settings import get_settings
from app.utils.logger import setup_logger
from app.utils.errors import ChatException

logger = setup_logger(__name__)
settings = get_settings()


class ChatService:
    """Chat service with RAG integration"""

    def __init__(self):
        """Initialize chat service"""
        self.llm = get_llm_service()
        self.search = get_semantic_search()
        self.cache = get_redis_cache()
        logger.info("ChatService initialized")

    def chat(
        self,
        query: str,
        session_id: Optional[str] = None,
        use_cache: bool = True,
        top_k: Optional[int] = None,
        min_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """Process chat query with RAG"""
        try:
            if not query or len(query.strip()) == 0:
                raise ChatException("Empty query provided")

            # Check cache
            cache_key = f"chat:{session_id}:{query}" if session_id else f"chat:{query}"
            if use_cache:
                cached_response = self.cache.get(cache_key)
                if cached_response:
                    logger.info(f"Cache hit for query: {query[:50]}...")
                    return cached_response

            # Search for context
            context = self.search.search_with_context(
                query=query,
                top_k=top_k,
                min_score=min_score
            )

            # Get response from LLM
            response_text = self.llm.chat_with_context(
                query=query,
                context=context,
                system_prompt=SYSTEM_PROMPT_CHAT
            )

            # Format response
            response = {
                "success": True,
                "query": query,
                "response": response_text,
                "context_used": len([c for c in context.split("---") if c.strip()]),
                "timestamp": datetime.utcnow().isoformat(),
                "model": settings.OPENAI_MODEL_CHAT
            }

            # Cache response
            if use_cache:
                self.cache.set(cache_key, response, ttl=3600)  # 1 hour TTL

            logger.info(f"Chat response generated for: {query[:50]}...")
            return response

        except ChatException:
            raise
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            raise ChatException(f"Chat processing failed: {str(e)}")

    def chat_with_history(
        self,
        query: str,
        history: list,
        session_id: Optional[str] = None,
        top_k: Optional[int] = None,
        min_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """Chat with conversation history"""
        try:
            # Search for context
            context = self.search.search_with_context(
                query=query,
                top_k=top_k,
                min_score=min_score
            )

            # Build messages with history
            messages = []

            # Add history
            for msg in history[-5:]:  # Last 5 messages for context
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

            # Add current query with context
            prompt = f"""Contexto dos documentos:
{context}

Pergunta atual:
{query}

Por favor, responda baseado no contexto dos documentos e na conversa anterior."""

            messages.append({"role": "user", "content": prompt})

            # Get response
            response_text = self.llm.chat(
                messages=messages,
                system_prompt=SYSTEM_PROMPT_CHAT
            )

            response = {
                "success": True,
                "query": query,
                "response": response_text,
                "context_used": len([c for c in context.split("---") if c.strip()]),
                "timestamp": datetime.utcnow().isoformat(),
                "model": settings.OPENAI_MODEL_CHAT
            }

            logger.info(f"Chat with history generated for: {query[:50]}...")
            return response

        except Exception as e:
            logger.error(f"Error in chat with history: {str(e)}")
            raise ChatException(f"Chat with history failed: {str(e)}")

    def clear_cache(self, session_id: Optional[str] = None) -> bool:
        """Clear cache for session"""
        try:
            if session_id:
                pattern = f"chat:{session_id}:*"
                keys = self.cache.keys(pattern)
                for key in keys:
                    self.cache.delete(key)
                logger.info(f"Cleared cache for session {session_id}")
            else:
                self.cache.flush_db()
                logger.info("Cleared entire cache")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            return False


# Global instance
_chat_service = None


def get_chat_service() -> ChatService:
    """Get or create chat service instance"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
