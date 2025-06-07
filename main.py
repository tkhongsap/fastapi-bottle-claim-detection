import os
import base64
import json
import re
import logging
import aiofiles
import pathlib # Import pathlib
import tempfile
import cv2 # For extracting frames from videos
import numpy as np
import subprocess
import ffmpeg # FFmpeg Python bindings for enhanced video processing
from typing import List, Dict, Optional, Any
import shutil
import pprint

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError, APIStatusError, APIConnectionError, AuthenticationError

# Import OpenAI client utilities
from utils.prompts import NEW_PROMPT
from utils import openai_client
# Updated imports for the refactored modules
from utils.media_analysis import analyze_media
from utils.video_processing import extract_frames_and_analyze_video, analyze_frames
from utils.story_generation import (
    generate_story_from_image,
    generate_story_from_multiple_images, 
    generate_story_from_video,
    parse_openai_response
)
# Import date verification modules
from utils.date_extraction import extract_date_from_image
from utils.date_verification import verify_production_date, format_verification_response
from utils.cost_utils import get_model_cost, USD_TO_THB_RATE

# --- Configuration & Setup --- 

# Get the directory where main.py is located
SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
# Construct the path to the .env file
DOTENV_PATH = SCRIPT_DIR / ".env"

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file in the script's directory
# Use override=True to ensure .env takes precedence over system variables
try:
    if DOTENV_PATH.is_file():
        logger.info(f"Loading environment variables from: {DOTENV_PATH}")
        load_dotenv(dotenv_path=DOTENV_PATH, override=True)
    else:
        logger.warning(f".env file not found at {DOTENV_PATH}. Relying on system environment variables.")
        load_dotenv(override=True) # Attempt to load from default locations or just use system vars
except Exception as e:
    logger.error(f"Error loading environment variables: {e}")
    # Continue execution, but log the error

# Create uploads directory if it doesn't exist
UPLOAD_DIR = SCRIPT_DIR / "uploads"
try:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
except Exception as e:
    logger.error(f"Error creating upload directory: {e}")
    # This is a critical error, but we'll continue and let it fail when accessed

# --- FastAPI App Setup --- 
app = FastAPI(title="Media Analysis Story Generator API")

# CORS Configuration (Allow frontend origin)
# Adjust origins as needed for deployment
origins = [
    "http://localhost",
    "http://localhost:8000", # Default FastAPI dev server
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    # Add other origins if needed, e.g., deployed frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"]
)

# Mount static files (CSS, JS)
try:
    app.mount("/static", StaticFiles(directory=SCRIPT_DIR / "static"), name="static")
except Exception as e:
    logger.error(f"Error mounting static files: {e}")
    # This is a warning, but we'll continue as API endpoints may still work

# Dynamically determine cost based on model
active_model = openai_client.get_active_model()
model_cost = get_model_cost(active_model)
INPUT_COST_USD_PER_MILLION = model_cost["input"]
OUTPUT_COST_USD_PER_MILLION = model_cost["output"]

# --- FastAPI Lifecycle Events ---

@app.on_event("startup")
async def startup_event():
    """Initialize resources on application startup"""
    logger.info("Application starting up, initializing OpenAI client...")
    try:
        openai_client.initialize_openai_client()
    except Exception as e:
        logger.error(f"Error initializing OpenAI client: {e}")
        # The application will continue but may not work correctly

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on application shutdown"""
    logger.info("Application shutting down, cleaning up resources...")
    try:
        openai_client.cleanup_client()
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

# --- API Endpoints --- 

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serves the main HTML page."""
    index_html_path = SCRIPT_DIR / "static" / "index.html"
    if not index_html_path.is_file():
        logger.error(f"Frontend HTML file not found at: {index_html_path}")
        raise HTTPException(status_code=500, detail="Internal server error: Frontend not found.")
    try:
        async with aiofiles.open(index_html_path, mode='r', encoding='utf-8') as f:
            content = await f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        logger.exception(f"Error reading frontend HTML file: {e}")
        raise HTTPException(status_code=500, detail="Internal server error: Could not load frontend.")
    
