# Jarvis AI Enterprise Platform - Backend

Advanced AI-powered RAG (Retrieval-Augmented Generation) system integrated with n8n.

## Architecture

```
server/
├── api/                 # FastAPI application
│   ├── main.py         # Application entry point
│   ├── dependencies.py  # FastAPI dependencies
│   └── routes/         # API endpoints
│       ├── health.py   # Health check endpoints
│       ├── system.py   # System status endpoints
│       ├── documents.py# Document ingestion endpoints
│       └── chat.py     # Chat with RAG endpoints
├── app/                # Application logic
│   ├── services/       # AI and chat services
│   │   ├── llm.py      # OpenAI LLM wrapper
│   │   ├── embeddings.py # Embedding generation
│   │   ├── vectorstore.py # Vector store abstraction
│   │   └── chat_service.py # Chat orchestration
│   ├── rag/            # RAG pipeline
│   │   ├── loader.py   # Document loading
│   │   ├── chunker.py  # Text chunking
│   │   ├── indexer.py  # Vector indexing
│   │   └── search.py   # Semantic search
│   ├── database/       # Database connections
│   │   ├── postgres.py # PostgreSQL wrapper
│   │   ├── redis.py    # Redis cache wrapper
│   │   └── qdrant.py   # Qdrant vector store wrapper
│   ├── memory/         # Conversation memory
│   │   ├── memory.py   # Session memory
│   │   └── history.py  # Chat history
│   ├── agents/         # AI agents (future)
│   └── utils/          # Utilities
│       ├── logger.py   # Logging configuration
│       └── errors.py   # Custom exceptions
├── config/             # Configuration
│   ├── settings.py     # Settings with Pydantic
│   └── prompts.py      # Prompt templates
├── ingest/             # Document ingestion scripts
│   └── ingest_documents.py # Standalone ingestion script
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
└── README.md          # This file
```

## Setup

### 1. Install Dependencies

```bash
cd C:\JarvisAI\server
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update with your values:

```bash
cp .env.example .env
```

**Important variables:**
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `QDRANT_HOST`: Qdrant server host (default: localhost)
- `REDIS_HOST`: Redis server host (default: localhost)
- `POSTGRES_HOST`: PostgreSQL server host (default: localhost)

### 3. Ensure Services Are Running

Make sure Docker containers are running:

```bash
cd C:\JarvisAI
docker-compose up -d
```

Check services:
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- Qdrant: localhost:6333
- MinIO: localhost:9000

### 4. Start the API Server

```bash
cd C:\JarvisAI\server
.\venv\Scripts\Activate
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at: `http://127.0.0.1:8000`

## API Endpoints

### Health Check
- **GET** `/health` - Health check
- **GET** `/` - Root endpoint

### System Status
- **GET** `/system/status` - System health status
- **GET** `/system/config` - System configuration

### Document Management
- **POST** `/documents/ingest` - Ingest documents from directory
- **POST** `/documents/upload` - Upload a single PDF document
- **GET** `/documents/status` - Check document index status

### Chat with RAG
- **POST** `/chat/` - Chat with RAG integration
- **POST** `/chat/with-history` - Chat with conversation history
- **GET** `/chat/history/{session_id}` - Get conversation history
- **DELETE** `/chat/history/{session_id}` - Clear conversation history
- **GET** `/chat/session-stats/{session_id}` - Get session statistics

## Document Ingestion

### Method 1: Using the API Endpoint

```bash
curl -X POST http://127.0.0.1:8000/documents/ingest
```

### Method 2: Using the Standalone Script

```bash
python ingest/ingest_documents.py
```

### Method 3: Upload Single Document

```bash
curl -X POST http://127.0.0.1:8000/documents/upload \
  -F "file=@your_document.pdf"
```

## Chat Examples

### Simple Chat
```bash
curl -X POST http://127.0.0.1:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "O que é VertexCode?",
    "session_id": "user_123"
  }'
```

### Chat with History
```bash
curl -X POST http://127.0.0.1:8000/chat/with-history \
  -H "Content-Type: application/json" \
  -d '{
    "query": "E quais são seus serviços?",
    "session_id": "user_123",
    "history": [
      {"role": "user", "content": "O que é VertexCode?"},
      {"role": "assistant", "content": "VertexCode é..."}
    ]
  }'
```

### Get History
```bash
curl http://127.0.0.1:8000/chat/history/user_123
```

## Testing

### Health Check
```bash
curl http://127.0.0.1:8000/health
```

### System Status
```bash
curl http://127.0.0.1:8000/system/status
```

### Interactive API Documentation
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Configuration Details

### RAG Settings
- `RAG_CHUNK_SIZE`: 1000 (text chunk size in characters)
- `RAG_CHUNK_OVERLAP`: 200 (overlap between chunks)
- `RAG_TOP_K`: 5 (number of documents to retrieve)
- `RAG_MIN_SCORE`: 0.5 (minimum similarity score)

### OpenAI Models
- Chat: `gpt-4-turbo-preview`
- Embeddings: `text-embedding-3-small`

### Vector Store
- Type: Qdrant
- Vector Size: 1536 (OpenAI embeddings dimension)
- Collection: jarvis_knowledge

## Features

### ✅ Implemented
- Document loading (PDF, TXT)
- Text chunking with overlap
- Embedding generation (OpenAI)
- Semantic search (Qdrant)
- Chat with RAG
- Conversation history
- Session memory
- Caching (Redis)
- API documentation (Swagger/ReDoc)
- Structured logging
- Error handling

### 🚀 Future Features
- AI Agents (Ivy Agent)
- n8n integration
- WhatsApp integration
- NexxoHub integration
- File upload to MinIO
- PostgreSQL persistence
- Advanced authentication
- Rate limiting
- Multi-language support

## Logging

Logs are stored in `./logs/` directory in JSON format. You can view logs:

```bash
tail -f logs/jarvis_ai.log
```

## Troubleshooting

### OpenAI API Key Error
```
Error: OPENAI_API_KEY not set
```
Solution: Add your OpenAI API key to `.env` file

### Qdrant Connection Error
```
Error: Qdrant connection failed
```
Solution: Ensure Qdrant is running on port 6333

### Redis Connection Error
```
Error: Redis connection failed
```
Solution: Ensure Redis is running on port 6379

### Document Not Found
```
Error: No documents found in documents/ directory
```
Solution: Place PDF files in the `documents/` directory

## Performance Tips

1. **Increase chunk size** for faster processing but less precise context
2. **Adjust RAG_TOP_K** based on document set size
3. **Use Redis caching** to cache frequently asked questions
4. **Monitor logs** for slow queries

## Support

For issues, check:
1. Logs in `./logs/` directory
2. System status: GET `/system/status`
3. Swagger UI: http://127.0.0.1:8000/docs

## License

Business License (VertexCode)
