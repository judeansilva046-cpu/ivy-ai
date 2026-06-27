"""
Vector store abstraction
"""
from typing import List, Dict, Any
from app.database.qdrant import get_qdrant_store
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class VectorStoreService:
    """Vector store service abstraction"""

    def __init__(self):
        """Initialize vector store service"""
        self.store = get_qdrant_store()
        logger.info("VectorStoreService initialized")

    def get_info(self) -> Dict[str, Any]:
        """Get vector store information"""
        try:
            return self.store.get_collection_info()
        except Exception as e:
            logger.error(f"Error getting store info: {str(e)}")
            return {"error": str(e)}

    def health_check(self) -> bool:
        """Check if vector store is healthy"""
        try:
            info = self.get_info()
            return "error" not in info
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False


# Global instance
_vectorstore_service = None


def get_vectorstore_service() -> VectorStoreService:
    """Get or create vector store service instance"""
    global _vectorstore_service
    if _vectorstore_service is None:
        _vectorstore_service = VectorStoreService()
    return _vectorstore_service
