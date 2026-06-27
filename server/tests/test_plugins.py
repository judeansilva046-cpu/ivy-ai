"""
Unit tests for Plugins
Comprehensive testing of plugin functionality
"""
import pytest
from app.plugins.base import (
    BasePlugin,
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


class TestPluginDependency:
    """Test PluginDependency"""

    def test_dependency_creation(self):
        """Test creating a dependency"""
        dep = PluginDependency(
            name="test-plugin",
            version="1.0.0",
            required=True
        )
        assert dep.name == "test-plugin"
        assert dep.required is True

    def test_dependency_to_dict(self):
        """Test dependency serialization"""
        dep = PluginDependency("test", "1.0.0")
        data = dep.to_dict()
        assert data["name"] == "test"


class TestPluginMetadata:
    """Test PluginMetadata"""

    def test_metadata_creation(self):
        """Test creating metadata"""
        meta = PluginMetadata(
            name="test",
            version="1.0.0",
            description="Test plugin",
            author="Test Author",
            plugin_type=PluginType.TOOL,
            entry_point="TestPlugin"
        )
        assert meta.name == "test"
        assert meta.plugin_type == PluginType.TOOL


class TestPluginRegistry:
    """Test PluginRegistry"""

    def test_registry_singleton(self):
        """Test registry is singleton"""
        reg1 = get_plugin_registry()
        reg2 = get_plugin_registry()
        assert reg1 is reg2

    def test_register_plugin(self):
        """Test registering a plugin"""
        registry = get_plugin_registry()
        meta = WeatherPlugin.create_metadata()
        plugin = WeatherPlugin(meta)
        registry.register(plugin)

        retrieved = registry.get_plugin("weather")
        assert retrieved is not None

    def test_list_plugins(self):
        """Test listing plugins"""
        registry = get_plugin_registry()
        plugins = registry.list_plugins()
        assert len(plugins) > 0

    @pytest.mark.asyncio
    async def test_enable_disable_plugin(self):
        """Test enabling and disabling plugins"""
        registry = get_plugin_registry()
        meta = WeatherPlugin.create_metadata()
        plugin = WeatherPlugin(meta)
        registry.register(plugin)

        # Enable
        success = await registry.enable_plugin("weather", {})
        assert success is True
        assert plugin.enabled is True

        # Disable
        success = await registry.disable_plugin("weather")
        assert success is True
        assert plugin.enabled is False


class TestWeatherPlugin:
    """Test WeatherPlugin"""

    def test_weather_plugin_creation(self):
        """Test creating weather plugin"""
        meta = WeatherPlugin.create_metadata()
        plugin = WeatherPlugin(meta)
        assert plugin.metadata.name == "weather"

    @pytest.mark.asyncio
    async def test_weather_plugin_init(self):
        """Test initializing weather plugin"""
        meta = WeatherPlugin.create_metadata()
        plugin = WeatherPlugin(meta)
        success = await plugin.initialize({})
        assert success is True

    @pytest.mark.asyncio
    async def test_weather_plugin_execute(self):
        """Test executing weather plugin"""
        meta = WeatherPlugin.create_metadata()
        plugin = WeatherPlugin(meta)
        await plugin.initialize({})

        result = await plugin.execute(location="São Paulo")
        assert result["success"] is True
        assert "data" in result


class TestCachePlugin:
    """Test CachePlugin"""

    def test_cache_plugin_creation(self):
        """Test creating cache plugin"""
        meta = CachePlugin.create_metadata()
        plugin = CachePlugin(meta)
        assert plugin.metadata.name == "cache"

    @pytest.mark.asyncio
    async def test_cache_set_get(self):
        """Test cache set/get operations"""
        meta = CachePlugin.create_metadata()
        plugin = CachePlugin(meta)
        await plugin.initialize({})

        # Set value
        result = await plugin.execute(action="set", key="test", value="data")
        assert result["success"] is True

        # Get value
        result = await plugin.execute(action="get", key="test")
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_cache_clear(self):
        """Test cache clear operation"""
        meta = CachePlugin.create_metadata()
        plugin = CachePlugin(meta)
        await plugin.initialize({})

        result = await plugin.execute(action="clear")
        assert result["success"] is True
