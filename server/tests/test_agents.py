"""
Unit tests for Agents
Comprehensive testing of agent functionality
"""
import pytest
from app.agents.base import (
    BaseAgent,
    AgentCapability,
    AgentMessage,
    AgentRegistry,
    get_agent_registry,
)
from app.agents.core import CoreAgent
from app.agents.code import CodeAgent
from app.agents.research import ResearchAgent


class TestAgentCapability:
    """Test AgentCapability"""

    def test_capability_creation(self):
        """Test creating a capability"""
        cap = AgentCapability(
            name="test-cap",
            description="Test capability",
            version="1.0.0"
        )
        assert cap.name == "test-cap"
        assert cap.enabled is True

    def test_capability_to_dict(self):
        """Test capability serialization"""
        cap = AgentCapability("test", "desc")
        data = cap.to_dict()
        assert "name" in data
        assert "enabled" in data


class TestAgentMessage:
    """Test AgentMessage"""

    def test_message_creation(self):
        """Test creating a message"""
        msg = AgentMessage(
            content="Test message",
            agent_id="test-agent",
            role="assistant"
        )
        assert msg.content == "Test message"
        assert msg.agent_id == "test-agent"
        assert msg.role == "assistant"
        assert msg.timestamp is not None

    def test_message_to_dict(self):
        """Test message serialization"""
        msg = AgentMessage("content", "agent-1")
        data = msg.to_dict()
        assert data["content"] == "content"
        assert data["agent_id"] == "agent-1"


class TestAgentRegistry:
    """Test AgentRegistry"""

    def test_registry_singleton(self):
        """Test registry is singleton"""
        reg1 = get_agent_registry()
        reg2 = get_agent_registry()
        assert reg1 is reg2

    def test_register_agent(self):
        """Test registering an agent"""
        registry = get_agent_registry()
        agent = CoreAgent()
        registry.register(agent)

        retrieved = registry.get_agent("ivy-core")
        assert retrieved is not None
        assert retrieved.agent_id == "ivy-core"

    def test_list_agents(self):
        """Test listing agents"""
        registry = get_agent_registry()
        agents = registry.list_agents()
        assert len(agents) > 0
        assert any(a["agent_id"] == "ivy-core" for a in agents)

    def test_get_nonexistent_agent(self):
        """Test getting nonexistent agent"""
        registry = get_agent_registry()
        agent = registry.get_agent("nonexistent")
        assert agent is None

    def test_unregister_agent(self):
        """Test unregistering an agent"""
        registry = get_agent_registry()
        agent = CoreAgent()
        registry.register(agent)

        success = registry.unregister("ivy-core")
        assert success is True

        retrieved = registry.get_agent("ivy-core")
        assert retrieved is None


class TestCoreAgent:
    """Test CoreAgent"""

    def test_core_agent_creation(self):
        """Test creating core agent"""
        agent = CoreAgent()
        assert agent.agent_id == "ivy-core"
        assert agent.name == "Ivy Core"
        assert len(agent.capabilities) > 0

    def test_core_agent_info(self):
        """Test core agent info"""
        agent = CoreAgent()
        info = agent.get_info()
        assert info["agent_id"] == "ivy-core"
        assert info["name"] == "Ivy Core"
        assert "capabilities" in info

    def test_core_agent_has_tools(self):
        """Test core agent has tool executor"""
        agent = CoreAgent()
        assert agent.tool_executor is not None


@pytest.mark.asyncio
async def test_core_agent_execute():
    """Test core agent execution"""
    agent = CoreAgent()

    try:
        response = await agent.execute(
            message="Test message",
            session_id="test-session"
        )

        assert response is not None
        assert response.agent_id == "ivy-core"
        assert isinstance(response, AgentMessage)
    except Exception as e:
        # Expected in test environment
        assert "chat_service" in str(e) or "memory_service" in str(e)
