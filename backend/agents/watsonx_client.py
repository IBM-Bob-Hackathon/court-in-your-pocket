"""
IBM watsonx Client Configuration
Centralized configuration for IBM watsonx.ai integration.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# IBM watsonx Configuration
WATSONX_API_KEY = os.getenv("IBM_WATSONX_API_KEY")
WATSONX_PROJECT_ID = os.getenv("IBM_WATSONX_PROJECT_ID")
WATSONX_URL = os.getenv("IBM_WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

# Model Configuration
DEFAULT_MODEL_ID = "meta-llama/llama-3-3-70b-instruct"
DEFAULT_MAX_TOKENS = 500
DEFAULT_TEMPERATURE = 0.7


class WatsonxClientError(Exception):
    """Custom exception for watsonx client errors"""
    pass


def get_watsonx_client():
    """
    Initialize and return IBM watsonx client.
    
    Returns:
        Configured watsonx client instance
    
    Raises:
        WatsonxClientError: If credentials are missing or invalid
    """
    try:
        from ibm_watsonx_ai import APIClient
        from ibm_watsonx_ai import Credentials
        
        # Validate credentials
        if not WATSONX_API_KEY:
            raise WatsonxClientError(
                "WATSONX_API_KEY not found in environment variables. "
                "Please set it in your .env file."
            )
        
        if not WATSONX_PROJECT_ID:
            raise WatsonxClientError(
                "WATSONX_PROJECT_ID not found in environment variables. "
                "Please set it in your .env file."
            )
        
        # Create credentials
        credentials = Credentials(
            api_key=WATSONX_API_KEY,
            url=WATSONX_URL
        )
        
        # Initialize client
        client = APIClient(credentials)
        
        return client
    
    except ImportError:
        raise WatsonxClientError(
            "ibm-watsonx-ai package not installed. "
            "Run: pip install ibm-watsonx-ai"
        )
    except Exception as e:
        raise WatsonxClientError(f"Failed to initialize watsonx client: {str(e)}")


def get_model_parameters(
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    top_k: Optional[int] = None
) -> dict:
    """
    Get model generation parameters.
    
    Args:
        max_tokens: Maximum tokens to generate (default: 500)
        temperature: Sampling temperature 0-1 (default: 0.7)
        top_p: Nucleus sampling parameter (default: 1.0)
        top_k: Top-k sampling parameter (default: 50)
    
    Returns:
        Dictionary of model parameters
    """
    return {
        "max_new_tokens": max_tokens or DEFAULT_MAX_TOKENS,
        "temperature": temperature or DEFAULT_TEMPERATURE,
        "top_p": top_p or 1.0,
        "top_k": top_k or 50,
        "repetition_penalty": 1.1
    }


def generate_text(
    client,
    prompt: str,
    model_id: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None
) -> str:
    """
    Generate text using IBM watsonx.
    
    Args:
        client: Initialized watsonx client
        prompt: Input prompt text
        model_id: Model identifier (default: granite-13b-chat-v2)
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature
    
    Returns:
        Generated text response
    
    Raises:
        WatsonxClientError: If generation fails
    """
    try:
        from ibm_watsonx_ai.foundation_models import ModelInference
        
        # Initialize model
        model = ModelInference(
            model_id=model_id or DEFAULT_MODEL_ID,
            api_client=client,
            project_id=WATSONX_PROJECT_ID,
            params=get_model_parameters(max_tokens, temperature)
        )
        
        # Generate response
        response = model.generate_text(prompt=prompt)

        return str(response).strip()
    
    except Exception as e:
        raise WatsonxClientError(f"Text generation failed: {str(e)}")


def test_connection() -> dict:
    """
    Test watsonx connection and credentials.
    
    Returns:
        Dictionary with connection status and details
    """
    try:
        client = get_watsonx_client()
        
        # Try a simple generation to verify everything works
        test_prompt = "Hello, this is a connection test."
        response = generate_text(
            client=client,
            prompt=test_prompt,
            max_tokens=10,
            temperature=0.1
        )
        
        return {
            "status": "success",
            "message": "Successfully connected to IBM watsonx",
            "project_id": WATSONX_PROJECT_ID,
            "url": WATSONX_URL,
            "test_response": response[:50] + "..." if len(response) > 50 else response
        }
    
    except WatsonxClientError as e:
        return {
            "status": "error",
            "message": str(e),
            "project_id": WATSONX_PROJECT_ID,
            "url": WATSONX_URL
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "project_id": WATSONX_PROJECT_ID,
            "url": WATSONX_URL
        }


# Singleton client instance (lazy initialization)
_client_instance: Optional[object] = None


def get_client_instance():
    """
    Get or create singleton watsonx client instance.
    
    Returns:
        Cached watsonx client instance
    """
    global _client_instance
    
    if _client_instance is None:
        _client_instance = get_watsonx_client()
    
    return _client_instance

# Made with Bob
