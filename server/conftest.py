"""
Pytest configuration and fixtures
"""
import pytest
import asyncio
import sys
from pathlib import Path

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent))


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_config():
    """Test configuration"""
    return {
        "debug": True,
        "database_url": "sqlite:///test.db",
        "redis_url": "redis://localhost:6379",
    }


@pytest.fixture(autouse=True)
async def cleanup():
    """Cleanup after each test"""
    yield
    # Cleanup code here if needed


@pytest.fixture
def mock_agent():
    """Mock agent for testing"""
    from app.agents.base import AgentCapability

    class MockAgent:
        agent_id = "mock"
        name = "Mock Agent"
        capabilities = [AgentCapability.CHAT]

    return MockAgent()


@pytest.fixture
def mock_tool():
    """Mock tool for testing"""

    class MockTool:
        tool_id = "mock"
        name = "Mock Tool"

    return MockTool()
