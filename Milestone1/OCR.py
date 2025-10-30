from pathlib import Path
from PIL import Image
import pytesseract
import os ## importing the operating system module
import sys


# Path to your image file (use raw string for Windows path)
image_path = Path(r"C:\Users\Acer\OneDrive\Gambar\Screenshots\Screenshot 2025-09-01 200556.png")

# Specify the path to the Tesseract executable
tesseract_exe = Path(r'C:\Program Files\Tesseract-OCR\tesseract.exe')
pytesseract.pytesseract.tesseract_cmd = str(tesseract_exe)

## using the try and except method to handle errors

# Check if image exists
if not image_path.exists():
    print(f"Image file not found: {image_path}")
    sys.exit(1)

# Check if Tesseract executable exists
if not tesseract_exe.exists():
    print(f"Tesseract executable not found:")
    sys.exit(1)

try:
    # Load the image
    image = Image.open(image_path)
except Exception as e:
    print(f"Error opening image: {e}")
    sys.exit(1)

try:
    # Perform OCR
    text = pytesseract.image_to_string(image)


    # Print the detected text from the image
    print("Hey Rahul, the OCR has detected the following text:")
    print(text)
except Exception as e:
    print(f"OCR failed: {e}")
    sys.exit(1)

