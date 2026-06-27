"""
Voice Agent - Audio conversation and voice interaction
Handles speech-to-text, text-to-speech, and voice conversations
"""
from typing import Dict, Any
from app.agents.base import BaseAgent, AgentCapability
from app.services.chat_service import get_chat_service
from app.memory.memory import get_memory_service
from app.services.llm import get_llm_service
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class VoiceAgent(BaseAgent):
    """Voice Agent - Audio conversation and voice interaction

    This agent provides:
    - Speech-to-Text (transcription)
    - Text-to-Speech (synthesis)
    - Voice conversations
    - Audio memory management
    """

    def __init__(self):
        """Initialize Voice Agent"""
        super().__init__(
            agent_id="ivy-voice",
            name="Ivy Voice",
            description="Voice interaction with speech-to-text and text-to-speech capabilities",
            version="1.0.0",
        )

        # Initialize services
        self.chat_service = get_chat_service()
        self.memory_service = get_memory_service()
        self.llm_service = get_llm_service()

        # Define capabilities
        self.add_capability(
            AgentCapability(
                name="speech-to-text",
                description="Transcribe audio to text",
            )
        )
        self.add_capability(
            AgentCapability(
                name="text-to-speech",
                description="Synthesize text to speech",
            )
        )
        self.add_capability(
            AgentCapability(
                name="voice-conversation",
                description="Conduct voice conversations",
            )
        )
        self.add_capability(
            AgentCapability(
                name="audio-memory",
                description="Store and retrieve audio interactions",
            )
        )

        logger.info("VoiceAgent initialized successfully")

    async def _transcribe_audio(
        self, audio_data: str, language: str = "en"
    ) -> str:
        """Transcribe audio to text

        Args:
            audio_data: Audio data
            language: Language code

        Returns:
            Transcribed text
        """
        try:
            # Use speech-to-text tool if available
            if self.tool_exists("speech-to-text"):
                result = await self.use_tool(
                    "speech-to-text",
                    audio_data=audio_data,
                    audio_type="base64",
                    language=language,
                )
                if result["success"]:
                    return result["data"]["transcription"]["text"]

            return "Audio transcription failed"

        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            raise

    async def _synthesize_speech(
        self,
        text: str,
        voice: str = "neutral",
        language: str = "en",
        speed: float = 1.0,
    ) -> Dict[str, Any]:
        """Synthesize text to speech

        Args:
            text: Text to synthesize
            voice: Voice type
            language: Language code
            speed: Speed multiplier

        Returns:
            Synthesis result
        """
        try:
            # Use text-to-speech tool if available
            if self.tool_exists("text-to-speech"):
                result = await self.use_tool(
                    "text-to-speech",
                    text=text,
                    voice=voice,
                    language=language,
                    speed=speed,
                )
                if result["success"]:
                    return result["data"]["synthesis"]

            return {"error": "Speech synthesis failed"}

        except Exception as e:
            logger.error(f"Error synthesizing speech: {str(e)}")
            raise

    async def process(self, message: str, context: Dict[str, Any]) -> str:
        """Process voice-related requests

        Args:
            message: User message (can include audio reference)
            context: Additional context

        Returns:
            Response text
        """
        try:
            logger.info("VoiceAgent processing message")

            session_id = context.get("session_id")

            # Check if message contains audio reference
            if "audio:" in message.lower() or message.startswith("audio_"):
                # Extract audio data
                audio_data = message.split(":", 1)[1].strip()
                language = context.get("language", "en")

                # Transcribe audio
                logger.info("Transcribing audio")
                transcribed = await self._transcribe_audio(
                    audio_data, language
                )

                # Add to memory
                if session_id:
                    self.memory_service.add_message(
                        session_id, "user", f"[Audio] {transcribed}"
                    )

                # Process transcribed text
                response = await self.chat_service.chat_with_context(
                    message=transcribed,
                    session_id=session_id,
                )

                # Synthesize response to speech
                synthesis = await self._synthesize_speech(
                    response,
                    voice=context.get("voice", "neutral"),
                    language=language,
                )

                # Add response to memory
                if session_id:
                    self.memory_service.add_message(
                        session_id, "assistant", response
                    )

                return f"[Voice Response] {response}"

            else:
                # Regular text message - convert to speech if requested
                response = await self.chat_service.chat_with_context(
                    message=message,
                    session_id=session_id,
                )

                # Add to memory
                if session_id:
                    self.memory_service.add_message(session_id, "user", message)
                    self.memory_service.add_message(
                        session_id, "assistant", response
                    )

                # Synthesize to speech if requested
                if context.get("synthesize_response"):
                    synthesis = await self._synthesize_speech(
                        response,
                        voice=context.get("voice", "neutral"),
                    )
                    return f"[Voice Response] {response}"

                return response

        except Exception as e:
            logger.error(f"Error in VoiceAgent.process: {str(e)}")
            raise


async def get_voice_agent() -> VoiceAgent:
    """Get or create voice agent instance"""
    return VoiceAgent()
