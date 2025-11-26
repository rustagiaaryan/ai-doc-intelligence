# Testing Guide

## Overview

This project includes comprehensive unit tests and CI/CD pipelines for all microservices.

## Running Tests Locally

### Run All Tests

```bash
./run-tests.sh
```

### Run Tests for Specific Service

```bash
./run-tests.sh auth-service
./run-tests.sh document-service
./run-tests.sh rag-service
```

### Manual Testing

```bash
cd services/auth-service
pip install -r requirements.txt
pip install pytest pytest-cov pytest-asyncio httpx
pytest tests/ -v --cov=app
```

## CI/CD Pipeline

### GitHub Actions

The project uses GitHub Actions for continuous integration. On every push and pull request:

1. **Lint** - Checks code style with flake8, black, isort
2. **Test** - Runs unit tests for all services
3. **Build** - Builds Docker images
4. **Integration** - Runs integration tests (on main branch)

### Pipeline Stages

```
┌─────────────┐
│    Lint     │ → Python code quality checks
└─────────────┘
       ↓
┌─────────────────────────────────────────────┐
│              Unit Tests                      │
│  ┌─────────┬─────────┬─────────┬─────────┐  │
│  │  Auth   │Document │   RAG   │   LLM   │  │
│  └─────────┴─────────┴─────────┴─────────┘  │
│  ┌─────────┬─────────┬─────────────────┐    │
│  │Ingestion│ Gateway │    Frontend     │    │
│  └─────────┴─────────┴─────────────────┘    │
└─────────────────────────────────────────────┘
       ↓
┌─────────────┐
│Build Images │ → Docker image builds
└─────────────┘
       ↓
┌─────────────┐
│Integration  │ → End-to-end tests
└─────────────┘
```

## Test Coverage

Each service has tests covering:

- ✅ Health check endpoints
- ✅ Authentication/authorization
- ✅ Core business logic
- ✅ Error handling
- ✅ Edge cases

### Coverage Goals

- **Minimum**: 60% code coverage
- **Target**: 80% code coverage
- **Ideal**: 90%+ code coverage

## Writing Tests

### Test Structure

```python
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

def test_feature_name():
    """Test description"""
    # Arrange - Set up test data
    # Act - Execute the code being tested
    # Assert - Verify the results
```

### Mocking External Dependencies

```python
@patch('app.routes.external_service.call')
def test_with_mock(mock_call):
    mock_call.return_value = "mocked response"
    # Test code here
```

### Async Tests

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected_value
```

## Integration Tests

Integration tests verify that services work together correctly. These run after unit tests pass.

### Running Integration Tests

```bash
# Start all services
kubectl apply -f k8s/

# Wait for services to be ready
kubectl wait --for=condition=ready pod -l app=api-gateway -n ai-doc-intelligence

# Run integration tests
pytest integration-tests/ -v
```

## Continuous Deployment

After all tests pass on the main branch:

1. Docker images are built and tagged
2. Images are pushed to registry (optional)
3. Kubernetes deployments are updated (manual for now)

## Troubleshooting

### Tests Failing Locally

1. Ensure all dependencies are installed: `pip install -r requirements.txt`
2. Check Python version: `python --version` (should be 3.11+)
3. Clear pytest cache: `pytest --cache-clear`

### CI/CD Failures

1. Check GitHub Actions logs
2. Verify secrets are configured (DOCKER_USERNAME, DOCKER_PASSWORD)
3. Ensure all tests pass locally first

## Best Practices

1. **Write tests first** (TDD approach)
2. **Keep tests isolated** - Use mocks for external dependencies
3. **Test edge cases** - Empty inputs, invalid data, errors
4. **Use descriptive names** - Test names should explain what they test
5. **Keep tests fast** - Unit tests should run in seconds
6. **Maintain high coverage** - Aim for 80%+ coverage
