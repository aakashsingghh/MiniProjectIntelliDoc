import os
import cv2
import numpy as np
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
if os.getenv("GEMINI_API_KEY"):
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

from flask import Flask, request, render_template, redirect, url_for, send_file, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io
import uuid
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'intellidoc_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///docDB.db'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)

class docTable(db.Model):
    __tablename__ = 'docTable'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    extracted_text = db.Column(db.Text, nullable=True)
    document_type = db.Column(db.String(100), nullable=True)
    summary = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(50), nullable=True)
    extracted_data = db.Column(db.Text, nullable=True)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

def preprocess_image(image_path):
    # This improves OCR accuracy significantly by making the text stand out clearly against the background.
    img = cv2.imread(image_path)
    if img is None:
        return image_path
    
    # Grayscale conversion
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Noise removal
    denoised = cv2.medianBlur(gray, 3)
    
    # Thresholding
    _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    
    processed_path = image_path.replace('.', '_processed.')
    cv2.imwrite(processed_path, thresh)
    return processed_path

def extract_text_from_file(file_path, lang='eng'):
    text = ""
    try:
        if file_path.lower().endswith('.pdf'):
            pages = convert_from_path(file_path, 300)
            for i, page in enumerate(pages):
                temp_path = f"{file_path}_page_{i}.jpg"
                page.save(temp_path, 'JPEG')
                
                # Preprocess before OCR
                processed_path = preprocess_image(temp_path)
                
                # Extract using selected language
                text += pytesseract.image_to_string(Image.open(processed_path), lang=lang) + "\n"
                
                # Cleanup
                os.remove(temp_path)
                if os.path.exists(processed_path):
                    os.remove(processed_path)
        else:
            # Preprocess image
            processed_path = preprocess_image(file_path)
            
            # Extract using selected language
            text = pytesseract.image_to_string(Image.open(processed_path), lang=lang)
            
            if processed_path != file_path and os.path.exists(processed_path):
                os.remove(processed_path)
                
    except Exception as e:
        print(f"Error extracting text: {e}")
        
    return text.strip()

