# FILE: services/llm-proxy/app/metrics.py

from prometheus_client import Counter, Histogram, Gauge, Info
import time

# Service information
service_info = Info('llm_proxy_service', 'LLM Proxy Service Information')
service_info.info({'version': '0.1.0', 'service': 'llm-proxy'})

# Request metrics
http_requests_total = Counter(
    'llm_proxy_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'llm_proxy_http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

# LLM API metrics
llm_requests_total = Counter(
    'llm_proxy_llm_requests_total',
    'Total LLM API requests',
    ['provider', 'model', 'endpoint_type']  # endpoint_type: chat, embedding
)

llm_request_duration_seconds = Histogram(
    'llm_proxy_llm_request_duration_seconds',
    'LLM API request latency in seconds',
    ['provider', 'model', 'endpoint_type']
)

llm_tokens_total = Counter(
    'llm_proxy_llm_tokens_total',
    'Total tokens processed by LLM',
    ['provider', 'model', 'token_type']  # token_type: prompt, completion
)

llm_errors_total = Counter(
    'llm_proxy_llm_errors_total',
    'Total LLM API errors',
    ['provider', 'model', 'error_type']
)

# Cache metrics
cache_hits_total = Counter(
    'llm_proxy_cache_hits_total',
    'Total cache hits',
    ['cache_type']  # cache_type: embedding, chat
)

cache_misses_total = Counter(
    'llm_proxy_cache_misses_total',
    'Total cache misses',
    ['cache_type']
)

cache_size_bytes = Gauge(
    'llm_proxy_cache_size_bytes',
    'Current cache size in bytes'
)

# Cost estimation metrics (based on OpenAI pricing)
estimated_cost_usd = Counter(
    'llm_proxy_estimated_cost_usd_total',
    'Estimated API cost in USD',
    ['provider', 'model']
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


def track_llm_request(provider: str, model: str, endpoint_type: str):
    """Context manager to track LLM API requests."""
    class LLMRequestTracker:
        def __init__(self):
            self.start_time = None

        def __enter__(self):
            self.start_time = time.time()
            llm_requests_total.labels(provider=provider, model=model, endpoint_type=endpoint_type).inc()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = time.time() - self.start_time
            llm_request_duration_seconds.labels(provider=provider, model=model, endpoint_type=endpoint_type).observe(duration)

            if exc_type is not None:
                error_type = exc_type.__name__
                llm_errors_total.labels(provider=provider, model=model, error_type=error_type).inc()

    return LLMRequestTracker()


def track_tokens(provider: str, model: str, prompt_tokens: int, completion_tokens: int = 0):
    """Track token usage."""
    llm_tokens_total.labels(provider=provider, model=model, token_type="prompt").inc(prompt_tokens)
    if completion_tokens > 0:
        llm_tokens_total.labels(provider=provider, model=model, token_type="completion").inc(completion_tokens)

    # Estimate cost (OpenAI GPT-3.5-turbo pricing as baseline)
    if provider == "openai":
        if "gpt-4" in model.lower():
            # GPT-4 pricing: $0.03/1K prompt tokens, $0.06/1K completion tokens
            cost = (prompt_tokens * 0.03 / 1000) + (completion_tokens * 0.06 / 1000)
        elif "gpt-3.5" in model.lower():
            # GPT-3.5-turbo: $0.0015/1K prompt tokens, $0.002/1K completion tokens
            cost = (prompt_tokens * 0.0015 / 1000) + (completion_tokens * 0.002 / 1000)
        elif "embedding" in model.lower():
            # text-embedding-3-small: $0.00002/1K tokens
            cost = prompt_tokens * 0.00002 / 1000
        else:
            cost = 0
        estimated_cost_usd.labels(provider=provider, model=model).inc(cost)


def track_cache_hit(cache_type: str):
    """Track cache hit."""
    cache_hits_total.labels(cache_type=cache_type).inc()


def track_cache_miss(cache_type: str):
    """Track cache miss."""
    cache_misses_total.labels(cache_type=cache_type).inc()
