# 🤖 Ivy AI - Agents Architecture

## Overview

Ivy AI now features a **modular multi-agent architecture** built on a solid foundation while maintaining 100% backward compatibility with existing chat functionality.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  API Endpoints                          │
│            (/chat, /agent, /admin, etc)                │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│            Agent Registry                               │
│  (Central dispatch and agent management)                │
└─────────────────┬───────────────────────────────────────┘
                  │
        ┌─────────┴──────────┬────────────────┐
        │                    │                │
┌───────▼────────┐ ┌─────────▼─────┐ ┌──────▼──────────┐
│   Core Agent   │ │   Code Agent  │ │ Research Agent │
│   (RAG Chat)   │ │  (FUTURE)     │ │   (FUTURE)     │
├────────────────┤ ├───────────────┤ ├─────────────────┤
│ • RAG Search   │ │ • Code exec   │ │ • Web search   │
│ • Memory       │ │ • Debugging   │ │ • Aggregation  │
│ • Context      │ │ • Testing     │ │ • Analysis     │
└────────────────┘ └───────────────┘ └─────────────────┘
        │                    │                │
        └────────────────────┴────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│              Shared Services                            │
│  LLM | Embeddings | Memory | Tools | N8N | etc        │
└─────────────────────────────────────────────────────────┘
```

## Base Classes

### BaseAgent

All agents inherit from `BaseAgent` class:

```python
class BaseAgent(ABC):
    agent_id: str           # Unique identifier
    name: str               # Display name
    description: str        # What this agent does
    capabilities: List      # List of capabilities
    
    async def process(message, context) -> str:
        # Implement in subclass
        pass
    
    async def execute(message, session_id, **context) -> AgentMessage:
        # Handles processing and memory management
        pass
```

### AgentCapability

Describes what an agent can do:

```python
class AgentCapability:
    name: str               # "rag-chat", "code-execution", etc
    description: str        # Human-readable description
    version: str            # Feature version
    enabled: bool           # Can be toggled on/off
```

## Current Agents

### CoreAgent (Ivy Core)

**Status:** ✅ Fully Implemented

The main intelligence engine providing:

- 🧠 RAG-powered chat with semantic search
- 💾 Conversation memory and history
- 📚 Document context integration
- 🔍 Semantic search across indexed documents

**Location:** `app/agents/core.py`

**Usage:**
```python
# Via API
POST /chat/ 
{
    "message": "What does the document say about X?",
    "session_id": "user-123"
}

# Via agent directly
agent = await get_core_agent()
response = await agent.execute(message, session_id="user-123")
```

## Future Agents (Planned)

### CodeAgent
- Code execution and debugging
- Testing and validation
- Performance analysis

### ResearchAgent
- Web search and aggregation
- Information synthesis
- Citation management

### CustomAgent
- User-defined agents via plugins
- Domain-specific specialization
- Tool integration

## Agent Registry

Central management of all agents:

```python
registry = get_agent_registry()

# Register agents
registry.register(core_agent, set_default=True)
registry.register(code_agent)

# Get agent
agent = registry.get_agent("ivy-core")

# Execute through registry
response = await registry.execute(message, agent_id="ivy-core")

# List available agents
agents = registry.list_agents()
```

## Message Structure

All agent communication uses structured messages:

```python
class AgentMessage:
    content: str            # The response text
    agent_id: str           # Which agent generated it
    role: str               # "assistant" or "user"
    timestamp: str          # ISO format
    metadata: Dict          # Additional context
```

## Integration Points

### With Existing Chat Endpoint

The `/chat/` endpoint now uses agents internally:

1. Request comes to endpoint
2. Routed to default agent (CoreAgent)
3. Agent processes with existing RAG pipeline
4. Response returned to client

**Backward Compatibility:** ✅ 100% - Existing code continues to work

### With Memory Service

Agents automatically integrate with conversation memory:

```python
memory = get_memory_service()
# Add user message
memory.add_message(session_id, "user", message)
# Add agent response
memory.add_message(session_id, "assistant", response)
# Get history
history = memory.get_conversation_history(session_id)
```

### With LLM Services

Agents can use any configured LLM service:

```python
llm = get_llm_service()
embeddings = get_embedding_service()
chat = get_chat_service()
```

## Creating Custom Agents

### 1. Create Agent File

Create `app/agents/my_agent.py`:

```python
from app.agents.base import BaseAgent, AgentCapability

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="my-agent",
            name="My Custom Agent",
            description="What this agent does"
        )
        
        self.add_capability(AgentCapability(
            name="custom-capability",
            description="What the agent can do"
        ))
    
    async def process(self, message: str, context: Dict[str, Any]) -> str:
        # Implement your logic here
        return "Response"
```

### 2. Register in Initialization

```python
from app.agents.my_agent import MyAgent

registry = get_agent_registry()
my_agent = MyAgent()
registry.register(my_agent)
```

### 3. Use via API

```
POST /chat/?agent_id=my-agent
{
    "message": "Your message here"
}
```

## Configuration

### Environment Variables

```env
# Agent settings (future)
AGENTS_ENABLED=True
DEFAULT_AGENT=ivy-core
MAX_AGENTS=10
```

### Agent-Specific Settings

Each agent can have its own config:

```python
# In agent's __init__
self.config = {
    "timeout": 30,
    "max_retries": 3,
    "temperature": 0.7,
}
```

## Monitoring & Metrics

### Agent Health

```python
agent_info = agent.get_info()
# Returns: agent_id, name, version, capabilities, created_at
```

### Registry Stats

```python
agents = registry.list_agents()
capabilities = registry.get_capabilities(agent_id)
```

## Testing Agents

### Unit Test Example

```python
import pytest
from app.agents.core import CoreAgent

@pytest.mark.asyncio
async def test_core_agent_chat():
    agent = CoreAgent()
    response = await agent.execute(
        "Test message",
        session_id="test-session"
    )
    
    assert response.agent_id == "ivy-core"
    assert len(response.content) > 0
    assert response.role == "assistant"
```

### Integration Test Example

```python
@pytest.mark.asyncio
async def test_agent_registry():
    registry = get_agent_registry()
    agent = await registry.get_agent("ivy-core")
    
    response = await registry.execute(
        "What can you do?",
        agent_id="ivy-core"
    )
    
    assert response is not None
```

## Performance Considerations

1. **Agent Initialization**: Happens once, cached in registry
2. **Message Processing**: Async processing for concurrent requests
3. **Memory Management**: Shared memory service, no duplication
4. **Service Reuse**: All services are singletons

## Security

1. **Input Validation**: All agent inputs validated via Pydantic
2. **Agent Isolation**: Each agent has its own processing logic
3. **Registry Access**: Central point for authentication/authorization
4. **Audit Trail**: All agent actions logged

## Next Steps

- [ ] Implement CodeAgent
- [ ] Implement ResearchAgent
- [ ] Add agent-specific endpoints (`/agent/{agent_id}/...`)
- [ ] Implement agent health monitoring
- [ ] Add plugin system for custom agents
- [ ] Create agent marketplace

---

**This architecture enables:**
- ✅ Easy addition of specialized agents
- ✅ Clean separation of concerns
- ✅ Backward compatibility with existing code
- ✅ Scalable multi-agent system
- ✅ Plugin ecosystem potential
