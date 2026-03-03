from flask import Flask, render_template, request
import os
import pytesseract
from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists('uploads'):
    os.makedirs('uploads')

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
    except Exception as e:
        return f"OCR Processing Failed: {str(e)}"

    return render_template("upload.html", text=extracted_text)

if __name__ == "__main__":
    app.run(debug=True)