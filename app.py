from flask import Flask, render_template, request, send_file
import os, io
import pytesseract
from PIL import Image
import fitz
import spacy
import re
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# create uploads folder
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# load NLP model
nlp = spacy.load("en_core_web_sm")


# ---------------------------
# SIMPLE SUMMARIZATION
# ---------------------------
def simple_summarize(text, max_lines=4):

    lines = text.split("\n")
    important_lines = []

    for line in lines:
        line = line.strip()

        if len(line) > 5:
            important_lines.append(line)

    summary = "\n".join(important_lines[:max_lines])

    return summary


# ---------------------------
# TEXT CLEANING
# ---------------------------
def clean_text(text):

    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:

        line = line.strip()

        if len(line) > 2:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


# ---------------------------
# ENTITY EXTRACTION
# ---------------------------
def extract_entities(text):

    doc = nlp(text)

    entities = []
    seen = set()

    for ent in doc.ents:

        if ent.text.lower() not in seen:
            entities.append((ent.text, ent.label_))
            seen.add(ent.text.lower())

    return entities


# ---------------------------
# PATTERN EXTRACTION
# ---------------------------
def extract_patterns(text):

    patterns = {}

    pan = re.findall(r"[A-Z]{5}[0-9]{4}[A-Z]", text)
    if pan:
        patterns["PAN Number"] = pan[0]

    date = re.findall(r"\d{2}/\d{2}/\d{4}", text)
    if date:
        patterns["Date"] = date[0]

    email = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    if email:
        patterns["Email"] = email[0]

    phone = re.findall(r"\b\d{10}\b", text)
    if phone:
        patterns["Phone"] = phone[0]

    return patterns


# ---------------------------
# HOME PAGE
# ---------------------------
@app.route("/")
def home():
    return render_template("upload.html")


# ---------------------------
# FILE UPLOAD + PROCESSING
# ---------------------------
@app.route("/upload", methods=["POST"])
def upload_file():

    file = request.files.get("document")

    if not file:
        return "No file selected"

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    try:

        # IMAGE OCR
        if file.filename.lower().endswith((".png", ".jpg", ".jpeg")):

            img = Image.open(filepath)
            img = img.convert('L')

            custom_config = r'--oem 3 --psm 6'

            extracted_text = pytesseract.image_to_string(
                img,
                config=custom_config
            )

        # PDF TEXT EXTRACTION
        elif file.filename.lower().endswith(".pdf"):

            doc = fitz.open(filepath)
            extracted_text = ""

            for page in doc:
                extracted_text += page.get_text()

        else:
            extracted_text = "Unsupported file format"

        extracted_text = clean_text(extracted_text)

        summary = simple_summarize(extracted_text)

        entities = extract_entities(extracted_text)

        patterns = extract_patterns(extracted_text)

    except Exception as e:
        return f"Processing Failed: {str(e)}"

    return render_template(
        "upload.html",
        text=extracted_text,
        summary=summary,
        entities=entities,
        patterns=patterns
    )


# ---------------------------
# TXT DOWNLOAD
# ---------------------------
@app.route('/download_txt')
def download_txt():

    text = request.args.get("text")

    memory_file = io.BytesIO()
    memory_file.write(text.encode('utf-8'))
    memory_file.seek(0)

    return send_file(
        memory_file,
        as_attachment=True,
        download_name="extracted_text.txt",
        mimetype="text/plain"
    )


# ---------------------------
# PDF DOWNLOAD
# ---------------------------
@app.route('/download_pdf')
def download_pdf():

    text = request.args.get("text")

    memory_file = io.BytesIO()

    p = canvas.Canvas(memory_file, pagesize=letter)

    y = 750

    for line in text.split('\n'):
        p.drawString(40, y, line)
        y -= 15

    p.save()

    memory_file.seek(0)

    return send_file(
        memory_file,
        as_attachment=True,
        download_name="extracted_text.pdf",
        mimetype="application/pdf"
    )


# ---------------------------
# RUN APP
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
