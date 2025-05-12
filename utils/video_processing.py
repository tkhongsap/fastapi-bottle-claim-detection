"""
Video Processing Utility Module

This module handles the extraction of frames from videos and their analysis.
"""

import os
import base64
import tempfile
import cv2
import ffmpeg
import shutil
import logging
from typing import List, Dict, Any

# Import from our utilities
from utils.prompts import NEW_PROMPT
from utils.story_generation import (
    generate_story_from_multiple_images,
    generate_story_from_video
)

# Configure logging
logger = logging.getLogger(__name__)

def extract_frames_and_analyze_video(video_details: Dict[str, Any], user_prompt: str) -> Dict[str, str]:
    """
    Extract frames from video, analyze them and generate a story.
    
    Args:
        video_details: Dictionary containing video details
        user_prompt: Optional user prompt to guide the story generation
        
    Returns:
        Dict with video details, story, and other metadata
    """
    temp_dir = tempfile.mkdtemp()
    logger.info(f"Processing video: {video_details.get('filename')}")
    
    # Extract more detailed metadata using FFmpeg before attempting frame extraction
    try:
        probe = ffmpeg.probe(video_details.get('file_path'))
        # Extract video stream info
        video_stream = next((stream for stream in probe['streams'] 
                           if stream['codec_type'] == 'video'), None)
        
        if video_stream:
            # Update video details with more accurate information
            video_details['width'] = int(video_stream.get('width', 0))
            video_details['height'] = int(video_stream.get('height', 0))
            video_details['frame_rate'] = eval(video_stream.get('r_frame_rate', '0/1'))
            
            # Calculate duration more accurately
            if 'duration' in video_stream:
                duration_sec = float(video_stream['duration'])
                video_details['duration'] = f"{int(duration_sec // 60)}:{int(duration_sec % 60):02d}"
                video_details['duration_seconds'] = duration_sec
            
            # Get total frames if available
            if 'nb_frames' in video_stream:
                video_details['total_frames'] = int(video_stream['nb_frames'])
            
        # Check for audio streams
        audio_stream = next((stream for stream in probe['streams'] 
                           if stream['codec_type'] == 'audio'), None)
        video_details['has_audio'] = audio_stream is not None
        if audio_stream:
            video_details['audio_codec'] = audio_stream.get('codec_name', 'unknown')
            
    except Exception as e:
        logger.warning(f"Failed to extract detailed metadata with FFmpeg: {e}")
    
    frames = extract_frames_opencv(video_details)
    
    # If OpenCV failed to extract any frames, try with FFmpeg as fallback
    if not frames:
        frames = extract_frames_ffmpeg(video_details, temp_dir)
    
    # If we have frames, convert them to base64 and analyze
    frame_images = []
    if frames:
        try:
            for frame in frames:
                # Convert to base64
                success, encoded_img = cv2.imencode('.jpg', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                if success:
                    img_base64 = base64.b64encode(encoded_img).decode('utf-8')
                    frame_images.append(img_base64)
            
            video_details['frame_count'] = len(frame_images)
            result = analyze_frames(frame_images, video_details, user_prompt)
            
            # Clean up temporary files
            shutil.rmtree(temp_dir, ignore_errors=True)
            return result
            
        except Exception as e:
            logger.error(f"Error processing frames: {e}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            # Fall through to metadata-only analysis
    
    # If we couldn't extract any frames, generate a story based on metadata only
    logger.warning("No frames could be extracted. Falling back to metadata-only analysis.")
    shutil.rmtree(temp_dir, ignore_errors=True)
    result = video_details.copy()
    story_result = generate_story_from_video(video_details, user_prompt)
    result.update(story_result)
    return result

def extract_frames_opencv(video_details: Dict[str, Any]) -> List[Any]:
    """
    Extract frames from a video using OpenCV.
    
    Args:
        video_details: Dictionary containing video metadata
        
    Returns:
        List of extracted frames (empty if extraction failed)
    """
    frames = []
    try:
        cap = cv2.VideoCapture(video_details.get('file_path'))
        if not cap.isOpened():
            raise Exception("Failed to open video file with OpenCV")
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
        # Update video_details with OpenCV values if we have them
        if fps > 0:
            video_details['frame_rate'] = fps
        if frame_count > 0:
            video_details['total_frames'] = frame_count
        if duration > 0:
            video_details['duration_seconds'] = duration
            video_details['duration'] = f"{int(duration // 60)}:{int(duration % 60):02d}"
        
        # Extract frames - aim for 10 evenly spaced frames
        if frame_count > 0:
            target_frames = min(10, frame_count)
            frame_indices = [int(i * frame_count / target_frames) for i in range(target_frames)]
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if ret:
                    # Convert from BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(frame_rgb)
                    
        cap.release()
        logger.info(f"Successfully extracted {len(frames)} frames with OpenCV")
        
    except Exception as e:
        logger.warning(f"Failed to extract frames with OpenCV: {e}")
    
    return frames

def extract_frames_ffmpeg(video_details: Dict[str, Any], temp_dir: str) -> List[Any]:
    """
    Extract frames from a video using FFmpeg as a fallback method.
    
    Args:
        video_details: Dictionary containing video metadata
        temp_dir: Temporary directory to store extracted frames
        
    Returns:
        List of extracted frames (empty if extraction failed)
    """
    frames = []
    logger.info("Falling back to FFmpeg for frame extraction")
    try:
        # Create output directory for frames
        frame_files = []
        
        # Calculate timestamps for 10 evenly distributed frames
        if 'duration_seconds' in video_details and video_details['duration_seconds'] > 0:
            duration_sec = video_details['duration_seconds']
            timestamps = [i * duration_sec / 10 for i in range(10)]
            
            for i, timestamp in enumerate(timestamps):
                out_file = os.path.join(temp_dir, f"frame_{i:03d}.jpg")
                ffmpeg.input(video_details.get('file_path'), ss=timestamp).output(
                    out_file, vframes=1, format='image2', vcodec='mjpeg'
                ).overwrite_output().run(quiet=True, capture_stdout=True, capture_stderr=True)
                
                frame_files.append(out_file)
                
            # Read the extracted frames
            for frame_file in frame_files:
                if os.path.exists(frame_file) and os.path.getsize(frame_file) > 0:
                    img = cv2.imread(frame_file)
                    if img is not None:
                        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        frames.append(img_rgb)
            
            logger.info(f"Successfully extracted {len(frames)} frames with FFmpeg")
        else:
            logger.warning("Could not determine video duration for FFmpeg frame extraction")
            
    except Exception as e:
        logger.error(f"FFmpeg frame extraction also failed: {e}")
        
    return frames

def analyze_frames(frame_images: List[str], video_details: Dict[str, Any], user_prompt: str) -> Dict[str, str]:
    """
    Analyzes video frames and generates a story based on the content of those frames.
    
    Args:
        frame_images: List of base64-encoded frames from the video
        video_details: Dictionary containing video metadata
        user_prompt: Optional user prompt to guide the story generation
        
    Returns:
        Dict with video details and generated story
    """
    logger.info(f"Analyzing {len(frame_images)} frames from video")
    
    if len(frame_images) == 0:
        raise ValueError("No frames provided for analysis")
    
    try:
        # Reuse the multiple images story generation function as it already handles
        # multiple base64-encoded images, which is what our frames are
        story_result = generate_story_from_multiple_images(frame_images, 
        NEW_PROMPT)
        
        # Log the token usage for debugging
        logger.info(f"Token usage for frame analysis - Input: {story_result.get('input_tokens', 0)}, "
                   f"Output: {story_result.get('output_tokens', 0)}")
        
        # Combine video details with the story result
        result = video_details.copy()
        result.update(story_result)
        return result
    except Exception as e:
        logger.error(f"Error in analyze_frames function: {e}")
        # Fall back to metadata-only analysis if frame analysis fails
        fallback_result = generate_story_from_video(video_details, user_prompt)
        
        # Log the fallback token usage for debugging
        logger.info(f"Fallback token usage - Input: {fallback_result.get('input_tokens', 0)}, "
                   f"Output: {fallback_result.get('output_tokens', 0)}")
        
        result = video_details.copy()
        result.update(fallback_result)
        return result 