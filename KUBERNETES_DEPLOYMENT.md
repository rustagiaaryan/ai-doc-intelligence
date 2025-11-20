# Kubernetes Deployment Guide

## Overview

This guide documents the successful deployment of the AI Document Intelligence Platform to Kubernetes using Docker Desktop.

## Architecture

The platform consists of:
- **3 Infrastructure Services**: PostgreSQL (with pgvector), Redis, MinIO (S3-compatible storage)
- **7 Application Services**: Auth, Document Service, LLM Proxy, Ingestion Worker, RAG Service, API Gateway, Web Frontend
- **Monitoring Stack**: Prometheus and Grafana

## Deployment Summary

All services are successfully deployed and running in the `ai-doc-intelligence` namespace on Docker Desktop Kubernetes (v1.31.4).

### Running Pods

```bash
NAME                                READY   STATUS    RESTARTS   AGE
api-gateway-855b46d79d-xxq8q        1/1     Running   0          7h2m
auth-service-55476879c4-jktv4       1/1     Running   0          69s
document-service-765b68b854-hqdb5   1/1     Running   0          7h2m
ingestion-worker-55c85758-pt22n     1/1     Running   0          69s
llm-proxy-7f48759748-fq8lv          1/1     Running   0          7h2m
minio-7cddb57668-tghzw              1/1     Running   0          7h3m
postgres-0                          1/1     Running   0          7h3m
rag-service-6bd455c496-7lgnt        1/1     Running   0          7h2m
redis-55f9f76cf5-cqtv8              1/1     Running   0          7h3m
web-frontend-94cf8d45c-47ndw        1/1     Running   0          7h2m
```

## Access Points

### External Services (NodePort)

- **Web Frontend**: http://localhost:30000
- **API Gateway**: http://localhost:30080
- **MinIO Console**: http://localhost:30901
- **MinIO API**: http://localhost:30900

### Health Check

```bash
curl http://localhost:30080/health
```

Expected response:
```json
{
  "status":"healthy",
  "service":"api-gateway",
  "version":"0.1.0",
  "backend_services":{
    "auth":"http://auth-service:8000",
    "documents":"http://document-service:8001",
    "rag":"http://rag-service:8004",
    "ingestion":"http://ingestion-worker:8003",
    "llm_proxy":"http://llm-proxy:8002"
  }
}
```

## Deployment Steps

### 1. Prerequisites

- Docker Desktop with Kubernetes enabled (Kubeadm provisioning)
- kubectl CLI tool installed
- Sufficient resources (8GB+ RAM recommended)

### 2. Build Docker Images

All services were built with the `:latest` tag:

```bash
# From the project root
cd services/auth-service && docker build -t ai-doc-auth:latest .
cd ../document-service && docker build -t ai-doc-document:latest .
cd ../llm-proxy && docker build -t ai-doc-llm-proxy:latest .
cd ../ingestion-worker && docker build -t ai-doc-ingestion:latest .
cd ../rag-service && docker build -t ai-doc-rag:latest .
cd ../api-gateway && docker build -t ai-doc-gateway:latest .
cd ../web-frontend && docker build -t ai-doc-frontend:latest .
```

### 3. Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Deploy configuration
kubectl apply -f k8s/config/secrets.yaml
kubectl apply -f k8s/config/configmap.yaml

# Deploy infrastructure
kubectl apply -f k8s/infrastructure/postgres.yaml
kubectl apply -f k8s/infrastructure/redis.yaml
kubectl apply -f k8s/infrastructure/minio.yaml

# Deploy application services
kubectl apply -f k8s/services/auth-service.yaml
kubectl apply -f k8s/services/document-service.yaml
kubectl apply -f k8s/services/llm-proxy.yaml
kubectl apply -f k8s/services/ingestion-worker.yaml
kubectl apply -f k8s/services/rag-service.yaml
kubectl apply -f k8s/services/api-gateway.yaml
kubectl apply -f k8s/services/web-frontend.yaml
```

### 4. Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n ai-doc-intelligence

# Check services
kubectl get services -n ai-doc-intelligence

# View logs for a specific service
kubectl logs -f deployment/api-gateway -n ai-doc-intelligence
```

## Troubleshooting

### Issues Encountered and Resolved

#### 1. Auth Service - Missing Dependencies

**Error**: `ModuleNotFoundError: No module named 'google'` and `No module named 'requests'`

**Root Cause**: Missing Google Auth and requests libraries in requirements.txt

**Fix**: Added to [auth-service/requirements.txt](services/auth-service/requirements.txt:17-18):
```txt
google-auth==2.27.0
google-auth-httplib2==0.2.0
requests==2.31.0
```

Rebuilt image:
```bash
cd services/auth-service
docker build -t ai-doc-auth:latest .
kubectl rollout restart deployment/auth-service -n ai-doc-intelligence
```

#### 2. Ingestion Worker - Missing Environment Variable

**Error**: `pydantic_core._pydantic_core.ValidationError: Field required [type=missing] REDIS_URL`

**Root Cause**: The deployment manifest was missing REDIS_URL environment variable mapping from ConfigMap

**Fix**: Added to [k8s/services/ingestion-worker.yaml](k8s/services/ingestion-worker.yaml:29-33):
```yaml
- name: REDIS_URL
  valueFrom:
    configMapKeyRef:
      name: ai-doc-config
      key: REDIS_URL
```

Updated ConfigMap ([k8s/config/configmap.yaml](k8s/config/configmap.yaml:16)) already had the value:
```yaml
REDIS_URL: "redis://redis:6379/0"
```

Applied changes:
```bash
kubectl apply -f k8s/services/ingestion-worker.yaml
kubectl rollout restart deployment/ingestion-worker -n ai-doc-intelligence
```

