"""
Media Validation Utility Module

This module contains validation functions for media files (images and videos).
"""

import logging
from typing import List
from fastapi import HTTPException, UploadFile

# Configure logging
logger = logging.getLogger(__name__)

# Constants
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/jpg', 'image/png']
ALLOWED_VIDEO_TYPES = ['video/mp4']
MAX_IMAGE_SIZE_MB = 10  # 10MB max per image
MAX_VIDEO_SIZE_MB = 50  # 50MB max for video
MB = 1024 * 1024  # 1MB in bytes

async def validate_files(files: List[UploadFile]) -> None:
    """
    Validates the uploaded files for type and size.
    
    Args:
        files: List of uploaded files
        
    Raises:
        HTTPException: If validation fails
    """
    if not files:
        raise HTTPException(status_code=400, detail="No media files provided.")
    
    # Check if we have a single video or multiple images
    if len(files) == 1 and files[0].content_type in ALLOWED_VIDEO_TYPES:
        # Video file validation
        video = files[0]
        if video.size and video.size > MAX_VIDEO_SIZE_MB * MB:
            raise HTTPException(
                status_code=413, 
                detail=f"Video file too large. Maximum size allowed is {MAX_VIDEO_SIZE_MB}MB."
            )
    elif all(f.content_type in ALLOWED_IMAGE_TYPES for f in files):
        # Image files validation
        for img in files:
            if img.size and img.size > MAX_IMAGE_SIZE_MB * MB:
                raise HTTPException(
                    status_code=413, 
                    detail=f"Image file '{img.filename}' too large. Maximum size allowed is {MAX_IMAGE_SIZE_MB}MB."
                )
    else:
        # Invalid file types
        invalid_files = [f.filename for f in files if (
            f.content_type not in ALLOWED_IMAGE_TYPES and 
            f.content_type not in ALLOWED_VIDEO_TYPES
        )]
        if invalid_files:
            raise HTTPException(
                status_code=415, 
                detail=f"Unsupported file type(s): {', '.join(invalid_files)}. Only JPG, PNG images and MP4 videos are supported."
            )
        else:
            raise HTTPException(
                status_code=400, 
                detail="Invalid file combination. Please upload one or more images (JPG, PNG) or a single video (MP4)."
            ) 