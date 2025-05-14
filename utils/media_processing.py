"""
Media Processing Utility Module

This module handles the processing of image files for analysis.
"""

import base64
import logging
from typing import List, Dict
from fastapi import UploadFile

# Import from our utilities
from utils.prompts import NEW_PROMPT
from utils.story_generation import (
    generate_story_from_image,
    generate_story_from_multiple_images
)

# Configure logging
logger = logging.getLogger(__name__)

async def process_images(files: List[UploadFile], prompt: str) -> Dict[str, str]:
    """
    Process image files by converting them to base64 and analyzing with OpenAI.
    
    Args:
        files: The uploaded image files
        prompt: The analysis prompt
        
    Returns:
        Analysis results as a dictionary
    """
    # Process images (read, encode, close) just before the API call
    base64_images = []
    try:
        for img_file in files:
            try:
                contents = await img_file.read()
                base64_image = base64.b64encode(contents).decode('utf-8')
                base64_images.append(base64_image)
            finally:
                await img_file.close()  # Ensure file is closed even if encoding fails
        
        # Call the appropriate story generation function based on number of images
        if len(base64_images) == 1:
            result = generate_story_from_image(base64_images[0], prompt)
        else:
            result = generate_story_from_multiple_images(base64_images, prompt)
            
        return result
        
    except Exception as e:
        logger.error(f"Error in process_images function: {e}")
        # Ensure files are closed in case of error
        for img_file in files:
            try:
                await img_file.close()
            except Exception:
                pass
        raise  # Re-raise the exception to be handled by the calling function 