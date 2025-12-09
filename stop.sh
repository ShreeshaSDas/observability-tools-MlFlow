#!/bin/bash

# Shutdown Script for MLflow and LiteLLM Servers
# This script gracefully stops both servers

echo "=========================================="
echo "Stopping MLflow and LiteLLM Servers"
echo "=========================================="

# Function to stop a process
stop_process() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo "Stopping $service_name (PID: $pid)..."
            kill $pid
            sleep 2
            
            # Force kill if still running
            if ps -p $pid > /dev/null 2>&1; then
                echo "  Force stopping $service_name..."
                kill -9 $pid
            fi
            echo "✓ $service_name stopped"
        else
            echo "✓ $service_name is not running"
        fi
        rm -f "$pid_file"
    else
        echo "✓ No PID file found for $service_name"
    fi
}

# Stop LiteLLM first
stop_process ".litellm.pid" "LiteLLM"

# Stop MLflow
stop_process ".mlflow.pid" "MLflow"

# Also try to kill by port (fallback)
echo ""
echo "Checking for any remaining processes..."

# Kill any process on port 4000 (LiteLLM)
LITELLM_PORT_PID=$(lsof -ti:4000 2>/dev/null)
if [ ! -z "$LITELLM_PORT_PID" ]; then
    echo "Found process on port 4000, stopping..."
    kill -9 $LITELLM_PORT_PID 2>/dev/null || true
fi

# Kill any process on port 5001 (MLflow)
MLFLOW_PORT_PID=$(lsof -ti:5001 2>/dev/null)
if [ ! -z "$MLFLOW_PORT_PID" ]; then
    echo "Found process on port 5001, stopping..."
    kill -9 $MLFLOW_PORT_PID 2>/dev/null || true
fi

echo ""
echo "=========================================="
echo "✓ All servers stopped"
echo "=========================================="
