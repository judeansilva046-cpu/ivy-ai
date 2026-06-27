"""
Plugin Framework for Ivy AI
Base classes and interfaces for plugin development
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class PluginType(str, Enum):
    """Plugin type enumeration"""
    AGENT = "agent"
    TOOL = "tool"
    STORAGE = "storage"
    SERVICE = "service"
    MIDDLEWARE = "middleware"
    CUSTOM = "custom"


class PluginDependency:
    """Represents a plugin dependency"""

    def __init__(
        self,
        name: str,
        version: str = "*",
        required: bool = True,
    ):
        self.name = name
        self.version = version
        self.required = required

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "required": self.required,
        }


class PluginMetadata:
    """Plugin metadata and information"""

    def __init__(
        self,
        name: str,
        version: str,
        description: str,
        author: str,
        plugin_type: PluginType,
        entry_point: str,
        min_ivy_version: str = "2.0.0",
        dependencies: Optional[List[PluginDependency]] = None,
        tags: Optional[List[str]] = None,
    ):
        self.name = name
        self.version = version
        self.description = description
        self.author = author
        self.plugin_type = plugin_type
        self.entry_point = entry_point
        self.min_ivy_version = min_ivy_version
        self.dependencies = dependencies or []
        self.tags = tags or []
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "plugin_type": self.plugin_type.value,
            "entry_point": self.entry_point,
            "min_ivy_version": self.min_ivy_version,
            "dependencies": [d.to_dict() for d in self.dependencies],
            "tags": self.tags,
            "created_at": self.created_at,
        }


class BasePlugin(ABC):
    """Abstract base class for all plugins"""

    def __init__(self, metadata: PluginMetadata):
        """Initialize plugin

        Args:
            metadata: Plugin metadata
        """
        self.metadata = metadata
        self.enabled = False
        self.loaded_at = None
        self.config: Dict[str, Any] = {}

        logger.info(f"Plugin initialized: {metadata.name} v{metadata.version}")

    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize plugin with configuration

        Args:
            config: Plugin configuration

        Returns:
            True if initialization successful
        """
        pass

    @abstractmethod
    async def validate(self) -> bool:
        """Validate plugin state and dependencies

        Returns:
            True if plugin is valid
        """
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute plugin functionality

        Args:
            **kwargs: Plugin-specific parameters

        Returns:
            Execution result
        """
        pass

    async def shutdown(self) -> bool:
        """Shutdown plugin gracefully

        Returns:
            True if shutdown successful
        """
        logger.info(f"Plugin shutdown: {self.metadata.name}")
        return True

    def get_info(self) -> Dict[str, Any]:
        """Get plugin information

        Returns:
            Plugin information
        """
        return {
            "metadata": self.metadata.to_dict(),
            "enabled": self.enabled,
            "loaded_at": self.loaded_at,
            "config": self.config,
        }


class PluginRegistry:
    """Registry for managing plugins"""

    def __init__(self):
        """Initialize plugin registry"""
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_metadata: Dict[str, PluginMetadata] = {}
        self.hooks: Dict[str, List[callable]] = {}

        logger.info("Plugin registry initialized")

    def register(self, plugin: BasePlugin) -> bool:
        """Register a plugin

        Args:
            plugin: Plugin instance

        Returns:
            True if registration successful
        """
        try:
            plugin_id = plugin.metadata.name
            if plugin_id in self.plugins:
                logger.warning(f"Plugin already registered: {plugin_id}")
                return False

            self.plugins[plugin_id] = plugin
            self.plugin_metadata[plugin_id] = plugin.metadata

            logger.info(f"Plugin registered: {plugin_id}")
            return True

        except Exception as e:
            logger.error(f"Error registering plugin: {str(e)}")
            return False

    def unregister(self, plugin_id: str) -> bool:
        """Unregister a plugin

        Args:
            plugin_id: Plugin identifier

        Returns:
            True if unregistration successful
        """
        try:
            if plugin_id not in self.plugins:
                logger.warning(f"Plugin not found: {plugin_id}")
                return False

            plugin = self.plugins.pop(plugin_id)
            self.plugin_metadata.pop(plugin_id, None)

            logger.info(f"Plugin unregistered: {plugin_id}")
            return True

        except Exception as e:
            logger.error(f"Error unregistering plugin: {str(e)}")
            return False

    def get_plugin(self, plugin_id: str) -> Optional[BasePlugin]:
        """Get plugin by ID

        Args:
            plugin_id: Plugin identifier

        Returns:
            Plugin instance or None
        """
        return self.plugins.get(plugin_id)

    async def enable_plugin(self, plugin_id: str, config: Dict[str, Any] = None) -> bool:
        """Enable a plugin

        Args:
            plugin_id: Plugin identifier
            config: Plugin configuration

        Returns:
            True if enabled successfully
        """
        try:
            plugin = self.get_plugin(plugin_id)
            if not plugin:
                logger.warning(f"Plugin not found: {plugin_id}")
                return False

            # Initialize with config
            if config:
                plugin.config = config

            if not await plugin.initialize(plugin.config):
                logger.error(f"Failed to initialize plugin: {plugin_id}")
                return False

            # Validate plugin
            if not await plugin.validate():
                logger.error(f"Plugin validation failed: {plugin_id}")
                return False

            plugin.enabled = True
            plugin.loaded_at = datetime.now().isoformat()

            logger.info(f"Plugin enabled: {plugin_id}")
            return True

        except Exception as e:
            logger.error(f"Error enabling plugin {plugin_id}: {str(e)}")
            return False

    async def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin

        Args:
            plugin_id: Plugin identifier

        Returns:
            True if disabled successfully
        """
        try:
            plugin = self.get_plugin(plugin_id)
            if not plugin:
                return False

            if not plugin.enabled:
                return True

            await plugin.shutdown()
            plugin.enabled = False

            logger.info(f"Plugin disabled: {plugin_id}")
            return True

        except Exception as e:
            logger.error(f"Error disabling plugin {plugin_id}: {str(e)}")
            return False

    async def execute_plugin(self, plugin_id: str, **kwargs) -> Dict[str, Any]:
        """Execute a plugin

        Args:
            plugin_id: Plugin identifier
            **kwargs: Plugin parameters

        Returns:
            Execution result
        """
        try:
            plugin = self.get_plugin(plugin_id)
            if not plugin:
                return {"success": False, "error": f"Plugin not found: {plugin_id}"}

            if not plugin.enabled:
                return {"success": False, "error": f"Plugin not enabled: {plugin_id}"}

            result = await plugin.execute(**kwargs)
            return result

        except Exception as e:
            logger.error(f"Error executing plugin {plugin_id}: {str(e)}")
            return {"success": False, "error": str(e)}

    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all plugins

        Returns:
            List of plugin information
        """
        return [plugin.get_info() for plugin in self.plugins.values()]

    def list_plugins_by_type(self, plugin_type: PluginType) -> List[Dict[str, Any]]:
        """List plugins by type

        Args:
            plugin_type: Plugin type filter

        Returns:
            List of plugins of that type
        """
        return [
            plugin.get_info()
            for plugin in self.plugins.values()
            if plugin.metadata.plugin_type == plugin_type
        ]

    def register_hook(self, hook_name: str, callback: callable) -> None:
        """Register a hook callback

        Args:
            hook_name: Hook name
            callback: Callback function
        """
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)

    async def execute_hook(self, hook_name: str, **kwargs) -> List[Any]:
        """Execute all callbacks for a hook

        Args:
            hook_name: Hook name
            **kwargs: Hook parameters

        Returns:
            List of callback results
        """
        results = []
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    if hasattr(callback, "__await__"):
                        result = await callback(**kwargs)
                    else:
                        result = callback(**kwargs)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error executing hook {hook_name}: {str(e)}")

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics

        Returns:
            Statistics about plugins
        """
        enabled_count = sum(1 for p in self.plugins.values() if p.enabled)
        by_type = {}
        for plugin in self.plugins.values():
            plugin_type = plugin.metadata.plugin_type.value
            by_type[plugin_type] = by_type.get(plugin_type, 0) + 1

        return {
            "total_plugins": len(self.plugins),
            "enabled_plugins": enabled_count,
            "disabled_plugins": len(self.plugins) - enabled_count,
            "by_type": by_type,
            "plugin_list": list(self.plugins.keys()),
        }


# Global plugin registry instance
_registry: Optional[PluginRegistry] = None


def get_plugin_registry() -> PluginRegistry:
    """Get or create plugin registry singleton

    Returns:
        PluginRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = PluginRegistry()
    return _registry
