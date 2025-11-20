# Kubernetes Deployment Guide

This directory contains Kubernetes manifests for deploying the AI Document Intelligence Platform.

## Prerequisites

- **Kubernetes Cluster**: minikube, kind, or any local Kubernetes cluster
- **kubectl**: Configured to connect to your cluster
- **Docker**: For building images locally

## Quick Start

### 1. Start Local Kubernetes Cluster

```bash
# Option 1: Using minikube
minikube start --cpus=4 --memory=8192

# Option 2: Using kind
kind create cluster --name ai-doc-intelligence
```

### 2. Build Docker Images

From the project root, build all service images:

```bash
# Build all images
docker build -t ai-doc-auth:latest ./services/auth-service
docker build -t ai-doc-document:latest ./services/document-service
docker build -t ai-doc-llm-proxy:latest ./services/llm-proxy
docker build -t ai-doc-ingestion:latest ./services/ingestion-worker
docker build -t ai-doc-rag:latest ./services/rag-service
docker build -t ai-doc-gateway:latest ./services/api-gateway
docker build -t ai-doc-frontend:latest ./services/web-frontend
```

### 3. Load Images into Cluster (if using minikube or kind)

```bash
# For minikube
minikube image load ai-doc-auth:latest
minikube image load ai-doc-document:latest
minikube image load ai-doc-llm-proxy:latest
minikube image load ai-doc-ingestion:latest
minikube image load ai-doc-rag:latest
minikube image load ai-doc-gateway:latest
minikube image load ai-doc-frontend:latest

# For kind
kind load docker-image ai-doc-auth:latest --name ai-doc-intelligence
kind load docker-image ai-doc-document:latest --name ai-doc-intelligence
kind load docker-image ai-doc-llm-proxy:latest --name ai-doc-intelligence
kind load docker-image ai-doc-ingestion:latest --name ai-doc-intelligence
kind load docker-image ai-doc-rag:latest --name ai-doc-intelligence
kind load docker-image ai-doc-gateway:latest --name ai-doc-intelligence
kind load docker-image ai-doc-frontend:latest --name ai-doc-intelligence
```

### 4. Update Secrets

Edit `k8s/config/secrets.yaml` to add your API keys:

```bash
kubectl edit secret ai-doc-secrets -n ai-doc-intelligence
```

Add your actual values for:
- `OPENAI_API_KEY`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`

### 5. Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f namespace.yaml

# Deploy configuration
kubectl apply -f config/

# Deploy infrastructure services
kubectl apply -f infrastructure/

# Wait for infrastructure to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n ai-doc-intelligence --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n ai-doc-intelligence --timeout=300s
kubectl wait --for=condition=ready pod -l app=minio -n ai-doc-intelligence --timeout=300s

# Deploy application services
kubectl apply -f services/

# Wait for all services to be ready
kubectl wait --for=condition=ready pod --all -n ai-doc-intelligence --timeout=300s
```

### 6. Access the Application

```bash
# Get service URLs
kubectl get svc -n ai-doc-intelligence

# For minikube, get URLs:
minikube service api-gateway -n ai-doc-intelligence --url
minikube service web-frontend -n ai-doc-intelligence --url
minikube service minio-external -n ai-doc-intelligence --url

# For kind or other clusters, use port-forwarding:
kubectl port-forward svc/api-gateway 8080:8080 -n ai-doc-intelligence
kubectl port-forward svc/web-frontend 3000:80 -n ai-doc-intelligence
kubectl port-forward svc/minio 9000:9000 9001:9001 -n ai-doc-intelligence
```

Access the application:
- **Frontend**: http://localhost:3000 (or NodePort 30000)
- **API Gateway**: http://localhost:8080 (or NodePort 30080)
- **MinIO Console**: http://localhost:9001 (or NodePort 30901)

## Directory Structure

