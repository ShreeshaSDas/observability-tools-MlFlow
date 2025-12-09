# LiteLLM + MLflow Setup Guide

This guide will help you set up and run the LiteLLM proxy with MLflow tracing for observability.

## Architecture

```mermaid
graph LR
    A[Your Application] -->|API Calls| B[LiteLLM Proxy :4000]
    B -->|Routes to| C[LLM Providers]
    B -->|Traces| D[MLflow :5001]
    D -->|Stores| E[PostgreSQL :5433]
    
    C -->|Gemini| F[Google AI]
    C -->|Groq| G[Groq]
    C -->|OpenAI| H[OpenAI]
```

## Components

| Component | Port | Purpose |
|-----------|------|---------|
| **LiteLLM Proxy** | 4000 | Unified API gateway for multiple LLM providers |
| **MLflow Server** | 5001 | Experiment tracking and trace visualization |
| **PostgreSQL** | 5433 | Backend storage for MLflow |

## Prerequisites

1. **Docker** - For running PostgreSQL
2. **Python 3.8+** - For LiteLLM and MLflow
3. **Virtual Environment** - Recommended for dependency isolation

## Installation

### 1. Set Up Virtual Environment

```bash
cd /Users/shreesha.dasthoughtworks.com/Documents/Observability_Tools

# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Edit the `.env` file and add your API keys:

```bash
# Required: LiteLLM master key for authentication
LITELLM_MASTER_KEY="sk-1234"

# Add your LLM provider API keys
GEMINI_API_KEY=your_actual_gemini_key
GROQ_API_KEY=your_actual_groq_key
# OPENAI_API_KEY=sk-...

# MLflow tracking URI (default)
MLFLOW_TRACKING_URI="http://localhost:5001"
```

> **Note:** The `LITELLM_MASTER_KEY` is used to authenticate requests to the LiteLLM proxy.

## Running the Stack

### Quick Start

```bash
./start.sh
```

This script will:
1. Start PostgreSQL in Docker
2. Start MLflow server on port 5001
3. Start LiteLLM proxy on port 4000

### Manual Start (Alternative)

If you prefer to start services individually:

#### 1. Start PostgreSQL

```bash
docker compose up -d
```

Wait a few seconds for PostgreSQL to be ready.

#### 2. Start MLflow

```bash
source .env

nohup mlflow server \
    --backend-store-uri postgresql://litellm:litellm_password@localhost:5433/mlflow \
    --default-artifact-root ./mlflow/artifacts \
    --host 0.0.0.0 \
    --port 5001 \
    > mlflow.log 2>&1 &

echo $! > mlflow.pid
```

#### 3. Start LiteLLM

```bash
source .env

# Unset database variables to run in-memory mode
unset DATABASE_URL
unset STORE_MODEL_IN_DB

nohup litellm --config config.yaml --port 4000 > litellm.log 2>&1 &
echo $! > litellm.pid
```

## Verifying the Setup

### Check Service Status

```bash
# Check if PostgreSQL is running
docker ps | grep litellm_postgres

# Check MLflow
curl http://localhost:5001/health

# Check LiteLLM
curl http://localhost:4000/health
```

### Access Web UIs

- **MLflow UI**: http://localhost:5001
- **LiteLLM Swagger Docs**: http://localhost:4000/docs

## Making Your First Request

### Using curl

```bash
curl -X POST http://localhost:4000/chat/completions \
  -H "Authorization: Bearer sk-1234" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-2.0-flash",
    "messages": [
      {"role": "user", "content": "Hello! How are you?"}
    ]
  }'
```

### Using Python

```python
from openai import OpenAI

# Point to LiteLLM proxy
client = OpenAI(
    api_key="sk-1234",  # Your LITELLM_MASTER_KEY
    base_url="http://localhost:4000"
)

response = client.chat.completions.create(
    model="gemini-2.0-flash",
    messages=[
        {"role": "user", "content": "Hello! How are you?"}
    ]
)

print(response.choices[0].message.content)
```

### View Traces in MLflow

1. Open http://localhost:5001 in your browser
2. Click on "Traces" in the left sidebar
3. You should see your request logged with:
   - Request parameters
   - Response content
   - Latency metrics
   - Token usage

## Stopping the Stack

```bash
./stop.sh
```

This will gracefully stop MLflow and LiteLLM, and you can stop PostgreSQL with:

```bash
docker compose down
```

## Configuration

### LiteLLM Models

Edit `config.yaml` to add or modify models:

```yaml
model_list:
  - model_name: gemini-2.0-flash
    litellm_params:
      model: gemini/gemini-2.0-flash
      api_key: os.environ/GEMINI_API_KEY
  
  - model_name: groq-llama
    litellm_params:
      model: groq/llama-3.1-70b-versatile
      api_key: os.environ/GROQ_API_KEY
```

### MLflow Callbacks

The `config.yaml` already includes MLflow callbacks:

```yaml
litellm_settings:
  success_callback: ["lite_debugger", "mlflow"]
  failure_callback: ["lite_debugger", "mlflow"]
```

This ensures all requests (successful or failed) are logged to MLflow.

## Troubleshooting

### LiteLLM shows "Missing Environment Variables: DATABASE_URL"

This is just an **informational warning**, not an error. LiteLLM is running correctly in in-memory mode (without a database). You can safely ignore this message.

The warning appears in the LiteLLM UI when you first access it. It doesn't affect functionality - your API calls will work fine.

To verify LiteLLM is working:
```bash
curl -X POST http://localhost:4000/chat/completions \
  -H "Authorization: Bearer sk-1234" \
  -H "Content-Type: application/json" \
  -d '{"model": "gemini-2.0-flash", "messages": [{"role": "user", "content": "test"}]}'
```

### LiteLLM fails with "All connection attempts failed"

This means LiteLLM is trying to connect to a database. Make sure:
1. Your `.env` file does NOT contain `DATABASE_URL` or `STORE_MODEL_IN_DB`
2. The `start.sh` script unsets these variables before starting LiteLLM

### MLflow database connection error

```bash
# Check if PostgreSQL is running
docker ps | grep litellm_postgres

# If not, start it
docker compose up -d

# Wait 5 seconds, then restart MLflow
```

### Port already in use

```bash
# Find and kill process on port 4000 (LiteLLM)
lsof -ti:4000 | xargs kill -9

# Find and kill process on port 5001 (MLflow)
lsof -ti:5001 | xargs kill -9
```

### View Logs

```bash
# MLflow logs
tail -f mlflow.log

# LiteLLM logs
tail -f litellm.log

# PostgreSQL logs
docker logs litellm_postgres
```

## Testing

Run the test suite to verify everything works:

```bash
# Make sure services are running first
./start.sh

# Run tests
pytest tests/ -v
```

## Next Steps

- **Add more models**: Edit `config.yaml` to add OpenAI, Anthropic, etc.
- **Explore MLflow**: Use the UI to analyze traces, compare requests, and monitor performance
- **Production deployment**: Consider using environment-specific configs and proper secrets management

## Resources

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [LiteLLM Proxy Guide](https://docs.litellm.ai/docs/proxy/quick_start)
