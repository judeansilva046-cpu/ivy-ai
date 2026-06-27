"""
Audio routes - Speech-to-text and text-to-speech
"""
from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import Optional
import base64
from app.agents.base import get_agent_registry
from app.tools.base import get_tool_registry
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter(prefix="/audio", tags=["Audio"])


# Request/Response models
class SpeechToTextRequest(BaseModel):
    """Speech-to-text request"""
    audio_data: str  # base64 encoded or URL
    audio_type: Optional[str] = "base64"
    language: Optional[str] = "en"
    detect_language: Optional[bool] = True


class TextToSpeechRequest(BaseModel):
    """Text-to-speech request"""
    text: str
    voice: Optional[str] = "neutral"  # male, female, neutral
    language: Optional[str] = "en"
    speed: Optional[float] = 1.0  # 0.5-2.0
    pitch: Optional[int] = 0  # -20 to +20


class VoiceConversationRequest(BaseModel):
    """Voice conversation request"""
    message: str  # Can be audio reference or text
    agent_id: Optional[str] = None  # If None, uses voice-agent
    session_id: Optional[str] = None
    language: Optional[str] = "en"
    voice: Optional[str] = "neutral"
    synthesize_response: Optional[bool] = False


@router.post("/speech-to-text")
async def speech_to_text(request: SpeechToTextRequest):
    """Transcribe audio to text"""
    try:
        if not request.audio_data:
            raise HTTPException(status_code=400, detail="audio_data is required")

        tool_registry = get_tool_registry()

        # Execute speech-to-text tool
        result = await tool_registry.execute(
            "speech-to-text",
            audio_data=request.audio_data,
            audio_type=request.audio_type,
            language=request.language,
            detect_language=request.detect_language,
        )

        if result.success:
            return {
                "success": True,
                "transcription": result.data["transcription"],
                "audio_type": request.audio_type,
            }
        else:
            return {
                "success": False,
                "error": result.error,
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in speech-to-text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/text-to-speech")
async def text_to_speech(request: TextToSpeechRequest):
    """Synthesize text to speech"""
    try:
        if not request.text:
            raise HTTPException(status_code=400, detail="text is required")

        tool_registry = get_tool_registry()

        # Execute text-to-speech tool
        result = await tool_registry.execute(
            "text-to-speech",
            text=request.text,
            voice=request.voice,
            language=request.language,
            speed=request.speed,
            pitch=request.pitch,
        )

        if result.success:
            return {
                "success": True,
                "synthesis": result.data["synthesis"],
            }
        else:
            return {
                "success": False,
                "error": result.error,
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in text-to-speech: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-audio")
async def upload_audio(file: UploadFile = File(...), language: str = "en"):
    """Upload and transcribe audio file"""
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded")

        # Read file
        contents = await file.read()
        audio_base64 = base64.b64encode(contents).decode("utf-8")

        tool_registry = get_tool_registry()

        # Execute speech-to-text tool
        result = await tool_registry.execute(
            "speech-to-text",
            audio_data=audio_base64,
            audio_type="base64",
            language=language,
            detect_language=True,
        )

        if result.success:
            return {
                "success": True,
                "filename": file.filename,
                "transcription": result.data["transcription"],
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
        logger.error(f"Error processing audio file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice-conversation")
async def voice_conversation(request: VoiceConversationRequest):
    """Conduct voice conversation"""
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="message is required")

        registry = get_agent_registry()

        # Use voice agent if not specified
        agent_id = request.agent_id or "ivy-voice"
        agent = registry.get_agent(agent_id)

        if not agent:
            raise HTTPException(
                status_code=404, detail=f"Agent {agent_id} not found"
            )

        logger.info(f"Voice conversation with agent {agent_id}")

        # Execute agent with voice context
        response = await agent.execute(
            message=request.message,
            session_id=request.session_id,
            language=request.language,
            voice=request.voice,
            synthesize_response=request.synthesize_response,
        )

        return {
            "success": True,
            "agent_id": response.agent_id,
            "agent_name": agent.name,
            "message": request.message,
            "response": response.content,
            "timestamp": response.timestamp,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in voice conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voices")
async def get_available_voices():
    """Get available voices for TTS"""
    return {
        "voices": [
            {
                "id": "male",
                "name": "Male Voice",
                "language_support": ["en", "pt", "es"],
            },
            {
                "id": "female",
                "name": "Female Voice",
                "language_support": ["en", "pt", "es"],
            },
            {
                "id": "neutral",
                "name": "Neutral Voice",
                "language_support": ["en", "pt", "es"],
            },
        ]
    }


@router.get("/languages")
async def get_supported_languages():
    """Get supported languages for speech"""
    return {
        "languages": [
            {
                "code": "en",
                "name": "English",
                "native_name": "English",
            },
            {
                "code": "pt",
                "name": "Portuguese",
                "native_name": "Português",
            },
            {
                "code": "es",
                "name": "Spanish",
                "native_name": "Español",
            },
            {
                "code": "fr",
                "name": "French",
                "native_name": "Français",
            },
            {
                "code": "de",
                "name": "German",
                "native_name": "Deutsch",
            },
        ]
    }


@router.get("/tools")
async def get_audio_tools():
    """Get available audio tools"""
    try:
        tool_registry = get_tool_registry()
        tools = tool_registry.list_tools_by_category("audio")

        logger.info(f"Retrieved {len(tools)} audio tools")
        return {
            "tools": tools,
            "total_tools": len(tools),
        }

    except Exception as e:
        logger.error(f"Error getting audio tools: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def get_audio_agents():
    """Get audio-capable agents"""
    try:
        registry = get_agent_registry()
        agents = registry.list_agents()

        # Filter audio-capable agents
        audio_agents = [
            {
                "agent_id": agent["agent_id"],
                "name": agent["name"],
                "description": agent["description"],
                "capabilities": agent["capabilities"],
            }
            for agent in agents
            if any(
                "voice" in cap.lower() or "audio" in cap.lower()
                for cap in [c.get("name", "") for c in agent.get("capabilities", [])]
            )
        ]

        logger.info(f"Retrieved {len(audio_agents)} audio-capable agents")
        return {"agents": audio_agents}

    except Exception as e:
        logger.error(f"Error getting audio agents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