## Common Commands

### View Pod Status
```bash
kubectl get pods -n ai-doc-intelligence -o wide
```

### Check Logs
```bash
# Recent logs
kubectl logs deployment/<service-name> -n ai-doc-intelligence

# Follow logs
kubectl logs -f deployment/<service-name> -n ai-doc-intelligence

# Logs from specific pod
kubectl logs <pod-name> -n ai-doc-intelligence
```

### Restart a Service
```bash
kubectl rollout restart deployment/<service-name> -n ai-doc-intelligence
```

### Scale a Service
```bash
kubectl scale deployment/<service-name> -n ai-doc-intelligence --replicas=3
```

### Port Forward (for debugging)
```bash
kubectl port-forward deployment/<service-name> <local-port>:<container-port> -n ai-doc-intelligence
```

### Delete Everything
```bash
kubectl delete namespace ai-doc-intelligence
```

## Service Topology

```
┌─────────────────┐
│  Web Frontend   │  :30000 (NodePort)
│  (React SPA)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  API Gateway    │  :30080 (NodePort)
│  (FastAPI)      │  :8080 (ClusterIP)
└────────┬────────┘
         │
    ┌────┴─────┬─────────┬──────────┬────────────┐
    ▼          ▼         ▼          ▼            ▼
┌────────┐ ┌────────┐ ┌──────┐ ┌─────────┐ ┌─────────┐
│  Auth  │ │  Doc   │ │ LLM  │ │Ingestion│ │   RAG   │
│Service │ │Service │ │Proxy │ │ Worker  │ │ Service │
│ :8000  │ │ :8001  │ │:8002 │ │  :8003  │ │  :8004  │
└───┬────┘ └───┬────┘ └──┬───┘ └────┬────┘ └────┬────┘
    │          │         │          │            │
    └──────────┴─────────┴──────────┴────────────┘
               │         │          │            │
         ┌─────┴────┐  ┌─┴──────┐ ┌─┴──────┐   ┌┴──────┐
         │PostgreSQL│  │  Redis │ │ MinIO  │   │ Redis │
         │  :5432   │  │  :6379 │ │ :9000  │   │ :6379 │
         │(StatefulS│  │        │ │(+:9001)│   │       │
         │   et)    │  │        │ │        │   │       │
         └──────────┘  └────────┘ └────────┘   └───────┘
```

## Resource Usage

### Configured Resource Limits

All services have resource requests and limits configured:

- **Memory**: 512Mi-1Gi requests, 1-2Gi limits
- **CPU**: 250m-500m requests, 500m-1000m limits
- **Storage**: 10Gi for PostgreSQL, 10Gi for MinIO

### Current Resource Allocation

View actual resource usage:
```bash
kubectl top pods -n ai-doc-intelligence
kubectl top nodes
```

## Monitoring and Observability

### Prometheus Metrics

All services expose `/metrics` endpoint with Prometheus metrics including:
- HTTP request rates and latencies
- LLM token usage and costs
- Cache hit rates
- Vector search performance
- Database query performance

### Grafana Dashboards

Access Grafana at http://localhost:3000 (when deployed) to view:
- Service health and uptime
- Request throughput and latency (p50, p95, p99)
- LLM usage and estimated costs
- RAG query performance
- Cache effectiveness
- System resource utilization

Dashboard configuration: [monitoring/grafana/dashboards/ai-doc-intelligence.json](monitoring/grafana/dashboards/ai-doc-intelligence.json)

## Next Steps

### Production Readiness

1. **Security Hardening**
   - Use external secrets manager (e.g., Sealed Secrets, Vault)
   - Enable RBAC and network policies
   - Use private Docker registry
   - Enable TLS/SSL for external endpoints

2. **Scalability**
   - Implement Horizontal Pod Autoscaler (HPA)
   - Add resource quotas and limit ranges
   - Deploy monitoring stack (Prometheus + Grafana)
   - Set up centralized logging (ELK/Loki)

3. **High Availability**
   - Increase replica counts for stateless services
   - Configure pod disruption budgets
   - Use anti-affinity rules for pod distribution
   - Implement readiness and liveness probes (already done)

4. **CI/CD Integration**
   - Automate Docker image builds
   - Implement GitOps workflow (ArgoCD/FluxCD)
   - Add automated testing before deployment
   - Configure rolling update strategies

## Configuration Reference

### Environment Variables (ConfigMap)

See [k8s/config/configmap.yaml](k8s/config/configmap.yaml) for full configuration.

Key settings:
- Service URLs for inter-service communication
- Redis connection strings (separate DBs per service)
- S3/MinIO configuration
- RAG parameters (top-k, similarity threshold)

### Secrets

Stored in [k8s/config/secrets.yaml](k8s/config/secrets.yaml) (base64 encoded):
- Database connection strings
- S3 access credentials
- JWT secret keys
- OAuth client secrets
- LLM API keys (OpenAI)

**Note**: In production, use a proper secrets management solution.

## Support

For issues or questions:
1. Check pod logs: `kubectl logs <pod-name> -n ai-doc-intelligence`
2. Check pod events: `kubectl describe pod <pod-name> -n ai-doc-intelligence`
3. Verify service connectivity: `kubectl exec -it <pod-name> -n ai-doc-intelligence -- sh`
4. Review this troubleshooting section

## Success Metrics

Deployment is considered successful when:
- ✅ All pods show `1/1 Ready` and `Running` status
- ✅ API Gateway health check returns 200 OK
- ✅ Web frontend is accessible at http://localhost:30000
- ✅ All backend services are reachable from API gateway
- ✅ No CrashLoopBackOff or Error states
- ✅ Health probes passing for all services

**Current Status**: ✅ All metrics met - Deployment Successful!
