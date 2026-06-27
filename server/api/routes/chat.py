"""
Chat routes with RAG integration
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from app.services.chat_service import get_chat_service
from app.memory.memory import get_conversation_memory
from app.memory.history import get_chat_history
from app.utils.logger import setup_logger
from app.utils.errors import ChatException

logger = setup_logger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])


# Request/Response models
class ChatRequest(BaseModel):
    """Chat request model"""
    query: str
    session_id: Optional[str] = None
    top_k: Optional[int] = None
    min_score: Optional[float] = None


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str
    content: str


class ChatWithHistoryRequest(BaseModel):
    """Chat with history request model"""
    query: str
    session_id: str
    history: Optional[List[ChatMessage]] = None
    top_k: Optional[int] = None
    min_score: Optional[float] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    success: bool
    query: str
    response: str
    context_used: int
    timestamp: str
    model: str


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint with RAG"""
    try:
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        chat_service = get_chat_service()

        # Get chat response
        response = chat_service.chat(
            query=request.query,
            session_id=request.session_id,
            top_k=request.top_k,
            min_score=request.min_score
        )

        # Save to memory if session_id provided
        if request.session_id:
            memory = get_conversation_memory(request.session_id)
            memory.add_message("user", request.query)
            memory.add_message("assistant", response["response"])

            # Save to history
            history = get_chat_history()
            history.save_exchange(
                session_id=request.session_id,
                query=request.query,
                response=response["response"],
                metadata={"context_used": response["context_used"]}
            )

        logger.info(f"Chat response generated: {request.query[:50]}...")
        return response

    except ChatException as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/with-history")
async def chat_with_history(request: ChatWithHistoryRequest):
    """Chat with conversation history"""
    try:
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        chat_service = get_chat_service()
        memory = get_conversation_memory(request.session_id)

        # Use provided history or get from memory
        history = request.history or memory.get_last_n_messages(n=5)

        if not history:
            history = []

        # Convert to dict if needed
        history_dicts = [
            {"role": h.role, "content": h.content} if isinstance(h, ChatMessage) else h
            for h in history
        ]

        # Get response
        response = chat_service.chat_with_history(
            query=request.query,
            history=history_dicts,
            session_id=request.session_id,
            top_k=request.top_k,
            min_score=request.min_score
        )

        # Save to memory
        memory.add_message("user", request.query)
        memory.add_message("assistant", response["response"])

        # Save to history
        chat_history = get_chat_history()
        chat_history.save_exchange(
            session_id=request.session_id,
            query=request.query,
            response=response["response"],
            metadata={"context_used": response["context_used"]}
        )

        logger.info(f"Chat with history response generated for session: {request.session_id}")
        return response

    except ChatException as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in chat with history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/history/{session_id}")
async def get_history(session_id: str, limit: int = 10):
    """Get conversation history"""
    try:
        history_service = get_chat_history()
        history = history_service.get_history(session_id, limit)

        return {
            "session_id": session_id,
            "history": history,
            "count": len(history)
        }

    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/history/{session_id}")
async def clear_history(session_id: str):
    """Clear conversation history"""
    try:
        memory = get_conversation_memory(session_id)
        history = get_chat_history()

        memory.clear_memory()
        history.clear_history(session_id)

        return {
            "success": True,
            "message": f"Cleared history for session: {session_id}"
        }

    except Exception as e:
        logger.error(f"Error clearing history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/session-stats/{session_id}")
async def get_session_stats(session_id: str):
    """Get session statistics"""
    try:
        history = get_chat_history()
        stats = history.get_statistics(session_id)

        return {
            "session_id": session_id,
            "statistics": stats
        }

    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
