"""
Configuration module for Jarvis AI
"""
from config.settings import Settings, get_settings
from config.prompts import (
    SYSTEM_PROMPT_CHAT,
    SYSTEM_PROMPT_ANALYSIS,
    SYSTEM_PROMPT_SUMMARIZATION,
    RAG_PROMPT_TEMPLATE
)

__all__ = [
    "Settings",
    "get_settings",
    "SYSTEM_PROMPT_CHAT",
    "SYSTEM_PROMPT_ANALYSIS",
    "SYSTEM_PROMPT_SUMMARIZATION",
    "RAG_PROMPT_TEMPLATE"
]
