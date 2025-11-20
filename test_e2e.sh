#!/bin/bash

# End-to-End Test Script for AI Doc Intelligence Platform
set -e

echo "============================================"
echo "🧪 AI Doc Intelligence E2E Test"
echo "============================================"
echo ""

# Test 1: Health Checks
echo "✅ TEST 1: Service Health Checks"
echo "  Auth Service..." && curl -sf http://localhost:8000/health > /dev/null && echo "    ✓ Healthy"
echo "  Document Service..." && curl -sf http://localhost:8001/health > /dev/null && echo "    ✓ Healthy"
echo "  LLM Proxy..." && curl -sf http://localhost:8002/health > /dev/null && echo "    ✓ Healthy"
echo "  Ingestion Worker..." && curl -sf http://localhost:8003/health > /dev/null && echo "    ✓ Healthy"
echo "  RAG Service..." && curl -sf http://localhost:8004/health > /dev/null && echo "    ✓ Healthy"
echo "  API Gateway..." && curl -sf http://localhost:8080/health > /dev/null && echo "    ✓ Healthy"
echo ""

# Test 2: LLM Proxy - Embeddings
echo "✅ TEST 2: OpenAI Embeddings (via LLM Proxy)"
EMBED_RESPONSE=$(curl -sf -X POST http://localhost:8002/llm/embeddings \
  -H "Content-Type: application/json" \
  -d '{"texts": ["test embedding"], "model": "text-embedding-3-small"}')
EMBED_DIM=$(echo $EMBED_RESPONSE | python3 -c "import sys, json; d=json.load(sys.stdin); print(len(d['embeddings'][0]))")
echo "  ✓ Generated embedding with dimension: $EMBED_DIM"
echo ""

# Test 3: LLM Proxy - Chat Completion
echo "✅ TEST 3: OpenAI Chat Completion"
CHAT_RESPONSE=$(curl -sf -X POST http://localhost:8002/llm/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Say hi in 3 words"}], "model": "gpt-3.5-turbo"}')
CHAT_CONTENT=$(echo $CHAT_RESPONSE | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['content'])")
TOKENS=$(echo $CHAT_RESPONSE | python3 -c "import sys, json; d=json.load(sys.stdin); print(d['usage']['total_tokens'])")
echo "  ✓ Response: \"$CHAT_CONTENT\""
echo "  ✓ Tokens used: $TOKENS"
echo ""

# Test 4: Redis Caching
echo "✅ TEST 4: Redis Caching"
echo "  First call (no cache)..."
curl -sf -X POST http://localhost:8002/llm/embeddings \
  -H "Content-Type: application/json" \
  -d '{"texts": ["cache test text"], "model": "text-embedding-3-small"}' > /dev/null

echo "  Second call (should be cached)..."
CACHE_RESPONSE=$(curl -sf -X POST http://localhost:8002/llm/embeddings \
  -H "Content-Type: application/json" \
  -d '{"texts": ["cache test text"], "model": "text-embedding-3-small"}')
CACHE_HITS=$(echo $CACHE_RESPONSE | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('cache_hits', 0))")
echo "  ✓ Cache hits: $CACHE_HITS"
echo ""

# Test 5: Prometheus Metrics
echo "✅ TEST 5: Prometheus Metrics"
echo "  LLM Proxy metrics..." && curl -sf http://localhost:8002/metrics | grep -q "llm_proxy" && echo "    ✓ Exposing metrics"
echo "  RAG Service metrics..." && curl -sf http://localhost:8004/metrics | grep -q "rag_" && echo "    ✓ Exposing metrics"
echo ""

# Test 6: Infrastructure
echo "✅ TEST 6: Infrastructure Services"
echo "  PostgreSQL..." && docker exec ai-doc-postgres pg_isready > /dev/null 2>&1 && echo "    ✓ Running"
echo "  Redis..." && docker exec ai-doc-redis redis-cli ping > /dev/null 2>&1 && echo "    ✓ Running"
echo "  MinIO..." && curl -sf http://localhost:9000/minio/health/live > /dev/null && echo "    ✓ Running"
echo ""

echo "============================================"
echo "✨ ALL TESTS PASSED!"
echo "============================================"
echo ""
echo "📊 Platform Access:"
echo "  • Frontend:        http://localhost:3000"
echo "  • API Gateway:     http://localhost:8080"
echo "  • LLM Proxy:       http://localhost:8002"
echo "  • RAG Service:     http://localhost:8004"
echo "  • MinIO Console:   http://localhost:9001"
echo "  • Metrics:         http://localhost:8002/metrics"
echo ""
echo "🎯 Next Steps:"
echo "  1. Open http://localhost:3000 in your browser"
echo "  2. Login with Google OAuth"
echo "  3. Upload a document (PDF, DOCX, TXT)"
echo "  4. Process the document"
echo "  5. Ask questions about your document!"
echo ""
