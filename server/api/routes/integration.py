"""
Integration routes - Agent and Tool integration
Allows agents to use tools and execute complex workflows
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.agents.base import get_agent_registry
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/integration", tags=["Integration"])


# Request/Response models
class AgentToolRequest(BaseModel):
    """Request to execute agent with tool support"""
    message: str
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    use_tools: bool = True


class ToolChainRequest(BaseModel):
    """Request to execute a chain of tools"""
    tools: List[Dict[str, Any]]
    agent_id: Optional[str] = None
    session_id: Optional[str] = None


class AgentToolResponse(BaseModel):
    """Response from agent with tool execution"""
    success: bool
    agent_id: str
    agent_name: str
    message: str
    response: str
    tools_used: List[str] = []
    timestamp: str


@router.get("/{agent_id}/tools")
async def get_agent_tools(agent_id: str):
    """Get tools available to an agent"""
    try:
        registry = get_agent_registry()
        agent = registry.get_agent(agent_id)

        if not agent:
            raise HTTPException(
                status_code=404, detail=f"Agent {agent_id} not found"
            )

        tools = agent.get_available_tools()
        logger.info(f"Retrieved {len(tools)} tools for agent {agent_id}")

        return {
            "agent_id": agent_id,
            "agent_name": agent.name,
            "tools": tools,
            "total_tools": len(tools),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent tools: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/tools/categories")
async def get_agent_tool_categories(agent_id: str):
    """Get tool categories available to an agent"""
    try:
        registry = get_agent_registry()
        agent = registry.get_agent(agent_id)

        if not agent:
            raise HTTPException(
                status_code=404, detail=f"Agent {agent_id} not found"
            )

        all_tools = agent.get_available_tools()
        categories = {}

        for tool in all_tools:
            cat = tool["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append({
                "tool_id": tool["tool_id"],
                "name": tool["name"]
            })

        logger.info(
            f"Retrieved {len(categories)} tool categories for agent {agent_id}"
        )

        return {
            "agent_id": agent_id,
            "categories": categories,
            "total_categories": len(categories),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent tool categories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}/use-tool/{tool_id}")
async def agent_use_tool(agent_id: str, tool_id: str, request: Dict[str, Any]):
    """Agent uses a specific tool"""
    try:
        registry = get_agent_registry()
        agent = registry.get_agent(agent_id)

        if not agent:
            raise HTTPException(
                status_code=404, detail=f"Agent {agent_id} not found"
            )

        if not agent.tool_exists(tool_id):
            raise HTTPException(
                status_code=404, detail=f"Tool {tool_id} not found"
            )

        logger.info(
            f"Agent {agent_id} using tool {tool_id} with params: {request}"
        )

        # Execute tool
        result = await agent.use_tool(tool_id, **request)

        return {
            "success": result["success"],
            "agent_id": agent_id,
            "tool_id": tool_id,
            "result": result.get("data") if result["success"] else None,
            "error": result.get("error"),
            "timestamp": result.get("timestamp"),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in agent tool execution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}/tool-chain")
async def agent_execute_tool_chain(agent_id: str, request: ToolChainRequest):
    """Agent executes a chain of tools"""
    try:
        registry = get_agent_registry()
        agent = registry.get_agent(agent_id)

        if not agent:
            raise HTTPException(
                status_code=404, detail=f"Agent {agent_id} not found"
            )

        logger.info(
            f"Agent {agent_id} executing tool chain with {len(request.tools)} tools"
        )

        # Execute tool chain
        results = await agent.use_tools_chain(request.tools)

        # Extract tool IDs
        tools_used = [
            r["metadata"].get("tool_id", tool["tool_id"])
            for tool, r in zip(request.tools, results)
            if r["success"]
        ]

        return {
            "agent_id": agent_id,
            "agent_name": agent.name,
            "tools_used": tools_used,
            "results": results,
            "total_tools": len(request.tools),
            "successful_tools": len(tools_used),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in agent tool chain: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/tool-stats")
async def get_agent_tool_statistics(agent_id: str):
    """Get tool usage statistics for an agent"""
    try:
        registry = get_agent_registry()
        agent = registry.get_agent(agent_id)

        if not agent:
            raise HTTPException(
                status_code=404, detail=f"Agent {agent_id} not found"
            )

        stats = agent.get_tool_statistics()
        logger.info(f"Retrieved tool statistics for agent {agent_id}")

        return {
            "agent_id": agent_id,
            "agent_name": agent.name,
            "statistics": stats,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent tool statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}/execute-with-tools")
async def agent_execute_with_tools(agent_id: str, request: AgentToolRequest):
    """Execute agent message with tool support

    Agent can automatically use tools to answer the question
    """
    try:
        if not request.message or len(request.message.strip()) == 0:
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        registry = get_agent_registry()
        agent = (
            registry.get_agent(agent_id)
            if agent_id
            else registry.get_default_agent()
        )

        if not agent:
            raise HTTPException(
                status_code=404,
                detail=f"Agent {agent_id or 'default'} not found",
            )

        logger.info(
            f"Executing agent {agent.agent_id} with tool support: {request.message}"
        )

        # Execute agent
        response = await agent.execute(
            message=request.message,
            session_id=request.session_id,
        )

        # Get tool statistics to show what was used
        tool_stats = agent.get_tool_statistics()
        tools_used = tool_stats.get("tools_used", [])

        return AgentToolResponse(
            success=True,
            agent_id=response.agent_id,
            agent_name=agent.name,
            message=request.message,
            response=response.content,
            tools_used=tools_used,
            timestamp=response.timestamp,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in agent execution with tools: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
