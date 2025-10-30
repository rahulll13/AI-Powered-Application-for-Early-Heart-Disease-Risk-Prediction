# app/services/ocr_service.py

import pytesseract
from PIL import Image
from flask import current_app

def configure_pytesseract():
    """Configures pytesseract to use the path from the app's config."""
    pytesseract.pytesseract.tesseract_cmd = current_app.config['TESSERACT_CMD']

def extract_text_from_image(filepath):
    """
    Extracts text from an image file using Tesseract OCR.
    Returns the extracted text as a string.
    """
    try:
        configure_pytesseract()
        text = pytesseract.image_to_string(Image.open(filepath))
        return text
    except Exception as e:
        print(f"An error occurred during OCR processing: {e}")
        return f"Error processing file: {e}"