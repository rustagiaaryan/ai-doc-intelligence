# AI Document Intelligence Platform

A production-grade microservices platform for intelligent document processing and AI-powered question-answering using Retrieval-Augmented Generation (RAG).

## Overview

This platform enables users to upload documents (PDF, DOCX, TXT, MD), automatically extract and process text, generate vector embeddings, and ask natural language questions with AI-powered answers backed by source citations. The system uses a microservices architecture deployed on Kubernetes, integrating OpenAI's GPT models for embeddings and question answering.

## Technologies

### Backend
- **Python 3.11** with FastAPI for microservices
- **PostgreSQL 16** with pgvector extension for vector storage
- **Redis 7** for caching embeddings and query results
- **MinIO/AWS S3** for document storage
- **SQLAlchemy** (async) with Alembic for database management

### Frontend
- **React 19** with TypeScript
- **TailwindCSS 4** for styling
- **React Router v7** for navigation
- **Google OAuth 2.0** for authentication

### AI/ML
- **OpenAI GPT-3.5-turbo** for question answering
- **OpenAI text-embedding-3-small** for vector embeddings (1536 dimensions)
- **RAG pipeline** with semantic similarity search using cosine distance

### DevOps
- **Docker** and Docker Compose for containerization
- **Kubernetes** for orchestration
- **Prometheus** for metrics collection
- **Nginx** for frontend serving

## Architecture

The platform consists of 7 microservices:

1. **Auth Service** (port 8000) - Google OAuth authentication and JWT token management
2. **Document Service** (port 8001) - Document upload, storage, and metadata management
3. **LLM Proxy** (port 8002) - OpenAI API integration with response caching
4. **Ingestion Worker** (port 8003) - Text extraction, document chunking, and embedding generation
5. **RAG Service** (port 8004) - Vector similarity search and AI-powered question answering
6. **API Gateway** (port 8080) - Unified API entry point with request routing
7. **Web Frontend** (port 3000/30000) - React-based user interface

### Data Flow

1. User uploads document via frontend
2. Document Service stores file in S3/MinIO and creates database record
3. User triggers processing, Document Service sends request to Ingestion Worker
4. Ingestion Worker extracts text, chunks into segments, generates embeddings via LLM Proxy
5. Embeddings stored in PostgreSQL with pgvector
6. User asks questions via RAG Service
7. RAG Service performs vector similarity search, retrieves relevant chunks
8. LLM Proxy sends question + context to OpenAI GPT for answer generation
9. Answer returned with source chunk citations and similarity scores

## How It Works

### Document Processing

Documents are chunked into smaller segments (approximately 500-1000 characters) to overcome LLM context limitations and improve retrieval precision. Each chunk is converted into a 1536-dimensional vector embedding using OpenAI's embedding model. These vectors are stored in PostgreSQL with the pgvector extension for efficient similarity search.

### Question Answering (RAG)

When a user asks a question:
1. The question is converted to a vector embedding
2. Vector similarity search (cosine distance) retrieves the top K most relevant document chunks
3. The question and retrieved chunks are sent to GPT-3.5-turbo as context
4. GPT generates an answer based on the provided context
5. The answer is returned along with source chunks and similarity scores (0-100%)

### Caching Strategy

Redis caches:
- Document embeddings to avoid regeneration
- Query embeddings for repeated questions
- LLM responses for identical queries
- JWT tokens and session data

## Kubernetes Deployment

### Prerequisites

- **kubectl** (v1.31+)
- **Docker Desktop** with Kubernetes enabled, OR
- **minikube** (v1.30+), OR
- **kind** (v0.20+)

### Build Docker Images

```bash
# Navigate to project root
cd ai-doc-intelligence

# Build all service images
docker build -t ai-doc-auth:latest ./services/auth-service
docker build -t ai-doc-document:latest ./services/document-service
docker build -t ai-doc-llm-proxy:latest ./services/llm-proxy
docker build -t ai-doc-ingestion:latest ./services/ingestion-worker
docker build -t ai-doc-rag:latest ./services/rag-service
docker build -t ai-doc-gateway:latest ./services/api-gateway

# Build frontend with environment variables
docker build \
  --build-arg REACT_APP_API_URL=http://localhost:30080 \
  --build-arg REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id \
  -t ai-doc-frontend:latest \
  ./services/web-frontend
```

