<<<<<<< HEAD
🚀 INTELLIDOC – Intelligent Document Processing System

📌 Overview

INTELLIDOC is an Intelligent Document Processing (IDP) platform built for enterprise automation.
It transforms unstructured documents (images, PDFs) into structured, searchable, and meaningful data using OCR and AI.

⸻

🛠️ Tech Stack

🔹 Frontend
	•	React 19
	•	Tailwind CSS 4
	•	Lucide Icons
	•	Framer Motion

🔹 Backend
	•	Node.js
	•	Express.js

🔹 AI & OCR
	•	OCR Engine: Tesseract.js (WASM-based)
	•	AI/NLP: Google Gemini 2.0

🔹 Database & Storage
	•	SQLite (via better-sqlite3)
	•	Multer (file uploads)
	•	jsPDF (report generation)

⸻

⚙️ How It Works (Pipeline)
	1.	📤 Upload
User uploads a document (PNG, JPG, PDF)
	2.	🔍 OCR Processing
Tesseract.js extracts raw text from the document
	3.	🧠 AI Processing
Extracted text is sent to Gemini AI
	4.	📊 Intelligent Output
	•	Summary generation
	•	Keyword extraction
	•	Text cleaning
	5.	💾 Storage
Data stored in SQLite:
	•	Filename
	•	Raw text
	•	Summary
	•	Keywords
	6.	📈 Dashboard
Interactive UI for:
	•	Viewing results
	•	Searching data
	•	Downloading reports

⸻

🧪 Why Preprocessing Matters in OCR

Preprocessing significantly improves OCR accuracy:
	•	🔆 Contrast Enhancement
Makes text clearly distinguishable from background
	•	🧹 Noise Removal
Eliminates unwanted artifacts
	•	⚫ Binarization
Converts image to black & white for better character recognition

⸻

🌍 Real-World Use Cases
	•	🧾 Invoice Automation
Extract structured billing data
	•	⚖️ Legal Tech
Summarize contracts and detect clauses
	•	🏥 Healthcare
Digitize and analyze patient records
	•	👨‍💼 HR Systems
Resume parsing and skill extraction

🚀 Getting Started

1️⃣ Install Dependencies
- npm install

2️⃣ Run the Application
- npm run dev

=======
# INTELLIDOC: Intelligent Document Processing Platform

**Intelligent Document Processing Platform for Enterprise Automation**

INTELLIDOC is an advanced AI-powered document automation platform designed to make manual document processing obsolete. It ingests unstructured documents (images & PDFs), extracts their text using OCR, understands the text content via NLP for summarization and keywords, and stores structured metadata in a searchable database.

## 🚀 Project Overview

Manual document processing is often slow, error-prone, and inefficient for enterprises. INTELLIDOC automates this pipeline by converting **Unstructured Documents into Intelligent Digital Data.**

The application workflow:
1. **User uploads document (PNG, JPG, JPEG, PDF)**
2. **Preprocessing via OpenCV**: Images are grayscaled, denoised, and thresholded to enhance text visibility.
3. **OCR Extraction via Tesseract**: Text is pulled from the processed images in multiple supported languages.
4. **NLP Processing via NLTK & Sumy**: Contextual data is analyzed. Summaries and relevant keywords are generated.
5. **Database Storage via SQLAlchemy**: Results are persisted with their metadata.
6. **Result Dashboard & Output Generation**: Users can review results, download raw TXT, or generate professional PDF Reports via ReportLab.

## 🛠 Technologies Used

* **Backend**: Python 3, Flask, SQLAlchemy (SQLite)
* **Image Processing**: OpenCV (`opencv-python`), Pillow
* **OCR**: PyTesseract
* **NLP Intelligence**: NLTK, Sumy
* **Frontend UI**: HTML5, Vanilla JavaScript, Bootstrap 5 UI framework
* **Document Generation**: ReportLab (`pdfgen` / `platypus`)
* **PDF Handling**: `pdf2image`

## 🤔 Why OpenCV Preprocessing Improves OCR

Optical Character Recognition (OCR) engines like Tesseract work by identifying shapes and matching them against trained character datasets. However, raw scans are often noisy, dark, or blurry, leading to inaccurate character recognition.

INTELLIDOC applies a processing pipeline before extracting text:
1. **Grayscale Conversion**: Eliminates color data which can confuse thresholding algorithms.
2. **Noise Removal (Median Blur)**: Softens background salt-and-pepper noise without blurring sharp text edges.
3. **Otsu's Thresholding**: Dynamically binarizes the image (converts everything to pure black and pure white) finding the optimal contrast threshold. This makes the textual content stand out distinctly from the background, resulting in significantly higher OCR accuracy.

## 🌍 Real-world Applications

* **Invoice processing and accounts payable automation**
* **Legal contract breakdown and summarization**
* **Digitizing legacy medical records**
* **Identity document verification (Passport/ID OCR)**

---

## ⚙️ Step-by-Step Setup Instructions

### Prerequisites
Make sure your system has the following core OS dependencies installed:
* **Python 3.8+**
* **Tesseract-OCR Engine**:
  * macOS: `brew install tesseract tesseract-lang`
  * Linux/Ubuntu: `sudo apt install tesseract-ocr`
  * Windows: Download the executable from the UB-Mannheim Tesseract project.
* **Poppler** (Required for PDF to Image conversion):
  * macOS: `brew install poppler`
  * Linux/Ubuntu: `sudo apt install poppler-utils`

### Installation

1. **Clone or Navigate to the Project Folder**
   ```bash
   cd INTELLIDOC
   ```

2. **Set up a Virtual Environment (Optional but Recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### 🏃 How to Run the Project Locally

1. **Run the Application**
   ```bash
   python app.py
   ```
   *The SQLite database (`docDB.db`) and necessary `uploads/` dir will automatically initialize on the first run. The script will also automatically attempt to download the necessary NLTK corpora.*

2. **Access the Web Interface**
   Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```
>>>>>>> 58b7d10 (new idea)
