# Jarvis AI - Getting Started Guide

## Quick Start (5 minutos)

### Pré-requisitos
- ✅ Docker rodando com containers:
  - PostgreSQL (5432)
  - Redis (6379)
  - Qdrant (6333)
  - MinIO (9000)
- ✅ Python 3.10+ com venv criado
- ✅ OpenAI API Key

### Passo 1: Ativar Environment
```bash
cd C:\JarvisAI\server
.\venv\Scripts\Activate
```

### Passo 2: Configurar .env
```bash
# Copiar template
copy .env.example .env

# Abrir com editor e adicionar sua OpenAI API Key
notepad .env
```

Variáveis mínimas necessárias:
```
OPENAI_API_KEY=sk-seu-api-key-aqui
QDRANT_HOST=localhost
QDRANT_PORT=6333
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Passo 3: Iniciar o Servidor
```bash
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Você deve ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Passo 4: Testar Health Check
```bash
# Em outro terminal
curl http://127.0.0.1:8000/health
```

Resposta esperada:
```json
{
  "status": "ok",
  "service": "Jarvis AI",
  "timestamp": "2026-06-27T...",
  "version": "2.0.0"
}
```

✅ Seu servidor está rodando!

---

## Workflow Completo

### 1. Ingerir Documentos
Coloque PDFs na pasta `C:\JarvisAI\documents\` e execute:

**Opção A: Via API**
```bash
curl -X POST http://127.0.0.1:8000/documents/ingest
```

**Opção B: Script Python**
```bash
python ingest/ingest_documents.py
```

**Opção C: Upload Individual**
```bash
curl -X POST http://127.0.0.1:8000/documents/upload \
  -F "file=@documento.pdf"
```

Resposta esperada:
```json
{
  "success": true,
  "message": "Ingested 10 documents",
  "documents_loaded": 10,
  "chunks_created": 125,
  "chunks_indexed": 125
}
```

### 2. Verificar Status do Índice
```bash
curl http://127.0.0.1:8000/documents/status
```

### 3. Chat Simples
```bash
curl -X POST http://127.0.0.1:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "O que é VertexCode?",
    "session_id": "usuario_123"
  }'
```

### 4. Chat com Histórico
```bash
curl -X POST http://127.0.0.1:8000/chat/with-history \
  -H "Content-Type: application/json" \
  -d '{
    "query": "E quais são os serviços?",
    "session_id": "usuario_123",
    "history": [
      {
        "role": "user",
        "content": "O que é VertexCode?"
      },
      {
        "role": "assistant",
        "content": "VertexCode é uma empresa..."
      }
    ]
  }'
```

### 5. Acessar Interface Web
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

---

## Exemplos com Python

### Chat Simples
```python
import requests

url = "http://127.0.0.1:8000/chat/"
data = {
    "query": "O que é VertexCode?",
    "session_id": "user_123"
}

response = requests.post(url, json=data)
print(response.json()["response"])
```

### Chat com Histórico
```python
import requests

url = "http://127.0.0.1:8000/chat/with-history"
data = {
    "query": "E os serviços?",
    "session_id": "user_123",
    "history": [
        {"role": "user", "content": "O que é VertexCode?"},
        {"role": "assistant", "content": "VertexCode é..."}
    ]
}

response = requests.post(url, json=data)
print(response.json())
```

### Obter Histórico
```python
import requests

session_id = "user_123"
response = requests.get(f"http://127.0.0.1:8000/chat/history/{session_id}")
print(response.json())
```

---

## Exemplos com cURL (PowerShell)

### Chat Simples
```powershell
$body = @{
    query = "O que é VertexCode?"
    session_id = "user_123"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://127.0.0.1:8000/chat/" `
  -Method POST `
  -Body $body `
  -ContentType "application/json"
```

### Upload de Documento
```powershell
$filePath = "C:\Path\To\documento.pdf"
$fileBytes = [System.IO.File]::ReadAllBytes($filePath)

$form = @{
    file = Get-Item $filePath
}

Invoke-WebRequest -Uri "http://127.0.0.1:8000/documents/upload" `
  -Method POST `
  -Form $form
```

---

## Troubleshooting

### Erro: "OPENAI_API_KEY not set"
**Solução**: Adicione sua chave no arquivo `.env`
```
OPENAI_API_KEY=sk-seu-api-key
```

### Erro: "Qdrant connection failed"
**Solução**: Verifique se Qdrant está rodando
```bash
# Testar conexão
curl http://localhost:6333/health
```

### Erro: "Redis connection failed"
**Solução**: Verifique se Redis está rodando
```bash
# Testar conexão
redis-cli ping
```

### Erro: "No documents found"
**Solução**: Coloque PDFs em `C:\JarvisAI\documents\`

### Servidor não inicia
**Solução**: Verifique logs em `./logs/jarvis_ai.log`

---

## Monitoramento

### Ver Logs
```bash
# Log geral
tail -f server/logs/jarvis_ai.log

# Ou abrir arquivo
notepad server/logs/jarvis_ai.log
```

### Status do Sistema
```bash
curl http://127.0.0.1:8000/system/status
```

### Configuração Carregada
```bash
curl http://127.0.0.1:8000/system/config
```

---

## Performance Tips

### 1. Aumentar Cache
Documentos frequentemente consultados são cacheados por 1 hora

### 2. Ajustar RAG_TOP_K
Para mais contexto:
```
RAG_TOP_K=10
```

### 3. Aumentar Chunk Size
Para processar mais rápido:
```
RAG_CHUNK_SIZE=2000
```

### 4. Reduzir Min Score
Para mais resultados:
```
RAG_MIN_SCORE=0.3
```

---

## Integração com n8n

### Webhook para n8n
Configure um webhook no n8n apontando para:
```
POST http://seu-servidor:8000/chat/
```

Payload:
```json
{
  "query": "{{$node.trigger.query}}",
  "session_id": "{{$node.trigger.session_id}}"
}
```

---

## Próximos Passos

1. ✅ Testar todos os endpoints
2. ✅ Ingerir seus documentos
3. ✅ Integrar com n8n
4. ✅ Treinar a equipe
5. ✅ Deploy em produção

---

## Suporte

- **Documentação**: Veja `server/README.md`
- **Código**: Veja comentários nos arquivos
- **Issues**: Verifique `server/logs/`

---

**Versão**: 2.0.0
**Data**: 27 de junho de 2026
