# 🚀 **PRODUCTION DEPLOYMENT - PASSO A PASSO**

**Tempo estimado:** 45 minutos  
**Resultado:** Platform LIVE com links permanentes  
**Status:** ✅ COMEÇANDO AGORA!

---

## **PRÉ-REQUISITOS (5 MIN)**

### Verificar se tem instalado:

```bash
# 1. Docker
docker --version
# Esperado: Docker version 20.10+

# 2. Kubernetes (kubectl)
kubectl version --client
# Esperado: Client version 1.24+

# 3. Terraform
terraform version
# Esperado: Terraform v1.0+

# 4. AWS CLI
aws --version
# Esperado: AWS CLI 2.0+

# 5. Git
git --version
# Esperado: git version 2.30+
```

### Se faltou algo:
```bash
# macOS (Homebrew)
brew install docker kubernetes-cli terraform awscli

# Ubuntu/Linux (apt)
sudo apt-get install docker.io kubectl terraform awscli

# Windows (Chocolatey)
choco install docker kubernetes-cli terraform awscli2
```

---

## **PASSO 1: CONFIGURAR AWS CREDENTIALS (5 MIN)**

### 1.1 Criar conta AWS (se não tiver)
```
Ir para: https://aws.amazon.com
Clicar: Create AWS Account
Seguir: Passos do wizard
```

### 1.2 Criar Access Keys
```bash
# AWS Console → IAM → Users → Your User
# Create Access Key
# Download CSV com: Access Key ID + Secret Access Key

# Guardar em local seguro!
```

### 1.3 Configurar CLI
```bash
aws configure

# Quando pedir:
# AWS Access Key ID: [Cole aqui]
# AWS Secret Access Key: [Cole aqui]
# Default region: us-east-1
# Default output format: json
```

### 1.4 Verificar
```bash
aws s3 ls
# Deve retornar: (vazio ou lista de buckets)
# Se der erro: Credentials incorretos
```

---

## **PASSO 2: PREPARAR CÓDIGO (5 MIN)**

### 2.1 Navegar para projeto
```bash
cd /path/to/ivy-ai
# ou onde você salvou o projeto
```

### 2.2 Verificar código pronto
```bash
# Verificar se todos os arquivos estão lá
ls -la
# Deve mostrar: server/, web/, k8s/, terraform/, etc.

# Verificar Git status
git status
# Deve mostrar: nothing to commit, working tree clean

# Se não estiver clean:
git add .
git commit -m "Final before production"
git push origin main
```

### 2.3 Criar .env production
```bash
cat > .env.prod << 'EOF'
# Production Environment
ENVIRONMENT=production
DEBUG=false
ALLOWED_HOSTS=api.ivyai.dev,app.ivyai.dev

# Database
DATABASE_URL=postgresql://admin:password@rds-endpoint:5432/ivy_ai
REDIS_URL=redis://cache-endpoint:6379

# Security
JWT_SECRET=$(openssl rand -hex 32)
API_KEY_SALT=$(openssl rand -hex 16)

# Email
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USERNAME=apikey
SMTP_PASSWORD=SG.xxxxx

# Analytics
SENTRY_DSN=https://xxxxx@sentry.io/123456
EOF

# Não commitar este arquivo!
echo ".env.prod" >> .gitignore
```

---

## **PASSO 3: BUILD DOCKER IMAGE (10 MIN)**

### 3.1 Criar Dockerfile (se não existir)
```dockerfile
# server/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 ivyai
USER ivyai

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/admin/health')"

# Run
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3.2 Build image
```bash
docker build -t ivy-ai:latest .
# Tempo: 5-10 minutos
# Esperado: Successfully tagged ivy-ai:latest
```

### 3.3 Testar localmente
```bash
docker run -p 8000:8000 ivy-ai:latest
# Ir em browser: http://localhost:8000/admin/health
# Esperado: {"status": "healthy"}
# Ctrl+C para parar
```

---

## **PASSO 4: PUSH PARA ECR (5 MIN)**

### 4.1 Criar ECR repository
```bash
# AWS Console → ECR → Create repository
# Nome: ivy-ai
# Clique: Create

# Ou via CLI:
aws ecr create-repository --repository-name ivy-ai --region us-east-1
```

### 4.2 Login no ECR
```bash
# Obter password
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789.dkr.ecr.us-east-1.amazonaws.com
  
