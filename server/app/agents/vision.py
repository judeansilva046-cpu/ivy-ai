"""
Vision Agent - Specialized agent for visual understanding
Handles image analysis, object detection, OCR, and visual reasoning
"""
from typing import Dict, Any
import base64
from app.agents.base import BaseAgent, AgentCapability
from app.services.llm import get_llm_service
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class VisionAgent(BaseAgent):
    """Vision Agent - Analyze images and understand visual content

    This agent provides:
    - Image analysis and description
    - Object detection
    - Optical Character Recognition (OCR)
    - Scene understanding
    - Visual reasoning
    """

    def __init__(self):
        """Initialize Vision Agent"""
        super().__init__(
            agent_id="ivy-vision",
            name="Ivy Vision",
            description="Visual understanding and image analysis with multiple capabilities",
            version="1.0.0",
        )

        # Initialize LLM service
        self.llm_service = get_llm_service()

        # Define capabilities
        self.add_capability(
            AgentCapability(
                name="image-analysis",
                description="Analyze and describe images",
            )
        )
        self.add_capability(
            AgentCapability(
                name="object-detection",
                description="Detect and identify objects in images",
            )
        )
        self.add_capability(
            AgentCapability(
                name="ocr",
                description="Extract text from images using OCR",
            )
        )
        self.add_capability(
            AgentCapability(
                name="scene-understanding",
                description="Analyze and understand scenes in images",
            )
        )
        self.add_capability(
            AgentCapability(
                name="visual-reasoning",
                description="Reason about visual content and answer questions",
            )
        )

        logger.info("VisionAgent initialized successfully")

    def _extract_image_data(self, message: str) -> Dict[str, Any]:
        """Extract image data from message

        Looks for:
        - Base64 encoded images
        - Image URLs
        - Image file references

        Returns:
            Dict with image_data, image_type, and remaining message
        """
        # Check for base64 image
        if "data:image" in message:
            # Extract base64 image
            start = message.find("data:image")
            end = message.find(",") + 1
            end = message.find(" ", end) if " " in message[end:] else len(message)
            image_data = message[start:end]
            remaining = message.replace(image_data, "").strip()
            return {
                "image_data": image_data,
                "image_type": "base64",
                "message": remaining,
            }

        # Check for image URL
        if "http" in message and any(ext in message.lower() for ext in [".jpg", ".png", ".gif", ".webp"]):
            # Extract URL
            import re
            url_pattern = r'https?://\S+\.(jpg|png|gif|webp)'
            match = re.search(url_pattern, message, re.IGNORECASE)
            if match:
                image_url = match.group(0)
                remaining = message.replace(image_url, "").strip()
                return {
                    "image_data": image_url,
                    "image_type": "url",
                    "message": remaining,
                }

        return {
            "image_data": None,
            "image_type": None,
            "message": message,
        }

    async def _analyze_image_with_context(
        self, image_data: str, image_type: str, question: str
    ) -> str:
        """Analyze image and answer question about it

        Args:
            image_data: Image data
            image_type: Type of image data
            question: Question about the image

        Returns:
            Analysis result
        """
        try:
            messages = [
                {
                    "role": "user",
                    "content": f"Analyze this image and answer: {question}\n\nProvide detailed analysis.",
                }
            ]

            analysis = self.llm_service.generate_response(
                messages=messages,
                system_prompt="You are a computer vision expert. Analyze images and answer questions about them.",
            )

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            raise

    async def process(self, message: str, context: Dict[str, Any]) -> str:
        """Process message for vision-related tasks

        Args:
            message: User message that may contain image reference
            context: Additional context

        Returns:
            Vision analysis or response
        """
        try:
            logger.info("VisionAgent processing message")

            # Extract image data from message
            image_info = self._extract_image_data(message)
            image_data = image_info.get("image_data")
            image_type = image_info.get("image_type")
            remaining_message = image_info.get("message")

            # If no image provided, ask for one
            if not image_data:
                return "I'm ready to analyze images. Please provide an image (URL or base64 encoded) along with your question."

            # Prepare question
            question = remaining_message if remaining_message else "Analyze this image"

            # Use vision tool if available
            if self.tool_exists("vision"):
                logger.info("Using vision tool for analysis")

                result = await self.use_tool(
                    "vision",
                    operation="analyze",
                    image_data=image_data,
                    image_type=image_type,
                    extract_text=True,
                    detect_objects=True,
                )

                if result["success"]:
                    # Format analysis results
                    analysis_parts = []
                    if "analysis" in result.get("data", {}):
                        analysis_parts.append(
                            f"**Analysis:** {result['data']['analysis']}"
                        )
                    if "ocr" in result.get("data", {}):
                        ocr = result["data"]["ocr"]
                        if ocr.get("text"):
                            analysis_parts.append(
                                f"**Text Found:** {ocr['text']}"
                            )
                    if "objects" in result.get("data", {}):
                        objects = result["data"]["objects"]
                        if objects:
                            obj_names = ", ".join(
                                [o.get("name", "unknown") for o in objects]
                            )
                            analysis_parts.append(
                                f"**Objects Detected:** {obj_names}"
                            )

                    return "\n\n".join(analysis_parts)
                else:
                    return f"Vision analysis failed: {result.get('error')}"

            # Fallback: analyze with LLM
            logger.info("Fallback: analyzing with LLM")
            analysis = await self._analyze_image_with_context(
                image_data, image_type, question
            )

            return analysis

        except Exception as e:
            logger.error(f"Error in VisionAgent.process: {str(e)}")
            raise


async def get_vision_agent() -> VisionAgent:
    """Get or create vision agent instance"""
    return VisionAgent()
