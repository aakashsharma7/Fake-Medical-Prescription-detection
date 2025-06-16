import cv2
import numpy as np
from PIL import Image
import io
from app.models.database import get_doctor_by_license
from typing import Dict, Any

def verify_doctor(license_number: str) -> Dict[str, Any]:
    """
    Verify doctor's license number against the database
    """
    if not license_number:
        return {
            'is_valid': False,
            'message': 'No license number provided'
        }
    
    doctor = get_doctor_by_license(license_number)
    
    if not doctor:
        return {
            'is_valid': False,
            'message': 'License number not found in database'
        }
    
    return {
        'is_valid': True,
        'doctor_info': {
            'name': doctor.get('name'),
            'specialty': doctor.get('specialty'),
            'license_status': doctor.get('status')
        }
    }

def detect_tampering(file) -> Dict[str, Any]:
    """
    Detect potential tampering in the prescription image
    """
    # Convert file to image
    if file.filename.lower().endswith('.pdf'):
        from pdf2image import convert_from_bytes
        images = convert_from_bytes(file.read())
        image = np.array(images[0])
    else:
        image = np.array(Image.open(file))
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Initialize results
    results = {
        'is_tampered': False,
        'confidence': 0.0,
        'detected_issues': []
    }
    
    # 1. Check for digital manipulation artifacts
    noise_level = detect_noise_level(gray)
    if noise_level > 0.8:
        results['detected_issues'].append('High noise level detected')
        results['confidence'] += 0.3
    
    # 2. Check for inconsistent text alignment
    alignment_score = check_text_alignment(gray)
    if alignment_score > 0.7:
        results['detected_issues'].append('Inconsistent text alignment detected')
        results['confidence'] += 0.2
    
    # 3. Check for image splicing
    splicing_score = detect_image_splicing(gray)
    if splicing_score > 0.6:
        results['detected_issues'].append('Possible image splicing detected')
        results['confidence'] += 0.3
    
    # 4. Check for inconsistent font patterns
    font_score = analyze_font_consistency(gray)
    if font_score > 0.7:
        results['detected_issues'].append('Inconsistent font patterns detected')
        results['confidence'] += 0.2
    
    # Determine if document is likely tampered
    results['is_tampered'] = results['confidence'] > 0.5
    
    return results

def detect_noise_level(image: np.ndarray) -> float:
    """Detect noise level in the image"""
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    
    # Calculate difference between original and blurred image
    diff = cv2.absdiff(image, blurred)
    
    # Calculate noise level
    noise_level = np.mean(diff) / 255.0
    
    return noise_level

def check_text_alignment(image: np.ndarray) -> float:
    """Check for inconsistent text alignment"""
    # Apply edge detection
    edges = cv2.Canny(image, 50, 150)
    
    # Use HoughLines to detect lines
    lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
    
    if lines is None:
        return 0.0
    
    # Calculate angle distribution
    angles = [line[0][1] for line in lines]
    angle_std = np.std(angles)
    
    # Normalize score
    return min(angle_std / np.pi, 1.0)

def detect_image_splicing(image: np.ndarray) -> float:
    """Detect potential image splicing"""
    # Apply Error Level Analysis (ELA)
    quality = 90
    temp_path = 'temp.jpg'
    cv2.imwrite(temp_path, image, [cv2.IMWRITE_JPEG_QUALITY, quality])
    compressed = cv2.imread(temp_path, cv2.IMREAD_GRAYSCALE)
    
    # Calculate difference
    diff = cv2.absdiff(image, compressed)
    
    # Calculate splicing score
    splicing_score = np.mean(diff) / 255.0
    
    return splicing_score

def analyze_font_consistency(image: np.ndarray) -> float:
    """Analyze font consistency in the image"""
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    # Find contours
    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    
    if not contours:
        return 0.0
    
    # Calculate height distribution of text regions
    heights = [cv2.boundingRect(contour)[3] for contour in contours]
    height_std = np.std(heights)
    
    # Normalize score
    return min(height_std / np.mean(heights), 1.0) 