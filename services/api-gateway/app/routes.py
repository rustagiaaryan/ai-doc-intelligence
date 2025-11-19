# FILE: services/api-gateway/app/routes.py

from fastapi import APIRouter, Request
from app.config import settings
from app.proxy import proxy_request

# Create routers for each service
auth_router = APIRouter(prefix="/api/auth", tags=["Auth"])
document_router = APIRouter(prefix="/api/documents", tags=["Documents"])
rag_router = APIRouter(prefix="/api/rag", tags=["RAG"])
ingestion_router = APIRouter(prefix="/api/process", tags=["Processing"])


# Auth Service Routes
@auth_router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_auth(request: Request, path: str = ""):
    """Proxy all auth service requests."""
    return await proxy_request(
        request=request,
        target_url=settings.AUTH_SERVICE_URL,
        path=f"auth/{path}" if path else "auth"
    )


# Document Service Routes
@document_router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_documents(request: Request, path: str = ""):
    """Proxy all document service requests."""
    return await proxy_request(
        request=request,
        target_url=settings.DOCUMENT_SERVICE_URL,
        path=f"documents/{path}" if path else "documents",
        timeout=60.0  # Longer timeout for file uploads
    )


# RAG Service Routes
@rag_router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_rag(request: Request, path: str = ""):
    """Proxy all RAG service requests."""
    return await proxy_request(
        request=request,
        target_url=settings.RAG_SERVICE_URL,
        path=f"rag/{path}" if path else "rag",
        timeout=60.0  # Longer timeout for LLM calls
    )


# Ingestion Worker Routes
@ingestion_router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_ingestion(request: Request, path: str = ""):
    """Proxy all ingestion worker requests."""
    return await proxy_request(
        request=request,
        target_url=settings.INGESTION_WORKER_URL,
        path=f"process/{path}" if path else "process",
        timeout=120.0  # Very long timeout for document processing
    )
