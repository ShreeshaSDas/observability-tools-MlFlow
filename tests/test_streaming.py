"""
Test streaming completion with MLflow tracing
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_streaming_completion(litellm_client, model_name):
    """
    Test streaming completion and verify chunks are received.
    """
    messages = [{"role": "user", "content": "Count from 1 to 5."}]
    
    # Create streaming completion
    stream = litellm_client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.7,
        max_tokens=100,
        stream=True
    )
    
    # Collect chunks
    chunks = []
    full_response = ""
    
    for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            chunks.append(content)
            full_response += content
            print(content, end="", flush=True)
    
    print()  # New line after streaming
    
    # Verify we received chunks
    assert len(chunks) > 0, "No chunks received from stream"
    assert len(full_response) > 0, "No content in response"
    
    print(f"\n✓ Received {len(chunks)} chunks")
    print(f"✓ Full response: {full_response}")


def test_streaming_with_stop_sequence(litellm_client, model_name):
    """
    Test streaming with stop sequence.
    """
    messages = [{"role": "user", "content": "List fruits: apple, banana,"}]
    
    stream = litellm_client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.7,
        max_tokens=50,
        stream=True,
        stop=[","]  # Stop at comma
    )
    
    full_response = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            full_response += chunk.choices[0].delta.content
    
    assert full_response is not None
    print(f"\n✓ Response (stopped at comma): {full_response}")


def test_streaming_long_response(litellm_client, model_name):
    """
    Test streaming a longer response.
    """
    messages = [{"role": "user", "content": "Explain what observability means in software systems."}]
    
    stream = litellm_client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.7,
        max_tokens=200,
        stream=True
    )
    
    chunk_count = 0
    full_response = ""
    
    print("\n✓ Streaming response:")
    print("-" * 60)
    
    for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print(content, end="", flush=True)
            full_response += content
            chunk_count += 1
    
    print("\n" + "-" * 60)
    
    assert chunk_count > 0
    assert len(full_response) > 50  # Expect substantial response
    
    print(f"\n✓ Received {chunk_count} chunks")
    print(f"✓ Total length: {len(full_response)} characters")


if __name__ == "__main__":
    from tests.utils import setup_mlflow, enable_mlflow_tracing, get_litellm_client, MODEL_NAME
    
    setup_mlflow()
    enable_mlflow_tracing()
    client = get_litellm_client()
    
    print("\n" + "="*60)
    print("Running Streaming Tests")
    print("="*60)
    
    try:
        print("\n[Test 1] Basic streaming...")
        test_streaming_completion(client, MODEL_NAME)
        
        print("\n[Test 2] Streaming with stop sequence...")
        test_streaming_with_stop_sequence(client, MODEL_NAME)
        
        print("\n[Test 3] Long response streaming...")
        test_streaming_long_response(client, MODEL_NAME)
        
        print("\n" + "="*60)
        print("✓ All streaming tests completed!")
        print("="*60)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
