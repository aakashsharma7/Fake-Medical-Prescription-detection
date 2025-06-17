import streamlit as st
import os
import cv2
import numpy as np
from PIL import Image
import io
import base64
from app.utils.ocr import extract_text_from_image, extract_text_from_pdf
from app.utils.verification import verify_prescription
import tempfile

# Set page config
st.set_page_config(
    page_title="Medical Prescription Verification",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        border: none;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .upload-section {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .result-section {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🏥 Medical Prescription Verification")
st.markdown("""
This application helps verify the authenticity of medical prescriptions using advanced image processing and text analysis.
Upload a prescription image or PDF to get started.
""")

# File upload section
st.markdown('<div class="upload-section">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload Prescription", type=['jpg', 'jpeg', 'png', 'pdf'])
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file is not None:
    # Create a temporary file to store the uploaded file
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    try:
        # Process the file based on its type
        if uploaded_file.type == 'application/pdf':
            extracted_text = extract_text_from_pdf(tmp_file_path)
        else:
            # Convert uploaded file to image
            image = Image.open(uploaded_file)
            image_np = np.array(image)
            extracted_text = extract_text_from_image(image_np)

        # Display results
        st.markdown('<div class="result-section">', unsafe_allow_html=True)
        st.subheader("Extracted Text")
        st.text_area("", extracted_text, height=200)

        # Verify prescription
        verification_result = verify_prescription(extracted_text)
        
        st.subheader("Verification Results")
        for key, value in verification_result.items():
            if key == 'is_authentic':
                st.markdown(f"**Prescription Status:** {'✅ Authentic' if value else '❌ Potentially Fake'}")
            else:
                st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")

        st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
    finally:
        # Clean up temporary file
        os.unlink(tmp_file_path)

# Add footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Built with ❤️ for healthcare security</p>
</div>
""", unsafe_allow_html=True) 