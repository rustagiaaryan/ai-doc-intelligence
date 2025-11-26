#!/bin/bash

# Run all unit tests for AI Document Intelligence Platform
# Usage: ./run-tests.sh [service-name]

set -e

echo "🧪 Running Unit Tests for AI Document Intelligence Platform"
echo "============================================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Array of services
services=(
    "auth-service"
    "document-service"
    "api-gateway"
    "rag-service"
    "llm-proxy"
    "ingestion-worker"
)

# Function to run tests for a single service
run_service_tests() {
    local service=$1
    echo ""
    echo -e "${YELLOW}Testing: $service${NC}"
    echo "-----------------------------------"

    cd "services/$service"

    # Check if tests directory exists
    if [ ! -d "tests" ]; then
        echo -e "${YELLOW}⚠️  No tests directory found for $service${NC}"
        cd ../..
        return
    fi

    # Install dependencies if requirements.txt exists
    if [ -f "requirements.txt" ]; then
        echo "📦 Installing dependencies..."
        pip install -q -r requirements.txt
        pip install -q pytest pytest-cov pytest-asyncio httpx
    fi

    # Run tests
    if pytest tests/ -v --cov=app --cov-report=term-missing --tb=short; then
        echo -e "${GREEN}✅ $service tests passed${NC}"
    else
        echo -e "${RED}❌ $service tests failed${NC}"
        exit 1
    fi

    cd ../..
}

# If service name provided, test only that service
if [ $# -eq 1 ]; then
    service=$1
    if [[ " ${services[@]} " =~ " ${service} " ]]; then
        run_service_tests "$service"
    else
        echo -e "${RED}Error: Unknown service '$service'${NC}"
        echo "Available services: ${services[@]}"
        exit 1
    fi
else
    # Run tests for all services
    for service in "${services[@]}"; do
        run_service_tests "$service"
    done

    echo ""
    echo -e "${GREEN}🎉 All tests passed!${NC}"
fi
