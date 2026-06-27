"""
Tool routes - Manage and execute tools
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.tools.base import get_tool_registry
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/tool", tags=["Tools"])


# Request/Response models
class ToolExecuteRequest(BaseModel):
    """Tool execution request"""
    parameters: Dict[str, Any]


class ToolExecuteResponse(BaseModel):
    """Tool execution response"""
    success: bool
    tool_id: str
    tool_name: str
    result: Any
    error: Optional[str] = None
    timestamp: str


class ToolInfo(BaseModel):
    """Tool information"""
    tool_id: str
    name: str
    description: str
    version: str
    category: str
    parameters: List[Dict[str, Any]]


@router.get("/list", response_model=List[ToolInfo])
async def list_tools():
    """List all registered tools"""
    try:
        registry = get_tool_registry()
        tools = registry.list_tools()

        result = [
            ToolInfo(
                tool_id=tool["tool_id"],
                name=tool["name"],
                description=tool["description"],
                version=tool["version"],
                category=tool["category"],
                parameters=tool["parameters"],
            )
            for tool in tools
        ]

        logger.info(f"Listed {len(result)} tools")
        return result

    except Exception as e:
        logger.error(f"Error listing tools: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories")
async def get_tool_categories():
    """Get available tool categories"""
    try:
        registry = get_tool_registry()
        tools = registry.list_tools()

        categories = {}
        for tool in tools:
            cat = tool["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append({
                "tool_id": tool["tool_id"],
                "name": tool["name"]
            })

        logger.info(f"Retrieved {len(categories)} categories")
        return {
            "categories": categories,
            "total_categories": len(categories),
        }

    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{tool_id}/info")
async def get_tool_info(tool_id: str):
    """Get information about a specific tool"""
    try:
        registry = get_tool_registry()
        tool = registry.get_tool(tool_id)

        if not tool:
            raise HTTPException(status_code=404, detail=f"Tool {tool_id} not found")

        info = tool.get_info()
        return {
            "tool_id": info["tool_id"],
            "name": info["name"],
            "description": info["description"],
            "version": info["version"],
            "category": info["category"],
            "parameters": info["parameters"],
            "execution_count": info["execution_count"],
            "last_execution": info["last_execution"],
            "created_at": info["created_at"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tool info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{tool_id}/execute", response_model=ToolExecuteResponse)
async def execute_tool(tool_id: str, request: ToolExecuteRequest):
    """Execute a specific tool"""
    try:
        registry = get_tool_registry()
        tool = registry.get_tool(tool_id)

        if not tool:
            raise HTTPException(status_code=404, detail=f"Tool {tool_id} not found")

        logger.info(f"Executing tool: {tool_id}")

        # Execute tool
        result = await registry.execute(tool_id, **request.parameters)

        if result.success:
            return ToolExecuteResponse(
                success=True,
                tool_id=tool_id,
                tool_name=tool.name,
                result=result.data,
                timestamp=result.timestamp,
            )
        else:
            return ToolExecuteResponse(
                success=False,
                tool_id=tool_id,
                tool_name=tool.name,
                result=None,
                error=result.error,
                timestamp=result.timestamp,
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing tool {tool_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_tool_statistics():
    """Get tool registry statistics"""
    try:
        registry = get_tool_registry()
        stats = registry.get_statistics()

        logger.info("Retrieved tool statistics")
        return {
            "total_tools": stats["total_tools"],
            "categories": stats["categories"],
            "total_executions": stats["total_executions"],
            "tools": stats["tools"],
        }

    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{tool_id}/usage")
async def get_tool_usage(tool_id: str):
    """Get usage statistics for a specific tool"""
    try:
        registry = get_tool_registry()
        tool = registry.get_tool(tool_id)

        if not tool:
            raise HTTPException(status_code=404, detail=f"Tool {tool_id} not found")

        info = tool.get_info()
        return {
            "tool_id": tool_id,
            "tool_name": tool.name,
            "execution_count": info["execution_count"],
            "last_execution": info["last_execution"],
            "created_at": info["created_at"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tool usage: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
