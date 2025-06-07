"""
OpenAI Client Initialization Utility

This module handles the initialization and management of the OpenAI client,
including API key validation, model selection, and error handling.
"""

import os
import logging
from typing import Optional, Tuple
from pathlib import Path
from openai import OpenAI, OpenAIError, APIStatusError, APIConnectionError, AuthenticationError, AzureOpenAI

# Configure logging
logger = logging.getLogger(__name__)

# Model selection
VISION_MODEL = "gpt-4.1"
DATE_EXTRACTION_MODEL = os.getenv("DATE_EXTRACTION_MODEL")
FALLBACK_VISION_MODEL = os.getenv("FALLBACK_VISION_MODEL") # Fallback if preferred is unavailable
api_version = "2025-03-01-preview"
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
# Global client variable and state tracking
client: Optional[AzureOpenAI] = None
active_vision_model = VISION_MODEL
using_fallback_mode = False

def initialize_openai_client() -> Tuple[Optional[AzureOpenAI], str, bool]:
    """
    Initialize and validate the OpenAI client with proper error handling.
    
    Returns:
        Tuple containing:
        - OpenAI client (or None if initialization failed)
        - Active vision model being used
        - Boolean indicating if we're in fallback mode
    """
    global client, active_vision_model, using_fallback_mode
    
    API_KEY = os.getenv("AZURE_OPENAI_API_KEY")

    if not API_KEY:
        logger.error("❌ OPENAI_API_KEY environment variable is not set. Falling back.")
        using_fallback_mode = True
        return None, active_vision_model, True

    key_preview = f"{API_KEY[:7]}...{API_KEY[-4:]}"
    is_project_based_key = API_KEY.startswith("sk-proj-")
    logger.info(f"OpenAI API key detected: {key_preview} ({'project-based' if is_project_based_key else 'standard'})")

    try:
        client = AzureOpenAI(
            api_key=API_KEY,
            api_version=api_version,
            azure_endpoint=endpoint
        )

        # Test API key with a simple call
        logger.info(f"Attempting to validate API key and check model: {VISION_MODEL}")
        # Using a simple, low-cost call for validation
        client.models.retrieve(VISION_MODEL) 
        logger.info(f"✅ OpenAI API key validated successfully. Using vision model: {VISION_MODEL}")
        active_vision_model = VISION_MODEL
        using_fallback_mode = False

    except AuthenticationError as e:
        logger.error(f"❌ AUTHENTICATION ERROR: Invalid OpenAI API key or insufficient permissions. Status: {e.status_code}. Message: {e.message}")
        if is_project_based_key:
            logger.error("Project-based keys (sk-proj-*) may have limited permissions. Check model access in your OpenAI project settings.")
        else:
            logger.error("Verify your API key at https://platform.openai.com/account/api-keys")
        client = None
        using_fallback_mode = True
    except APIStatusError as e:
        # Handle cases like model not found or other API errors during validation
        logger.error(f"❌ API ERROR during validation: Status {e.status_code}. Message: {e.message}")
        if e.code == 'model_not_found':
            logger.warning(f"Model '{VISION_MODEL}' not found or not accessible with this key. Trying fallback '{FALLBACK_VISION_MODEL}'.")
            try:
                client.models.retrieve(FALLBACK_VISION_MODEL)
                logger.info(f"✅ Fallback model '{FALLBACK_VISION_MODEL}' validated. Using fallback.")
                active_vision_model = FALLBACK_VISION_MODEL
                using_fallback_mode = False
            except Exception as fallback_e:
                logger.error(f"❌ Fallback model '{FALLBACK_VISION_MODEL}' also failed validation: {fallback_e}. Enabling fallback mode.")
                client = None
                using_fallback_mode = True
        else:
             client = None
             using_fallback_mode = True  # Fallback for other API errors
    except APIConnectionError as e:
        logger.error(f"❌ CONNECTION ERROR: Could not connect to OpenAI API. {e}")
        client = None
        using_fallback_mode = True
    except Exception as e:
        logger.error(f"❌ An unexpected error occurred during OpenAI client initialization: {e}")
        client = None
        using_fallback_mode = True

    return client, active_vision_model, using_fallback_mode

def get_client() -> Optional[AzureOpenAI]:
    """
    Get the current OpenAI client instance.
    
    Returns:
        The OpenAI client or None if not initialized
    """
    return client

def get_active_model() -> str:
    """
    Get the current active vision model.
    
    Returns:
        The active vision model name
    """
    return active_vision_model

def get_date_extraction_model() -> str:
    """
    Get the model used for date extraction.
    
    Returns:
        The date extraction model name
    """
    active_vision_model = DATE_EXTRACTION_MODEL
    return active_vision_model # Placeholder for actual date extraction model

def is_fallback_mode() -> bool:
    """
    Check if the client is in fallback mode.
    
    Returns:
        True if in fallback mode, False otherwise
    """
    return using_fallback_mode

def reinitialize_client_if_needed() -> bool:
    """
    Re-initialize the OpenAI client if it's None or in fallback mode.
    
    Returns:
        True if reinitialization was attempted, False otherwise
    """
    global client, using_fallback_mode, active_vision_model
    
    if client is None or using_fallback_mode:
        logger.info("Attempting to reinitialize OpenAI client...")
        client, active_vision_model, using_fallback_mode = initialize_openai_client()
        return True
    return False

def cleanup_client():
    """Clean up the OpenAI client resources"""
    global client
    # Note: OpenAI client doesn't have a close/cleanup method as of now
    # but we can set it to None to help with garbage collection
    client = None 