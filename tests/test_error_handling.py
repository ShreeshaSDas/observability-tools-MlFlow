"""
Test error handling with MLflow tracing
"""

import pytest
import sys
import os
from openai import BadRequestError, AuthenticationError

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_invalid_model_name(litellm_client):
    """
    Test handling of invalid model name.
    """
    with pytest.raises(Exception) as exc_info:
        litellm_client.chat.completions.create(
            model="invalid-model-name",
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.7,
            max_tokens=50
        )
    
    print(f"\n✓ Caught expected error: {type(exc_info.value).__name__}")


def test_empty_messages(litellm_client, model_name):
    """
    Test handling of empty messages list.
    """
    with pytest.raises(Exception) as exc_info:
        litellm_client.chat.completions.create(
            model=model_name,
            messages=[],  # Empty messages
            temperature=0.7,
            max_tokens=50
        )
    
    print(f"\n✓ Caught expected error for empty messages: {type(exc_info.value).__name__}")


def test_invalid_temperature(litellm_client, model_name):
    """
    Test handling of invalid temperature value.
    """
    with pytest.raises(Exception) as exc_info:
        litellm_client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Hello"}],
            temperature=2.5,  # Invalid: should be 0-2
            max_tokens=50
        )
    
    print(f"\n✓ Caught expected error for invalid temperature: {type(exc_info.value).__name__}")


def test_negative_max_tokens(litellm_client, model_name):
    """
    Test handling of negative max_tokens.
    """
    with pytest.raises(Exception) as exc_info:
        litellm_client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.7,
            max_tokens=-10  # Invalid: negative value
        )
    
    print(f"\n✓ Caught expected error for negative max_tokens: {type(exc_info.value).__name__}")


def test_malformed_message(litellm_client, model_name):
    """
    Test handling of malformed message structure.
    """
    with pytest.raises(Exception) as exc_info:
        litellm_client.chat.completions.create(
            model=model_name,
            messages=[{"invalid_key": "value"}],  # Missing 'role' and 'content'
            temperature=0.7,
            max_tokens=50
        )
    
    print(f"\n✓ Caught expected error for malformed message: {type(exc_info.value).__name__}")


def test_recovery_after_error(litellm_client, model_name):
    """
    Test that client can recover after an error.
    """
    # First, cause an error
    try:
        litellm_client.chat.completions.create(
            model="invalid-model",
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.7,
            max_tokens=50
        )
    except Exception:
        pass  # Expected error
    
    # Then, make a valid request
    response = litellm_client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": "Hello after error"}],
        temperature=0.7,
        max_tokens=50
    )
    
    assert response is not None
    print(f"\n✓ Successfully recovered after error")
    print(f"✓ Response: {response.choices[0].message.content}")


if __name__ == "__main__":
    from tests.utils import setup_mlflow, enable_mlflow_tracing, get_litellm_client, MODEL_NAME
    
    setup_mlflow()
    enable_mlflow_tracing()
    client = get_litellm_client()
    
    print("\n" + "="*60)
    print("Running Error Handling Tests")
    print("="*60)
    
    try:
        print("\n[Test 1] Invalid model name...")
        test_invalid_model_name(client)
        
        print("\n[Test 2] Invalid temperature...")
        test_invalid_temperature(client, MODEL_NAME)
        
        print("\n[Test 3] Negative max_tokens...")
        test_negative_max_tokens(client, MODEL_NAME)
        
        print("\n[Test 4] Recovery after error...")
        test_recovery_after_error(client, MODEL_NAME)
        
        print("\n" + "="*60)
        print("✓ All error handling tests completed!")
        print("="*60)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
