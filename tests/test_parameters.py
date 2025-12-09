"""
Test parameter variations with MLflow tracing
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_temperature_variations(litellm_client, model_name):
    """
    Test different temperature values.
    """
    temperatures = [0.0, 0.3, 0.7, 1.0, 1.5]
    message = [{"role": "user", "content": "Generate a creative sentence about clouds."}]
    
    for temp in temperatures:
        response = litellm_client.chat.completions.create(
            model=model_name,
            messages=message,
            temperature=temp,
            max_tokens=50
        )
        
        assert response is not None
        print(f"\n✓ Temperature {temp}: {response.choices[0].message.content[:80]}...")


def test_max_tokens_variations(litellm_client, model_name):
    """
    Test different max_tokens values.
    """
    max_tokens_values = [10, 50, 100, 200]
    message = [{"role": "user", "content": "Explain MLflow in detail."}]
    
    for max_tokens in max_tokens_values:
        response = litellm_client.chat.completions.create(
            model=model_name,
            messages=message,
            temperature=0.7,
            max_tokens=max_tokens
        )
        
        assert response is not None
        actual_tokens = response.usage.completion_tokens
        assert actual_tokens <= max_tokens
        
        print(f"\n✓ Max tokens {max_tokens}: Used {actual_tokens} tokens")
        print(f"  Response: {response.choices[0].message.content[:100]}...")


def test_top_p_variations(litellm_client, model_name):
    """
    Test different top_p (nucleus sampling) values.
    """
    top_p_values = [0.1, 0.5, 0.9, 1.0]
    message = [{"role": "user", "content": "Write a sentence about observability."}]
    
    for top_p in top_p_values:
        response = litellm_client.chat.completions.create(
            model=model_name,
            messages=message,
            temperature=0.8,
            top_p=top_p,
            max_tokens=50
        )
        
        assert response is not None
        print(f"\n✓ Top-p {top_p}: {response.choices[0].message.content[:80]}...")


def test_combined_parameters(litellm_client, model_name):
    """
    Test combinations of parameters.
    """
    test_cases = [
        {"temp": 0.3, "max_tokens": 30, "top_p": 0.9, "desc": "Conservative"},
        {"temp": 1.0, "max_tokens": 100, "top_p": 1.0, "desc": "Creative"},
        {"temp": 0.7, "max_tokens": 50, "top_p": 0.95, "desc": "Balanced"}
    ]
    
    message = [{"role": "user", "content": "Describe a sunset."}]
    
    for case in test_cases:
        response = litellm_client.chat.completions.create(
            model=model_name,
            messages=message,
            temperature=case["temp"],
            max_tokens=case["max_tokens"],
            top_p=case["top_p"]
        )
        
        assert response is not None
        print(f"\n✓ {case['desc']} (temp={case['temp']}, max_tokens={case['max_tokens']}, top_p={case['top_p']})")
        print(f"  {response.choices[0].message.content[:100]}...")


def test_stop_sequences(litellm_client, model_name):
    """
    Test stop sequences.
    """
    message = [{"role": "user", "content": "List programming languages: Python, JavaScript,"}]
    
    response = litellm_client.chat.completions.create(
        model=model_name,
        messages=message,
        temperature=0.7,
        max_tokens=50,
        stop=[",", "."]  # Stop at comma or period
    )
    
    assert response is not None
    print(f"\n✓ Response with stop sequence: {response.choices[0].message.content}")
    print(f"✓ Finish reason: {response.choices[0].finish_reason}")


def test_presence_and_frequency_penalty(litellm_client, model_name):
    """
    Test presence and frequency penalties.
    """
    message = [{"role": "user", "content": "Write about MLflow MLflow MLflow."}]
    
    # With penalties
    response = litellm_client.chat.completions.create(
        model=model_name,
        messages=message,
        temperature=0.7,
        max_tokens=100,
        presence_penalty=0.5,
        frequency_penalty=0.5
    )
    
    assert response is not None
    print(f"\n✓ Response with penalties: {response.choices[0].message.content[:100]}...")


if __name__ == "__main__":
    from tests.utils import setup_mlflow, enable_mlflow_tracing, get_litellm_client, MODEL_NAME
    
    setup_mlflow()
    enable_mlflow_tracing()
    client = get_litellm_client()
    
    print("\n" + "="*60)
    print("Running Parameter Variation Tests")
    print("="*60)
    
    try:
        print("\n[Test 1] Temperature variations...")
        test_temperature_variations(client, MODEL_NAME)
        
        print("\n[Test 2] Max tokens variations...")
        test_max_tokens_variations(client, MODEL_NAME)
        
        print("\n[Test 3] Top-p variations...")
        test_top_p_variations(client, MODEL_NAME)
        
        print("\n[Test 4] Combined parameters...")
        test_combined_parameters(client, MODEL_NAME)
        
        print("\n[Test 5] Stop sequences...")
        test_stop_sequences(client, MODEL_NAME)
        
        print("\n" + "="*60)
        print("✓ All parameter tests completed!")
        print("="*60)
        print("\nNote: Skipping presence/frequency penalty test (not supported by Gemini)")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
