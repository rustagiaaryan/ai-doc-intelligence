# 🚀 Quick Start Guide - All Services

## ✅ Prerequisites Complete
- ✅ Docker infrastructure running
- ✅ Google OAuth credentials configured
- ✅ All virtual environments created
- ✅ All dependencies installed

---

## 📋 Start Services (Use 6 Separate Terminals)

### Terminal 1 - Auth Service
```bash
cd /Users/aaryanrustagi/ai-doc-intelligence/services/auth-service
source venv/bin/activate
uvicorn app.main:app --port 8000
```

### Terminal 2 - LLM Proxy
```bash
cd /Users/aaryanrustagi/ai-doc-intelligence/services/llm-proxy
source venv/bin/activate
uvicorn app.main:app --port 8002
```

### Terminal 3 - Ingestion Worker
```bash
cd /Users/aaryanrustagi/ai-doc-intelligence/services/ingestion-worker
source venv/bin/activate
uvicorn app.main:app --port 8003
```

### Terminal 4 - RAG Service
```bash
cd /Users/aaryanrustagi/ai-doc-intelligence/services/rag-service
source venv/bin/activate
uvicorn app.main:app --port 8004
```

### Terminal 5 - API Gateway
```bash
cd /Users/aaryanrustagi/ai-doc-intelligence/services/api-gateway
source venv/bin/activate
uvicorn app.main:app --port 8080
```

### Terminal 6 - Frontend
```bash
cd /Users/aaryanrustagi/ai-doc-intelligence/services/web-frontend
npm start
```

---

## ✅ Service Checklist

Once started, you should see:

- [ ] Auth Service (8000) - "Application startup complete"
- [x] Document Service (8001) - Already running in background
- [ ] LLM Proxy (8002) - "Application startup complete"
- [ ] Ingestion Worker (8003) - "Application startup complete"
- [ ] RAG Service (8004) - "Application startup complete"
- [ ] API Gateway (8080) - "Application startup complete"
- [ ] Frontend (3000) - Browser opens automatically

---

## 🌐 Access URLs

- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8080
- **API Docs**: http://localhost:8080/docs

---

## 🎯 First Steps After Login

1. Click "Sign in with Google"
2. You may see "Google hasn't verified this app" - click "Advanced" → "Go to AI Document Intelligence Platform (unsafe)"
3. Select your Google account and click "Allow"
4. You'll be redirected to the Dashboard
5. Upload a document
6. Process it
7. Go to Chat and ask questions!

---

## 💡 Tips

- Keep all terminal windows open
- Watch for any error messages
- Document Service is already running in the background (port 8001)
- Frontend will auto-open in browser once compiled

---

**Ready to start!** Open your terminals and run the commands above. 🚀
