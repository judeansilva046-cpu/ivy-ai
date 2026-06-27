"""
Chat history storage
"""
from typing import List, Dict, Any
from datetime import datetime
from app.database.redis import get_redis_cache
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ChatHistory:
    """Store and retrieve chat history"""

    def __init__(self):
        """Initialize chat history"""
        self.cache = get_redis_cache()
        logger.info("ChatHistory initialized")

    def save_exchange(
        self,
        session_id: str,
        query: str,
        response: str,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Save query-response exchange"""
        try:
            history_key = f"history:{session_id}"
            histories = self.cache.get(history_key) or []

            exchange = {
                "timestamp": datetime.utcnow().isoformat(),
                "query": query,
                "response": response,
                "metadata": metadata or {}
            }

            histories.append(exchange)

            # Keep last 100 exchanges
            if len(histories) > 100:
                histories = histories[-100:]

            self.cache.set(history_key, histories, ttl=86400 * 7)  # 7 days
            logger.debug(f"Saved exchange for session: {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving exchange: {str(e)}")
            return False

    def get_history(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get chat history for session"""
        try:
            history_key = f"history:{session_id}"
            histories = self.cache.get(history_key) or []
            return histories[-limit:] if histories else []
        except Exception as e:
            logger.error(f"Error retrieving history: {str(e)}")
            return []

    def clear_history(self, session_id: str) -> bool:
        """Clear chat history for session"""
        try:
            history_key = f"history:{session_id}"
            self.cache.delete(history_key)
            logger.info(f"Cleared history for session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing history: {str(e)}")
            return False

    def get_statistics(self, session_id: str) -> Dict[str, Any]:
        """Get statistics about session history"""
        try:
            histories = self.get_history(session_id, limit=1000)

            if not histories:
                return {"messages": 0, "duration": "0 seconds"}

            first_msg = histories[0]
            last_msg = histories[-1]

            first_time = datetime.fromisoformat(first_msg["timestamp"])
            last_time = datetime.fromisoformat(last_msg["timestamp"])
            duration = (last_time - first_time).total_seconds()

            return {
                "total_exchanges": len(histories),
                "first_message": first_msg["timestamp"],
                "last_message": last_msg["timestamp"],
                "duration_seconds": int(duration)
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {}


# Global instance
_chat_history = None


def get_chat_history() -> ChatHistory:
    """Get or create chat history instance"""
    global _chat_history
    if _chat_history is None:
        _chat_history = ChatHistory()
    return _chat_history