@app.get('/document')
async def getDocument():
    index_html_path = SCRIPT_DIR / "static" / "docs.html"
    if not index_html_path.is_file():
        logger.error(f"Frontend HTML file not found at: {index_html_path}")
        raise HTTPException(status_code=500, detail="Internal server error: Frontend not found.")
    try:
        async with aiofiles.open(index_html_path, mode='r') as f:
            content = await f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        logger.exception(f"Error reading frontend HTML file: {e}")
        raise HTTPException(status_code=500, detail="Internal server error: Could not load frontend.")

@app.get("/manual", response_class=HTMLResponse)
async def read_manual(request: Request):
    """Serves the user manual page."""
    manual_html_path = SCRIPT_DIR / "static" / "manual.html"
    if not manual_html_path.is_file():
        logger.error(f"Manual HTML file not found at: {manual_html_path}")
        raise HTTPException(status_code=404, detail="User manual not found.")
    try:
        async with aiofiles.open(manual_html_path, mode='r', encoding='utf-8') as f:
            content = await f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        logger.exception(f"Error reading manual HTML file: {e}")
        raise HTTPException(status_code=500, detail="Internal server error: Could not load user manual.")

@app.post("/verify-date/")
async def verify_date_endpoint(
    file: UploadFile = File(..., description="Image file of bottle label showing production date")
):
    """
    Endpoint to verify if a Chang beer bottle is eligible for claims based on its production date.
    
    First extracts the production date from the bottle label image, then verifies if it's within
    the 120-day eligibility window.
    """
    try:
        # Validate file type (only accept images)
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=415, 
                detail="Unsupported file type. Please upload an image file (JPG, PNG)."
            )
        
        # Extract production date from the image
        extraction_result = await extract_date_from_image(file)
        
        # Check if extraction was successful
        if extraction_result["status"] == "ERROR":
            return JSONResponse(
                content={
                    "english": {
                        "status": "ERROR",
                        "message": extraction_result["error"]
                    },
                    "thai": {
                        "status": "ข้อผิดพลาด",
                        "message": f"เกิดข้อผิดพลาดในการดึงข้อมูลวันที่ผลิต: {extraction_result['error']}"
                    },
                    "token_usage": extraction_result["token_usage"]
                }
            )
        
        # Verify the production date
        verification_result = verify_production_date(extraction_result["production_date"])

        logger.info(f"Verification result: {verification_result}")
        
        # Format the response
        response_data = format_verification_response(verification_result)
        
        # Add token usage information to the response
        response_data["token_usage"] = extraction_result["token_usage"]

        logger.info(f"response data: {response_data}")

        # Calculate cost in THB
        input_tokens = extraction_result["token_usage"]["input_tokens"]
        output_tokens = extraction_result["token_usage"]["output_tokens"]
        input_cost_thb = input_tokens * INPUT_COST_USD_PER_MILLION * USD_TO_THB_RATE / 1000000
        output_cost_thb = output_tokens * OUTPUT_COST_USD_PER_MILLION * USD_TO_THB_RATE / 1000000

        response_data["input_cost_thb"] = input_cost_thb
        response_data["output_cost_thb"] = output_cost_thb

        logger.info(f"response data final: {response_data}")

        
        return JSONResponse(content=response_data)
    
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except OpenAIError as e:
        # Handle OpenAI API errors
        logger.error(f"OpenAI API error in date verification endpoint: {e}")
        detail = f"OpenAI API Error: {e.message}" if hasattr(e, 'message') else str(e)
        status_code = e.status_code if hasattr(e, 'status_code') else 503
        raise HTTPException(status_code=status_code, detail=detail)
    except Exception as e:
        # Handle unexpected errors
        logger.exception("An unexpected error occurred in the /verify-date endpoint.")
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {str(e)}")
    finally:
        # Reset file position
        await file.seek(0)

