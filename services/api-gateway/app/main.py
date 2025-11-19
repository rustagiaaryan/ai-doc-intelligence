# FILE: services/api-gateway/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import auth_router, document_router, rag_router, ingestion_router

app = FastAPI(
    title="API Gateway",
    description="Unified API Gateway for AI Document Intelligence Platform",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(document_router)
app.include_router(rag_router)
app.include_router(ingestion_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": "0.1.0",
        "backend_services": {
            "auth": settings.AUTH_SERVICE_URL,
            "documents": settings.DOCUMENT_SERVICE_URL,
            "rag": settings.RAG_SERVICE_URL,
            "ingestion": settings.INGESTION_WORKER_URL,
            "llm_proxy": settings.LLM_PROXY_URL
        }
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.SERVICE_NAME,
        "message": "API Gateway for AI Document Intelligence Platform",
        "docs": "/docs"
    }
