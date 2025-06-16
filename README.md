# Medical Prescription Verification System

A Streamlit-based application that helps verify the authenticity of medical prescriptions using OCR and text analysis.

## Features

- Upload and process prescription images (JPG, PNG) and PDFs
- Extract text using OCR (Optical Character Recognition)
- Verify prescription authenticity
- Modern and user-friendly interface

## Prerequisites

- Python 3.8 or higher
- Tesseract OCR installed on your system
- Poppler (for PDF processing)

### Installing Tesseract OCR

#### Windows
1. Download the installer from [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install and add to PATH

#### Linux
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

#### macOS
```bash
brew install tesseract
```

### Installing Poppler

#### Windows
1. Download from [https://github.com/oschwartz10612/poppler-windows/releases/](https://github.com/oschwartz10612/poppler-windows/releases/)
2. Extract and add to PATH

#### Linux
```bash
sudo apt-get install poppler-utils
```

#### macOS
```bash
brew install poppler
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Activate your virtual environment if not already activated:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Run the Streamlit app:
```bash
streamlit run app.py
```

3. Open your web browser and navigate to the URL shown in the terminal (usually http://localhost:8501)

## Usage

1. Click on "Upload Prescription" to select an image or PDF file
2. Wait for the processing to complete
3. View the extracted text and verification results
4. The application will indicate if the prescription is authentic or potentially fake

## Contributing

Feel free to submit issues and enhancement requests! 