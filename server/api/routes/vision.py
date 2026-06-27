"""
Vision routes - Image analysis and visual understanding
"""
from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import Optional, List
import base64
from app.agents.base import get_agent_registry
from app.tools.base import get_tool_registry
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/vision", tags=["Vision"])


# Request/Response models
class VisionAnalysisRequest(BaseModel):
    """Vision analysis request"""
    image_data: str  # base64 encoded or URL
    image_type: Optional[str] = "base64"  # base64, url, or filepath
    operation: Optional[str] = "analyze"  # analyze, detect-objects, ocr, scene-analysis, describe
    extract_text: Optional[bool] = False
    detect_objects: Optional[bool] = False


class VisionAnalysisResponse(BaseModel):
    """Vision analysis response"""
    success: bool
    operation: str
    image_type: str
    results: dict


class AgentVisionRequest(BaseModel):
    """Agent vision request"""
    message: str  # Can contain image reference
    agent_id: Optional[str] = None  # If None, uses vision-agent
    session_id: Optional[str] = None


@router.post("/analyze")
async def analyze_image(request: VisionAnalysisRequest):
    """Analyze image using vision tool"""
    try:
        if not request.image_data:
            raise HTTPException(status_code=400, detail="image_data is required")

        tool_registry = get_tool_registry()

        # Execute vision tool
        result = await tool_registry.execute(
            "vision",
            operation=request.operation,
            image_data=request.image_data,
            image_type=request.image_type,
            extract_text=request.extract_text,
            detect_objects=request.detect_objects,
        )

        if result.success:
            return VisionAnalysisResponse(
                success=True,
                operation=request.operation,
                image_type=request.image_type,
                results=result.data,
            )
        else:
            return VisionAnalysisResponse(
                success=False,
                operation=request.operation,
                image_type=request.image_type,
                results={"error": result.error},
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-and-analyze")
async def upload_and_analyze(file: UploadFile = File(...), operation: str = "analyze"):
    """Upload image and analyze it"""
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded")

        # Read file
        contents = await file.read()
        image_base64 = base64.b64encode(contents).decode("utf-8")

        tool_registry = get_tool_registry()

        # Execute vision tool
        result = await tool_registry.execute(
            "vision",
            operation=operation,
            image_data=image_base64,
            image_type="base64",
            extract_text=True,
            detect_objects=True,
        )

        if result.success:
            return {
                "success": True,
                "filename": file.filename,
                "operation": operation,
                "results": result.data,
            }
        else:
            return {
                "success": False,
                "filename": file.filename,
                "error": result.error,
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing uploaded image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent-analyze")
async def agent_analyze_image(request: AgentVisionRequest):
    """Use Vision Agent to analyze image"""
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="message is required")

        registry = get_agent_registry()

        # Use vision agent if not specified
        agent_id = request.agent_id or "ivy-vision"
        agent = registry.get_agent(agent_id)

        if not agent:
            raise HTTPException(
                status_code=404, detail=f"Agent {agent_id} not found"
            )

        logger.info(f"Agent {agent_id} analyzing image message")

        # Execute agent
        response = await agent.execute(
            message=request.message,
            session_id=request.session_id,
        )

        return {
            "success": True,
            "agent_id": response.agent_id,
            "agent_name": agent.name,
            "message": request.message,
            "analysis": response.content,
            "timestamp": response.timestamp,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in agent image analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/operations")
async def get_vision_operations():
    """Get available vision operations"""
    return {
        "operations": [
            {
                "name": "analyze",
                "description": "General image analysis",
            },
            {
                "name": "detect-objects",
                "description": "Detect objects in image",
            },
            {
                "name": "ocr",
                "description": "Extract text (OCR)",
            },
            {
                "name": "scene-analysis",
                "description": "Analyze scene content",
            },
            {
                "name": "describe",
                "description": "Generate image description",
            },
        ]
    }


@router.get("/agents")
async def get_vision_agents():
    """Get available vision-capable agents"""
    try:
        registry = get_agent_registry()
        agents = registry.list_agents()

        # Filter vision-capable agents
        vision_agents = [
            {
                "agent_id": agent["agent_id"],
                "name": agent["name"],
                "description": agent["description"],
                "capabilities": agent["capabilities"],
            }
            for agent in agents
            if any(
                "vision" in cap.lower() or "visual" in cap.lower()
                for cap in [c.get("name", "") for c in agent.get("capabilities", [])]
            )
        ]

        logger.info(f"Retrieved {len(vision_agents)} vision-capable agents")
        return {"agents": vision_agents}

    except Exception as e:
        logger.error(f"Error getting vision agents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools")
async def get_vision_tools():
    """Get available vision tools"""
    try:
        tool_registry = get_tool_registry()
        tools = tool_registry.list_tools_by_category("vision")

        logger.info(f"Retrieved {len(tools)} vision tools")
        return {
            "tools": tools,
            "total_tools": len(tools),
        }

    except Exception as e:
        logger.error(f"Error getting vision tools: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
