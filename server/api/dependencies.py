"""
FastAPI dependencies
"""
from typing import Generator
from app.services.chat_service import get_chat_service
from app.rag.search import get_semantic_search
from app.database.qdrant import get_qdrant_store
from app.database.redis import get_redis_cache
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


# Service dependencies
def get_chat_service_dep():
    """Get chat service dependency"""
    return get_chat_service()


def get_semantic_search_dep():
    """Get semantic search dependency"""
    return get_semantic_search()


def get_vector_store_dep():
    """Get vector store dependency"""
    return get_qdrant_store()


def get_cache_dep():
    """Get cache dependency"""
    return get_redis_cache()
