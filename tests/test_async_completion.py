"""
Test async completion with MLflow tracing
"""

import pytest
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from openai import AsyncOpenAI
from tests.utils import LITELLM_PROXY_URL, VIRTUAL_KEY


@pytest.fixture
def async_client():
    """Fixture for async OpenAI client"""
    return AsyncOpenAI(
        api_key=VIRTUAL_KEY,
        base_url=LITELLM_PROXY_URL
    )


@pytest.mark.asyncio
async def test_async_completion(async_client, model_name):
    """
    Test async completion.
    """
    messages = [{"role": "user", "content": "Say hello asynchronously!"}]
    
    response = await async_client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.7,
        max_tokens=50
    )
    
    assert response is not None
    assert response.choices[0].message.content is not None
    
    print(f"\n✓ Async response: {response.choices[0].message.content}")


@pytest.mark.asyncio
async def test_concurrent_async_requests(async_client, model_name):
    """
    Test multiple concurrent async requests.
    """
    messages_list = [
        [{"role": "user", "content": f"What is {i} + {i}?"}]
        for i in range(1, 4)
    ]
    
    # Create tasks for concurrent execution
    tasks = [
        async_client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=30
        )
        for messages in messages_list
    ]
    
    # Execute concurrently
    responses = await asyncio.gather(*tasks)
    
    # Verify all responses
    assert len(responses) == 3
    for i, response in enumerate(responses):
        assert response is not None
        print(f"\n✓ Response {i+1}: {response.choices[0].message.content}")


@pytest.mark.asyncio
async def test_async_streaming(async_client, model_name):
    """
    Test async streaming completion.
    """
    messages = [{"role": "user", "content": "Count from 1 to 3."}]
    
    stream = await async_client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.7,
        max_tokens=50,
        stream=True
    )
    
    full_response = ""
    chunk_count = 0
    
    print("\n✓ Async streaming:")
    async for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            print(content, end="", flush=True)
            full_response += content
            chunk_count += 1
    
    print()
    
    assert chunk_count > 0
    assert len(full_response) > 0
    
    print(f"\n✓ Received {chunk_count} chunks asynchronously")


if __name__ == "__main__":
    from tests.utils import setup_mlflow, enable_mlflow_tracing, LITELLM_PROXY_URL, VIRTUAL_KEY, MODEL_NAME
    from openai import AsyncOpenAI
    
    setup_mlflow()
    enable_mlflow_tracing()
    
    async def run_all_tests():
        async_client = AsyncOpenAI(
            api_key=VIRTUAL_KEY,
            base_url=LITELLM_PROXY_URL
        )
        
        print("\n" + "="*60)
        print("Running Async Completion Tests")
        print("="*60)
        
        try:
            print("\n[Test 1] Async completion...")
            await test_async_completion(async_client, MODEL_NAME)
            
            print("\n[Test 2] Concurrent async requests...")
            await test_concurrent_async_requests(async_client, MODEL_NAME)
            
            print("\n[Test 3] Async streaming...")
            await test_async_streaming(async_client, MODEL_NAME)
            
            print("\n" + "="*60)
            print("✓ All async tests completed!")
            print("="*60)
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
    
    asyncio.run(run_all_tests())
