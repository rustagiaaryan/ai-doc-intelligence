# AI Document Intelligence Platform

A microservices-based document processing platform that uses RAG (Retrieval-Augmented Generation) to answer questions about uploaded documents. Built as part of my learning journey into modern backend architecture, AI integration, and cloud-native deployment.

## What This Project Does

Users can upload PDF, DOCX, TXT, or Markdown files, and the system automatically extracts text, breaks it into chunks, generates vector embeddings, and stores them in a PostgreSQL database. When users ask questions, the system searches for relevant text chunks using vector similarity, then uses GPT-3.5 to generate answers based on those chunks. The frontend highlights the exact locations in the PDF where the information came from.

## Technologies I Used

### Backend (Python 3.11)
- **FastAPI** - Async web framework for all microservices
- **PostgreSQL 16** - Database with pgvector extension for storing vector embeddings
- **Redis 7** - Caching layer for embeddings and API responses
- **MinIO** - S3-compatible object storage for documents (can also use AWS S3)
- **SQLAlchemy** - Async ORM for database operations
- **aioboto3** - Async S3 client for file operations

### Frontend (React 19 + TypeScript)
- **React 19** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS 4** - Styling
- **React Router v7** - Navigation
- **react-pdf** - PDF rendering and highlighting
- **Google OAuth 2.0** - User authentication

### AI/ML Integration
- **OpenAI GPT-3.5-turbo** - Question answering
- **OpenAI text-embedding-3-small** - Converting text to 1536-dimensional vectors
- **pgvector** - PostgreSQL extension for vector similarity search (cosine distance)

### Infrastructure & DevOps
- **Docker** - Containerization with multi-stage builds
- **Kubernetes** - Orchestration (tested on Docker Desktop)
- **GitHub Actions** - CI/CD pipeline with automated testing
- **pytest** - Unit testing framework
- **Terraform** - Infrastructure as Code for AWS resources (VPC, RDS, S3, ElastiCache)
- **Prometheus** - Metrics collection (basic setup)
- **Grafana** - Monitoring dashboards

## Architecture

The system is split into 7 independent microservices:

1. **Auth Service** (8000) - Handles Google OAuth login and JWT token management
2. **Document Service** (8001) - Manages document uploads and downloads to/from S3
3. **LLM Proxy** (8002) - Centralizes all OpenAI API calls and implements caching
4. **Ingestion Worker** (8003) - Extracts text from documents, chunks it, and generates embeddings
5. **RAG Service** (8004) - Performs vector searches and generates answers using GPT
6. **API Gateway** (8080) - Routes requests to appropriate backend services
7. **Web Frontend** (30000) - React app for users to interact with the system

## How It Works

### Document Processing Flow

1. User uploads a document through the React frontend
2. Document Service stores the file in MinIO/S3 and creates a database record
3. Document Service triggers the Ingestion Worker
4. Ingestion Worker:
   - Extracts text (using PyMuPDF for PDFs, python-docx for Word files)
   - Splits text into chunks (~500-1000 characters with 100 character overlap)
   - Sends chunks to LLM Proxy to generate embeddings
   - Stores chunks and embeddings in PostgreSQL
5. Document status updates to "completed"

### Question Answering Flow (RAG)

1. User types a question in the chat interface
2. RAG Service converts the question to a vector embedding
3. Performs cosine similarity search in PostgreSQL to find top 5 most relevant chunks
4. Constructs a prompt with the question and retrieved chunks
5. Sends to GPT-3.5-turbo via LLM Proxy
6. Returns the answer along with source chunks and similarity scores
7. Frontend displays the answer and allows viewing highlighted sections in the PDF

### Caching Strategy

