# 🚀 **SETUP COMPLETO - NETLIFY + RAILWAY**

**Tempo Total:** 30-45 minutos  
**Resultado:** Platform LIVE com links permanentes  
**Custo:** ~$5-10/mês

---

## 📋 **CHECKLIST DE TUDO QUE PRECISA**

```
PRÉ-REQUISITOS:
☐ GitHub account
☐ Seu código no GitHub (public repo)
☐ Netlify account (grátis)
☐ Railway account (trial grátis 7 dias)
☐ Upstash account (grátis)
☐ Domínio ivyai.dev (já tem?)
```

---

## **FASE 1: SETUP GITHUB (5 MIN)**

### **Passo 1.1: Criar/verificar GitHub repo**

```bash
# Verificar se já tem repo:
cd /path/to/ivy-ai
git remote -v
# Deve mostrar: origin https://github.com/seu-usuario/ivy-ai.git

# Se não tiver, criar:
git init
git add .
git commit -m "Initial commit - Ivy AI production ready"
git branch -M main
git remote add origin https://github.com/seu-usuario/ivy-ai.git
git push -u origin main
```

✅ **Status:** Código no GitHub

---

## **FASE 2: DEPLOY FRONTEND - NETLIFY (10 MIN)**

### **Passo 2.1: Preparar Next.js**

```bash
# 1. Navegar para frontend
cd web

# 2. Criar netlify.toml (configuração)
cat > netlify.toml << 'EOF'
[build]
  command = "npm run build"
  publish = ".next"

[dev]
  command = "npm run dev"
  port = 3000

[[redirects]]
  from = "/api/*"
  to = "https://api.ivyai.dev/api/:splat"
  status = 200

[env]
  NEXT_PUBLIC_API_URL = "https://api.ivyai.dev"
EOF

# 3. Criar .env.production
cat > .env.production << 'EOF'
NEXT_PUBLIC_API_URL=https://api.ivyai.dev
NEXT_PUBLIC_APP_URL=https://app.ivyai.dev
EOF

# 4. Fazer commit
git add netlify.toml .env.production
git commit -m "Add Netlify configuration"
git push origin main
```

✅ **Status:** Frontend pronto para Netlify

---

### **Passo 2.2: Conectar Netlify**

**🌐 ABRIR NAVEGADOR - FAZER ISTO MANUALMENTE:**

```
1. Ir para: https://app.netlify.com
2. Login com GitHub (ou criar conta)
3. Clicar: "Add new site" → "Import an existing project"
4. Selecionar repositório: ivyai/ivy
5. Configurar:
   Base directory: web
   Build command: npm run build
   Publish directory: .next
6. Em "Environment variables" adicionar:
   NEXT_PUBLIC_API_URL = https://api.ivyai.dev
7. Clicar: "Deploy site"
8. ⏳ Aguardar 2-5 minutos para build
9. ✅ Netlify gera URL automática: https://[random].netlify.app
```

✅ **Status:** Frontend LIVE em Netlify

---

### **Passo 2.3: Configurar Custom Domain (5 MIN)**

**🌐 FAZER ISTO NO NETLIFY DASHBOARD:**

```
1. Site settings → Domain management
2. Clicar: "Add custom domain"
3. Digitar: app.ivyai.dev
4. Netlify mostra: "Check your DNS records"
5. Ir em seu registrador de domínio (GoDaddy, Namecheap, Route53, etc)
6. Adicionar registros DNS que Netlify sugere (CNAME ou A records)
7. Aguardar propagação (5-30 min)
8. Voltar ao Netlify → Verificar domínio

✅ app.ivyai.dev aponta para seu site Netlify
```

**Seu registrador de domínio:** [RESPONDA AQUI]

✅ **Status:** Frontend em app.ivyai.dev

---

## **FASE 3: DEPLOY BACKEND - RAILWAY (15 MIN)**

### **Passo 3.1: Preparar Backend**

```bash
# 1. Navegar para server
cd server

# 2. Criar Procfile (para Railway saber como rodar)
cat > Procfile << 'EOF'
web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
worker: python -m celery -A app.tasks worker
EOF

# 3. Criar railway.json (configuração)
cat > railway.json << 'EOF'
{
  "build": {
    "builder": "dockerfile"
  }
}
EOF

# 4. Criar Dockerfile (se não tiver)
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
    CMD python -c "import requests; requests.get('http://localhost:8000/admin/health')"

# Expose port
EXPOSE 8000

# Run
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# 5. Fazer commit
git add Procfile railway.json Dockerfile
git commit -m "Add Railway and Docker configuration"
git push origin main
```

✅ **Status:** Backend pronto para Railway

---

### **Passo 3.2: Conectar Railway**

**🌐 ABRIR NAVEGADOR - FAZER ISTO MANUALMENTE:**

```
1. Ir para: https://railway.app
2. Sign up com GitHub
3. Criar novo project
4. "Deploy from GitHub"
5. Selecionar: ivy-ai repository
6. Aguardar Railway fazer build
7. Railway auto-detecta requirements.txt e Dockerfile
8. Em "Variables" adicionar:
   DATABASE_URL = (Railway cria automático com PostgreSQL)
   REDIS_URL = (Upstash - próximo passo)
   JWT_SECRET = (gerar: openssl rand -hex 32)
   API_KEY_SALT = (gerar: openssl rand -hex 16)
9. Railway deploy automático
10. ✅ Railway gera URL: https://[seu-app].railway.app
```

✅ **Status:** Backend LIVE em Railway

---

### **Passo 3.3: Configurar Custom Domain Backend (5 MIN)**

**🌐 NO RAILWAY DASHBOARD:**