@app.post("/claimability/")
async def analyze_media_endpoint(
    files: List[UploadFile] = File(..., description="Media files (JPG, PNG images or MP4 video)"),
    prompt: Optional[str] = Form(None), # Make prompt optional
    date_verification = Form(None, description="Optional date verification result")
):
    """
    Endpoint to receive media files and an optional prompt for analysis.
    Supports JPG, PNG images (multiple allowed) or a single MP4 video.
    Maximum file size: 10MB per image, 50MB for video.
    
    If date_verification is provided and shows the bottle is ineligible,
    the damage assessment will be skipped.
    
    Delegates the core logic to the analyze_media function.
    """
    try:
        # Check if date verification was provided and bottle is ineligible
        if date_verification and isinstance(date_verification, dict):
            # Parse the date_verification if it was sent as a JSON string
            if isinstance(date_verification, str):
                try:
                    date_verification = json.loads(date_verification)
                except json.JSONDecodeError:
                    logger.error("Invalid JSON in date_verification parameter")
                    date_verification = None
            
            # Check eligibility status
            status = (date_verification.get("english", {}) or {}).get("status")
            if status == "INELIGIBLE":
                # Return early with ineligibility message
                return JSONResponse(content={
                    "english": "This bottle is not eligible for claim assessment as it exceeds the 120-day production limit.",
                    "thai": "ขวดนี้ไม่มีสิทธิ์ได้รับการประเมินการเคลมเนื่องจากเกินกำหนด 120 วันหลังจากวันผลิต",
                    "date_verification": date_verification
                })
        
        # Pass empty string if prompt is None
        result = await analyze_media(files=files, prompt=NEW_PROMPT) 

        logger.info(f"result: {result}")

        # --- Convert date_verification from string to dict if needed ---
        if date_verification:
            if isinstance(date_verification, str):
                try:
                    date_verification = json.loads(date_verification)
                except json.JSONDecodeError:
                    logger.error("Invalid JSON in date_verification parameter")
                    raise HTTPException(status_code=400, detail="Invalid JSON format for date_verification")

        
        # If we have date verification, include it in the response
        if date_verification:
            result["date_verification"] = date_verification

        input_tokens_damage = result.get("input_tokens", 0)
        output_tokens_damage = result.get("output_tokens", 0)

        input_tokens_date = date_verification.get("token_usage", {}).get("input_tokens", 0) if date_verification else 0
        output_tokens_date = date_verification.get("token_usage", {}).get("output_tokens", 0) if date_verification else 0

        total_input_tokens = input_tokens_damage + input_tokens_date
        total_output_tokens = output_tokens_damage + output_tokens_date

        total_input_cost_thb = total_input_tokens * INPUT_COST_USD_PER_MILLION * USD_TO_THB_RATE / 1_000_000
        total_output_cost_thb = total_output_tokens * OUTPUT_COST_USD_PER_MILLION * USD_TO_THB_RATE / 1_000_000
        total_cost_thb = total_input_cost_thb + total_output_cost_thb
        total_cost_usd = total_cost_thb / USD_TO_THB_RATE

        # Add combined result back
        result["total_input_tokens"] = total_input_tokens
        result["total_output_tokens"] = total_output_tokens
        result["total_cost_thb"] = total_cost_thb
        result["total_cost_usd"] = total_cost_usd


        logger.info(f"result final: {result}")


        return JSONResponse(content=result)
    
    except HTTPException as e:
        # Re-raise known HTTP exceptions from analyze_media
        raise e
    except OpenAIError as e:
        # Handle OpenAI errors specifically if they bubble up unexpectedly
        logger.error(f"OpenAI API error in endpoint: {e}")
        detail = f"OpenAI API Error: {e.message}" if hasattr(e, 'message') else str(e)
        status_code = e.status_code if hasattr(e, 'status_code') else 503
        raise HTTPException(status_code=status_code, detail=detail)
    except Exception as e:
        # Catch any other unexpected errors during endpoint processing
        logger.exception("An unexpected error occurred in the /analyze endpoint.")
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server...")
    try:
        # Use reload=True for development
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        logger.error(f"Failed to start server: {e}") 