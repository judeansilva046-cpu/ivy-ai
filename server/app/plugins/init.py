"""
Plugin Initialization and Registration
Registers built-in example plugins during application startup
"""
from app.plugins.base import get_plugin_registry
from app.plugins.examples import (
    WeatherPlugin,
    NotificationPlugin,
    TranslationPlugin,
    CachePlugin,
)
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


def initialize_plugins():
    """Initialize and register built-in plugins

    Called during application startup to register example plugins:
    - WeatherPlugin
    - NotificationPlugin
    - TranslationPlugin
    - CachePlugin
    """
    try:
        logger.info("Initializing plugins...")

        registry = get_plugin_registry()

        # Register WeatherPlugin
        logger.info("Registering WeatherPlugin...")
        weather_metadata = WeatherPlugin.create_metadata()
        weather_plugin = WeatherPlugin(weather_metadata)
        registry.register(weather_plugin)
        logger.info(f"✓ WeatherPlugin registered: {weather_plugin.metadata.name}")

        # Register NotificationPlugin
        logger.info("Registering NotificationPlugin...")
        notif_metadata = NotificationPlugin.create_metadata()
        notif_plugin = NotificationPlugin(notif_metadata)
        registry.register(notif_plugin)
        logger.info(
            f"✓ NotificationPlugin registered: {notif_plugin.metadata.name}"
        )

        # Register TranslationPlugin
        logger.info("Registering TranslationPlugin...")
        trans_metadata = TranslationPlugin.create_metadata()
        trans_plugin = TranslationPlugin(trans_metadata)
        registry.register(trans_plugin)
        logger.info(
            f"✓ TranslationPlugin registered: {trans_plugin.metadata.name}"
        )

        # Register CachePlugin
        logger.info("Registering CachePlugin...")
        cache_metadata = CachePlugin.create_metadata()
        cache_plugin = CachePlugin(cache_metadata)
        registry.register(cache_plugin)
        logger.info(f"✓ CachePlugin registered: {cache_plugin.metadata.name}")

        # Log summary
        stats = registry.get_statistics()
        logger.info(
            f"✓ Plugin initialization complete: {stats['total_plugins']} plugins registered"
        )

        for plugin_id in stats["plugin_list"]:
            logger.info(f"  - {plugin_id}")

        return registry

    except Exception as e:
        logger.error(f"Error initializing plugins: {str(e)}")
        raise
