"""
Agent routes - Manage and interact with agents
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.agents.base import get_agent_registry
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/agent", tags=["Agents"])


# Request/Response models
class AgentRequest(BaseModel):
    """Agent request model"""
    message: str
    agent_id: Optional[str] = None
    session_id: Optional[str] = None


class AgentResponse(BaseModel):
    """Agent response model"""
    success: bool
    agent_id: str
    agent_name: str
    message: str
    response: str
    timestamp: str


class AgentInfo(BaseModel):
    """Agent information"""
    agent_id: str
    name: str
    description: str
    capabilities: List[str]


class CapabilityInfo(BaseModel):
    """Capability information"""
    name: str
    description: str
    version: str
    enabled: bool


@router.get("/list", response_model=List[AgentInfo])
async def list_agents():
    """List all registered agents"""
    try:
        registry = get_agent_registry()
        agents = registry.list_agents()

        result = [
            AgentInfo(
                agent_id=agent["agent_id"],
                name=agent["name"],
                description=agent["description"],
                capabilities=[c["name"] for c in agent["capabilities"]],
            )
            for agent in agents
        ]

        logger.info(f"Listed {len(result)} agents")
        return result

    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/info")
async def get_agent_info(agent_id: str):
    """Get information about a specific agent"""
    try:
        registry = get_agent_registry()
        agent = registry.get_agent(agent_id)

        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

        return {
            "agent_id": agent.agent_id,
            "name": agent.name,
            "description": agent.description,
            "version": agent.version,
            "capabilities": [
                {
                    "name": cap.name,
                    "description": cap.description,
                    "version": cap.version,
                    "enabled": cap.enabled,
                }
                for cap in agent.capabilities
            ],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{agent_id}/execute", response_model=AgentResponse)
async def execute_agent(agent_id: str, request: AgentRequest):
    """Execute a specific agent"""
    try:
        if not request.message or len(request.message.strip()) == 0:
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        registry = get_agent_registry()

        # Execute through registry
        response = await registry.execute(
            message=request.message,
            agent_id=agent_id,
            session_id=request.session_id,
        )

        return AgentResponse(
            success=True,
            agent_id=response.agent_id,
            agent_name=registry.get_agent(agent_id).name,
            message=request.message,
            response=response.content,
            timestamp=response.timestamp,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/default/execute", response_model=AgentResponse)
async def execute_default_agent(request: AgentRequest):
    """Execute default agent"""
    try:
        if not request.message or len(request.message.strip()) == 0:
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        registry = get_agent_registry()
        default_agent = registry.get_default_agent()

        if not default_agent:
            raise HTTPException(status_code=500, detail="No default agent configured")

        # Execute through registry
        response = await registry.execute(
            message=request.message,
            agent_id=default_agent.agent_id,
            session_id=request.session_id,
        )

        return AgentResponse(
            success=True,
            agent_id=response.agent_id,
            agent_name=default_agent.name,
            message=request.message,
            response=response.content,
            timestamp=response.timestamp,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing default agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/capabilities")
async def get_agent_capabilities(agent_id: str):
    """Get capabilities of a specific agent"""
    try:
        registry = get_agent_registry()
        agent = registry.get_agent(agent_id)

        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

        capabilities = registry.get_capabilities(agent_id)

        return {
            "agent_id": agent_id,
            "agent_name": agent.name,
            "capabilities": [
                {
                    "name": cap["name"],
                    "description": cap["description"],
                    "version": cap["version"],
                    "enabled": cap["enabled"],
                }
                for cap in capabilities
            ],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent capabilities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
