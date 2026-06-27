"""
Integration Tests for Agent-Tool System
Testing complete workflows combining agents and tools
"""
import pytest
from app.agents.base import get_agent_registry
from app.agents.executor import ToolExecutor
from app.tools.base import get_tool_registry
from app.plugins.base import get_plugin_registry


class TestAgentToolIntegration:
    """Test agent-tool integration"""

    @pytest.mark.asyncio
    async def test_core_agent_with_calculator(self):
        """Test CoreAgent using calculator tool"""
        agent_registry = get_agent_registry()
        tool_registry = get_tool_registry()
        executor = ToolExecutor()

        # Get CoreAgent
        core_agent = agent_registry.get_agent("core")
        assert core_agent is not None

        # Get calculator tool
        calc_tool = tool_registry.get_tool("calculator")
        assert calc_tool is not None

        # Execute tool through executor
        result = await executor.execute_tool(
            tool_id="calculator",
            operation="add",
            a=10,
            b=20
        )
        assert result.success is True

    @pytest.mark.asyncio
    async def test_code_agent_execution(self):
        """Test CodeAgent"""
        agent_registry = get_agent_registry()
        code_agent = agent_registry.get_agent("code")
        assert code_agent is not None

    @pytest.mark.asyncio
    async def test_research_agent_execution(self):
        """Test ResearchAgent"""
        agent_registry = get_agent_registry()
        research_agent = agent_registry.get_agent("research")
        assert research_agent is not None

    @pytest.mark.asyncio
    async def test_vision_agent_execution(self):
        """Test VisionAgent"""
        agent_registry = get_agent_registry()
        vision_agent = agent_registry.get_agent("vision")
        assert vision_agent is not None

    @pytest.mark.asyncio
    async def test_voice_agent_execution(self):
        """Test VoiceAgent"""
        agent_registry = get_agent_registry()
        voice_agent = agent_registry.get_agent("voice")
        assert voice_agent is not None


class TestToolExecutor:
    """Test ToolExecutor functionality"""

    @pytest.mark.asyncio
    async def test_executor_singleton(self):
        """Test executor is accessible"""
        executor = ToolExecutor()
        assert executor is not None

    @pytest.mark.asyncio
    async def test_tool_chaining(self):
        """Test chaining multiple tools"""
        executor = ToolExecutor()

        # First tool: calculate
        result1 = await executor.execute_tool(
            tool_id="calculator",
            operation="add",
            a=5,
            b=5
        )
        assert result1.success is True

        # Second tool: parse data
        result2 = await executor.execute_tool(
            tool_id="data-parser",
            format="json",
            data='{"result": 10}'
        )
        assert result2.success is True


class TestPluginIntegration:
    """Test plugin integration with agents"""

    @pytest.mark.asyncio
    async def test_plugin_with_agent(self):
        """Test using plugin with agent"""
        plugin_registry = get_plugin_registry()
        agent_registry = get_agent_registry()

        core_agent = agent_registry.get_agent("core")
        plugins = plugin_registry.list_plugins()

        assert core_agent is not None
        assert len(plugins) > 0

    @pytest.mark.asyncio
    async def test_plugin_execute_workflow(self):
        """Test complete plugin execution workflow"""
        plugin_registry = get_plugin_registry()

        # Get weather plugin
        weather = plugin_registry.get_plugin("weather")
        if weather:
            await weather.initialize({})
            result = await weather.execute(location="São Paulo")
            assert result["success"] is True


class TestEndToEndWorkflows:
    """End-to-end workflow tests"""

    @pytest.mark.asyncio
    async def test_chat_workflow(self):
        """Test complete chat workflow"""
        agent_registry = get_agent_registry()
        core_agent = agent_registry.get_agent("core")
        assert core_agent is not None

    @pytest.mark.asyncio
    async def test_code_analysis_workflow(self):
        """Test code analysis workflow"""
        agent_registry = get_agent_registry()
        code_agent = agent_registry.get_agent("code")
        assert code_agent is not None

    @pytest.mark.asyncio
    async def test_vision_analysis_workflow(self):
        """Test vision analysis workflow"""
        agent_registry = get_agent_registry()
        vision_agent = agent_registry.get_agent("vision")
        assert vision_agent is not None

    @pytest.mark.asyncio
    async def test_voice_conversation_workflow(self):
        """Test voice conversation workflow"""
        agent_registry = get_agent_registry()
        voice_agent = agent_registry.get_agent("voice")
        assert voice_agent is not None


class TestRegistrySystems:
    """Test registry systems"""

    def test_agent_registry_singleton(self):
        """Test agent registry is singleton"""
        reg1 = get_agent_registry()
        reg2 = get_agent_registry()
        assert reg1 is reg2

    def test_tool_registry_singleton(self):
        """Test tool registry is singleton"""
        reg1 = get_tool_registry()
        reg2 = get_tool_registry()
        assert reg1 is reg2

    def test_plugin_registry_singleton(self):
        """Test plugin registry is singleton"""
        reg1 = get_plugin_registry()
        reg2 = get_plugin_registry()
        assert reg1 is reg2

    def test_all_agents_registered(self):
        """Test all 5 agents are registered"""
        registry = get_agent_registry()
        agents = registry.list_agents()
        assert len(agents) == 5
        agent_ids = [a.agent_id for a in agents]
        assert "core" in agent_ids
        assert "code" in agent_ids
        assert "research" in agent_ids
        assert "vision" in agent_ids
        assert "voice" in agent_ids

    def test_all_tools_registered(self):
        """Test all 9 tools are registered"""
        registry = get_tool_registry()
        tools = registry.list_tools()
        assert len(tools) >= 9

    def test_plugins_registered(self):
        """Test plugins are registered"""
        registry = get_plugin_registry()
        plugins = registry.list_plugins()
        assert len(plugins) >= 4
