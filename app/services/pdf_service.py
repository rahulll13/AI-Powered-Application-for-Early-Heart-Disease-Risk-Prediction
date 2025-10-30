# app/services/pdf_service.py

from fpdf import FPDF
import io

def create_prediction_report(prediction, user):
    """Generates a PDF report for a given prediction and returns it as bytes."""
    
    pdf = FPDF()
    pdf.add_page()
    
    # Set Title
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, 'Heart Disease Prediction Report', 0, 1, 'C')
    pdf.ln(10)
    
    # User and Prediction Info
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 10, f"Report Date: {prediction.timestamp.strftime('%Y-%m-%d %H:%M:%S')} UTC", 0, 1)
    pdf.cell(0, 10, f"Patient Username: {user.username}", 0, 1)
    pdf.ln(5)
    
    # Results Section
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'Prediction Results', 0, 1)
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 10, f"Risk Category: {prediction.risk_category}", 0, 1)
    
    # --- THIS IS THE FIX ---
    # The .output('S') method returns bytes directly. The .encode() call is removed.
    pdf_bytes = pdf.output(dest='S')
    # ---------------------
    
    return io.BytesIO(pdf_bytes)