# MLflow Tracing Tests

This directory contains comprehensive tests for MLflow tracing with LiteLLM.

## Setup

1. **Ensure services are running**:
   ```bash
   docker compose up -d  # PostgreSQL
   ./start_all.sh        # LiteLLM + MLflow
   ```

2. **Install test dependencies**:
   ```bash
   pip install pytest pytest-asyncio
   ```

## Running Tests

**Run all tests**:
```bash
pytest tests/ -v
```

**Run specific test file**:
```bash
pytest tests/test_basic_completion.py -v
```

**Run with output**:
```bash
pytest tests/ -v -s
```

## Test Files

- `test_basic_completion.py` - Basic LLM completion with tracing
- `test_streaming.py` - Streaming responses with tracing
- `test_async_completion.py` - Async operations with tracing
- `test_conversation.py` - Multi-turn conversations
- `test_error_handling.py` - Error scenarios
- `test_parameters.py` - Parameter variations

## Viewing Traces

1. Open MLflow UI: http://localhost:5001
2. Navigate to **Experiments** → **MLflow-Tracing-Tests**
3. Click on runs to view traces
4. Check the **Traces** tab for detailed information

## Configuration

- **Virtual Key**: `sk-Fm8tVLNgar3AAMNGzTcuLA`
- **Model**: `gemini/gemini-2.0-flash`
- **LiteLLM Proxy**: http://localhost:4000
- **MLflow Server**: http://localhost:5001