# Substituir 123456789 pelo seu AWS Account ID:
aws sts get-caller-identity --query Account --output text
```

### 4.3 Tag e Push
```bash
# Tag image
docker tag ivy-ai:latest \
  123456789.dkr.ecr.us-east-1.amazonaws.com/ivy-ai:latest

# Push
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/ivy-ai:latest
# Tempo: 2-5 minutos

# Verificar
aws ecr describe-images --repository-name ivy-ai
```

---

## **PASSO 5: TERRAFORM DEPLOYMENT (15 MIN)**

### 5.1 Configurar variáveis
```bash
cd terraform

# Criar terraform.tfvars
cat > terraform.tfvars << 'EOF'
aws_region           = "us-east-1"
cluster_name         = "ivy-ai-prod"
cluster_version      = "1.28"
node_count           = 3
node_type            = "t3.large"
database_size        = "20"
database_type        = "db.t3.medium"
redis_type           = "cache.t3.micro"
environment          = "production"
EOF

# Verificar variáveis
cat terraform.tfvars
```

### 5.2 Terraform Init
```bash
terraform init
# Tempo: 1-2 minutos
# Esperado: Terraform has been successfully initialized
```

### 5.3 Terraform Plan
```bash
terraform plan -out=tfplan
# Tempo: 3-5 minutos
# Esperado: Plan: XX to add, 0 to change, 0 to destroy
# Revisar o plano antes de apply!
```

### 5.4 Terraform Apply
```bash
terraform apply tfplan
# Tempo: 10-15 minutos
# Esperado: Apply complete!

# Obter outputs
terraform output
# Você verá:
# - EKS cluster endpoint
# - RDS endpoint
# - Redis endpoint
# - Load Balancer DNS
```

### 5.5 Configurar kubeconfig
```bash
aws eks update-kubeconfig \
  --region us-east-1 \
  --name ivy-ai-prod
  
# Testar
kubectl get nodes
# Esperado: 3 nodes in Ready state
```

---

## **PASSO 6: KUBERNETES DEPLOYMENT (10 MIN)**

### 6.1 Criar namespace
```bash
kubectl create namespace ivy-ai
# ou
kubectl apply -f k8s/namespace.yaml
```

### 6.2 Criar secrets
```bash
kubectl create secret generic app-secrets \
  --from-literal=database-url="postgresql://..." \
  --from-literal=redis-url="redis://..." \
  --from-literal=jwt-secret="$(openssl rand -hex 32)" \
  -n ivy-ai
```

### 6.3 Deploy aplicação
```bash
# Atualizar imagem no deployment.yaml
# Procurar por: image: e substituir pelo seu ECR URI

# Depois deploy
kubectl apply -f k8s/configmap.yaml -n ivy-ai
kubectl apply -f k8s/secret.yaml -n ivy-ai
kubectl apply -f k8s/deployment.yaml -n ivy-ai
kubectl apply -f k8s/service.yaml -n ivy-ai
kubectl apply -f k8s/ingress.yaml -n ivy-ai
kubectl apply -f k8s/hpa.yaml -n ivy-ai
kubectl apply -f k8s/monitoring.yaml -n ivy-ai

# Verificar
kubectl get pods -n ivy-ai
# Esperado: 3 api pods em Running state
```

### 6.4 Aguardar pods
```bash
# Monitorar deployments
kubectl rollout status deployment/ivy-ai-api -n ivy-ai

# Esperar até: deployment "ivy-ai-api" successfully rolled out
# Tempo: 3-5 minutos
```

---

## **PASSO 7: CONFIGURAR DNS (5 MIN)**

### 7.1 Obter Load Balancer DNS
```bash
kubectl get svc -n ivy-ai ingress-nginx-controller

# Procurar por EXTERNAL-IP
# Exemplo: a1234567890abcdef-123456789.us-east-1.elb.amazonaws.com
```

### 7.2 Registrar domínios
```bash
# Route 53 (AWS) ou seu registrador
# Criar A records:

# api.ivyai.dev → Load Balancer DNS
# app.ivyai.dev → CloudFront (frontend)

# Se usar Route 53:
# AWS Console → Route 53 → Create Record
# Type: A (alias)
# Target: Load Balancer
```

### 7.3 SSL Certificate
```bash
# Cert-manager já configurado no K8s
# Certificates serão auto-geradas para api.ivyai.dev

