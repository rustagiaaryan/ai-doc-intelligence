#!/bin/bash

# Test the complete document intelligence pipeline

echo "=== AI Document Intelligence - End-to-End Test ==="
echo ""

# Configuration
AUTH_SERVICE="http://localhost:8000"
DOCUMENT_SERVICE="http://localhost:8001"
INGESTION_SERVICE="http://localhost:8003"
RAG_SERVICE="http://localhost:8004"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Step 1: Check all services are healthy"
echo "--------------------------------------"

services=("$AUTH_SERVICE" "$DOCUMENT_SERVICE" "$INGESTION_SERVICE" "$RAG_SERVICE")
for service in "${services[@]}"; do
    if curl -s "$service/health" > /dev/null; then
        echo -e "${GREEN}✓${NC} $(echo $service | cut -d'/' -f3) is healthy"
    else
        echo -e "${RED}✗${NC} $(echo $service | cut -d'/' -f3) is not responding"
    fi
done

echo ""
echo "Test script created. You'll need to:"
echo "1. Get a JWT token from auth service (requires Google OAuth setup)"
echo "2. Upload a document"
echo "3. Process it with ingestion worker"
echo "4. Ask questions with RAG service"
