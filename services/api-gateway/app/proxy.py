# FILE: services/api-gateway/app/proxy.py

from fastapi import Request, Response
from fastapi.responses import StreamingResponse
import httpx
from typing import Optional
import logging

logger = logging.getLogger(__name__)


async def proxy_request(
    request: Request,
    target_url: str,
    path: str = "",
    timeout: float = 30.0
) -> Response:
    """
    Proxy HTTP request to target service.

    Args:
        request: Incoming FastAPI request
        target_url: Base URL of target service
        path: Path to append to target URL
        timeout: Request timeout in seconds

    Returns:
        Response from target service
    """
    # Build target URL
    url = f"{target_url.rstrip('/')}/{path.lstrip('/')}"

    # Get query parameters
    query_params = dict(request.query_params)

    # Get headers (exclude host header)
    headers = dict(request.headers)
    headers.pop("host", None)

    # Get body for non-GET requests
    body = None
    if request.method != "GET":
        body = await request.body()

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            # Make request to target service
            response = await client.request(
                method=request.method,
                url=url,
                params=query_params,
                headers=headers,
                content=body,
            )

            # Return response
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type")
            )

    except httpx.TimeoutException:
        logger.error(f"Timeout proxying request to {url}")
        return Response(
            content='{"error": "Service timeout"}',
            status_code=504,
            media_type="application/json"
        )
    except Exception as e:
        logger.error(f"Error proxying request to {url}: {e}")
        return Response(
            content=f'{{"error": "Service unavailable: {str(e)}"}}',
            status_code=503,
            media_type="application/json"
        )