### Configure Secrets

Create your secrets file from the template:

```bash
cp k8s/config/secrets.yaml.template k8s/config/secrets.yaml
```

Edit `k8s/config/secrets.yaml` and add your credentials:

```yaml
OPENAI_API_KEY: "your-openai-api-key"
GOOGLE_CLIENT_ID: "your-google-client-id"
GOOGLE_CLIENT_SECRET: "your-google-client-secret"
```

**Note:** The actual `secrets.yaml` file is gitignored for security. Never commit real credentials to version control.

### Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Apply configurations (secrets and configmaps)
kubectl apply -f k8s/config/

# Deploy infrastructure (postgres, redis, minio)
kubectl apply -f k8s/infrastructure/

# Wait for infrastructure to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n ai-doc-intelligence --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n ai-doc-intelligence --timeout=300s
kubectl wait --for=condition=ready pod -l app=minio -n ai-doc-intelligence --timeout=300s

# Deploy application services
kubectl apply -f k8s/services/

# Wait for all services to be ready
kubectl wait --for=condition=ready pod --all -n ai-doc-intelligence --timeout=300s

# Verify deployment
kubectl get pods -n ai-doc-intelligence
```

### Access the Application

The services are exposed via NodePort:

- **Web Frontend**: http://localhost:30000
- **API Gateway**: http://localhost:30080
- **MinIO Console**: http://localhost:30901 (credentials: minioadmin/minioadmin)

### Google OAuth Configuration

Add the following authorized JavaScript origins and redirect URIs to your Google Cloud Console OAuth 2.0 client:

**Authorized JavaScript origins:**
- http://localhost:30000
- http://localhost:3000

**Authorized redirect URIs:**
- http://localhost:30000
- http://localhost:3000

## Major Issues and Solutions

### Issue 1: Google OAuth Client ID Not Found

**Problem**: Frontend showed "Missing required parameter: client_id" error when attempting Google OAuth login.

**Root Cause**: React environment variables must be available at build time, but .dockerignore was excluding .env files from the Docker build context.

**Solution**: Modified the frontend Dockerfile to accept build arguments and set environment variables explicitly:

```dockerfile
ARG REACT_APP_API_URL=http://localhost:8080
ARG REACT_APP_GOOGLE_CLIENT_ID

ENV REACT_APP_API_URL=${REACT_APP_API_URL}
ENV REACT_APP_GOOGLE_CLIENT_ID=${REACT_APP_GOOGLE_CLIENT_ID}
```

Build command with arguments:
```bash
docker build --no-cache \
  --build-arg REACT_APP_GOOGLE_CLIENT_ID="your-client-id" \
  -t ai-doc-frontend:latest .
```

**Learning**: React environment variables (prefixed with REACT_APP_) are baked into the build at compile time, not runtime. When using Docker, these must be provided as build arguments if .env files are excluded from the build context.

### Issue 2: CORS Blocking Frontend Requests

**Problem**: Browser blocked API requests with CORS errors when accessing API Gateway from frontend on port 30000.

**Root Cause**: API Gateway CORS configuration only allowed http://localhost:3000, not http://localhost:30000 (the Kubernetes NodePort).

**Solution**: Updated API Gateway CORS configuration to include both origins:

```python
CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:30000"]
```

**Learning**: When deploying to Kubernetes with NodePort services, ensure all CORS origins include both development and deployment URLs.

### Issue 3: Document Processing Failed - Connection Refused

**Problem**: Document processing failed with "Failed to send to ingestion worker: All connection attempts failed" error.

**Root Cause**: The document-service Kubernetes deployment was missing the INGESTION_WORKER_URL environment variable, so the service didn't know where to send processing requests.

**Solution**: Added the missing environment variable to the deployment manifest:

```yaml
- name: INGESTION_WORKER_URL
  valueFrom:
    configMapKeyRef:
      name: ai-doc-config
      key: INGESTION_WORKER_URL
