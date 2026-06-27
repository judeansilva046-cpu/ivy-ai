"""
Example Plugins for Ivy AI
Demonstrates how to create custom plugins
"""
from typing import Dict, Any
from app.plugins.base import (
    BasePlugin,
    PluginMetadata,
    PluginType,
    PluginDependency,
)
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class WeatherPlugin(BasePlugin):
    """Example Weather Plugin - Provides weather information"""

    @staticmethod
    def create_metadata() -> PluginMetadata:
        """Create plugin metadata"""
        return PluginMetadata(
            name="weather",
            version="1.0.0",
            description="Provides weather information for locations",
            author="Ivy Team",
            plugin_type=PluginType.SERVICE,
            entry_point="WeatherPlugin",
            min_ivy_version="2.0.0",
            tags=["weather", "service", "example"],
        )

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize weather plugin

        Args:
            config: Configuration

        Returns:
            True if successful
        """
        try:
            self.config = config
            logger.info("WeatherPlugin initialized")
            return True
        except Exception as e:
            logger.error(f"WeatherPlugin initialization error: {str(e)}")
            return False

    async def validate(self) -> bool:
        """Validate plugin"""
        logger.info("WeatherPlugin validation passed")
        return True

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute weather plugin

        Args:
            **kwargs: location, unit (C/F)

        Returns:
            Weather information
        """
        try:
            location = kwargs.get("location", "Unknown")
            unit = kwargs.get("unit", "C")

            # In production, would call real weather API
            weather_data = {
                "location": location,
                "temperature": 25,
                "unit": unit,
                "condition": "Sunny",
                "humidity": 65,
                "wind_speed": 10,
            }

            logger.info(f"Weather fetched for {location}")
            return {"success": True, "data": weather_data}

        except Exception as e:
            logger.error(f"WeatherPlugin execution error: {str(e)}")
            return {"success": False, "error": str(e)}


class NotificationPlugin(BasePlugin):
    """Example Notification Plugin - Sends notifications"""

    @staticmethod
    def create_metadata() -> PluginMetadata:
        """Create plugin metadata"""
        return PluginMetadata(
            name="notifications",
            version="1.0.0",
            description="Send notifications via multiple channels",
            author="Ivy Team",
            plugin_type=PluginType.SERVICE,
            entry_point="NotificationPlugin",
            tags=["notifications", "service", "example"],
        )

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize notification plugin

        Args:
            config: Configuration with channels

        Returns:
            True if successful
        """
        try:
            self.config = config
            self.channels = config.get("channels", ["email", "slack"])
            logger.info(f"NotificationPlugin initialized with channels: {self.channels}")
            return True
        except Exception as e:
            logger.error(f"NotificationPlugin initialization error: {str(e)}")
            return False

    async def validate(self) -> bool:
        """Validate plugin"""
        if not self.channels:
            logger.error("No notification channels configured")
            return False
        return True

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute notification plugin

        Args:
            **kwargs: message, channels, recipients

        Returns:
            Notification result
        """
        try:
            message = kwargs.get("message", "")
            recipients = kwargs.get("recipients", [])
            target_channels = kwargs.get("channels", self.channels)

            if not message or not recipients:
                return {
                    "success": False,
                    "error": "message and recipients required",
                }

            results = {}
            for channel in target_channels:
                if channel in self.channels:
                    # Simulate sending notification
                    results[channel] = {
                        "sent": True,
                        "recipients": len(recipients),
                    }
                else:
                    results[channel] = {"sent": False, "error": "Channel not configured"}

            logger.info(f"Notifications sent via channels: {list(results.keys())}")
            return {"success": True, "data": results}

        except Exception as e:
            logger.error(f"NotificationPlugin execution error: {str(e)}")
            return {"success": False, "error": str(e)}


