# 📄 IntelliDoc – Intelligent Document Processing Platform
> **Transforming Unstructured Documents into Actionable Insights with AI-powered OCR and NLP.**

---

## 🌟 Overview
**IntelliDoc** is a robust, production-level Intelligent Document Processing (IDP) platform designed to automate the extraction, classification, and management of data from various document types. By leveraging state-of-the-art **OCR (Optical Character Recognition)** and **NLP (Natural Language Processing)**, IntelliDoc converts messy, unstructured files (Images/PDFs) into structured, searchable digital assets with industry-level accuracy.

---

## 🚩 Problem Statement
Manual data entry and document sorting are slow, error-prone, and expensive. Businesses and individuals struggle with:
- Extracting text from non-searchable scanned images or PDFs.
- Identifying and categorizing document types (Invoices vs. Resumes vs. IDs).
- Manually capturing critical fields like names, dates, and organizations.
- Maintaining a secure, searchable history of processed documents.

## ✅ The Solution
IntelliDoc provides a **unified AI-driven workspace** that automates the entire document lifecycle. It classifies documents instantly, extracts key entities using hybrid rule-based and machine-learning models, and generates contextual summaries—all within a secure, user-specific dashboard.

---

## 🚀 Key Features

### 🔍 Advanced Intelligence
*   **Intelligent OCR**: High-accuracy text extraction from images (PNG, JPG) and multi-page PDFs using **Tesseract OCR**.
*   **Hybrid Entity Extraction**: Captures structured data (**Name, DOB, Email, Phone, Organization**) using **spaCy NER** and optimized **Regex** heuristics.
*   **Smart Classification**: Automatically categorizes files into **PAN Cards, Aadhaar Cards, Resumes, Invoices**, or **Forms**.
*   **Contextual Summarization**: Generates human-readable, document-aware summaries of complex content.

### 💻 User Experience (UX)
*   **Personalized Dashboard**: Real-time insights with **graph-based visualization** of document statistics.
*   **Universal Search & Filter**: Instant search with **live suggestions** and type-based filtering.
*   **Grid/List Views**: Toggleable document library layout with persistent user preference.
*   **Responsive UI**: Modern, sleek design with high-contrast **Dark Mode** and **Light Mode** support.

### 🛠 Management & Security
*   **Secure Authentication**: User registration and login system with **PBKDF2-hashed passwords**.
*   **Data Integrity**: Primary storage in **PostgreSQL** with secondary **JSON backups** for reliability.
*   **File Management**: Simple upload, download (TXT/PDF formats), and deletion workflows.

---

## 🛠 Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Backend** | Python (Flask), psycopg2 |
| **Frontend** | Vanilla JavaScript (ES6+), CSS3 (Modern Glassmorphism), HTML5 |
| **Database** | PostgreSQL |
| **AI / NLP** | Tesseract OCR, spaCy (en_core_web_sm), Regex Heuristics |
| **Formatting** | PIL (Pillow), pdf2image |

---

## 📂 Project Structure

```text
INTELLIDOC/
├── app.py              # Main Flask Backend Logic
├── init_db.py          # PostgreSQL Schema Initialization
├── requirements.txt    # Python Dependencies
├── .env                # Environment Secrets (DB Credentials)
├── .gitignore          # Production-ready git exclusions
├── static/
│   ├── style.css       # Global Design System & Animations
│   └── script.js       # Dynamic UI logic
├── templates/          # Jinja2 HTML Templates
└── uploads/            # Temporary storage for processed files
```

---

## ⚙️ Installation (macOS)

### 1. Prerequisites
Ensure you have **Python 3.x**, **PostgreSQL**, and **Tesseract OCR** installed.

```bash
# Install Tesseract using Homebrew
brew install tesseract
```

### 2. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/intellidoc.git
cd intellidoc

# Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Database Setup (PostgreSQL)
1. Start your PostgreSQL server.
2. Create a database named `intellidoc`.
3. Update your `.env` file with your DB credentials.
4. Run the initialization script:
```bash
python init_db.py
```

### 4. Run Locally
```bash
python app.py
```
Visit `http://127.0.0.1:5000` in your browser.

---

## 🌐 Deployment

*   **Backend**: Ready for **Render** or **AWS EC2** (Gunicorn).
*   **Frontend**: Static assets can be optimized for **Vercel** or **Netlify**.
*   **Storage**: Connect to a managed instance like **Supabase/ElephantSQL** or **AWS RDS**.

---

## 🔒 Security Features
*   **Password Salting/Hashing**: No plain-text passwords ever stored.
*   **Session-based Auth**: Server-side session management for secure document isolation.
*   **Input Sanitization**: Protection against SQL injection using parameterized queries via `psycopg2`.

---

## 🗺 Use Cases
*   **HR Automation**: Parsing resumes and verifying government IDs.
*   **Finance/Accounting**: Automating data entry from invoices and bills.
*   **Personal Management**: Organizing and searching through scanned documents and forms.

---

## 📈 Future Improvements
*   [ ] Multi-language OCR support.
*   [ ] Integration with OpenAI/Gemini for advanced reasoning.
*   [ ] Bulk processing for large document folders.
*   [ ] Mobile application with camera-based scanning.

---

## 👤 Author
**Akash Singh Chauhan**  
*Full Stack Developer & AI Enthusiast*

---

> **IntelliDoc** — Bridging the gap between physical documents and digital intelligence. ✨
