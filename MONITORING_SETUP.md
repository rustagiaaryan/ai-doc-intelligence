# Monitoring Setup Guide

This guide covers setting up Prometheus and Grafana for monitoring the AI Document Intelligence Platform.

## Overview

The monitoring stack includes:
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Service Metrics**: Custom application metrics from all services

## Architecture

```
Services (Port /metrics) → Prometheus (Scraping) → Grafana (Visualization)
```

All FastAPI services expose metrics at `/metrics` endpoint in Prometheus format.

## Option 1: Local Kubernetes with Helm (Recommended)

### Prerequisites

- Kubernetes cluster (minikube or kind)
- Helm 3 installed
- kubectl configured

### Step 1: Install Prometheus

```bash
# Add Prometheus Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Create monitoring namespace
kubectl create namespace monitoring

# Install Prometheus
helm install prometheus prometheus-community/prometheus \
  --namespace monitoring \
  --set alertmanager.enabled=false \
  --set pushgateway.enabled=false \
  --set server.persistentVolume.size=5Gi

# Verify installation
kubectl get pods -n monitoring
```

### Step 2: Configure Service Discovery

Create a ServiceMonitor to auto-discover services:

```bash
kubectl apply -f - <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s

    scrape_configs:
      # AI Doc Intelligence Services
      - job_name: 'ai-doc-services'
        kubernetes_sd_configs:
          - role: pod
            namespaces:
              names:
                - ai-doc-intelligence
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_label_app]
            action: keep
            regex: (auth-service|document-service|llm-proxy|ingestion-worker|rag-service|api-gateway)
          - source_labels: [__meta_kubernetes_pod_name]
            target_label: pod
          - source_labels: [__meta_kubernetes_pod_label_app]
            target_label: service
          - source_labels: [__address__]
            target_label: __address__
            regex: ([^:]+)(?::\d+)?
            replacement: \${1}:8000
EOF
```

### Step 3: Install Grafana

```bash
# Add Grafana Helm repository
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install Grafana
helm install grafana grafana/grafana \
  --namespace monitoring \
  --set persistence.enabled=true \
  --set persistence.size=5Gi \
  --set adminPassword=admin

# Get Grafana password
kubectl get secret --namespace monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo

# Port-forward to access Grafana
kubectl port-forward --namespace monitoring svc/grafana 3000:80
```

Access Grafana at http://localhost:3000
- Username: `admin`
- Password: (from command above)

### Step 4: Configure Prometheus as Data Source

1. In Grafana, go to **Configuration** → **Data Sources**
2. Click **Add data source**
3. Select **Prometheus**
4. Set URL: `http://prometheus-server.monitoring.svc.cluster.local:80`
5. Click **Save & Test**

## Option 2: Docker Compose (Development)

For local development without Kubernetes:

Create `monitoring/docker-compose.yml`:

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - ai-doc-network

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
    networks:
      - ai-doc-network

volumes:
  prometheus-data:
  grafana-data:

networks:
  ai-doc-network:
    external: true
```

Create `monitoring/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'llm-proxy'
    static_configs:
      - targets: ['ai-doc-llm-proxy:8002']

  - job_name: 'rag-service'
    static_configs:
      - targets: ['ai-doc-rag:8004']

  - job_name: 'document-service'
    static_configs:
      - targets: ['ai-doc-document:8001']

  - job_name: 'ingestion-worker'
    static_configs:
      - targets: ['ai-doc-ingestion:8003']

  - job_name: 'auth-service'
    static_configs:
      - targets: ['ai-doc-auth:8000']

  - job_name: 'api-gateway'
    static_configs:
      - targets: ['ai-doc-gateway:8080']
```

Start monitoring stack:

```bash
cd monitoring
docker-compose up -d
```

Access:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001

## Available Metrics

### LLM Proxy Service

**HTTP Metrics:**
- `llm_proxy_http_requests_total` - Total requests by method, endpoint, status
- `llm_proxy_http_request_duration_seconds` - Request latency

**LLM API Metrics:**
- `llm_proxy_llm_requests_total` - LLM API calls by provider, model
- `llm_proxy_llm_request_duration_seconds` - LLM API latency
- `llm_proxy_llm_tokens_total` - Token usage (prompt/completion)
- `llm_proxy_llm_errors_total` - API errors by type
- `llm_proxy_estimated_cost_usd_total` - Estimated API costs

**Cache Metrics:**
- `llm_proxy_cache_hits_total` - Cache hits by type (embedding/chat)
- `llm_proxy_cache_misses_total` - Cache misses by type

### RAG Service

**HTTP Metrics:**
- `rag_http_requests_total` - Total requests
- `rag_http_request_duration_seconds` - Request latency

**RAG Query Metrics:**
- `rag_queries_total` - Queries by status (success/no_results/error)
- `rag_query_duration_seconds` - Query processing time by stage
- `rag_chunks_retrieved` - Number of chunks per query
- `rag_context_length_chars` - Context length distribution

**Cache Metrics:**
- `rag_cache_hits_total` - Cache hits
- `rag_cache_misses_total` - Cache misses

**Vector Search:**
- `rag_vector_search_duration_seconds` - Search latency
- `rag_vector_search_results` - Results count distribution

## Example Queries

### LLM Proxy Queries

```promql
# Total API requests per minute
rate(llm_proxy_llm_requests_total[1m])

