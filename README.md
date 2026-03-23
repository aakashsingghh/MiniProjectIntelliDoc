# INTELLIDOC - Project Documentation

## Project Overview
INTELLIDOC is an Intelligent Document Processing (IDP) platform designed for enterprise automation. It leverages Optical Character Recognition (OCR) and Artificial Intelligence (AI) to convert unstructured documents (images, PDFs) into structured, searchable, and intelligent digital data.

## Technologies Used
- **Frontend**: React 19, Tailwind CSS 4, Lucide Icons, Framer Motion.
- **Backend**: Node.js, Express.
- **OCR Engine**: Tesseract.js (WASM-based OCR).
- **AI/NLP**: Google Gemini 2.0 (for summarization, keyword extraction, and text cleaning).
- **Database**: SQLite (via better-sqlite3) for structured data persistence.
- **File Handling**: Multer for uploads, jsPDF for report generation.

## Working Pipeline
1. **Upload**: User uploads a document (PNG, JPG, PDF).
2. **Preprocessing & OCR**: The system uses Tesseract.js to extract raw text from the document.
3. **AI Analysis**: The extracted text is sent to the Gemini AI model.
4. **Intelligent Output**: Gemini generates a concise summary, extracts key entities (keywords), and cleans the text.
5. **Storage**: The filename, raw text, summary, and keywords are stored in a local SQLite database.
6. **Dashboard**: Results are displayed in a modern dashboard with search and download capabilities.

## Why Preprocessing Improves OCR
Preprocessing (like grayscaling, thresholding, and noise removal) improves OCR accuracy by:
- **Increasing Contrast**: Making text stand out from the background.
- **Removing Noise**: Eliminating artifacts that might be mistaken for characters.
- **Binarization**: Converting images to black and white helps the OCR engine identify character shapes more clearly.

## Real-World Applications
- **Invoice Automation**: Extracting data from billing documents.
- **Legal Tech**: Summarizing long contracts and searching for clauses.
- **Healthcare**: Digitizing patient records and extracting key medical terms.
- **HR**: Processing resumes and extracting skills/experience.

## Setup Instructions
1. **Install Dependencies**: `npm install`
2. **Configure API Key**: Add `GEMINI_API_KEY` to your environment variables or AI Studio Secrets.
3. **Run Project**: `npm run dev`
4. **Access App**: Open `http://localhost:3000` in your browser.
