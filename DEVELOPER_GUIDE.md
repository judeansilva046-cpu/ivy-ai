# 🚀 Ivy AI - Developer Guide

**Status:** Production-Ready  
**Version:** 1.0.0  
**Date:** 2026-06-27

---

## Quick Start

### Prerequisites
```bash
Python 3.9+
Node.js 18+
Docker
Kubernetes
```

### 1. Setup Backend
```bash
cd server
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Setup Frontend
```bash
cd web
npm install
npm run dev  # http://localhost:3000
```

### 3. Start Backend
```bash
python -m uvicorn api.main:app --reload
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### 4. Test API
```bash
# Health check
curl http://localhost:8000/admin/health

# List agents
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/agent/list

# Chat
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

---

## Project Structure

```
ivy-ai/
├── server/              # Backend (FastAPI)
│   ├── app/            # Main application
│   │   ├── agents/     # Agent implementations
│   │   ├── tools/      # Tool implementations
│   │   ├── plugins/    # Plugin system
│   │   ├── services/   # Business logic
│   │   ├── cache/      # Caching layer
│   │   ├── queue/      # Message queues
│   │   ├── analytics/  # Analytics engine
│   │   └── api/        # REST endpoints
│   ├── tests/          # Test suite
│   └── requirements.txt
├── web/                 # Frontend (Next.js)
│   ├── app/           # Pages
│   ├── components/    # React components
│   ├── lib/           # Utilities
│   └── package.json
├── k8s/               # Kubernetes
├── terraform/         # Infrastructure
├── openapi.yaml       # API spec
└── README.md
```

---

## Key Concepts

### Agents
```python
# 5 Built-in Agents
- CoreAgent: Chat & RAG
- CodeAgent: Code execution
- ResearchAgent: Web search
- VisionAgent: Image analysis
- VoiceAgent: Speech processing
```

### Tools
```python
# 9 Built-in Tools
- Calculator
- DataParser
- TextTool
- VisionTool
- SpeechToText
- TextToSpeech
- ...and more
```

### Plugins
```python
# Create custom plugins
class MyPlugin(BasePlugin):
    async def execute(self, **kwargs):
        return {"success": True, "data": {}}
```

---

## API Authentication

```python
# 1. Login
POST /auth/login
{
  "email": "user@example.com",
  "password": "password"
}

Response:
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "expires_in": 86400
}

# 2. Use token in requests
Authorization: Bearer <access_token>

# 3. Refresh token
POST /auth/refresh
{
  "refresh_token": "eyJ..."
}
```

---

## Creating a Custom Plugin

```python
# 1. Create directory
mkdir my-plugin
cd my-plugin

# 2. Use CLI
ivy plugin create my-plugin

# 3. Implement plugin.py
from app.plugins.base import BasePlugin

class MyPlugin(BasePlugin):
    @staticmethod
    def create_metadata():
        return PluginMetadata(
            name="my-plugin",
            version="1.0.0",
            description="My awesome plugin",
            author="Your Name",
            plugin_type=PluginType.TOOL,
            entry_point="MyPlugin"
        )
    
    async def execute(self, **kwargs):
        result = # do something
        return {"success": True, "data": result}

# 4. Test
ivy plugin test

# 5. Publish
ivy plugin publish --token YOUR_TOKEN
```

---

## Deployment

### Local (Docker Compose)
```bash
docker-compose up -d
```

### Production (Kubernetes)
```bash
# 1. Build image
docker build -t ivy-ai:latest .

# 2. Push to registry
docker push registry.example.com/ivy-ai:latest

# 3. Deploy
kubectl apply -f k8s/

# 4. Verify
kubectl get pods -n ivy-ai
kubectl logs -n ivy-ai deployment/ivy-ai-api
```

### AWS (Terraform)
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

---

## Common Tasks

### Start development server
```bash
python -m uvicorn api.main:app --reload
```

### Run tests
```bash
pytest tests/ -v
pytest tests/ --cov=app
```

### Add new endpoint
```python
# api/routes/my_route.py
@router.get("/my-endpoint")
async def my_endpoint():
    return {"message": "Hello"}
```

### Add new agent
```python
# app/agents/my_agent.py
class MyAgent(BaseAgent):
    agent_id = "my_agent"
    capabilities = [AgentCapability.CHAT]
    
    async def execute(self, message: str):
        return {"response": "..."}
```

---

## Troubleshooting

### Port already in use
```bash
lsof -i :8000
kill -9 <PID>
```

### Database connection error
```bash
# Check database is running
docker ps | grep postgres

# Reset database
python -m alembic downgrade base
python -m alembic upgrade head
```

### Redis connection error
```bash
# Start Redis
docker run -d -p 6379:6379 redis

# Test connection
redis-cli ping  # Should return PONG
```

---

## Performance Monitoring

```bash
# View Prometheus metrics
http://localhost:9090

# View logs (if ELK enabled)
http://localhost:5601

# Health check
curl http://localhost:8000/admin/health
```

---

## Documentation

- **API Docs:** http://localhost:8000/docs (Swagger)
- **OpenAPI Spec:** openapi.yaml
- **Architecture:** ARCHITECTURE_ANALYSIS.md
- **Agents:** AGENTS_ARCHITECTURE.md

---

## Support

- 📧 Email: support@ivyai.dev
- 💬 Discord: https://discord.gg/ivyai
- 📖 Docs: https://docs.ivyai.dev
- 🐛 Issues: https://github.com/ivyai/ivy/issues

---

