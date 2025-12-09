#!/bin/bash

# LiteLLM Wrapper Script
# This script starts LiteLLM with a clean environment (no database mode)

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Load only the necessary environment variables
if [ -f "$SCRIPT_DIR/.env" ]; then
    export LITELLM_MASTER_KEY=$(grep LITELLM_MASTER_KEY "$SCRIPT_DIR/.env" | cut -d '=' -f2- | tr -d '"' | tr -d "'")
    export LITELLM_SALT_KEY=$(grep LITELLM_SALT_KEY "$SCRIPT_DIR/.env" | cut -d '=' -f2- | tr -d '"' | tr -d "'")
    export GEMINI_API_KEY=$(grep GEMINI_API_KEY "$SCRIPT_DIR/.env" | cut -d '=' -f2- | tr -d '"' | tr -d "'")
    export GROQ_API_KEY=$(grep GROQ_API_KEY "$SCRIPT_DIR/.env" | cut -d '=' -f2- | tr -d '"' | tr -d "'")
    export MLFLOW_TRACKING_URI=$(grep MLFLOW_TRACKING_URI "$SCRIPT_DIR/.env" | cut -d '=' -f2- | tr -d '"' | tr -d "'")
    export DATABASE_URL=$(grep DATABASE_URL "$SCRIPT_DIR/.env" | cut -d '=' -f2- | tr -d '"' | tr -d "'")
    export STORE_MODEL_IN_DB=$(grep STORE_MODEL_IN_DB "$SCRIPT_DIR/.env" | cut -d '=' -f2- | tr -d '"' | tr -d "'")
fi

# Add venv bin to PATH so subprocess calls to 'prisma' work
export PATH="$SCRIPT_DIR/.venv/bin:$PATH"

# Explicitly unset database-related variables
# unset DATABASE_URL
# unset STORE_MODEL_IN_DB

# Start LiteLLM
exec "$SCRIPT_DIR/.venv/bin/litellm" --config "$SCRIPT_DIR/config.yaml" --port 4000
