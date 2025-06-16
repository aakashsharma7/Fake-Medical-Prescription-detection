import pytesseract
from PIL import Image
import pdf2image
import io
import re
from typing import Dict, Any
import os
import sys

# Configure Tesseract path
if sys.platform.startswith('win'):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def process_document(file) -> Dict[str, Any]:
    """
    Process uploaded document (image or PDF) and extract text using OCR
    """
    try:
        # Save file content to bytes buffer
        file_content = file.read()
        file.seek(0)  # Reset file pointer for future reads
        
        # Convert PDF to image if necessary
        if file.filename.lower().endswith('.pdf'):
            try:
                images = pdf2image.convert_from_bytes(file_content)
                if not images:
                    return {
                        'error': 'Could not extract any pages from the PDF.',
                        'details': 'Please ensure the PDF is not corrupted and contains at least one page.'
                    }
                image = images[0]  # Process first page
            except Exception as e:
                if "poppler" in str(e).lower():
                    return {
                        'error': 'PDF processing requires Poppler to be installed. Please install Poppler and try again.',
                        'installation_guide': get_poppler_installation_guide()
                    }
                return {
                    'error': f'Error processing PDF: {str(e)}',
                    'details': 'Please ensure the PDF is not corrupted and try again.'
                }
        else:
            try:
                image = Image.open(io.BytesIO(file_content))
                # Convert image to RGB if it's in a different mode (e.g., RGBA, CMYK)
                if image.mode != 'RGB':
                    image = image.convert('RGB')
            except Exception as e:
                return {
                    'error': f'Error opening image: {str(e)}',
                    'details': 'Please ensure the file is a valid image format (JPG, PNG, GIF, BMP, TIFF, WEBP) or PDF.'
                }

        # Perform OCR
        try:
            text = pytesseract.image_to_string(image)
            if not text.strip():
                return {
                    'error': 'No text could be extracted from the image.',
                    'details': 'Please ensure the image is clear and contains readable text.'
                }
        except Exception as e:
            return {
                'error': f'Error during OCR processing: {str(e)}',
                'details': 'Please ensure Tesseract is installed and in your PATH.'
            }
        
        # Extract relevant information using regex patterns
        extracted_data = {
            'prescription_text': text,
            'doctor_name': extract_doctor_name(text),
            'doctor_license': extract_license_number(text),
            'patient_name': extract_patient_name(text),
            'medications': extract_medications(text),
            'date': extract_date(text)
        }
        
        return extracted_data
    except Exception as e:
        return {
            'error': f'Error processing document: {str(e)}',
            'details': 'Please ensure the file is a valid image or PDF document.'
        }

def get_poppler_installation_guide() -> str:
    """Return installation guide based on the operating system"""
    if sys.platform.startswith('win'):
        return """
        For Windows:
        1. Download Poppler for Windows from: https://github.com/oschwartz10612/poppler-windows/releases/
        2. Extract the downloaded file
        3. Add the 'bin' directory to your system PATH
        4. Restart your application
        """
    elif sys.platform.startswith('darwin'):  # macOS
        return """
        For macOS:
        1. Install using Homebrew: brew install poppler
        2. Restart your application
        """
    else:  # Linux
        return """
        For Linux:
        1. Install using apt: sudo apt-get install poppler-utils
        2. Restart your application
        """

def extract_doctor_name(text: str) -> str:
    """Extract doctor's name from text"""
    # Common patterns for doctor names
    patterns = [
        r'Dr\.\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
        r'Doctor:\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
        r'Physician:\s*([A-Z][a-z]+\s+[A-Z][a-z]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return ""

def extract_license_number(text: str) -> str:
    """Extract medical license number"""
    patterns = [
        r'License\s*#?\s*:?\s*([A-Z0-9-]+)',
        r'License\s*Number\s*:?\s*([A-Z0-9-]+)',
        r'MD\s*License\s*:?\s*([A-Z0-9-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return ""

def extract_patient_name(text: str) -> str:
    """Extract patient's name"""
    patterns = [
        r'Patient:\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
        r'Name:\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
        r'Patient\s*Name:\s*([A-Z][a-z]+\s+[A-Z][a-z]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return ""

def extract_medications(text: str) -> list:
    """Extract prescribed medications"""
    # Look for common medication patterns
    medications = []
    lines = text.split('\n')
    
    for line in lines:
        # Look for common medication indicators
        if any(indicator in line.lower() for indicator in ['rx', 'prescribe', 'medication', 'drug']):
            # Extract medication name and dosage
            med_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*(\d+\s*(?:mg|g|ml|tablet|capsule)s?)', line)
            if med_match:
                medications.append({
                    'name': med_match.group(1),
                    'dosage': med_match.group(2)
                })
    
    return medications

def extract_date(text: str) -> str:
    """Extract prescription date"""
    patterns = [
        r'Date:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'Prescribed\s*on:\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return "" 