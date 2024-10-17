# Compliance Document Screening Web App

This Python web app allows users to upload PDF documents and screen them for compliance terms based on frameworks like GDPR, NIST, FAR, and others. The app highlights the flagged terms and shows where in the document they appear.

## Features
- Upload PDF files for compliance screening.
- Flag terms from various compliance frameworks such as GDPR, NIST, and FAR.
- View flagged terms in a clean table format, with page numbers and occurrence counts.
- Highlight terms in the document text.

## Requirements
- Python 3.12+
- Flask
- PyPDF2
- pytesseract
- pdf2image
- PIL (Pillow)

To install dependencies:
```bash
pip install -r requirements.txt
