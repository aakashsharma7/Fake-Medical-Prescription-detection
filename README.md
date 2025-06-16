# MedAuth - Medical Prescription Verification System

MedAuth is an AI-powered web application designed to detect and prevent the misuse of forged or tampered medical prescriptions. The system uses advanced technologies to verify prescription authenticity and ensure patient safety.

## Features

- Document Upload: Support for scanned images and PDFs
- OCR Processing: Extracts prescription details using Tesseract OCR
- Doctor Verification: Validates doctor's license against registered database
- Tampering Detection: Uses OpenCV for image analysis and forgery detection
- Drug Pattern Analysis: NLP-based analysis of prescription content
- Responsive UI: Modern interface built with Tailwind CSS

## Tech Stack

### Backend
- Python 3.8+
- Flask
- Tesseract OCR
- OpenCV
- spaCy
- MongoDB/PostgreSQL

### Frontend
- HTML5
- Tailwind CSS
- Vanilla JavaScript

## Setup Instructions

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Tesseract OCR:
- Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
- Linux: `sudo apt-get install tesseract-ocr`
- macOS: `brew install tesseract`

3. Download spaCy model:
```bash
python -m spacy download en_core_web_sm
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
python app.py
```

## Project Structure

```
medauth/
├── app/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/
│   ├── models/
│   ├── utils/
│   └── config.py
├── tests/
├── requirements.txt
└── README.md
```

## License

MIT License 