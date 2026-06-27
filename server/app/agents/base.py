"""
Base Agent Architecture for Ivy AI
Defines the foundation for all specialized agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Deferred import to avoid circular dependency
_tool_executor = None

def _get_tool_executor():
    """Lazy import ToolExecutor to avoid circular imports"""
    global _tool_executor
    if _tool_executor is None:
        from app.agents.executor import ToolExecutor
        _tool_executor = ToolExecutor
    return _tool_executor


class AgentCapability:
    """Represents a capability that an agent has"""

    def __init__(self, name: str, description: str, version: str = "1.0.0"):
        self.name = name
        self.description = description
        self.version = version
        self.enabled = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "enabled": self.enabled,
        }


class AgentMessage:
    """Message structure for agent communication"""

    def __init__(
        self,
        content: str,
        agent_id: str,
        role: str = "assistant",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.content = content
        self.agent_id = agent_id
        self.role = role
        self.timestamp = datetime.utcnow().isoformat()
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "agent_id": self.agent_id,
            "role": self.role,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


class BaseAgent(ABC):
    """Base class for all Ivy AI agents"""

    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        version: str = "1.0.0",
    ):
        """Initialize base agent"""
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.version = version
        self.capabilities: List[AgentCapability] = []
        self.created_at = datetime.utcnow().isoformat()

        # Initialize tool executor
        ToolExecutor = _get_tool_executor()
        self.tool_executor = ToolExecutor(agent_id)

        logger.info(f"Agent initialized: {name} ({agent_id})")

    def add_capability(self, capability: AgentCapability) -> None:
        """Add a capability to the agent"""
        self.capabilities.append(capability)
        logger.info(f"Capability added to {self.name}: {capability.name}")

    @abstractmethod
    async def process(self, message: str, context: Dict[str, Any]) -> str:
        """Process a message and return response

        This method must be implemented by subclasses
        """
        pass

    async def execute(
        self, message: str, session_id: str = None, **context
    ) -> AgentMessage:
        """Execute agent processing and return structured message

        This is the main entry point for agent execution
        """
        try:
            response = await self.process(message, context)
            return AgentMessage(
                content=response,
                agent_id=self.agent_id,
                metadata={"session_id": session_id, **context},
            )
        except Exception as e:
            logger.error(f"Error in agent {self.name}: {str(e)}")
            raise

    def get_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "capabilities": [cap.to_dict() for cap in self.capabilities],
            "created_at": self.created_at,
        }

    # Tool-related methods
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools for this agent"""
        return self.tool_executor.get_available_tools()

    def get_available_tools_by_category(
        self, category: str
    ) -> List[Dict[str, Any]]:
        """Get tools by category"""
        return self.tool_executor.get_available_tools_by_category(category)

    def tool_exists(self, tool_id: str) -> bool:
        """Check if a tool is available"""
        return self.tool_executor.tool_exists(tool_id)

    async def use_tool(self, tool_id: str, **parameters) -> Dict[str, Any]:
        """Execute a tool

        Args:
            tool_id: Tool identifier
            **parameters: Tool parameters

        Returns:
            Tool result data or error
        """
        result = await self.tool_executor.execute_tool(tool_id, **parameters)
        return result.to_dict()

    async def use_tools_chain(
        self, tools: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Execute a chain of tools sequentially

        Args:
            tools: List of {'tool_id': str, 'parameters': dict}

        Returns:
            List of tool results
        """
        results = await self.tool_executor.execute_tool_chain(tools)
        return [r.to_dict() for r in results]

    def set_tool_context(self, key: str, value: Any) -> None:
        """Set context variable for tools"""
        self.tool_executor.set_context(key, value)

    def get_tool_context(self, key: str, default: Any = None) -> Any:
        """Get context variable"""
        return self.tool_executor.get_context(key, default)

    def get_tool_statistics(self) -> Dict[str, Any]:
        """Get tool usage statistics"""
        return self.tool_executor.get_statistics()


class AgentRegistry:
    """Registry for managing multiple agents"""

    def __init__(self):
        """Initialize agent registry"""
        self.agents: Dict[str, BaseAgent] = {}
        self.default_agent: Optional[str] = None

        logger.info("Agent registry initialized")

    def register(self, agent: BaseAgent, set_default: bool = False) -> None:
        """Register an agent"""
        self.agents[agent.agent_id] = agent
        if set_default or self.default_agent is None:
            self.default_agent = agent.agent_id
        logger.info(f"Agent registered: {agent.name} ({agent.agent_id})")

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)

    def get_default_agent(self) -> Optional[BaseAgent]:
        """Get default agent"""
        if self.default_agent:
            return self.agents.get(self.default_agent)
        return None

    async def execute(
        self, message: str, agent_id: str = None, **context
    ) -> AgentMessage:
        """Execute message through an agent"""
        # Use specified agent or default
        agent = (
            self.get_agent(agent_id)
            if agent_id
            else self.get_default_agent()
        )

        if not agent:
            raise ValueError(
                f"Agent not found: {agent_id or 'default'}"
            )

        return await agent.execute(message, **context)

    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents"""
        return [agent.get_info() for agent in self.agents.values()]

    def get_capabilities(self, agent_id: str = None) -> List[Dict[str, Any]]:
        """Get capabilities of an agent"""
        agent = self.get_agent(agent_id) if agent_id else self.get_default_agent()
        if not agent:
            return []
        return [cap.to_dict() for cap in agent.capabilities]


# Global agent registry instance
_registry: Optional[AgentRegistry] = None


def get_agent_registry() -> AgentRegistry:
    """Get or create agent registry"""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry
