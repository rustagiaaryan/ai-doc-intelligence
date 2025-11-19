# Testing Guide - AI Document Intelligence Platform

## Currently Running Services ✅

- **Auth Service** - Port 8000
- **Document Service** - Port 8001
- **LLM Proxy** - Port 8002

## Services Not Yet Started

- **Ingestion Worker** - Port 8003
- **RAG Service** - Port 8004

---

## What We Can Test Right Now

### 1. Service Health Checks

```bash
# Check all services
curl http://localhost:8000/health  # Auth
curl http://localhost:8001/health  # Documents
curl http://localhost:8002/health  # LLM Proxy
```

### 2. LLM Proxy (Already Tested ✅)

```bash
# Chat completion
curl -X POST http://localhost:8002/llm/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello!"}],
    "provider": "openai",
    "model": "gpt-3.5-turbo"
  }'

# Embeddings
curl -X POST http://localhost:8002/llm/embeddings \
  -H "Content-Type: application/json" \
  -d '{"texts": ["test"], "model": "text-embedding-3-small"}'
```

### 3. API Documentation

Open in browser:
- http://localhost:8000/docs - Auth Service API
- http://localhost:8001/docs - Document Service API
- http://localhost:8002/docs - LLM Proxy API

---

## Limitation: OAuth Required for Full Testing

To test the **Document Service** and **RAG Service**, we need:

1. **Google OAuth Setup** (not yet configured)
   - Required to get JWT tokens
   - Tokens needed for authenticated endpoints

2. **Alternative**: We can skip OAuth and test the **processing pipeline** directly:
   - Manually call Ingestion Worker
   - Manually call RAG Service
   - Bypass authentication for testing

---

## Option 1: Test Without Authentication (Quick)

We can modify the services temporarily to skip JWT validation for testing.

## Option 2: Set Up Google OAuth (Complete)

Follow these steps:

### A. Create Google OAuth App

1. Go to: https://console.cloud.google.com
2. Create a new project (or select existing)
3. Enable "Google+ API"
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Application type: "Web application"
6. Add authorized redirect URIs:
   - `http://localhost:3000/auth/callback`
7. Copy Client ID and Client Secret

### B. Update Auth Service

Edit `/services/auth-service/.env`:
```
GOOGLE_CLIENT_ID=your-actual-client-id
GOOGLE_CLIENT_SECRET=your-actual-client-secret
```

Restart auth service.

### C. Get a Token

You'll need to implement a simple OAuth flow or use the frontend (when built).

---

## Recommended Next Steps

Given the OAuth requirement, here are your options:

### Option A: Continue Building (Recommended)
1. Build the **API Gateway**
2. Build the **React Frontend** with Google OAuth login
3. Then test the full pipeline end-to-end

### Option B: Test Processing Pipeline Directly
1. Start Ingestion Worker and RAG Service
2. Create a test document in the database manually
3. Call processing endpoints directly (bypass auth)
4. Test vector search and Q&A

### Option C: Set Up OAuth Now
1. Follow steps above to get Google OAuth credentials
2. Implement a test login flow
3. Get JWT token
4. Test authenticated endpoints

---

## What Works Right Now (No Auth Needed)

✅ **LLM Proxy Service**
- Chat completions
- Embedding generation
- Both tested and working with OpenAI

✅ **Service Health Checks**
- All services respond to `/health`

✅ **API Documentation**
- Swagger UI available for all services

---

## What Needs OAuth/Auth

🔒 **Document Service**
- Upload documents
- List documents
- Download documents

🔒 **RAG Service**
- Ask questions
- Get answers

---

**Recommendation**: Let's continue building the **API Gateway** and **Frontend**, then we can test everything together with proper OAuth flow.

**Alternative**: I can temporarily disable auth for testing if you want to test the processing pipeline right now.

Which approach would you like to take?