# Verificar:
kubectl get certificate -n ivy-ai
# Esperado: READY True
```

---

## **PASSO 8: HEALTH CHECKS (2 MIN)**

### 8.1 Testar API
```bash
# Aguarde 2-3 minutos para DNS propagação
curl https://api.ivyai.dev/admin/health

# Esperado:
# {"status": "healthy", "timestamp": "2026-06-27T..."}
```

### 8.2 Testar App
```bash
# Ir para browser
https://app.ivyai.dev

# Esperado: Login page carrega
```

### 8.3 Testar Swagger
```
https://api.ivyai.dev/docs

# Esperado: Swagger UI com todos endpoints
```

### 8.4 Verificar Logs
```bash
kubectl logs -n ivy-ai deployment/ivy-ai-api
# Deve mostrar: Successfully started

kubectl logs -n ivy-ai deployment/ivy-api-worker
# Deve mostrar: Worker ready
```

---

## **PASSO 9: MONITORING & ALERTS (2 MIN)**

### 9.1 Acessar Prometheus
```bash
kubectl port-forward -n ivy-ai svc/prometheus 9090:9090
# Browser: http://localhost:9090

# Procurar por: Status → Targets
# Esperado: Todos targets em "UP"
```

### 9.2 Configurar Alertas
```bash
# Slack webhook para alertas
kubectl set env deployment/prometheus \
  SLACK_WEBHOOK="https://hooks.slack.com/..." \
  -n ivy-ai
```

---

## **🎉 SUCESSO! SEU LINKS AGORA SÃO:**

```
🌐 FRONTEND (App)
   https://app.ivyai.dev

🔌 API ENDPOINTS
   https://api.ivyai.dev
   https://api.ivyai.dev/admin/health
   https://api.ivyai.dev/docs

📊 MONITORING
   http://localhost:9090 (Prometheus - port forward)
   
📚 DOCUMENTAÇÃO
   https://api.ivyai.dev/redoc

✅ TODOS FUNCIONANDO!
```

---

## **PRÓXIMOS PASSOS**

```
1. ✅ Agora você tem links PERMANENTES
2. ✅ Platform está LIVE para mundo
3. ✅ Kubernetes auto-scaling ativo
4. ✅ Monitoring funcionando
5. ✅ Backups rodando

AGORA:
→ Abra LAUNCH_DAY_CHECKLIST.md
→ Continue com sociais, emails, etc.
→ Comece a convidar usuários!
```

---

## **TROUBLESHOOTING**

### Pods não subindo?
```bash
kubectl describe pod <pod-name> -n ivy-ai
# Ver events e erro
```

### DNS não resolvendo?
```bash
# Aguarde 5-10 minutos para propagação
# Ou use: nslookup api.ivyai.dev
```

### Banco de dados erro?
```bash
# Verificar RDS
aws rds describe-db-instances

# Verificar conexão
psql -h <rds-endpoint> -U admin -d ivy_ai
```

### SSL certificate pendente?
```bash
kubectl describe certificate -n ivy-ai
# Ver eventos de issuance
```

---

## **CUSTOS AWS (Estimado/Mês)**

```
EKS Cluster:        $73
3 t3.large nodes:   $180
RDS t3.medium:      $75
ElastiCache t3:     $25
NAT Gateway:        $45
Load Balancer:      $18
Data transfer:      $5-20
────────────────────────
TOTAL:             ~$420-435/mês

Com 10k users:
Revenue $160k/mês
Custos: $420/mês
Margem: 99.7%!
```

---

## ✅ **DEPLOYMENT CHECKLIST**

- [ ] AWS credentials configuradas
- [ ] Docker image built e testado
- [ ] Image pushed para ECR
- [ ] Terraform init/plan/apply completo
- [ ] Kubernetes nodes healthy
- [ ] Pods rodando
- [ ] DNS configurado
- [ ] SSL certificado
- [ ] API respondendo (/admin/health)
- [ ] Frontend carregando
- [ ] Monitoring ativo
- [ ] Links permanentes funcionando

---

**Parabéns! 🎉 Sua plataforma está LIVE!**

**Próximo: LAUNCH_DAY_CHECKLIST.md**

---

*Production deployment complete!*  
*Your platform is now live to the world!*  
*Links are permanent and scalable!*

🚀 **VOCÊ CONSEGUIU!** 🚀
