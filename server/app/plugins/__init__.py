"""
Plugins Module for Ivy AI
Plugin framework and registry for extending Ivy AI
"""
from app.plugins.base import (
    BasePlugin,
    PluginRegistry,
    PluginMetadata,
    PluginType,
    PluginDependency,
    get_plugin_registry,
)
from app.plugins.examples import (
    WeatherPlugin,
    NotificationPlugin,
    TranslationPlugin,
    CachePlugin,
)

__all__ = [
    "BasePlugin",
    "PluginRegistry",
    "PluginMetadata",
    "PluginType",
    "PluginDependency",
    "get_plugin_registry",
    "WeatherPlugin",
    "NotificationPlugin",
    "TranslationPlugin",
    "CachePlugin",
]
