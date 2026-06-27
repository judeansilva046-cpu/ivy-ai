"""
Base Tool Framework
Abstract base class and registry for all tools
"""
from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod
from datetime import datetime
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ToolParameter:
    """Represents a tool parameter"""

    def __init__(
        self,
        name: str,
        type: str,
        description: str,
        required: bool = True,
        default: Any = None,
    ):
        self.name = name
        self.type = type
        self.description = description
        self.required = required
        self.default = default

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "required": self.required,
            "default": self.default,
        }


class ToolResult:
    """Standardized tool execution result"""

    def __init__(
        self,
        success: bool,
        data: Any = None,
        error: str = None,
        metadata: Dict[str, Any] = None,
    ):
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


class BaseTool(ABC):
    """Abstract base class for all tools

    All tools inherit from this and must implement:
    - execute() - Main tool logic
    """

    def __init__(
        self,
        tool_id: str,
        name: str,
        description: str,
        version: str = "1.0.0",
        category: str = "utility",
    ):
        """Initialize tool

        Args:
            tool_id: Unique identifier (e.g., "calculator", "file-ops")
            name: Display name (e.g., "Calculator")
            description: What the tool does
            version: Tool version
            category: Category (utility, search, code, data, etc)
        """
        self.tool_id = tool_id
        self.name = name
        self.description = description
        self.version = version
        self.category = category
        self.parameters: List[ToolParameter] = []
        self.created_at = datetime.now().isoformat()
        self.execution_count = 0
        self.last_execution = None

        logger.info(f"Tool initialized: {self.tool_id}")

    def add_parameter(self, parameter: ToolParameter) -> None:
        """Add a parameter to this tool

        Args:
            parameter: ToolParameter instance
        """
        self.parameters.append(parameter)

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute tool logic

        Must be implemented by subclasses.

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            ToolResult with success, data, error, metadata
        """
        pass

    async def run(self, **kwargs) -> ToolResult:
        """Run tool with validation and tracking

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            ToolResult
        """
        try:
            # Validate parameters
            validation_error = self._validate_parameters(kwargs)
            if validation_error:
                return ToolResult(
                    success=False,
                    error=validation_error,
                )

            # Execute tool
            logger.info(f"Executing tool: {self.tool_id}")
            result = await self.execute(**kwargs)

            # Update tracking
            self.execution_count += 1
            self.last_execution = datetime.now().isoformat()

            logger.info(
                f"Tool executed successfully: {self.tool_id} (count: {self.execution_count})"
            )
            return result

        except Exception as e:
            logger.error(f"Error executing tool {self.tool_id}: {str(e)}")
            return ToolResult(
                success=False,
                error=str(e),
                metadata={"tool_id": self.tool_id},
            )

    def _validate_parameters(self, kwargs: Dict[str, Any]) -> Optional[str]:
        """Validate provided parameters

        Args:
            kwargs: Provided parameters

        Returns:
            Error message if validation fails, None otherwise
        """
        for param in self.parameters:
            if param.required and param.name not in kwargs:
                return f"Missing required parameter: {param.name}"

            if param.name in kwargs:
                value = kwargs[param.name]
                # Basic type checking
                if param.type == "string" and not isinstance(value, str):
                    return f"Parameter {param.name} must be string"
                elif param.type == "number" and not isinstance(
                    value, (int, float)
                ):
                    return f"Parameter {param.name} must be number"
                elif param.type == "boolean" and not isinstance(value, bool):
                    return f"Parameter {param.name} must be boolean"

        return None

    def get_info(self) -> Dict[str, Any]:
        """Get tool information

        Returns:
            Dictionary with tool metadata
        """
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "category": self.category,
            "parameters": [p.to_dict() for p in self.parameters],
            "execution_count": self.execution_count,
            "last_execution": self.last_execution,
            "created_at": self.created_at,
        }


class ToolRegistry:
    """Central registry for all tools

    Manages tool registration, retrieval, and execution.
    Implemented as singleton.
    """

    _instance = None

    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super(ToolRegistry, cls).__new__(cls)
            cls._instance._tools: Dict[str, BaseTool] = {}
            logger.info("ToolRegistry created")
        return cls._instance

    def register(self, tool: BaseTool) -> None:
        """Register a tool

        Args:
            tool: BaseTool instance
        """
        if tool.tool_id in self._tools:
            logger.warning(
                f"Tool {tool.tool_id} already registered, overwriting"
            )
        self._tools[tool.tool_id] = tool
        logger.info(f"Tool registered: {tool.tool_id}")

    def get_tool(self, tool_id: str) -> Optional[BaseTool]:
        """Get a tool by ID

        Args:
            tool_id: Tool identifier

        Returns:
            BaseTool instance or None if not found
        """
        return self._tools.get(tool_id)

    def list_tools(self) -> List[Dict[str, Any]]:
        """List all registered tools

        Returns:
            List of tool information dicts
        """
        return [tool.get_info() for tool in self._tools.values()]

    def list_tools_by_category(self, category: str) -> List[Dict[str, Any]]:
        """List tools by category

        Args:
            category: Tool category

        Returns:
            List of tools in that category
        """
        return [
            tool.get_info()
            for tool in self._tools.values()
            if tool.category == category
        ]

    async def execute(
        self, tool_id: str, **kwargs
    ) -> ToolResult:
        """Execute a tool

        Args:
            tool_id: Tool to execute
            **kwargs: Tool parameters

        Returns:
            ToolResult
        """
        tool = self.get_tool(tool_id)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool {tool_id} not found",
            )

        return await tool.run(**kwargs)

    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics

        Returns:
            Stats about registered tools
        """
        total_tools = len(self._tools)
        categories = {}
        total_executions = 0

        for tool in self._tools.values():
            # Count by category
            cat = tool.category
            categories[cat] = categories.get(cat, 0) + 1
            # Count total executions
            total_executions += tool.execution_count

        return {
            "total_tools": total_tools,
            "categories": categories,
            "total_executions": total_executions,
            "tools": [t.tool_id for t in self._tools.values()],
        }

    def unregister(self, tool_id: str) -> bool:
        """Unregister a tool

        Args:
            tool_id: Tool to unregister

        Returns:
            True if unregistered, False if not found
        """
        if tool_id in self._tools:
            del self._tools[tool_id]
            logger.info(f"Tool unregistered: {tool_id}")
            return True
        return False


def get_tool_registry() -> ToolRegistry:
    """Get or create tool registry singleton

    Returns:
        ToolRegistry instance
    """
    return ToolRegistry()
