"""
Pytest configuration and fixtures for MLflow tracing tests
"""

import pytest
from tests.utils import (
    setup_mlflow,
    enable_mlflow_tracing,
    get_litellm_client,
    MODEL_NAME
)


@pytest.fixture(scope="session", autouse=True)
def setup_mlflow_session():
    """
    Session-level fixture to configure MLflow.
    Runs once before all tests.
    """
    setup_mlflow()
    enable_mlflow_tracing()
    yield


@pytest.fixture
def litellm_client():
    """
    Fixture to provide a configured LiteLLM client.
    
    Returns:
        OpenAI: Configured client pointing to LiteLLM proxy
    """
    return get_litellm_client()


@pytest.fixture
def model_name():
    """
    Fixture to provide the model name for tests.
    
    Returns:
        str: Model name
    """
    return MODEL_NAME


@pytest.fixture
def simple_message():
    """
    Fixture to provide a simple test message.
    
    Returns:
        list: Message list for completion
    """
    return [
        {"role": "user", "content": "Say 'Hello, MLflow tracing!' and nothing else."}
    ]


@pytest.fixture
def conversation_messages():
    """
    Fixture to provide multi-turn conversation messages.
    
    Returns:
        list: Conversation message list
    """
    return [
        {"role": "user", "content": "What is MLflow?"},
        {"role": "assistant", "content": "MLflow is an open-source platform for managing machine learning workflows."},
        {"role": "user", "content": "What are its main components?"}
    ]
