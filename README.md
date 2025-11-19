# AI Document Intelligence Platform

A production-grade, multi-service platform for document ingestion, processing, and RAG-based question answering.

## Architecture

### Microservices
- **API Gateway**: Entry point for all client requests
- **Auth Service**: Google OAuth + JWT authentication
- **Document Service**: Document upload, storage (S3/MinIO), metadata management
- **Ingestion Worker**: Text extraction, chunking, embedding generation
- **RAG Service**: Vector search + LLM-based question answering
- **LLM Proxy Service**: Centralized LLM API calls (OpenAI/Anthropic)
- **Web Frontend**: React + TypeScript + TailwindCSS

### Data Layer
- PostgreSQL + pgvector (vector storage)
- Redis (cache + message queue)
- MinIO (local S3-compatible storage) / AWS S3 (production)

### Infrastructure
- Docker + Docker Compose (local dev)
- Kubernetes (kind/minikube local, AWS EKS production)
- Terraform (AWS infrastructure as code)
- Helm (K8s package management)
- GitHub Actions (CI/CD)

### Observability
- Prometheus + Grafana (metrics)
- Loki (logs, optional)

## Quick Start (Local Development)

```bash
# Start local infrastructure (Postgres, Redis, MinIO)
docker-compose up -d

# Each service will have its own setup instructions
```

## Project Structure

```
.
├── services/
│   ├── api-gateway/
│   ├── auth-service/
│   ├── document-service/
│   ├── ingestion-worker/
│   ├── rag-service/
│   ├── llm-proxy/
│   └── web-frontend/
├── infra/
│   ├── terraform/
│   ├── k8s/
│   └── helm/
├── docker-compose.yml
└── README.md
```

## Development Workflow

This project follows strict incremental development:
1. Local development with Docker Compose
2. Kubernetes deployment (local)
3. Cloud deployment (AWS EKS)
4. CI/CD automation

## License

MIT
