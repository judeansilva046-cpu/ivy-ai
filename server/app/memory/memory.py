"""
Memory management for chat sessions
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.database.redis import get_redis_cache
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ConversationMemory:
    """Manage conversation memory for sessions"""

    def __init__(self, session_id: str, max_messages: int = 10):
        """Initialize conversation memory"""
        self.session_id = session_id
        self.max_messages = max_messages
        self.cache = get_redis_cache()
        self.memory_key = f"memory:{session_id}"
        logger.info(f"Initialized memory for session: {session_id}")

    def add_message(self, role: str, content: str) -> bool:
        """Add message to memory"""
        try:
            messages = self.get_messages()

            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            }

            messages.append(message)

            # Keep only last N messages
            if len(messages) > self.max_messages:
                messages = messages[-self.max_messages:]

            self.cache.set(self.memory_key, messages, ttl=86400)  # 24 hours
            logger.debug(f"Added message to memory: {role}")
            return True

        except Exception as e:
            logger.error(f"Error adding message: {str(e)}")
            return False

    def get_messages(self) -> List[Dict[str, Any]]:
        """Get all messages from memory"""
        try:
            messages = self.cache.get(self.memory_key)
            return messages if messages else []
        except Exception as e:
            logger.error(f"Error retrieving messages: {str(e)}")
            return []

    def get_last_n_messages(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get last N messages"""
        try:
            messages = self.get_messages()
            return messages[-n:] if messages else []
        except Exception as e:
            logger.error(f"Error retrieving last messages: {str(e)}")
            return []

    def clear_memory(self) -> bool:
        """Clear conversation memory"""
        try:
            self.cache.delete(self.memory_key)
            logger.info(f"Cleared memory for session: {self.session_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing memory: {str(e)}")
            return False

    def get_summary(self) -> str:
        """Get summary of conversation"""
        try:
            messages = self.get_messages()
            if not messages:
                return "Nenhuma mensagem no histórico."

            summary = f"Histórico de conversa ({len(messages)} mensagens):\n"
            for msg in messages[-3:]:  # Last 3 messages
                summary += f"- {msg['role'].upper()}: {msg['content'][:100]}...\n"
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return "Erro ao gerar resumo."


# Global instances cache
_memory_instances = {}


def get_conversation_memory(session_id: str) -> ConversationMemory:
    """Get or create conversation memory for session"""
    if session_id not in _memory_instances:
        _memory_instances[session_id] = ConversationMemory(session_id)
    return _memory_instances[session_id]
