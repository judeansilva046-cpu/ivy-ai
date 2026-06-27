#!/bin/bash

################################################################################
# IVY AI - MEGA DEPLOY AUTOMATION SCRIPT
# Automatiza TUDO para Netlify + Railway
#
# Usage: bash MEGA_DEPLOY_SCRIPT.sh
################################################################################

set -e

echo "🚀 IVY AI - MEGA DEPLOY AUTOMATION"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# GitHub config
GITHUB_USER="judeanssilva046"
GITHUB_REPO="ivy-ai"

echo -e "${BLUE}STEP 1: Preparar Frontend para Netlify${NC}"
echo "========================================"

cd web

# Criar netlify.toml
echo -e "${YELLOW}Criando netlify.toml...${NC}"
cat > netlify.toml << 'EOF'
[build]
  command = "npm run build"
  publish = ".next"

[dev]
  command = "npm run dev"
  port = 3000

[[redirects]]
  from = "/api/*"
  to = "https://api.ivyai.dev/:splat"
  status = 200

[env]
  NEXT_PUBLIC_API_URL = "https://api.ivyai.dev"
  NEXT_PUBLIC_APP_URL = "https://app.ivyai.dev"
EOF
echo -e "${GREEN}✅ netlify.toml criado${NC}"

# Criar .env.production
echo -e "${YELLOW}Criando .env.production...${NC}"
cat > .env.production << 'EOF'
NEXT_PUBLIC_API_URL=https://api.ivyai.dev
NEXT_PUBLIC_APP_URL=https://app.ivyai.dev
EOF
echo -e "${GREEN}✅ .env.production criado${NC}"

# Fazer commit
echo -e "${YELLOW}Fazendo commit no GitHub...${NC}"
git add netlify.toml .env.production
git commit -m "Add Netlify configuration" || true
git push origin main || true
echo -e "${GREEN}✅ Frontend pronto para Netlify${NC}"

echo ""
echo -e "${BLUE}STEP 2: Preparar Backend para Railway${NC}"
echo "========================================="

cd ../server

# Criar Procfile
echo -e "${YELLOW}Criando Procfile...${NC}"
cat > Procfile << 'EOF'
web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
EOF
echo -e "${GREEN}✅ Procfile criado${NC}"

# Criar railway.json
echo -e "${YELLOW}Criando railway.json...${NC}"
cat > railway.json << 'EOF'
{
  "build": {
    "builder": "dockerfile"
  }
}
EOF
echo -e "${GREEN}✅ railway.json criado${NC}"

# Criar Dockerfile se não existir
if [ ! -f "Dockerfile" ]; then
  echo -e "${YELLOW}Criando Dockerfile...${NC}"
  cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/admin/health')" || exit 1

# Expose port
EXPOSE 8000

# Run
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
  echo -e "${GREEN}✅ Dockerfile criado${NC}"
else
  echo -e "${GREEN}✅ Dockerfile já existe${NC}"
fi

# Gerar variáveis de ambiente
echo -e "${YELLOW}Gerando variáveis de ambiente...${NC}"
JWT_SECRET=$(openssl rand -hex 32)
API_KEY_SALT=$(openssl rand -hex 16)

# Criar .env.railway
cat > .env.railway << EOF
JWT_SECRET=$JWT_SECRET
API_KEY_SALT=$API_KEY_SALT
DATABASE_URL=postgresql://user:pass@db:5432/ivy_ai
REDIS_URL=redis://redis:6379
ENVIRONMENT=production
DEBUG=false
EOF
echo -e "${GREEN}✅ .env.railway criado${NC}"

# Fazer commit
echo -e "${YELLOW}Fazendo commit no GitHub...${NC}"
git add Procfile railway.json Dockerfile .env.railway || true
git commit -m "Add Railway and Docker configuration" || true
git push origin main || true
echo -e "${GREEN}✅ Backend pronto para Railway${NC}"