```

**Learning**: Kubernetes deployments require explicit environment variable mappings. Services don't automatically inherit configuration from ConfigMaps - each variable must be explicitly mapped.

### Issue 4: Embedding Generation Failed - 400 Bad Request

**Problem**: Ingestion worker failed with "Client error '400 Bad Request' for url 'http://llm-proxy:8002/llm/embeddings'".

**Root Cause**: The OPENAI_API_KEY in secrets.yaml was an empty string, causing OpenAI API to reject requests.

**Solution**: Updated secrets.yaml with valid OpenAI API key and restarted dependent services:

```bash
kubectl apply -f k8s/config/secrets.yaml
kubectl rollout restart deployment/llm-proxy -n ai-doc-intelligence
kubectl rollout restart deployment/ingestion-worker -n ai-doc-intelligence
kubectl rollout restart deployment/rag-service -n ai-doc-intelligence
```

**Learning**: Always verify API keys are set correctly before deployment. Empty or invalid API keys may not cause immediate errors but will fail during actual API calls.

## Key Learnings

1. **Microservices Communication**: Learned to design service-to-service communication patterns, including sync HTTP calls (document → ingestion) and the importance of service discovery in Kubernetes via DNS (service-name.namespace.svc.cluster.local).

2. **Kubernetes Configuration Management**: Understanding the separation between ConfigMaps (non-sensitive config) and Secrets (credentials), and how to properly mount them as environment variables in deployments.

3. **Docker Build Context**: Deep understanding of how .dockerignore affects builds, especially for React apps where environment variables must be available at build time. Learned to use multi-stage builds and build arguments effectively.

4. **CORS in Microservices**: Frontend applications deployed separately from backends require careful CORS configuration, especially when using different ports or Kubernetes NodePort services.

5. **Vector Databases**: Practical experience implementing semantic search using PostgreSQL pgvector extension, understanding cosine similarity for document retrieval, and optimizing vector index performance.

6. **RAG Architecture**: Hands-on implementation of a complete RAG pipeline, including document chunking strategies, embedding generation, similarity search thresholds, and context injection for LLM queries.

7. **Kubernetes Debugging**: Learned systematic debugging approaches using kubectl logs, describe pod, and rollout restart. Understanding pod lifecycle, readiness/liveness probes, and troubleshooting ImagePullBackOff and CrashLoopBackOff errors.

8. **Caching Strategies**: Implemented multi-layer caching with Redis to reduce API costs and latency. Learned to cache embeddings (expensive to generate), query results (improve response time), and handle cache invalidation.

## Project Structure

```
ai-doc-intelligence/
├── services/
│   ├── api-gateway/           # FastAPI request router
│   ├── auth-service/          # OAuth + JWT authentication
│   ├── document-service/      # Document management + S3
│   ├── ingestion-worker/      # Text extraction + chunking
│   ├── llm-proxy/            # OpenAI API client + caching
│   ├── rag-service/          # Vector search + Q&A
│   └── web-frontend/         # React TypeScript UI
├── k8s/
│   ├── namespace.yaml        # Kubernetes namespace
│   ├── config/              # Secrets and ConfigMaps
│   ├── infrastructure/      # Postgres, Redis, MinIO
│   └── services/            # Application deployments
├── infra/                   # Database initialization scripts
├── docker-compose.yml       # Local development setup
└── README.md               # This file
```

## Development Setup

For local development without Kubernetes:

```bash
# Start infrastructure
docker-compose up -d postgres redis minio

# Start each service in a separate terminal
cd services/auth-service && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000
cd services/document-service && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8001
cd services/llm-proxy && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8002
cd services/ingestion-worker && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8003
cd services/rag-service && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8004
cd services/api-gateway && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8080

# Start frontend
cd services/web-frontend && npm install && npm start
```

## Environment Variables

Key environment variables required:

```env
# OpenAI API
OPENAI_API_KEY=sk-...

# Google OAuth
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-...

# Database
DATABASE_URL=postgresql+asyncpg://docai:password@postgres:5432/docai

# Redis
REDIS_URL=redis://redis:6379/0

# S3/MinIO
S3_ENDPOINT_URL=http://minio:9000
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin
S3_BUCKET_NAME=documents

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
```

## License

MIT License - free to use for learning and portfolio purposes.
