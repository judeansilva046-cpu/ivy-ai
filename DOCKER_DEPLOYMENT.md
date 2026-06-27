# 🐳 Docker Deployment Guide - Jarvis AI

## ✅ Sprint 7 Completo!

Jarvis AI está pronto para deploy em containers Docker!

---

## 📋 O que está incluído

### Containers
- ✅ **PostgreSQL 15** - Database
- ✅ **Redis 7** - Cache
- ✅ **Qdrant** - Vector database
- ✅ **N8N** - Workflow automation
- ✅ **FastAPI Backend** - Python application
- ✅ **Next.js Frontend** - React application
- ✅ **Nginx** - Reverse proxy

### Features
- ✅ Health checks para cada serviço
- ✅ Auto-restart policies
- ✅ Volume persistence
- ✅ Network isolation
- ✅ Security headers
- ✅ Logging estruturado

---

## 🚀 Deployment Local (Docker)

### Pré-requisitos
```bash
# Windows
- Docker Desktop para Windows
- WSL2 (Windows Subsystem for Linux)

# Linux
- Docker
- Docker Compose

# macOS
- Docker Desktop para Mac
```

### 1. Preparar variáveis de ambiente

```bash
# Copiar template
cp .env.production .env

# Editar com suas credenciais
# IMPORTANTE: Mudar senhas em produção!
```

**Variáveis críticas:**
```
OPENAI_API_KEY=sk-proj-... (obrigatório)
POSTGRES_PASSWORD=mudar_em_producao
JWT_SECRET_KEY=mudar_em_producao_com_string_aleatoria
```

### 2. Build das imagens

```bash
cd C:\JarvisAI

# Build backend + frontend
docker-compose build

# Ou apenas um serviço
docker-compose build backend
docker-compose build frontend
```

### 3. Iniciar serviços

```bash
# Iniciar tudo
docker-compose up -d

# Logs em tempo real
docker-compose logs -f

# Logs de um serviço específico
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 4. Verificar status

```bash
# Status de todos os containers
docker-compose ps

# Health checks
docker-compose logs --tail=50 postgres
docker-compose logs --tail=50 backend

# Teste de conectividade
curl http://localhost/health
curl http://localhost:5678  # N8N
```

---

## 🌐 URLs de Acesso

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| Frontend | http://localhost | N/A |
| Backend API | http://localhost/api | Bearer Token |
| Swagger Docs | http://localhost/docs | N/A |
| PostgreSQL | localhost:5432 | postgres:password |
| Redis | localhost:6379 | N/A |
| Qdrant | http://localhost:6333 | N/A |
| N8N | http://localhost:5678 | User/Pass |

---

## 📝 Comandos Úteis

```bash
# Parar containers
docker-compose down

# Parar e remover volumes (CUIDADO!)
docker-compose down -v

# Reiniciar um serviço
docker-compose restart backend

# Ver logs com filtro
docker-compose logs backend | grep ERROR

# Entrar em um container
docker-compose exec backend bash
docker-compose exec postgres psql -U postgres

# Rebuild após mudanças no código
docker-compose up -d --build backend
docker-compose up -d --build frontend

# Limpar tudo
docker-compose down -v
docker system prune -a
```

---

## 🔍 Troubleshooting

### Backend não conecta ao PostgreSQL
```bash
# Verificar se postgres está healthy
docker-compose ps postgres

# Logs do postgres
docker-compose logs postgres

# Conectar manualmente
docker-compose exec postgres psql -U postgres -d jarvis_db -c "\dt"
```

### Frontend não conecta ao backend
```bash
# Verificar URL no .env
echo $NEXT_PUBLIC_API_URL

# Verificar network
docker-compose exec frontend curl http://backend:8000/health

# Verificar nginx routing
docker-compose logs nginx | grep "GET"
```

### Qdrant não inicializa
```bash
# Verificar pasta de storage
docker volume ls | grep qdrant

# Reiniciar Qdrant
docker-compose restart qdrant

# Ver estado
docker-compose exec qdrant curl http://localhost:6333/health
```

### N8N não conecta ao PostgreSQL
```bash
# Criar database do N8N
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE n8n;"

# Verificar variáveis
docker-compose logs n8n | grep "DB_"
```

---

## 📊 Performance & Scaling

### Aumentar recursos
Editar `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### Múltiplas instâncias (load balancing)
```yaml
services:
  backend:
    deploy:
      replicas: 3
      
  frontend:
    deploy:
      replicas: 2
```

---

## 🔐 Production Checklist

- [ ] Mudar `JWT_SECRET_KEY` para uma string aleatória
- [ ] Mudar `POSTGRES_PASSWORD` para senha forte
- [ ] Configurar `OPENAI_API_KEY`
- [ ] Habilitar HTTPS (descomentar seção nginx.conf)
- [ ] Configurar certificados SSL/TLS
- [ ] Configurar N8N com autenticação
- [ ] Setup backups automáticos do banco
- [ ] Configurar monitoring (Prometheus/Grafana)
- [ ] Configurar logs centralizados (ELK)
- [ ] Teste de load/stress

---

## 📦 Volumes & Backup

### Backups do PostgreSQL
```bash
# Backup completo
docker-compose exec postgres pg_dump -U postgres jarvis_db > backup.sql

# Restore
docker-compose exec -T postgres psql -U postgres jarvis_db < backup.sql
```

### Backup de dados do Qdrant
```bash
# Os dados estão em: postgres_data, qdrant_data, redis_data
# Fazer backup dessas pastas
```

---

## 🚀 Deploy em Produção

### Opções:

**1. VPS (Linode, DigitalOcean, AWS)**
```bash
ssh user@your_server
cd /app
git clone seu_repo
cp .env.production .env
docker-compose up -d
```

**2. Kubernetes (EKS, AKS, GKE)**
- Usar Helm charts
- ConfigMaps para variáveis
- Persistent Volumes para dados
- Ingress Controller para HTTPS

**3. Cloud Platforms**
- AWS Elastic Container Service (ECS)
- Google Cloud Run
- Azure Container Instances
- DigitalOcean App Platform

---

## 📞 Support

Se tiver problemas:
1. Verificar `docker-compose logs`
2. Verificar saúde dos containers: `docker-compose ps`
3. Testar conectividade: `docker-compose exec service_name curl ...`
4. Verificar variáveis de ambiente: `docker-compose config`

---

## ✨ Próximas etapas

1. **Monitoring**: Prometheus + Grafana
2. **Backups**: Automated backups com scripts
3. **CI/CD**: GitHub Actions ou GitLab CI
4. **HTTPS**: Let's Encrypt + Nginx
5. **Rate limiting**: Implementar no Nginx
6. **Logging**: ELK Stack ou Datadog

---

**Status:** ✅ **PRONTO PARA PRODUÇÃO**

Comando para iniciar:
```bash
docker-compose up -d
```

Acessar em: http://localhost