```
k8s/
├── README.md                    # This file
├── namespace.yaml               # Namespace definition
├── config/
│   ├── secrets.yaml            # Secrets (DB passwords, API keys)
│   └── configmap.yaml          # Configuration (service URLs, settings)
├── infrastructure/
│   ├── postgres.yaml           # PostgreSQL with pgvector
│   ├── redis.yaml              # Redis for caching
│   └── minio.yaml              # MinIO for object storage
└── services/
    ├── auth-service.yaml       # Authentication service
    ├── document-service.yaml   # Document management
    ├── llm-proxy.yaml          # LLM integration
    ├── ingestion-worker.yaml   # Document processing
    ├── rag-service.yaml        # RAG query service
    ├── api-gateway.yaml        # API Gateway
    └── web-frontend.yaml       # React frontend
```

## Service Ports

| Service | Internal Port | NodePort | Purpose |
|---------|--------------|----------|---------|
| postgres | 5432 | - | PostgreSQL database |
| redis | 6379 | - | Redis cache |
| minio | 9000, 9001 | 30900, 30901 | Object storage |
| auth-service | 8000 | - | Authentication |
| document-service | 8001 | - | Document management |
| llm-proxy | 8002 | - | LLM integration |
| ingestion-worker | 8003 | - | Document processing |
| rag-service | 8004 | - | RAG queries |
| api-gateway | 8080 | 30080 | API Gateway |
| web-frontend | 80 | 30000 | Frontend UI |

## Monitoring and Debugging

```bash
# Check pod status
kubectl get pods -n ai-doc-intelligence

# View logs for a service
kubectl logs -f deployment/auth-service -n ai-doc-intelligence
kubectl logs -f deployment/rag-service -n ai-doc-intelligence

# Describe a pod for details
kubectl describe pod <pod-name> -n ai-doc-intelligence

# Execute commands in a pod
kubectl exec -it deployment/postgres -n ai-doc-intelligence -- psql -U docai

# Check events
kubectl get events -n ai-doc-intelligence --sort-by='.lastTimestamp'
```

## Database Initialization

The database tables will be created automatically by the services on first run. To manually initialize:

```bash
# Connect to PostgreSQL
kubectl exec -it deployment/postgres -n ai-doc-intelligence -- psql -U docai

# Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

# Check tables
\dt
```

## Scaling

To scale services horizontally:

```bash
# Scale RAG service to 3 replicas
kubectl scale deployment rag-service --replicas=3 -n ai-doc-intelligence

# Scale ingestion worker to 2 replicas
kubectl scale deployment ingestion-worker --replicas=2 -n ai-doc-intelligence
```

## Cleanup

```bash
# Delete all resources
kubectl delete namespace ai-doc-intelligence

# Stop minikube
minikube stop

# Or delete kind cluster
kind delete cluster --name ai-doc-intelligence
```

## Resource Requirements

Minimum cluster resources:
- **CPU**: 4 cores
- **Memory**: 8GB RAM
- **Storage**: 20GB

Current resource allocation:
- **Total CPU requests**: ~2.5 cores
- **Total Memory requests**: ~3GB
- **Total CPU limits**: ~5 cores
- **Total Memory limits**: ~6GB

## Troubleshooting

### Pods not starting
```bash
kubectl describe pod <pod-name> -n ai-doc-intelligence
kubectl logs <pod-name> -n ai-doc-intelligence
```

### ImagePullBackOff error
Make sure images are loaded into the cluster:
```bash
minikube image ls | grep ai-doc
# or
docker exec -it kind-control-plane crictl images | grep ai-doc
```

### Services can't connect to each other
Check that all services are running:
```bash
kubectl get svc -n ai-doc-intelligence
```

DNS should resolve service names like `postgres`, `redis`, etc. within the namespace.

### Database connection errors
Ensure PostgreSQL is ready:
```bash
kubectl wait --for=condition=ready pod -l app=postgres -n ai-doc-intelligence
kubectl exec -it deployment/postgres -n ai-doc-intelligence -- pg_isready -U docai
```

## Next Steps

1. **Setup Prometheus + Grafana** for monitoring (see Day 2 tasks)
2. **Configure AWS S3** instead of MinIO for production
3. **Add Ingress** for external access (Nginx or Traefik)
4. **Implement HPA** (Horizontal Pod Autoscaler) for auto-scaling
5. **Add Network Policies** for security
