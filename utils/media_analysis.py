"""
Media Analysis Utility Module

This module handles the analysis of media files (images and videos) using OpenAI's vision model.
It delegates to specialized submodules for validation, processing, and video handling.
"""

import os
import logging
from typing import List, Dict, Optional, Any
from fastapi import HTTPException, UploadFile
from openai import OpenAIError

# Import from our utilities
from utils import openai_client
from utils.prompts import NEW_PROMPT
from utils.story_generation import (
    generate_story_from_image,
    generate_story_from_multiple_images,
    generate_story_from_video
)
from utils.media_validation import validate_files
from utils.media_processing import process_images
from utils.video_processing import extract_frames_and_analyze_video

# Configure logging
logger = logging.getLogger(__name__)

async def analyze_media(files: List[UploadFile], prompt: str) -> Dict[str, str]:
    """
    Analyzes media files using OpenAI Vision.

    Handles:
    - Single image upload
    - Multiple image uploads
    - Single video upload (metadata only)
    - Optional text prompt to guide the AI

    Returns:
    - JSON response: {"english": "...", "thai": "..."}
    - Raises HTTPException on errors.
    """
    logger.info(f"Received request for analysis. Files: {[f.filename for f in files]}, Prompt: '{prompt}'")
    
    # Validate the uploaded files
    await validate_files(files)
    
    # Ensure client is initialized or try to reinitialize if needed
    if openai_client.is_fallback_mode() or openai_client.get_client() is None:
        # Try to reinitialize the client one more time
        if not openai_client.reinitialize_client_if_needed():
            logger.warning("OpenAI client still not available or in fallback mode. Returning fallback response.")
            # Return a specific fallback response structure
            return { 
                "english": "Analysis service is currently unavailable due to configuration issues.",
                "thai": "บริการวิเคราะห์ไม่พร้อมใช้งานในขณะนี้เนื่องจากปัญหาการกำหนดค่า"
            }

    if not files:
        logger.warning("No files provided in the request to analyze_media.")
        raise HTTPException(status_code=400, detail="No media files provided.")

    # Determine if we're processing a video or images
    is_video = (len(files) == 1 and files[0].content_type and 
                files[0].content_type.startswith('video/'))

    try:
        if is_video:
            # Process video file
            video_file = files[0]
            logger.info(f"Detected video file: {video_file.filename}")
            result = await process_video(video_file, prompt)
        else:
            # Process image files
            logger.info(f"Detected {len(files)} image file(s).")
            result = await process_images(files, prompt)
            
        logger.info(f"Successfully generated analysis for: {[f.filename for f in files]}")
        return result
    
    except OpenAIError as e:
        logger.error(f"OpenAI API error during analysis: {e}")
        detail = f"OpenAI API Error: {e.message}" if hasattr(e, 'message') else str(e)
        status_code = e.status_code if hasattr(e, 'status_code') else 503
        raise HTTPException(status_code=status_code, detail=detail)
    except Exception as e:
        logger.exception("An unexpected error occurred during analysis function execution.")
        # Ensure any remaining open files are closed
        for f in files: 
            try:
                await f.close()
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during analysis: {str(e)}")

async def process_video(video_file: UploadFile, prompt: str) -> Dict[str, str]:
    """
    Process a video file by saving it to a temporary location and analyzing it.
    
    Args:
        video_file: The uploaded video file
        prompt: The analysis prompt
        
    Returns:
        Analysis results as a dictionary
    """
    import tempfile
    
    # Save video file to temporary location
    temp_file_path = None
    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{video_file.filename.split('.')[-1]}") as temp_file:
            temp_file_path = temp_file.name
            contents = await video_file.read()
            temp_file.write(contents)
        
        # Create video details dictionary
        video_details = {
            "filename": video_file.filename or "unknown_video",
            "mimetype": video_file.content_type,
            "size": video_file.size or 0,
            "duration": "Unknown", 
            "thumbnailBase64": None,
            "file_path": temp_file_path  # Store path for frame extraction
        }
        
        # Extract frames and analyze the video
        result = extract_frames_and_analyze_video(video_details, prompt)
        return result
    
    finally:
        # Reset file position for potential future reads
        await video_file.seek(0)
        # Delete temp file when done (if it exists)
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path) 