def process_document_with_llm(text):
    if not text or len(text.strip()) < 5:
        return {"document_type": "Other", "extracted_data": {}, "priority": "", "summary": "No readable text found."}
    
    prompt = """You are an Intelligent Document Processing system.

Your task is to:
1. Classify the document into ONE of these categories:
   - Invoice/Bill
   - Resume
   - Form
   - Other

2. Based on the category, extract relevant structured data:
If Invoice/Bill: Extract Total Amount, Date, Vendor Name. Categorize priority: Amount < 2500 -> "Low Priority", 2500-10000 -> "Normal Priority", >10000 -> "High Priority".
If Resume: Extract Name, Skills (list), Education, Experience.
If Form: Extract Key-value pairs.
If Other: Return short description.

3. Output STRICTLY in JSON format:
{
  "document_type": "",
  "extracted_data": {},
  "priority": "",
  "summary": "Concise 2-3 line intelligent summary."
}
Do not include any extra text outside JSON.
"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            f"{prompt}\n\nDocument Text:\n{text}",
            generation_config=genai.GenerationConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return {"document_type": "Error", "extracted_data": {}, "priority": "", "summary": f"Failed to process with AI: {e}"}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
            
        lang = request.form.get('language', 'eng')
        
        if file:
            unique_filename = str(uuid.uuid4())[:8] + "_" + file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            # 1. OCR Extraction
            extracted_text = extract_text_from_file(filepath, lang=lang)
            
            # 2. AI Processing
            llm_result = process_document_with_llm(extracted_text)
            
            # 3. Store in DB
            new_doc = docTable(
                filename=file.filename,
                extracted_text=extracted_text,
                document_type=llm_result.get("document_type", "Unknown"),
                summary=llm_result.get("summary", ""),
                priority=llm_result.get("priority", ""),
                extracted_data=json.dumps(llm_result.get("extracted_data", {}))
            )
            db.session.add(new_doc)
            db.session.commit()
            
            flash('Document processed successfully!', 'success')
            return redirect(url_for('result', doc_id=new_doc.id))
            
    return render_template('upload.html')

@app.route('/result/<int:doc_id>')
def result(doc_id):
    doc = docTable.query.get_or_404(doc_id)
    extracted_data_dict = {}
    if doc.extracted_data:
        try:
            extracted_data_dict = json.loads(doc.extracted_data)
        except:
            pass
    return render_template('result.html', doc=doc, extracted_data=extracted_data_dict)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if query:
        # Search by keyword or filename
        results = docTable.query.filter(
            (docTable.filename.ilike(f'%{query}%')) |
            (docTable.extracted_text.ilike(f'%{query}%')) |
            (docTable.document_type.ilike(f'%{query}%')) |
            (docTable.summary.ilike(f'%{query}%'))
        ).order_by(docTable.upload_date.desc()).all()
    else:
        results = docTable.query.order_by(docTable.upload_date.desc()).all()
        
    return render_template('search.html', results=results, query=query)

@app.route('/reprocess/<int:doc_id>')
def reprocess(doc_id):
    # Optional endpoint to demonstrate reprocessing - currently just redirects to result
    flash('Document scheduled for reprocessing.', 'info')
    return redirect(url_for('result', doc_id=doc_id))

@app.route('/download/txt/<int:doc_id>')
def download_txt(doc_id):
    doc = docTable.query.get_or_404(doc_id)
    
    mem = io.BytesIO()
    content = f"INTELLIDOC RESULT\n\nFilename: {doc.filename}\nUpload Date: {doc.upload_date.strftime('%Y-%m-%d %H:%M:%S')}\nDocument Type: {doc.document_type}\nPriority: {doc.priority}\n\nSUMMARY:\n{doc.summary}\n\nEXTRACTED DATA:\n{doc.extracted_data}\n\nFULL EXTRACTED TEXT:\n{doc.extracted_text}"
    mem.write(content.encode('utf-8'))
    mem.seek(0)
    
    return send_file(
        mem,
        as_attachment=True,
        download_name=f"{doc.filename}_result.txt",
        mimetype='text/plain'
    )

@app.route('/download/pdf/<int:doc_id>')
def download_pdf(doc_id):
    doc = docTable.query.get_or_404(doc_id)
    
    buffer = io.BytesIO()
    pdf_doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    Story = []
    
    Story.append(Paragraph(f"INTELLIDOC Report: {doc.filename}", styles['Title']))
    Story.append(Paragraph(f"Date: {doc.upload_date.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    Story.append(Spacer(1, 12))
    
    Story.append(Paragraph("Document Details", styles['Heading2']))
    Story.append(Paragraph(f"Type: {doc.document_type or 'N/A'}", styles['Normal']))
    if doc.priority:
        Story.append(Paragraph(f"Priority: {doc.priority}", styles['Normal']))
    Story.append(Spacer(1, 12))
    
    Story.append(Paragraph("Summary", styles['Heading2']))
    Story.append(Paragraph(doc.summary or "N/A", styles['Normal']))
    Story.append(Spacer(1, 12))
    
    Story.append(Paragraph("Extracted Text", styles['Heading2']))
    text_processed = (doc.extracted_text or "").replace('\n', '<br/>')
    Story.append(Paragraph(text_processed, styles['Normal']))
    
    pdf_doc.build(Story)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{doc.filename}_report.pdf",
        mimetype='application/pdf'
    )

@app.route('/delete/<int:doc_id>', methods=['POST'])
def delete_doc(doc_id):
    doc = docTable.query.get_or_404(doc_id)
    db.session.delete(doc)
    db.session.commit()
    flash('Document deleted successfully.', 'success')
    return redirect(url_for('search'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
