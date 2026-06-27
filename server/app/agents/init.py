"""
Agent Initialization and Registration
Registers all agents to the AgentRegistry during application startup
"""
from app.agents.base import get_agent_registry
from app.agents.core import CoreAgent
from app.agents.code import CodeAgent
from app.agents.research import ResearchAgent
from app.agents.vision import VisionAgent
from app.agents.voice import VoiceAgent
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def initialize_agents():
    """Initialize and register all agents

    Called during application startup to register:
    - CoreAgent (default)
    - CodeAgent
    - ResearchAgent
    """
    try:
        logger.info("Initializing agents...")

        registry = get_agent_registry()

        # Register CoreAgent (main agent)
        logger.info("Registering CoreAgent...")
        core_agent = CoreAgent()
        registry.register(core_agent, set_default=True)
        logger.info(f"✓ CoreAgent registered: {core_agent.agent_id}")

        # Register CodeAgent
        logger.info("Registering CodeAgent...")
        code_agent = CodeAgent()
        registry.register(code_agent)
        logger.info(f"✓ CodeAgent registered: {code_agent.agent_id}")

        # Register ResearchAgent
        logger.info("Registering ResearchAgent...")
        research_agent = ResearchAgent()
        registry.register(research_agent)
        logger.info(f"✓ ResearchAgent registered: {research_agent.agent_id}")

        # Register VisionAgent
        logger.info("Registering VisionAgent...")
        vision_agent = VisionAgent()
        registry.register(vision_agent)
        logger.info(f"✓ VisionAgent registered: {vision_agent.agent_id}")

        # Register VoiceAgent
        logger.info("Registering VoiceAgent...")
        voice_agent = VoiceAgent()
        registry.register(voice_agent)
        logger.info(f"✓ VoiceAgent registered: {voice_agent.agent_id}")

        # Log summary
        agents = registry.list_agents()
        logger.info(f"✓ Agent initialization complete: {len(agents)} agents registered")

        for agent_info in agents:
            logger.info(f"  - {agent_info['name']} ({agent_info['agent_id']})")

        return registry

    except Exception as e:
        logger.error(f"Error initializing agents: {str(e)}")
        raise
