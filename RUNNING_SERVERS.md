# How to Run LiteLLM and MLflow Servers

This guide provides step-by-step instructions to run the fully integrated LiteLLM and MLflow observability stack in **Database Mode**.

## Prerequisites

- **Docker** (must be running for PostgreSQL)
- **Python 3.8+**
- **Git**

## 1. Environment Setup

Ensure you have your environment variables configured.

1.  **Check `.env` file**:
    Ensure `/Users/shreesha.dasthoughtworks.com/Documents/Observability_Tools/.env` exists and contains:
    ```bash
    LITELLM_MASTER_KEY="sk-1234"
    GEMINI_API_KEY=...
    GROQ_API_KEY=...
    MLFLOW_TRACKING_URI="http://localhost:5001"
    DATABASE_URL="postgresql://litellm:litellm_password@localhost:5433/litellm"
    STORE_MODEL_IN_DB="True"
    ```

2.  **Activate Virtual Environment**:
    ```bash
    cd /Users/shreesha.dasthoughtworks.com/Documents/Observability_Tools
    source .venv/bin/activate
    ```

3.  **Install Dependencies** (if not already done):
    ```bash
    pip install -r requirements.txt
    pip install 'litellm[proxy]'
    ```

## 2. Starting the Servers

We have simplified the startup process into a single script.

**Run the startup script:**
```bash
./start.sh
```

This script will automatically:
1.  Start the **PostgreSQL** database (Docker container `litellm_postgres` on port `5433`).
2.  Start the **MLflow Server** (on port `5001`).
3.  Run database migrations (Prisma).
4.  Start the **LiteLLM Proxy** (on port `4000`).

## 3. Verification

Once the script completes, verifying the services is easy.

### Check Service Health
- **LiteLLM Proxy**: [http://localhost:4000/health](http://localhost:4000/health) (Should return `401 Unauthorized` or health status)
- **MLflow UI**: [http://localhost:5001](http://localhost:5001) (Should load the MLflow dashboard)

### Check Logs
You can monitor the logs in real-time:
```bash
# Monitor LiteLLM Logs
tail -f litellm.log

# Monitor MLflow Logs
tail -f mlflow.log
```

## 4. Stopping the Servers

To stop all services gracefully:

```bash
./stop.sh
```

## Troubleshooting

### "Relation does not exist" Error
If you see database errors about missing tables, try resetting the database:
```bash
./stop.sh
docker compose down -v
./start.sh
```
*Note: This will delete all existing data.*

### Port Conflicts
If a port is already in use (`4000` or `5001`), modify the `start.sh` or kill the existing process:
```bash
lsof -ti:4000 | xargs kill -9
lsof -ti:5001 | xargs kill -9
```
