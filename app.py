from flask import Flask, render_template, request, send_file
import os, io
import pytesseract
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists('uploads'):
    os.makedirs('uploads')


# ----------------------------
# Simple Summarization Function
# ----------------------------
def simple_summarize(text, num_sentences=3):
    sentences = text.split('.')
    summary = '.'.join(sentences[:num_sentences])
    return summary


@app.route("/")
def home():
    return render_template("upload.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("document")

    if not file:
        return "No file selected"

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    try:
        img = Image.open(filepath)
        extracted_text = pytesseract.image_to_string(img)
        summary = simple_summarize(extracted_text)
    except Exception as e:
        return f"OCR Processing Failed: {str(e)}"

    return render_template("upload.html", text=extracted_text, summary=summary)


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


if __name__ == "__main__":
    app.run(debug=True)