echo ""
echo -e "${BLUE}STEP 3: Gerar Instruções Copy-Paste${NC}"
echo "======================================"

# Voltar para raiz
cd ..

# Criar arquivo com instruções
cat > DEPLOY_INSTRUCTIONS.md << 'EOF'
# 🚀 DEPLOY INSTRUCTIONS - COPY & PASTE

## NETLIFY DEPLOY (Frontend)

### 1. Go to Netlify Dashboard
https://app.netlify.com

### 2. Click "Add new site" → "Import an existing project"

### 3. Select Repository
- GitHub user: judeanssilva046
- Repository: ivy-ai

### 4. Configure Build Settings
```
Base directory: web
Build command: npm run build
Publish directory: .next
```

### 5. Environment Variables
Add these:
```
NEXT_PUBLIC_API_URL = https://api.ivyai.dev
NEXT_PUBLIC_APP_URL = https://app.ivyai.dev
```

### 6. Click "Deploy site"
⏳ Wait 2-5 minutes for build

### 7. Add Custom Domain (Optional)
- Go to: Site settings → Domain management
- Click: Add custom domain
- Enter: app.ivyai.dev
- Add DNS records in your domain registrar

✅ Frontend LIVE!

---

## RAILWAY DEPLOY (Backend)

### 1. Go to Railway Dashboard
https://railway.app

### 2. Create New Project
- Click "New Project"
- Select "Deploy from GitHub"

### 3. Select Repository
- GitHub user: judeanssilva046
- Repository: ivy-ai

### 4. Configure
Railway will auto-detect:
- requirements.txt
- Dockerfile
- Procfile

### 5. Add PostgreSQL
- Click "Add Database"
- Select "PostgreSQL"
- Railway creates it automatically

### 6. Environment Variables
Add these to Railway:
```
JWT_SECRET = [copy from .env.railway]
API_KEY_SALT = [copy from .env.railway]
DATABASE_URL = [Railway auto-generates]
REDIS_URL = [from Upstash - see below]
ENVIRONMENT = production
DEBUG = false
```

### 7. Deploy
Railway auto-deploys when you push to GitHub

✅ Backend LIVE!

---

## REDIS SETUP (Upstash)

### 1. Go to Upstash
https://upstash.com

### 2. Create Database
- Sign up (free)
- Create Database → Redis
- Region: us-east-1

### 3. Copy Connection String
- Copy "UPSTASH_REDIS_REST_URL"
- Format it as: redis://default:[password]@[host]:[port]

### 4. Add to Railway
- Add as environment variable: REDIS_URL = [your connection string]

✅ Cache LIVE!

---

## VERIFY EVERYTHING

### Frontend
```
https://app.ivyai.dev → should load
```

### Backend
```
https://api.ivyai.dev/admin/health → should return JSON
https://api.ivyai.dev/docs → should show Swagger
```

### Integration
```
1. Go to https://app.ivyai.dev
2. Try to login
3. Check if it connects to backend
4. If works → ✅ COMPLETE!
```

---

## NEXT: LAUNCH DAY

When everything is live:
1. Open: LAUNCH_DAY_CHECKLIST.md
2. Follow: 8 hours of launch tasks
3. Result: 1,000+ users

🎉 YOU'RE DONE!
EOF

echo -e "${GREEN}✅ DEPLOY_INSTRUCTIONS.md criado${NC}"

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║                                                        ║"
echo "║  ✅ AUTOMAÇÃO COMPLETA!                               ║"
echo "║                                                        ║"
echo "║  PRÓXIMOS PASSOS:                                      ║"
echo "║  1. Abrir: DEPLOY_INSTRUCTIONS.md                     ║"
echo "║  2. Seguir instruções copy-paste                      ║"
echo "║  3. 30 min depois: Platform LIVE!                     ║"
echo "║                                                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}🚀 Todos os arquivos de configuração foram criados!${NC}"
echo -e "${GREEN}📄 Instruções estão em: DEPLOY_INSTRUCTIONS.md${NC}"
echo ""