```
1. Project → Settings → Custom Domain
2. Clicar: "Add custom domain"
3. Digitar: api.ivyai.dev
4. Railway mostra registros DNS
5. Adicionar no seu registrador de domínio
6. Aguardar propagação

✅ api.ivyai.dev aponta para seu backend Railway
```

✅ **Status:** Backend em api.ivyai.dev

---

## **FASE 4: DATABASE - RAILWAY (AUTOMÁTICO - 2 MIN)**

### **Passo 4.1: Criar PostgreSQL no Railway**

```
1. Railway dashboard → Add → Database
2. Selecionar: PostgreSQL
3. Railway cria automático e gera DATABASE_URL
4. Copiar DATABASE_URL
5. Adicionar em variáveis de ambiente do Railway
6. Backend auto-conecta!

✅ Database pronto
```

✅ **Status:** PostgreSQL online

---

## **FASE 5: CACHE - UPSTASH (3 MIN)**

### **Passo 5.1: Criar Redis no Upstash**

```
1. Ir para: https://upstash.com
2. Sign up (grátis)
3. Create Database → Redis
4. Nome: ivy-ai-prod
5. Region: us-east-1
6. Copiar "UPSTASH_REDIS_REST_URL"
7. Copiar "UPSTASH_REDIS_REST_TOKEN"
8. Montar REDIS_URL:
   redis://default:[password]@[host]:[port]
   (Upstash mostra o formato exato)
9. Adicionar em Railway Environment

✅ Redis pronto
```

✅ **Status:** Redis online

---

## **FASE 6: TESTAR TUDO (5 MIN)**

### **Passo 6.1: Verificar Frontend**

```
1. Abrir navegador: https://app.ivyai.dev
2. Deve carregar sua aplicação Next.js
3. Tentar fazer login
4. Se funcionar ✅ sucesso!
```

### **Passo 6.2: Verificar Backend**

```
1. Abrir: https://api.ivyai.dev/admin/health
2. Deve retornar JSON:
   {"status": "healthy", "timestamp": "..."}
3. Abrir: https://api.ivyai.dev/docs
4. Deve mostrar Swagger UI
5. Se tudo funciona ✅ sucesso!
```

### **Passo 6.3: Testar Integração**

```
1. Ir para https://app.ivyai.dev
2. Fazer login
3. Clicar em "Chat"
4. Enviar mensagem
5. Deve vir do backend (api.ivyai.dev)
6. Se funciona ✅ TUDO PRONTO!
```

✅ **Status:** Tudo online e funcionando

---

## **📊 SUMMARY - O QUE FOI FEITO**

```
FRONTEND:
✅ Code no GitHub
✅ Deployed no Netlify
✅ Domain app.ivyai.dev aponta para Netlify
✅ Auto-build e deploy em cada push

BACKEND:
✅ Code no GitHub
✅ Deployed no Railway
✅ Domain api.ivyai.dev aponta para Railway
✅ Auto-build e deploy em cada push

DATABASE:
✅ PostgreSQL no Railway
✅ Automático e provisionado
✅ Backups automáticos

CACHE:
✅ Redis no Upstash
✅ Gratuito (até 30MB)
✅ Production-ready

TOTAL SETUP: 45 min
CUSTO MENSAL: $5-10
MANUTENÇÃO: Praticamente 0
```

---

## **🎯 PRÓXIMO PASSO - LAUNCH DAY**

Quando tudo acima estiver pronto:

```
1. Abra: LAUNCH_DAY_CHECKLIST.md
2. Use: CONTENT_TEMPLATES_READY_TO_USE.md
3. Comece: 8 horas de launch tasks

Resultado: 1,000+ usuarios + buzz
```

---

## **⚠️ TROUBLESHOOTING**

### **Frontend não carrega**
```
1. Verificar: https://[seu-site].netlify.app (versão automática)
2. Se funciona → problema é DNS
3. Aguardar mais 30 min para propagação
4. Se não funciona → verificar build logs no Netlify
```

### **Backend retorna erro**
```
1. Railway Dashboard → Logs
2. Ver mensagem de erro
3. Adicionar variáveis de ambiente faltantes
4. Redeploy automático
```

### **Database não conecta**
```
1. Verificar DATABASE_URL em Railway
2. Confirmar que começa com: postgresql://
3. Testar conexão local:
   psql postgresql://user:pass@host:port/db
```

### **Domain não resolve**
```
1. Aguardar 5-30 min de propagação
2. Verificar registros DNS: nslookup app.ivyai.dev
3. Confirmar que aponta para Netlify
4. Se ainda não, verificar DNS configuração no registrador
```

---

## **✅ FINAL CHECKLIST**

```
☐ GitHub repo criado e código pushed
☐ Frontend deployed em Netlify
☐ Backend deployed em Railway
☐ PostgreSQL criado no Railway
☐ Redis criado no Upstash
☐ app.ivyai.dev aponta para Netlify
☐ api.ivyai.dev aponta para Railway
☐ https://app.ivyai.dev carrega
☐ https://api.ivyai.dev/admin/health retorna JSON
☐ https://api.ivyai.dev/docs mostra Swagger
☐ Login funciona no app
☐ API responde corretamente
☐ Database conecta
☐ Redis conecta

SE TODOS OS ITENS ACIMA ✅:
→ Platform LIVE!
→ Próximo: LAUNCH_DAY_CHECKLIST.md
```

---

## **🚀 RESUMO - SUA PRÓXIMA AÇÃO**

```
1. Você já tem domínio ivyai.dev? (RESPONDA!)
2. Qual é seu registrador (GoDaddy, Namecheap, Route53)?
3. Código já está no GitHub?

Depois disso:
→ Siga FASE 1-6 acima (45 min)
→ Platform fica LIVE!
```

---

*Last updated: Junho 27, 2026*  
**Status: Ready to execute!**

🚀 **VAMOS LÁ!**
