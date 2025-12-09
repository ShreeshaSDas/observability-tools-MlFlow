#!/bin/bash

# Start all services in the correct order
# 1. PostgreSQL (Docker)
# 2. MLflow Server
# 3. LiteLLM Proxy

set -e  # Exit on error

echo "=========================================="
echo "Starting Observability Stack"
echo "=========================================="
echo ""

# 1. Start PostgreSQL
echo "[1/3] Starting PostgreSQL..."
docker compose up -d
sleep 3
echo "✓ PostgreSQL started"
echo ""

# 2. Start MLflow
echo "[2/3] Starting MLflow Server..."
source .env
nohup ./.venv/bin/mlflow server \
    --backend-store-uri postgresql://litellm:litellm_password@localhost:5433/mlflow \
    --default-artifact-root ./mlflow/artifacts \
    --host 0.0.0.0 \
    --port 5001 \
    > mlflow.log 2>&1 &
echo $! > mlflow.pid
sleep 5
echo "✓ MLflow started on http://localhost:5001"
echo ""

# 3. Start LiteLLM (without database mode)
echo "[3/3] Starting LiteLLM Proxy..."
nohup ./start_litellm_clean.sh > litellm.log 2>&1 &
echo $! > litellm.pid
sleep 5
echo "✓ LiteLLM started on http://localhost:4000"
echo "  Note: Running in-memory mode (no database)"
echo ""

echo "=========================================="
echo "All services started successfully!"
echo "=========================================="
echo ""
echo "Services:"
echo "  - PostgreSQL: localhost:5433"
echo "  - MLflow UI:  http://localhost:5001"
echo "  - LiteLLM:    http://localhost:4000"
echo ""
echo "To stop all services: ./stop.sh"
echo "To view logs:"
echo "  - MLflow:   tail -f mlflow.log"
echo "  - LiteLLM:  tail -f litellm.log"
