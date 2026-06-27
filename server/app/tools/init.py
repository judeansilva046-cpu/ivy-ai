"""
Tool Initialization and Registration
Registers all built-in tools during application startup
"""
from app.tools.base import get_tool_registry
from app.tools.builtin import (
    CalculatorTool,
    DataParserTool,
    TextTool,
    ListTool,
)
from app.tools.vision import VisionTool, ImageMetadataTool
from app.tools.audio import (
    SpeechToTextTool,
    TextToSpeechTool,
    AudioMetadataTool,
)
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def initialize_tools():
    """Initialize and register all built-in tools

    Called during application startup to register:
    - CalculatorTool
    - DataParserTool
    - TextTool
    - ListTool
    """
    try:
        logger.info("Initializing tools...")

        registry = get_tool_registry()

        # Register CalculatorTool
        logger.info("Registering CalculatorTool...")
        calculator = CalculatorTool()
        registry.register(calculator)
        logger.info(f"✓ CalculatorTool registered: {calculator.tool_id}")

        # Register DataParserTool
        logger.info("Registering DataParserTool...")
        parser = DataParserTool()
        registry.register(parser)
        logger.info(f"✓ DataParserTool registered: {parser.tool_id}")

        # Register TextTool
        logger.info("Registering TextTool...")
        text_tool = TextTool()
        registry.register(text_tool)
        logger.info(f"✓ TextTool registered: {text_tool.tool_id}")

        # Register ListTool
        logger.info("Registering ListTool...")
        list_tool = ListTool()
        registry.register(list_tool)
        logger.info(f"✓ ListTool registered: {list_tool.tool_id}")

        # Register VisionTool
        logger.info("Registering VisionTool...")
        vision_tool = VisionTool()
        registry.register(vision_tool)
        logger.info(f"✓ VisionTool registered: {vision_tool.tool_id}")

        # Register ImageMetadataTool
        logger.info("Registering ImageMetadataTool...")
        image_meta_tool = ImageMetadataTool()
        registry.register(image_meta_tool)
        logger.info(
            f"✓ ImageMetadataTool registered: {image_meta_tool.tool_id}"
        )

        # Register SpeechToTextTool
        logger.info("Registering SpeechToTextTool...")
        stt_tool = SpeechToTextTool()
        registry.register(stt_tool)
        logger.info(f"✓ SpeechToTextTool registered: {stt_tool.tool_id}")

        # Register TextToSpeechTool
        logger.info("Registering TextToSpeechTool...")
        tts_tool = TextToSpeechTool()
        registry.register(tts_tool)
        logger.info(f"✓ TextToSpeechTool registered: {tts_tool.tool_id}")

        # Register AudioMetadataTool
        logger.info("Registering AudioMetadataTool...")
        audio_meta_tool = AudioMetadataTool()
        registry.register(audio_meta_tool)
        logger.info(
            f"✓ AudioMetadataTool registered: {audio_meta_tool.tool_id}"
        )

        # Log summary
        stats = registry.get_statistics()
        logger.info(
            f"✓ Tool initialization complete: {stats['total_tools']} tools registered"
        )

        for tool_info in registry.list_tools():
            logger.info(f"  - {tool_info['name']} ({tool_info['tool_id']})")

        return registry

    except Exception as e:
        logger.error(f"Error initializing tools: {str(e)}")
        raise
