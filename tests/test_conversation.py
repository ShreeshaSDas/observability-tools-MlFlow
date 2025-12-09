"""
Test multi-turn conversation with MLflow tracing
Includes user and session tracking as per MLflow documentation
"""

import pytest
import sys
import os
import mlflow

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@mlflow.trace
def test_simple_conversation(litellm_client, model_name):
    """
    Test a simple multi-turn conversation with user and session tracking.
    """
    user_id = "user_001"
    session_id = "session_conv_001"
    
    # Update trace with user and session
    mlflow.update_current_trace(
        metadata={
            "mlflow.trace.user": user_id,
            "mlflow.trace.session": session_id,
        }
    )
    
    # Start conversation
    messages = [
        {"role": "user", "content": "What is MLflow?"}
    ]
    
    
    # First turn
    response1 = litellm_client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.7,
        max_tokens=100
    )
    
    assert response1 is not None
    assistant_response = response1.choices[0].message.content
    print(f"\n✓ Turn 1 - Assistant: {assistant_response}")
    print(f"  [User: {user_id}, Session: {session_id}]")
    
    # Add assistant response to conversation
    messages.append({"role": "assistant", "content": assistant_response})
    
    # Second turn
    messages.append({"role": "user", "content": "What are its main components?"})
    
    
    response2 = litellm_client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.7,
        max_tokens=150
    )
    
    assert response2 is not None
    print(f"\n✓ Turn 2 - Assistant: {response2.choices[0].message.content}")
    print(f"  [User: {user_id}, Session: {session_id}]")
    
    # Return summary for trace
    return {"turns": 2, "final_response": response2.choices[0].message.content[:100]}


@mlflow.trace
def test_conversation_with_context(litellm_client, model_name, conversation_messages):
    """
    Test conversation with pre-existing context and user/session tracking.
    """
    user_id = "user_002"
    session_id = "session_conv_002"
    
    # Update trace with user and session
    mlflow.update_current_trace(
        metadata={
            "mlflow.trace.user": user_id,
            "mlflow.trace.session": session_id,
        }
    )
    
    response = litellm_client.chat.completions.create(
        model=model_name,
        messages=conversation_messages,
        temperature=0.7,
        max_tokens=150
    )
    
    assert response is not None
    print(f"\n✓ Response with context: {response.choices[0].message.content}")
    print(f"  [User: {user_id}, Session: {session_id}]")
    
    # Return response for trace
    return {"response": response.choices[0].message.content[:100]}


@mlflow.trace
def test_long_conversation(litellm_client, model_name):
    """
    Test a longer multi-turn conversation with session tracking.
    """
    user_id = "user_003"
    session_id = "session_conv_003"
    messages = []
    
    conversation_turns = [
        "What is observability?",
        "How does it differ from monitoring?",
        "Can you give me a specific example?"
    ]
    
    for i, user_message in enumerate(conversation_turns):
        messages.append({"role": "user", "content": user_message})
        
        # Update trace for each turn
        mlflow.update_current_trace(
            metadata={
                "mlflow.trace.user": user_id,
                "mlflow.trace.session": session_id,
                "turn_number": str(i + 1),
            }
        )
        
        response = litellm_client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=100
        )
        
        assistant_response = response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_response})
        
        print(f"\n✓ Turn {i+1}")
        print(f"  User: {user_message}")
        print(f"  Assistant: {assistant_response[:100]}...")
        print(f"  [User: {user_id}, Session: {session_id}, Turn: {i+1}]")
    
    # Verify we have all turns
    assert len(messages) == len(conversation_turns) * 2
    
    # Return summary for trace
    return {"turns": len(conversation_turns), "conversation_complete": True}


@mlflow.trace
def test_conversation_with_system_prompt(litellm_client, model_name):
    """
    Test conversation with system prompt and user/session tracking.
    """
    user_id = "user_004"
    session_id = "session_conv_004"
    
    # Update trace
    mlflow.update_current_trace(
        metadata={
            "mlflow.trace.user": user_id,
            "mlflow.trace.session": session_id,
            "has_system_prompt": "true",
        }
    )
    
    messages = [
        {"role": "system", "content": "You are a concise assistant. Answer in one sentence."},
        {"role": "user", "content": "What is MLflow?"}
    ]
    
    response = litellm_client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.7,
        max_tokens=50
    )
    
    assert response is not None
    print(f"\n✓ Concise response: {response.choices[0].message.content}")
    print(f"  [User: {user_id}, Session: {session_id}]")
    
    # Return response for trace
    return {"response": response.choices[0].message.content}


if __name__ == "__main__":
    from tests.utils import setup_mlflow, enable_mlflow_tracing, get_litellm_client, set_user_context, MODEL_NAME
    
    setup_mlflow()
    enable_mlflow_tracing()
    user_id = "user_005"
    session_id = "session_conv_005"
    client = get_litellm_client()
    set_user_context(user_id, session_id)
    conv_messages = [
        {"role": "user", "content": "What is MLflow?"},
        {"role": "assistant", "content": "MLflow is an open-source platform for managing machine learning workflows."},
        {"role": "user", "content": "What are its main components?"}
    ]
    
    print("\n" + "="*60)
    print("Running Conversation Tests")
    print("="*60)
    
    try:
        print("\n[Test 1] Simple conversation...")
        test_simple_conversation(client, MODEL_NAME)
        
        print("\n[Test 2] Conversation with context...")
        test_conversation_with_context(client, MODEL_NAME, conv_messages)
        
        print("\n[Test 3] Long conversation...")
        test_long_conversation(client, MODEL_NAME)
        
        print("\n[Test 4] Conversation with system prompt...")
        test_conversation_with_system_prompt(client, MODEL_NAME)
        
        print("\n" + "="*60)
        print("✓ All conversation tests completed!")
        print("="*60)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
