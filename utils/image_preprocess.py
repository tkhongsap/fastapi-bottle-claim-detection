import cv2
import numpy as np
from pathlib import Path

def preprocess_image_for_llm(image_path: str, output_path: str) -> str:
    """
    Preprocess an image for LLM vision model:
    - Convert to grayscale
    - Resize to enlarge the label region
    - Enhance contrast
    - Crop the area with text heuristically (bounding box)
    - Save and return the new image path

    Args:
        image_path (str): Path to original image
        output_path (str): Path to save processed image

    Returns:
        str: Path to processed image
    """
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Image not found or invalid format.")

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Enhance contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Threshold to highlight text regions
    _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find contours to detect regions of interest (likely text)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Get bounding boxes and crop largest text-like area
    cropped = None
    max_area = 0
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        if area > max_area and w > 50 and h > 10:
            cropped = image[y:y + h, x:x + w]
            max_area = area

    if cropped is None:
        cropped = image  # Fallback to original if no suitable crop found

    # Resize to enlarge text area (double size)
    resized = cv2.resize(cropped, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

    # Save the result
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    print(f"[✅] Saving preprocessed image to: {output_path}")
    cv2.imwrite(output_path, resized)

    return output_path
