#!/bin/bash
# IVY AI - PRODUCTION DEPLOYMENT SCRIPT
# Complete deployment to AWS + Kubernetes

set -e

echo "🚀 IVY AI PRODUCTION DEPLOYMENT"
echo "================================"

# Step 1: Build & Push Docker Image
echo "📦 Building Docker image..."
docker build \
  --tag ivy-ai:latest \
  --tag 123456789.dkr.ecr.us-east-1.amazonaws.com/ivy-ai:latest \
  .

echo "📤 Pushing to ECR..."
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/ivy-ai:latest

# Step 2: Terraform Infrastructure
echo "🏗️  Provisioning AWS infrastructure..."
cd terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan
cd ..

# Step 3: Deploy to Kubernetes
echo "☸️  Deploying to Kubernetes..."
kubectl create namespace ivy-ai --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/monitoring.yaml

# Step 4: Setup monitoring
echo "📊 Setting up monitoring..."
kubectl apply -f k8s/monitoring.yaml
kubectl port-forward -n prometheus svc/prometheus 9090:9090 &

# Step 5: Health checks
echo "✅ Running health checks..."
sleep 30
HEALTH_CHECK=$(curl -s http://localhost:8000/admin/health)
if [[ $HEALTH_CHECK == *"healthy"* ]]; then
  echo "✅ API Health: OK"
else
  echo "❌ API Health: FAILED"
  exit 1
fi

# Step 6: Database migrations
echo "🗄️  Running database migrations..."
kubectl exec -it deployment/ivy-ai-api -n ivy-ai -- python -m alembic upgrade head

# Step 7: Verify deployment
echo "🔍 Verifying deployment..."
kubectl get pods -n ivy-ai
kubectl get svc -n ivy-ai

# Step 8: Setup DNS
echo "🌐 Configuring DNS..."
# aws route53 change-resource-record-sets ...
echo "⚠️  Manual step: Configure DNS for api.ivyai.dev and app.ivyai.dev"

# Step 9: Slack notification
echo "📢 Sending deployment notification..."
curl -X POST $SLACK_WEBHOOK \
  -H 'Content-Type: application/json' \
  -d '{"text":"✅ IVY AI deployed to production!","channel":"#deployments"}'

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "====================="
echo "API:     https://api.ivyai.dev"
echo "APP:     https://app.ivyai.dev"
echo "Status:  https://status.ivyai.dev"
echo "Docs:    https://docs.ivyai.dev"
