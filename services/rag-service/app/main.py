# FILE: services/rag-service/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import router as rag_router
from app.cache import cache

app = FastAPI(
    title="RAG Service",
    description="Retrieval Augmented Generation Service",
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
