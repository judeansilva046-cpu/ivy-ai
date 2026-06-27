"""
Tool Executor for Agents
Allows agents to discover, validate, and execute tools
"""
from typing import Dict, Any, List, Optional
from app.tools.base import get_tool_registry, ToolResult
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ToolExecutor:
    """Executes tools on behalf of agents

    Provides:
    - Tool discovery and listing
    - Parameter validation
    - Tool execution with error handling
    - Tool chaining support
    - Execution context management
    """

    def __init__(self, agent_id: str):
        """Initialize tool executor for an agent

        Args:
            agent_id: ID of the agent using this executor
        """
        self.agent_id = agent_id
        self.tool_registry = get_tool_registry()
        self.execution_history: List[Dict[str, Any]] = []
        self.context: Dict[str, Any] = {}

        logger.info(f"ToolExecutor initialized for agent: {agent_id}")

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools

        Returns:
            List of tool information
        """
        return self.tool_registry.list_tools()

    def get_available_tools_by_category(
        self, category: str
    ) -> List[Dict[str, Any]]:
        """Get tools by category

        Args:
            category: Tool category

        Returns:
            List of tools in that category
        """
        return self.tool_registry.list_tools_by_category(category)

    def tool_exists(self, tool_id: str) -> bool:
        """Check if tool exists

        Args:
            tool_id: Tool identifier

        Returns:
            True if tool exists
        """
        return self.tool_registry.get_tool(tool_id) is not None

    async def execute_tool(
        self, tool_id: str, **kwargs
    ) -> ToolResult:
        """Execute a tool

        Args:
            tool_id: Tool to execute
            **kwargs: Tool parameters

        Returns:
            ToolResult
        """
        try:
            logger.info(f"Agent {self.agent_id} executing tool: {tool_id}")

            # Get tool
            tool = self.tool_registry.get_tool(tool_id)
            if not tool:
                return ToolResult(
                    success=False,
                    error=f"Tool {tool_id} not found",
                    metadata={"agent_id": self.agent_id},
                )

            # Execute tool through registry
            result = await self.tool_registry.execute(tool_id, **kwargs)

            # Track execution
            self._track_execution(tool_id, kwargs, result)

            logger.info(
                f"Agent {self.agent_id} tool execution completed: {tool_id}"
            )
            return result

        except Exception as e:
            logger.error(
                f"Error executing tool {tool_id} for agent {self.agent_id}: {str(e)}"
            )
            return ToolResult(
                success=False,
                error=str(e),
                metadata={"agent_id": self.agent_id, "tool_id": tool_id},
            )

    async def execute_tool_chain(
        self, tools: List[Dict[str, Any]]
    ) -> List[ToolResult]:
        """Execute a chain of tools sequentially

        Args:
            tools: List of dicts with 'tool_id' and 'parameters'

        Returns:
            List of ToolResults
        """
        try:
            results = []
            context = {}

            for tool_config in tools:
                tool_id = tool_config.get("tool_id")
                parameters = tool_config.get("parameters", {})

                # Add previous results to context
                parameters["_context"] = context

                logger.info(
                    f"Agent {self.agent_id} executing chain tool: {tool_id}"
                )

                # Execute tool
                result = await self.execute_tool(tool_id, **parameters)
                results.append(result)

                # Store successful result in context
                if result.success:
                    context[tool_id] = result.data
                else:
                    logger.warning(
                        f"Tool chain interrupted at {tool_id}: {result.error}"
                    )
                    break

            logger.info(
                f"Agent {self.agent_id} tool chain completed: {len(results)} tools"
            )
            return results

        except Exception as e:
            logger.error(
                f"Error in tool chain for agent {self.agent_id}: {str(e)}"
            )
            return []

    def set_context(self, key: str, value: Any) -> None:
        """Set context variable for tools

        Args:
            key: Context key
            value: Context value
        """
        self.context[key] = value
        logger.debug(f"Agent {self.agent_id} context set: {key}")

    def get_context(self, key: str, default: Any = None) -> Any:
        """Get context variable

        Args:
            key: Context key
            default: Default value if not found

        Returns:
            Context value or default
        """
        return self.context.get(key, default)

    def clear_context(self) -> None:
        """Clear all context variables"""
        self.context.clear()
        logger.debug(f"Agent {self.agent_id} context cleared")

    def _track_execution(
        self, tool_id: str, parameters: Dict, result: ToolResult
    ) -> None:
        """Track tool execution for audit trail

        Args:
            tool_id: Executed tool
            parameters: Tool parameters
            result: Execution result
        """
        execution = {
            "tool_id": tool_id,
            "parameters": parameters,
            "success": result.success,
            "timestamp": result.timestamp,
        }
        self.execution_history.append(execution)

    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get execution history

        Returns:
            List of executed tools
        """
        return self.execution_history.copy()

    def clear_execution_history(self) -> None:
        """Clear execution history"""
        self.execution_history.clear()
        logger.debug(f"Agent {self.agent_id} execution history cleared")

    def get_statistics(self) -> Dict[str, Any]:
        """Get executor statistics

        Returns:
            Statistics about tool usage
        """
        total_executions = len(self.execution_history)
        successful = sum(
            1 for e in self.execution_history if e["success"]
        )
        failed = total_executions - successful

        tools_used = set(e["tool_id"] for e in self.execution_history)

        return {
            "agent_id": self.agent_id,
            "total_executions": total_executions,
            "successful": successful,
            "failed": failed,
            "tools_used": list(tools_used),
            "available_tools": len(self.get_available_tools()),
        }
