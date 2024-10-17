# webapp
from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
import PyPDF2
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

# Initialize Flask app
app = Flask(__name__)

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16MB file size

# Compliance keywords for GDPR, FAR, NIST
GDPR_KEYWORDS = ['data', 'subject', 'consent', 'data breach', 'encryption', 'right to be forgotten']
FAR_KEYWORDS = ['contracting officer', 'term', 'procurement', 'cost', 'termination', 'clause']
NIST_KEYWORDS = ['access control', 'encryption', 'security', 'compliance', 'audit']

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Highlight terms function
def highlight_terms(text, keywords):
    for keyword in keywords:
        text = text.replace(keyword, f'<mark>{keyword}</mark>')
    return text

# Optionally, merge all keywords into a single list
ALL_KEYWORDS = GDPR_KEYWORDS + FAR_KEYWORDS + NIST_KEYWORDS

# PDF text extraction
def extract_text_from_pdf(filepath):
    with open(filepath, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

# OCR for scanned PDFs
def ocr_pdf(filepath):
    images = convert_from_path(filepath)
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image)
    return text

# Compliance check
def check_compliance_against_keywords(text, keywords, reader):
    results = {}
    
    for page_num, page in enumerate(reader.pages):
        page_text = page.extract_text()
        for keyword in keywords:
            count = page_text.lower().count(keyword.lower())
            if count > 0:
                if keyword not in results:
                    results[keyword] = []
                results[keyword].append({'page': page_num + 1, 'count': count})
    
    return results
# Route for home page
@app.route('/')
def home():
    return render_template('upload.html')

# Route to handle PDF uploads and display results
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Extract text from the PDF and create a reader object
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)  # Pass the reader object to check function
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        
        # Extract text from the PDF
        text = extract_text_from_pdf(filepath)
        
        # If no text was extracted, try OCR (for scanned PDFs)
        if not text.strip():
            text = ocr_pdf(filepath)
        
        # Perform compliance screening
        flagged_terms = check_compliance_against_keywords(text, GDPR_KEYWORDS, reader)
        
        # Highlight the found terms in the extracted text
        highlighted_text = highlight_terms(text, GDPR_KEYWORDS)
        
        # Render the result in the 'results.html' template
        return render_template('results.html', flagged_terms=flagged_terms, highlighted_text=highlighted_text)
    else:
        return "Invalid file type. Only PDFs are allowed."

if __name__ == '__main__':
    app.run(debug=True)
