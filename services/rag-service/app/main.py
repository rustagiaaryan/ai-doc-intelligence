# FILE: services/rag-service/app/main.py

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import router as rag_router
from app.cache import cache
from app.metrics import MetricsMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(
    title="RAG Service",
    description="Retrieval Augmented Generation Service",
    version="0.1.0"
)

# Metrics middleware (must be first)
app.add_middleware(MetricsMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup."""
    await cache.connect()


@app.on_event("shutdown")
async def shutdown_event():
    """Close connections on shutdown."""
    await cache.disconnect()


# Register routers
app.include_router(rag_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": "0.1.0"
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.SERVICE_NAME,
        "message": "RAG Service API"
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
