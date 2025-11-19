# FILE: services/llm-proxy/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import router as llm_router

app = FastAPI(
    title="LLM Proxy Service",
    description="Centralized LLM API Management Service",
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
app.include_router(llm_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": "0.1.0",
        "providers": {
            "openai": bool(settings.OPENAI_API_KEY),
            "anthropic": bool(settings.ANTHROPIC_API_KEY)
        }
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.SERVICE_NAME,
        "message": "LLM Proxy Service API"
    }
