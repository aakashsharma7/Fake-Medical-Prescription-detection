# This file makes the app directory a Python package 

import os
# Disable oneDNN warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from app.utils.ocr import process_document
from app.utils.verification import verify_doctor, detect_tampering
from app.utils.drug_analysis import analyze_prescription
from app.models.database import init_db

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
CORS(app)

# Initialize database
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/verify', methods=['POST'])
def verify_prescription():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        # Process document and extract text
        extracted_data = process_document(file)
        
        # Check if there was an error during document processing
        if 'error' in extracted_data:
            return jsonify(extracted_data), 400
        
        # Verify doctor's license
        doctor_verification = verify_doctor(extracted_data.get('doctor_license'))
        
        # Detect tampering
        tampering_detection = detect_tampering(file)
        
        # Analyze drug patterns
        drug_analysis = analyze_prescription(extracted_data.get('prescription_text'))
        
        return jsonify({
            'status': 'success',
            'data': {
                'extracted_data': extracted_data,
                'doctor_verification': doctor_verification,
                'tampering_detection': tampering_detection,
                'drug_analysis': drug_analysis
            }
        })
    
    except Exception as e:
        app.logger.error(f"Error processing prescription: {str(e)}")
        return jsonify({
            'error': 'An unexpected error occurred while processing the prescription.',
            'details': str(e)
        }), 500 