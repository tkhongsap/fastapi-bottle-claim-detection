"""
Utilities Package

This package contains utility modules for the FastAPI ImgStory application.
"""

# Expose key utility functions for easier imports
from utils.media_validation import validate_files
from utils.media_processing import process_images
from utils.video_processing import extract_frames_and_analyze_video
from utils.openai_client import get_client, get_active_model, is_fallback_mode 