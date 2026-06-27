"""
Agents Module for Ivy AI
Modular agent architecture supporting multiple specialized agents
"""
from app.agents.base import (
    BaseAgent,
    AgentCapability,
    AgentMessage,
    AgentRegistry,
    get_agent_registry,
)
from app.agents.core import CoreAgent, get_core_agent
from app.agents.code import CodeAgent, get_code_agent
from app.agents.research import ResearchAgent, get_research_agent
from app.agents.vision import VisionAgent, get_vision_agent
from app.agents.voice import VoiceAgent, get_voice_agent
from app.agents.executor import ToolExecutor

__all__ = [
    "BaseAgent",
    "AgentCapability",
    "AgentMessage",
    "AgentRegistry",
    "get_agent_registry",
    "CoreAgent",
    "get_core_agent",
    "CodeAgent",
    "get_code_agent",
    "ResearchAgent",
    "get_research_agent",
    "VisionAgent",
    "get_vision_agent",
    "VoiceAgent",
    "get_voice_agent",
    "ToolExecutor",
]
