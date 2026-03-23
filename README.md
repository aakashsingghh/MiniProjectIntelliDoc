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