Redis is used throughout to minimize costs and latency:
- Document embeddings (so we don't re-embed the same text)
- Question embeddings (for frequently asked questions)
- LLM responses (exact same questions get cached responses)
- Session tokens

## Features I Implemented

- User authentication with Google OAuth
- Document upload (PDF, DOCX, TXT, MD)
- Automatic text extraction and processing
- Vector-based semantic search
- GPT-powered question answering
- PDF highlighting showing exact source locations
- Chat history with persistent conversations
- Real-time status updates during processing
- Responsive UI with dark/light modes

## Setup Instructions

### Prerequisites

- Docker Desktop with Kubernetes enabled
- Python 3.11+
- Node.js 20+
- Google Cloud account (for OAuth credentials)
- OpenAI API key

### Environment Variables

Create `k8s/config/secrets.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: ai-doc-secrets
  namespace: ai-doc-intelligence
type: Opaque
stringData:
  DATABASE_URL: "postgresql://docai:your-password@postgres:5432/docai"
  S3_ACCESS_KEY_ID: "minioadmin"
  S3_SECRET_ACCESS_KEY: "minioadmin"
  OPENAI_API_KEY: "your-openai-api-key"
  GOOGLE_CLIENT_ID: "your-google-client-id"
  GOOGLE_CLIENT_SECRET: "your-google-client-secret"
  JWT_SECRET_KEY: "your-jwt-secret"
```

### Build and Deploy

```bash
# Create namespace
kubectl create namespace ai-doc-intelligence

# Build all Docker images
docker build -t ai-doc-auth:latest ./services/auth-service
docker build -t ai-doc-document:latest ./services/document-service
docker build -t ai-doc-llm-proxy:latest ./services/llm-proxy
docker build -t ai-doc-ingestion:latest ./services/ingestion-worker
docker build -t ai-doc-rag:latest ./services/rag-service
docker build -t ai-doc-gateway:latest ./services/api-gateway
docker build -t ai-doc-frontend:latest ./services/web-frontend

# Deploy to Kubernetes
kubectl apply -f k8s/config/
kubectl apply -f k8s/infrastructure/
kubectl apply -f k8s/services/

# Wait for pods to be ready
kubectl get pods -n ai-doc-intelligence -w
```

### Run Database Migrations

```bash
# Apply chat history migration
cat services/rag-service/migrations/002_add_chat_history.sql | \
  kubectl exec -i -n ai-doc-intelligence postgres-0 -- psql -U docai -d docai
```

### Access the Application

- Frontend: http://localhost:30000
- API Gateway: http://localhost:30080
- API Docs: http://localhost:30080/docs
- MinIO Console: http://localhost:30901

## Testing

### Run Unit Tests

```bash
# All services
./run-tests.sh

# Specific service
./run-tests.sh auth-service
```

### CI/CD Pipeline

GitHub Actions automatically runs on every push:
- Code linting (flake8, black, isort)
- Unit tests for all services
- Docker image builds
- Code coverage reporting

See `.github/workflows/ci.yml` for the full pipeline.

## AWS Deployment (Optional)

Terraform configuration is included for deploying to AWS:

```bash
cd infra/terraform

# Initialize Terraform
terraform init

# Review planned changes
terraform plan

# Deploy infrastructure
terraform apply
```

This creates:
- VPC with public/private subnets
- RDS PostgreSQL instance
- S3 bucket for documents
- ElastiCache Redis cluster

Update `k8s/config/configmap.yaml` to use AWS endpoints instead of local MinIO/Postgres.

## What I Learned

### Technical Skills
- Designing and implementing microservices architecture
- Working with async Python (asyncio, async/await patterns)
- Integrating OpenAI's API for embeddings and chat completions
- Using vector databases for semantic search
- Implementing JWT-based authentication
- Kubernetes deployment and service orchestration
- Docker multi-stage builds for optimized images
- Setting up CI/CD pipelines with GitHub Actions
- Writing comprehensive unit tests

### Challenges Faced
- Handling CORS in microservices architecture
- Managing database connections efficiently with async SQLAlchemy
- Optimizing text chunking for better retrieval results
- Implementing proper error handling across services
- Coordinating presigned URLs between internal and external services
- Understanding Kubernetes networking (ClusterIP vs NodePort)

### Architecture Decisions
- Split into microservices for scalability and maintainability
- Used async throughout for better performance
- Implemented caching at multiple layers
- Chose PostgreSQL + pgvector over dedicated vector DB for simplicity
- Used MinIO locally but designed for easy AWS S3 migration

## Project Structure

```
ai-doc-intelligence/
├── services/
│   ├── auth-service/          # Google OAuth + JWT
│   ├── document-service/      # File upload/download
│   ├── llm-proxy/             # OpenAI API integration
│   ├── ingestion-worker/      # Text extraction + embeddings
│   ├── rag-service/           # Vector search + Q&A
│   ├── api-gateway/           # Request routing
│   └── web-frontend/          # React UI
├── k8s/
│   ├── config/                # ConfigMaps and Secrets
│   ├── infrastructure/        # Postgres, Redis, MinIO
│   └── services/              # Application deployments
├── infra/terraform/           # AWS infrastructure
├── monitoring/                # Prometheus + Grafana
└── .github/workflows/         # CI/CD pipeline
```

## API Endpoints

### Authentication
- `POST /api/auth/google` - Login with Google
- `GET /api/auth/verify` - Verify JWT token

### Documents
- `POST /api/documents/upload` - Upload document
- `GET /api/documents/` - List user's documents
- `GET /api/documents/{id}/download` - Get download URL
- `DELETE /api/documents/{id}` - Delete document
- `POST /api/documents/{id}/process` - Process document

### RAG
- `POST /api/rag/ask` - Ask question about documents
- `POST /api/rag/search` - Search document chunks

### Conversations
- `GET /api/conversations/` - List conversations
- `POST /api/conversations/` - Create conversation
- `GET /api/conversations/{id}` - Get conversation with messages

## Future Improvements

- Add support for more document types (Excel, PowerPoint)
- Implement streaming responses for real-time answers
- Add document comparison features
- Deploy to production cloud environment
- Implement rate limiting and better error handling
- Add support for multiple languages
- Fine-tune embedding models for domain-specific documents

## License

This is a personal learning project. Feel free to use any part of the code for your own learning.
