# Observability Tools

This project sets up a local observability stack for LLM applications using LiteLLM and MLflow.

## Components
- **LiteLLM**: Proxy for LLM calls (OpenAI, Gemini, Groq, etc.)
- **MLflow**: Tracing and experiment tracking
- **PostgreSQL**: Backend storage for MLflow

## Quick Start

### 1. Configure Environment
Copy `.env.example` to `.env` and set your API keys:
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY, GROQ_API_KEY, etc.
```

### 2. Start Services
```bash
./start.sh
```
This will start:
- PostgreSQL (Docker on port 5433)
- MLflow Server (http://localhost:5001)
- LiteLLM Proxy (http://localhost:4000)

### 3. Test the Setup
```bash
curl -X POST http://localhost:4000/chat/completions \
  -H "Authorization: Bearer sk-1234" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-2.0-flash",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### 4. View Traces
Open http://localhost:5001 in your browser to see traces in MLflow.

### 5. Stop Services
```bash
./stop.sh
```

## Documentation

For detailed setup instructions, configuration options, and troubleshooting, see [SETUP_GUIDE.md](SETUP_GUIDE.md).

## Logs
- MLflow: `mlflow.log`
- LiteLLM: `litellm.log`
- PostgreSQL: `docker logs litellm_postgres`
