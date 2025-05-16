"""
Date Extraction Utility Module

This module handles the extraction of production dates from Chang beer bottle labels
using OpenAI's vision model.
"""

import logging
import base64
from typing import Dict, Any, Optional, List
from fastapi import UploadFile, HTTPException
from openai import OpenAIError, APIStatusError

# Import from our utilities
from utils import openai_client
from utils.prompts import DATE_EXTRACTION_PROMPT
from utils.media_validation import validate_files

# Configure logging
logger = logging.getLogger(__name__)

async def extract_date_from_image(file: UploadFile) -> Dict[str, Any]:
    """
    Extracts the production date from an image of a Chang beer bottle label.
    
    Args:
        file: The uploaded image file containing the bottle label with production date
        
    Returns:
        Dictionary containing:
        - status: "SUCCESS" or "ERROR"
        - production_date: Extracted date in YYYY-MM-DD format or None
        - error: Error message if status is "ERROR"
        - token_usage: Token usage information
    """
    # Ensure client is properly initialized
    client = openai_client.get_client()
    if client is None:
        logger.error("OpenAI client is not initialized")
        return {
            "status": "ERROR",
            "production_date": None,
            "error": "OpenAI client is not available",
            "token_usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
        }

    try:
        # Reset file position and read content
        await file.seek(0)
        contents = await file.read()
        base64_image = base64.b64encode(contents).decode('utf-8')
        
        # Create input with the image and prompt for responses API
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": DATE_EXTRACTION_PROMPT
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{file.content_type};base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        
        # Call OpenAI API using responses endpoint
        logger.info(f"Sending request to OpenAI for date extraction from: {file.filename}")
        
        # Using the responses API instead of chat completions
        response = client.chat.completions.create(
            model=openai_client.get_date_extraction_model(),  # Use the date extraction model from client
            messages=messages,
            max_completion_tokens=300,
        )
        
        # Extract the response text
        response_text = response.choices[0].message.content.strip()
        logger.info(f"Date extraction response: {response_text}")
        
        # Check if a date was found
        if response_text.lower() == "no production date visible":
            logger.warning(f"No production date found in image: {file.filename}")
            return {
                "status": "ERROR",
                "production_date": None,
                "error": "No production date visible on the bottle label",
                "token_usage": {
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
        
        # Return the extracted date
        return {
            "status": "SUCCESS",
            "production_date": response_text,
            "error": None,
            "token_usage": {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
    
    except OpenAIError as e:
        logger.error(f"OpenAI API error during date extraction: {e}")
        detail = f"OpenAI API Error: {e.message}" if hasattr(e, 'message') else str(e)
        status_code = e.status_code if hasattr(e, 'status_code') else 503
        
        return {
            "status": "ERROR",
            "production_date": None,
            "error": detail,
            "token_usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
        }
    
    except Exception as e:
        logger.exception(f"Unexpected error during date extraction: {e}")
        
        return {
            "status": "ERROR",
            "production_date": None,
            "error": f"Unexpected error: {str(e)}",
            "token_usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
        }
    
    finally:
        # Reset file position for potential future reads
        await file.seek(0) 