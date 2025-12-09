"""
Test basic completion with MLflow tracing
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.utils import verify_trace_exists


def test_simple_completion(litellm_client, model_name, simple_message):
    """
    Test basic completion and verify MLflow trace is created.
    """
    # Make completion request
    response = litellm_client.chat.completions.create(
        model=model_name,
        messages=simple_message,
        temperature=0.7,
        max_tokens=50
    )
    
    # Verify response
    assert response is not None
    assert len(response.choices) > 0
    assert response.choices[0].message.content is not None
    
    # Verify trace was created (MLflow autolog should capture this)
    # Note: Trace verification might need a small delay
    import time
    time.sleep(1)
    assert verify_trace_exists(), "MLflow trace was not created"
    
    print(f"\n✓ Response: {response.choices[0].message.content}")
    print(f"✓ Model: {response.model}")
    print(f"✓ Tokens used: {response.usage.total_tokens}")


def test_completion_with_system_message(litellm_client, model_name):
    """
    Test completion with system message.
    """
    messages = [
        {"role": "system", "content": "You are a helpful assistant that speaks like a pirate."},
        {"role": "user", "content": "Tell me about MLflow in one sentence."}
    ]
    
    response = litellm_client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.8,
        max_tokens=100
    )
    
    assert response is not None
    assert response.choices[0].message.content is not None
    
    print(f"\n✓ Pirate response: {response.choices[0].message.content}")


def test_completion_with_different_temperatures(litellm_client, model_name):
    """
    Test completions with different temperature settings.
    """
    temperatures = [0.1, 0.5, 1.0]
    message = [{"role": "user", "content": "Say hello."}]
    
    for temp in temperatures:
        response = litellm_client.chat.completions.create(
            model=model_name,
            messages=message,
            temperature=temp,
            max_tokens=20
        )
        
        assert response is not None
        print(f"\n✓ Temperature {temp}: {response.choices[0].message.content}")


def test_completion_with_max_tokens(litellm_client, model_name):
    """
    Test completion with max_tokens limit.
    """
    response = litellm_client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": "Write a long story about MLflow."}],
        temperature=0.7,
        max_tokens=50  # Limit response length
    )
    
    assert response is not None
    assert response.usage.completion_tokens <= 50
    
    print(f"\n✓ Tokens used: {response.usage.completion_tokens} (max: 50)")
    print(f"✓ Response: {response.choices[0].message.content}")


if __name__ == "__main__":
    # Setup for standalone execution
    from tests.utils import setup_mlflow, enable_mlflow_tracing, get_litellm_client, MODEL_NAME
    
    setup_mlflow()
    enable_mlflow_tracing()
    client = get_litellm_client()
    simple_msg = [{"role": "user", "content": "Say 'Hello, MLflow tracing!' and nothing else."}]
    
    print("\n" + "="*60)
    print("Running Basic Completion Tests")
    print("="*60)
    
    try:
        print("\n[Test 1] System message...")
        test_completion_with_system_message(client, MODEL_NAME)
        
        print("\n[Test 2] Different temperatures...")
        test_completion_with_different_temperatures(client, MODEL_NAME)
        
        print("\n[Test 3] Max tokens...")
        test_completion_with_max_tokens(client, MODEL_NAME)
        
        print("\n" + "="*60)
        print("✓ All tests completed successfully!")
        print("="*60)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
