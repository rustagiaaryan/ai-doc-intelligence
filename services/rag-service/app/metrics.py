# FILE: services/rag-service/app/metrics.py

from prometheus_client import Counter, Histogram, Gauge, Info
import time

# Service information
service_info = Info('rag_service', 'RAG Service Information')
service_info.info({'version': '0.1.0', 'service': 'rag-service'})

# Request metrics
http_requests_total = Counter(
    'rag_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'rag_http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

# RAG query metrics
rag_queries_total = Counter(
    'rag_queries_total',
    'Total RAG queries processed',
    ['status']  # success, no_results, error
)

rag_query_duration_seconds = Histogram(
    'rag_query_duration_seconds',
    'RAG query processing time in seconds',
    ['stage']  # embedding, retrieval, generation, total
)

rag_chunks_retrieved = Histogram(
    'rag_chunks_retrieved',
    'Number of chunks retrieved per query',
    buckets=[0, 1, 3, 5, 10, 20, 50]
)

rag_context_length_chars = Histogram(
    'rag_context_length_chars',
    'Context length in characters',
    buckets=[100, 500, 1000, 2000, 4000, 8000]
)

# Cache metrics
cache_hits_total = Counter(
    'rag_cache_hits_total',
    'Total cache hits'
)

cache_misses_total = Counter(
    'rag_cache_misses_total',
    'Total cache misses'
)

# Vector search metrics
vector_search_duration_seconds = Histogram(
    'rag_vector_search_duration_seconds',
    'Vector similarity search duration'
)

vector_search_results = Histogram(
    'rag_vector_search_results',
    'Number of results from vector search',
    buckets=[0, 1, 5, 10, 20, 50, 100]
)


class MetricsMiddleware:
    """Middleware to track HTTP request metrics."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        method = scope["method"]
        path = scope["path"]

        # Skip metrics endpoint itself
        if path == "/metrics":
            return await self.app(scope, receive, send)

        start_time = time.time()
        status_code = 200

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration = time.time() - start_time
            http_requests_total.labels(method=method, endpoint=path, status=status_code).inc()
            http_request_duration_seconds.labels(method=method, endpoint=path).observe(duration)