# Average request latency by provider
avg(rate(llm_proxy_llm_request_duration_seconds_sum[5m])) by (provider, model)
  / avg(rate(llm_proxy_llm_request_duration_seconds_count[5m])) by (provider, model)

# Cache hit rate
rate(llm_proxy_cache_hits_total[5m])
  / (rate(llm_proxy_cache_hits_total[5m]) + rate(llm_proxy_cache_misses_total[5m]))

# Estimated cost per hour
rate(llm_proxy_estimated_cost_usd_total[1h]) * 3600

# Token usage by model
sum(rate(llm_proxy_llm_tokens_total[5m])) by (model, token_type)
```

### RAG Service Queries

```promql
# Query success rate
rate(rag_queries_total{status="success"}[5m])
  / rate(rag_queries_total[5m])

# Average chunks retrieved
avg(rag_chunks_retrieved)

# P95 query latency
histogram_quantile(0.95, rate(rag_query_duration_seconds_bucket[5m]))

# Cache effectiveness
rate(rag_cache_hits_total[5m])
  / (rate(rag_cache_hits_total[5m]) + rate(rag_cache_misses_total[5m]))
```

## Grafana Dashboards

### Dashboard 1: System Overview

**Panels:**
1. Service Health (all services /health status)
2. Total Requests per Service
3. Error Rate by Service
4. P95 Latency by Service

### Dashboard 2: LLM Proxy Performance

**Panels:**
1. API Requests by Provider & Model
2. Average Latency by Provider
3. Cache Hit Rate (Embeddings vs Chat)
4. Token Usage Over Time
5. Estimated Cost (Hourly/Daily)
6. Error Rate by Provider

### Dashboard 3: RAG Service Performance

**Panels:**
1. Query Success Rate
2. Query Latency (P50, P95, P99)
3. Chunks Retrieved Distribution
4. Context Length Distribution
5. Cache Hit Rate
6. Vector Search Performance

### Dashboard 4: Cost Tracking

**Panels:**
1. Estimated Hourly Cost
2. Cost by Model
3. Token Usage Breakdown
4. Cost Trend (24h, 7d, 30d)

## Alerting Rules

### Example Prometheus Alerts

Create `monitoring/alerts.yml`:

```yaml
groups:
  - name: ai_doc_intelligence
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "{{ $labels.service }} has error rate above 5%"

      - alert: HighAPILatency
        expr: histogram_quantile(0.95, rate(llm_proxy_llm_request_duration_seconds_bucket[5m])) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High LLM API latency"
          description: "P95 latency is above 5 seconds"

      - alert: HighAPICost
        expr: rate(llm_proxy_estimated_cost_usd_total[1h]) * 24 > 10
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High API cost projection"
          description: "Daily cost projection exceeds $10"
```

## Best Practices

1. **Retention**: Keep metrics for 15 days (development) or 90 days (production)
2. **Scrape Interval**: 15 seconds for fine-grained monitoring
3. **Alert Fatigue**: Set appropriate thresholds to avoid false positives
4. **Dashboard Organization**: Group related metrics together
5. **Cost Tracking**: Monitor API costs closely to stay within budget

## Accessing Metrics

### Via curl

```bash
# LLM Proxy metrics
curl http://localhost:8002/metrics

# RAG Service metrics
curl http://localhost:8004/metrics
```

### Via Prometheus UI

1. Go to http://localhost:9090
2. Navigate to **Status** → **Targets** to see all scraped services
3. Use **Graph** tab to query metrics

## Troubleshooting

### Metrics not appearing in Prometheus

1. Check service is running: `kubectl get pods -n ai-doc-intelligence`
2. Verify /metrics endpoint: `curl http://service:port/metrics`
3. Check Prometheus targets: http://localhost:9090/targets
4. Verify service discovery configuration

### Grafana can't connect to Prometheus

1. Check Prometheus is running: `kubectl get pods -n monitoring`
2. Verify data source URL in Grafana
3. Test connectivity: `kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- curl http://prometheus-server.monitoring.svc.cluster.local:80`

### High memory usage

1. Reduce retention period in Prometheus config
2. Decrease scrape frequency
3. Limit number of metrics being collected

## Cost Tracking

The LLM Proxy automatically tracks estimated costs based on OpenAI pricing:

- **GPT-4**: $0.03/1K prompt tokens, $0.06/1K completion tokens
- **GPT-3.5-turbo**: $0.0015/1K prompt tokens, $0.002/1K completion tokens
- **Embeddings**: $0.00002/1K tokens

Query for daily cost projection:
```promql
rate(llm_proxy_estimated_cost_usd_total[1h]) * 24
```

## Next Steps

1. Import pre-built dashboards from Grafana marketplace
2. Set up Alertmanager for notifications (Slack, Email)
3. Configure Grafana datasource provisioning
4. Add custom business metrics
5. Implement SLO (Service Level Objective) tracking
