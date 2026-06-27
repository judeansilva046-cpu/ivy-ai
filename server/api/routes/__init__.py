"""
API routes module
"""
from api.routes.health import router as health_router
from api.routes.system import router as system_router
from api.routes.documents import router as documents_router
from api.routes.chat import router as chat_router

__all__ = [
    "health_router",
    "system_router",
    "documents_router",
    "chat_router"
]