class TranslationPlugin(BasePlugin):
    """Example Translation Plugin - Translates text"""

    @staticmethod
    def create_metadata() -> PluginMetadata:
        """Create plugin metadata"""
        return PluginMetadata(
            name="translation",
            version="1.0.0",
            description="Translate text between languages",
            author="Ivy Team",
            plugin_type=PluginType.TOOL,
            entry_point="TranslationPlugin",
            tags=["translation", "tool", "example"],
        )

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize translation plugin

        Args:
            config: Configuration

        Returns:
            True if successful
        """
        try:
            self.config = config
            self.supported_languages = [
                "en",
                "pt",
                "es",
                "fr",
                "de",
                "it",
                "ja",
                "zh",
            ]
            logger.info("TranslationPlugin initialized")
            return True
        except Exception as e:
            logger.error(f"TranslationPlugin initialization error: {str(e)}")
            return False

    async def validate(self) -> bool:
        """Validate plugin"""
        if not self.supported_languages:
            logger.error("No supported languages configured")
            return False
        return True

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute translation plugin

        Args:
            **kwargs: text, source_lang, target_lang

        Returns:
            Translation result
        """
        try:
            text = kwargs.get("text", "")
            source_lang = kwargs.get("source_lang", "en")
            target_lang = kwargs.get("target_lang", "pt")

            if not text:
                return {"success": False, "error": "text is required"}

            if target_lang not in self.supported_languages:
                return {
                    "success": False,
                    "error": f"Language not supported: {target_lang}",
                }

            # In production, would call real translation API
            translated = {
                "original_text": text,
                "translated_text": f"[Translated to {target_lang}] {text}",
                "source_language": source_lang,
                "target_language": target_lang,
                "confidence": 0.95,
            }

            logger.info(f"Text translated from {source_lang} to {target_lang}")
            return {"success": True, "data": translated}

        except Exception as e:
            logger.error(f"TranslationPlugin execution error: {str(e)}")
            return {"success": False, "error": str(e)}


class CachePlugin(BasePlugin):
    """Example Cache Plugin - Caches frequently accessed data"""

    @staticmethod
    def create_metadata() -> PluginMetadata:
        """Create plugin metadata"""
        return PluginMetadata(
            name="cache",
            version="1.0.0",
            description="Cache frequently accessed data",
            author="Ivy Team",
            plugin_type=PluginType.MIDDLEWARE,
            entry_point="CachePlugin",
            tags=["cache", "middleware", "example"],
        )

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize cache plugin

        Args:
            config: Configuration

        Returns:
            True if successful
        """
        try:
            self.config = config
            self.cache = {}
            self.ttl = config.get("ttl", 3600)  # 1 hour default
            logger.info(f"CachePlugin initialized with TTL: {self.ttl}s")
            return True
        except Exception as e:
            logger.error(f"CachePlugin initialization error: {str(e)}")
            return False

    async def validate(self) -> bool:
        """Validate plugin"""
        return True

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute cache plugin

        Args:
            **kwargs: action (get/set/clear), key, value

        Returns:
            Cache operation result
        """
        try:
            action = kwargs.get("action", "get")
            key = kwargs.get("key", "")
            value = kwargs.get("value")

            if action == "get":
                if key in self.cache:
                    return {"success": True, "data": self.cache[key]}
                return {"success": False, "error": f"Key not found: {key}"}

            elif action == "set":
                if not key or value is None:
                    return {"success": False, "error": "key and value required"}
                self.cache[key] = value
                return {"success": True, "message": f"Cached: {key}"}

            elif action == "clear":
                if key:
                    self.cache.pop(key, None)
                    return {"success": True, "message": f"Cleared: {key}"}
                else:
                    self.cache.clear()
                    return {"success": True, "message": "Cache cleared"}

            else:
                return {"success": False, "error": f"Unknown action: {action}"}

        except Exception as e:
            logger.error(f"CachePlugin execution error: {str(e)}")
            return {"success": False, "error": str(e)}
