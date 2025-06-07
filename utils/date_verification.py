"""
Date Verification Utility Module

This module handles the verification of production dates for Chang beer bottles
to determine eligibility for the claim process (within 120 days).
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import json

# Configure logging
logger = logging.getLogger(__name__)

# Constants
MAX_ELIGIBLE_DAYS = 120  # Maximum days since production for eligibility

def verify_production_date(production_date: Dict[str, str]) -> Dict[str, Any]:
    """
    Verifies if a Chang beer bottle with the given production date is eligible for claims
    based on the 120-day rule.
    
    Args:
        production_date: The production date in YYYY-MM-DD format
    
    Returns:
        Dictionary containing:
        - status: "ELIGIBLE" or "INELIGIBLE"
        - production_date: The original date received
        - days_elapsed: Number of days since production
        - max_allowed_days: Maximum allowed days for eligibility (120)
        - message: A message explaining the eligibility status (English)
        - message_thai: A message explaining the eligibility status (Thai)
    """
    
    try:
        production_date = json.loads(production_date)
        production_date = production_date.get("manufactured_date")
        # Parse the production date
        prod_date = datetime.strptime(production_date, "%d/%m/%Y")
        
        # Get current date (use UTC to avoid timezone issues)
        current_date = datetime.utcnow()
        
        # Calculate days elapsed
        days_elapsed = (current_date - prod_date).days

        # Determine eligibility
        is_eligible = days_elapsed <= MAX_ELIGIBLE_DAYS
        
        # Generate status and messages
        status = "ELIGIBLE" if is_eligible else "INELIGIBLE"
        
        # Format dates for messages
        formatted_prod_date = prod_date.strftime("%d/%m/%Y")
        
        # Create result messages (English and Thai)
        if is_eligible:
            message = (
                f"This bottle was produced on {formatted_prod_date}, which is {days_elapsed} days ago. "
                f"It is eligible for claim assessment."
            )
            message_thai = (
                f"ขวดนี้ผลิตเมื่อวันที่ {formatted_prod_date} ซึ่งเป็นเวลา {days_elapsed} วันที่ผ่านมา "
                f"ขวดนี้มีสิทธิ์ได้รับการประเมินการเคลม"
            )
        else:
            message = (
                f"This bottle was produced on {formatted_prod_date}, which is {days_elapsed} days ago. "
                f"It is not eligible for claim assessment as it exceeds the {MAX_ELIGIBLE_DAYS}-day limit."
            )
            message_thai = (
                f"ขวดนี้ผลิตเมื่อวันที่ {formatted_prod_date} ซึ่งเป็นเวลา {days_elapsed} วันที่ผ่านมา "
                f"ขวดนี้ไม่มีสิทธิ์ได้รับการประเมินการเคลมเนื่องจากเกินกำหนด {MAX_ELIGIBLE_DAYS} วัน"
            )
        
        # Return verification result
        return {
            "status": status,
            "production_date": production_date,
            "days_elapsed": days_elapsed,
            "max_allowed_days": MAX_ELIGIBLE_DAYS,
            "message": message,
            "message_thai": message_thai
        }
    
    except ValueError as e:
        # Handle invalid date format
        logger.error(f"Invalid date format: {production_date}. Error: {e}")
        return {
            "status": "ERROR",
            "production_date": production_date,
            "days_elapsed": None,
            "max_allowed_days": MAX_ELIGIBLE_DAYS,
            "message": f"Invalid production date format: {production_date}. Expected format: YYYY-MM-DD.",
            "message_thai": f"รูปแบบวันที่ผลิตไม่ถูกต้อง: {production_date} รูปแบบที่คาดหวัง: YYYY-MM-DD"
        }
    
    except Exception as e:
        # Handle other unexpected errors
        logger.exception(f"Unexpected error during date verification: {e}")
        return {
            "status": "ERROR",
            "production_date": production_date,
            "days_elapsed": None,
            "max_allowed_days": MAX_ELIGIBLE_DAYS,
            "message": f"Error verifying production date: {str(e)}",
            "message_thai": f"เกิดข้อผิดพลาดในการตรวจสอบวันที่ผลิต: {str(e)}"
        }

def format_verification_response(verification_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formats the verification result into the standardized API response format.
    
    Args:
        verification_result: The result from verify_production_date
    
    Returns:
        Structured response dictionary with english and thai sections
    """
    if verification_result.get("status") == "ERROR":
        # Handle error case
        return {
            "english": {
                "status": "ERROR",
                "production_date": verification_result.get("production_date"),
                "days_elapsed": verification_result.get("days_elapsed"),
                "max_allowed_days": verification_result.get("max_allowed_days"),
                "message": verification_result.get("message")
            },
            "thai": {
                "status": "ข้อผิดพลาด",
                "production_date": verification_result.get("production_date"),
                "days_elapsed": verification_result.get("days_elapsed"),
                "max_allowed_days": verification_result.get("max_allowed_days"),
                "message": verification_result.get("message_thai")
            }
        }
    
    # Standard case (ELIGIBLE or INELIGIBLE)
    return {
        "english": {
            "status": verification_result.get("status"),
            "production_date": verification_result.get("production_date"),
            "days_elapsed": verification_result.get("days_elapsed"),
            "max_allowed_days": verification_result.get("max_allowed_days"),
            "message": verification_result.get("message")
        },
        "thai": {
            "status": "มีสิทธิ์" if verification_result.get("status") == "ELIGIBLE" else "ไม่มีสิทธิ์",
            "production_date": verification_result.get("production_date"),
            "days_elapsed": verification_result.get("days_elapsed"),
            "max_allowed_days": verification_result.get("max_allowed_days"),
            "message": verification_result.get("message_thai")
        }
    } 