"""
Test utilities for MLflow tracing tests
"""

import os
import mlflow
from openai import OpenAI


# Test configuration
LITELLM_PROXY_URL = "http://localhost:4000"
VIRTUAL_KEY = "sk-1234"
MODEL_NAME = "gemini/gemini-2.0-flash"  # Include provider prefix
MLFLOW_TRACKING_URI = "http://localhost:5001"
TEST_EXPERIMENT_NAME = "MLflow-Tracing-Tests"


def get_litellm_client():
    """
    Create and return a configured OpenAI client pointing to LiteLLM proxy.
    
    Returns:
        OpenAI: Configured client instance
    """
    return OpenAI(
        api_key=VIRTUAL_KEY,
        base_url=LITELLM_PROXY_URL
    )


def setup_mlflow():
    """
    Configure MLflow for tracing tests.
    Sets tracking URI and experiment.
    """
    os.environ["MLFLOW_TRACKING_URI"] = MLFLOW_TRACKING_URI
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(TEST_EXPERIMENT_NAME)


def set_user_context(user_id, session_id):
    """
    Set user and session context for tracing.
    Note: This should be called within a traced function context.
    For standalone execution, metadata should be set per request.
    """
    print(f"  [User: {user_id}, Session: {session_id}]")
    # Store in environment for use in traced functions
    os.environ["MLFLOW_USER_ID"] = user_id
    os.environ["MLFLOW_SESSION_ID"] = session_id


def enable_mlflow_tracing():
    """
    Enable MLflow autologging for OpenAI/LiteLLM.
    """
    mlflow.openai.autolog()


def get_latest_trace():
    """
    Get the most recent trace from MLflow.
    
    Returns:
        dict: Trace data or None if no traces found
    """
    try:
        client = mlflow.tracking.MlflowClient()
        experiment = client.get_experiment_by_name(TEST_EXPERIMENT_NAME)
        
        if not experiment:
            return None
            
        runs = client.search_runs(
            experiment_ids=[experiment.experiment_id],
            max_results=1,
            order_by=["start_time DESC"]
        )
        
        if not runs:
            return None
            
        return runs[0]
    except Exception as e:
        print(f"Error getting trace: {e}")
        return None


def verify_trace_exists(run_id=None):
    """
    Verify that a trace was created in MLflow.
    
    Args:
        run_id: Optional run ID to check. If None, checks latest run.
        
    Returns:
        bool: True if trace exists, False otherwise
    """
    try:
        if run_id:
            client = mlflow.tracking.MlflowClient()
            run = client.get_run(run_id)
            return run is not None
        else:
            trace = get_latest_trace()
            return trace is not None
    except Exception:
        return False


def cleanup_test_experiments():
    """
    Clean up test experiments from MLflow.
    Use with caution - only for test cleanup.
    """
    try:
        client = mlflow.tracking.MlflowClient()
        experiment = client.get_experiment_by_name(TEST_EXPERIMENT_NAME)
        
        if experiment:
            # Delete all runs in the experiment
            runs = client.search_runs(experiment_ids=[experiment.experiment_id])
            for run in runs:
                client.delete_run(run.info.run_id)
                
            print(f"Cleaned up {len(runs)} test runs")
    except Exception as e:
        print(f"Error cleaning up experiments: {e}")


# User management test utilities
def create_test_user(username: str, email: str, password: str, role: str = "viewer"):
    """
    Create a test user with specified role.
    
    Args:
        username: Username for the test user
        email: Email for the test user
        password: Password for the test user
        role: Role to assign (admin, developer, viewer)
        
    Returns:
        User ID
    """
    from user_management.models import User, Role
    from user_management.database import get_db_context
    
    with get_db_context() as db:
        # Create user
        user = User(username=username, email=email)
        user.set_password(password)
        db.add(user)
        db.commit()
        
        # Assign role
        role_obj = db.query(Role).filter(Role.name == role).first()
        if role_obj:
            user.roles.append(role_obj)
            db.commit()
        
        return user.id


def get_auth_token(username: str, password: str) -> str:
    """
    Get authentication token for a user.
    
    Args:
        username: Username
        password: Password
        
    Returns:
        JWT access token
    """
    import requests
    
    response = requests.post(
        "http://localhost:8000/api/v1/auth/login",
        json={"username": username, "password": password}
    )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Authentication failed: {response.text}")


def get_authenticated_client(token: str):
    """
    Get LiteLLM client with authentication headers.
    
    Args:
        token: JWT access token
        
    Returns:
        OpenAI client with auth headers
    """
    from openai import OpenAI
    
    return OpenAI(
        api_key=VIRTUAL_KEY,
        base_url=LITELLM_PROXY_URL,
        default_headers={"Authorization": f"Bearer {token}"}
    )


def cleanup_test_users():
    """
    Clean up test users from database.
    Use with caution - only for test cleanup.
    """
    from user_management.models import User
    from user_management.database import get_db_context
    
    with get_db_context() as db:
        # Delete test users (those with test in username or email)
        test_users = db.query(User).filter(
            (User.username.like('%test%')) | (User.email.like('%test%'))
        ).all()
        
        for user in test_users:
            db.delete(user)
        
        db.commit()
        print(f"Cleaned up {len(test_users)} test users")
