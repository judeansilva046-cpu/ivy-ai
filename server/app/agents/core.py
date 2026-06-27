"""
Core Agent - Main chat agent for Ivy AI
Implements the existing RAG + LLM chat functionality
"""
from typing import Dict, Any
from app.agents.base import BaseAgent, AgentCapability
from app.services.chat_service import get_chat_service
from app.memory.memory import get_memory_service
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class CoreAgent(BaseAgent):
    """Core Agent - Main intelligence for Ivy AI

    This agent provides:
    - Chat with RAG (Retrieval-Augmented Generation)
    - Context awareness from indexed documents
    - Conversation memory management
    """

    def __init__(self):
        """Initialize Core Agent"""
        super().__init__(
            agent_id="ivy-core",
            name="Ivy Core",
            description="Main intelligence engine with RAG capabilities",
            version="2.0.0",
        )

        # Initialize services
        self.chat_service = get_chat_service()
        self.memory_service = get_memory_service()

        # Define capabilities
        self.add_capability(
            AgentCapability(
                name="rag-chat",
                description="Chat with Retrieval-Augmented Generation from indexed documents",
            )
        )
        self.add_capability(
            AgentCapability(
                name="conversation-memory",
                description="Maintain conversation history and context",
            )
        )
        self.add_capability(
            AgentCapability(
                name="semantic-search",
                description="Search documents by semantic meaning",
            )
        )

        logger.info("CoreAgent initialized successfully")

    async def process(self, message: str, context: Dict[str, Any]) -> str:
        """Process message using RAG + LLM

        Args:
            message: User message
            context: Additional context (session_id, user_id, etc)

        Returns:
            Response from LLM with context from indexed documents
        """
        try:
            # Extract session_id from context
            session_id = context.get("session_id")

            # Add message to memory
            if session_id:
                self.memory_service.add_message(session_id, "user", message)

            # Get conversation history
            history = None
            if session_id:
                history = self.memory_service.get_conversation_history(
                    session_id, limit=10
                )

            # Use chat service to generate response with RAG
            response = await self.chat_service.chat_with_context(
                message=message,
                history=history,
                session_id=session_id,
            )

            # Add response to memory
            if session_id:
                self.memory_service.add_message(
                    session_id, "assistant", response
                )

            logger.info(f"CoreAgent processed message for session {session_id}")
            return response

        except Exception as e:
            logger.error(f"Error in CoreAgent.process: {str(e)}")
            raise


async def get_core_agent() -> CoreAgent:
    """Get or create core agent instance"""
    # Create new instance each time (singleton handled by registry)
    return CoreAgent()
