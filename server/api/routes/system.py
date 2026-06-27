"""
System status routes
"""
from fastapi import APIRouter, Depends
from app.services.vectorstore import get_vectorstore_service
from app.database.redis import get_redis_cache
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/system", tags=["System"])


@router.get("/status")
async def system_status():
    """Get system status"""
    try:
        vectorstore = get_vectorstore_service()
        cache = get_redis_cache()

        # Check vector store
        vector_store_info = vectorstore.get_info()
        vector_store_healthy = "error" not in vector_store_info

        # Check cache
        cache_healthy = True
        try:
            cache.client.ping()
        except:
            cache_healthy = False

        return {
            "status": "online" if (vector_store_healthy and cache_healthy) else "degraded",
            "services": {
                "vector_store": {
                    "status": "ok" if vector_store_healthy else "error",
                    "info": vector_store_info if vector_store_healthy else None
                },
                "cache": {
                    "status": "ok" if cache_healthy else "error"
                }
            }
        }

    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


@router.get("/config")
async def get_config():
    """Get system configuration (sanitized)"""
    from config.settings import get_settings

    settings = get_settings()
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "debug": settings.DEBUG,
        "rag": {
            "chunk_size": settings.RAG_CHUNK_SIZE,
            "chunk_overlap": settings.RAG_CHUNK_OVERLAP,
            "top_k": settings.RAG_TOP_K
        },
        "openai_model": settings.OPENAI_MODEL_CHAT,
        "embedding_model": settings.OPENAI_MODEL_EMBEDDINGS
    }
