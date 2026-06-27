"""
Health check routes
"""
from fastapi import APIRouter
from datetime import datetime
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="", tags=["Health"])


@router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Jarvis AI",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }


@router.get("/", tags=["Health"])
async def root():
    """Root endpoint"""
    return {
        "name": "Jarvis AI Enterprise Platform",
        "version": "2.0.0",
        "status": "online",
        "description": "Advanced AI-powered RAG system integrated with n8n"
    }
