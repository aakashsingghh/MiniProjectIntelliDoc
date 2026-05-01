import os
import sqlite3
import time
import json
import uuid
import cv2
import numpy as np
import pytesseract
import spacy
import re
from PIL import Image
from pdf2image import convert_from_path
from flask import Flask, render_template, request, redirect, url_for, send_file, flash, abort, session
from datetime import datetime
from dotenv import load_dotenv
from flask_cors import CORS
import tempfile
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from init_db import init_database

# Fallback NLP imports
import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer

# Make sure nltk data is available for sumy
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

# Load spacy for offline NLP
print("🤖 Loading AI models (spaCy)...")
try:
    nlp = spacy.load("en_core_web_sm")
    print("✅ AI models loaded.")
except OSError:
    print("Downloading en_core_web_sm model...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

load_dotenv()
init_database()

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY'] = 'intellidoc-secret-super-key'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ------------------------------------------------
# IN-MEMORY DATABASE
# ------------------------------------------------
documents = []
doc_id_counter = 1

class Document:
    def __init__(self, filename, document_type, extracted_text, structured_data, priority, summary, user_id=None, doc_id=None):
        global doc_id_counter
        if doc_id:
            self.id = doc_id
        else:
            self.id = doc_id_counter
            doc_id_counter += 1
        self.filename = filename
        self.document_type = document_type
        self.extracted_text = extracted_text
        self.structured_data = structured_data
        self.priority = priority
        self.summary = summary
        self.user_id = user_id
        self.created_at = datetime.utcnow()

# ------------------------------------------------
# STORAGE FUNCTIONS
# ------------------------------------------------
def get_db_connection():
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        try:
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
            return psycopg2.connect(db_url, connect_timeout=3)
        except Exception as e:
            print(f"📡 Render DB unreachable ({e}). Falling back to local SQLite...")
    return sqlite3.connect("intellidoc.db", check_same_thread=False)

def execute_query(conn, cur, sql, params=()):
    is_sqlite = isinstance(conn, sqlite3.Connection)
    if is_sqlite:
        sql = sql.replace("%s", "?").replace("ILIKE", "LIKE").replace("RETURNING id", "")
        # Remove RETURNING if it's there
        if "INSERT" in sql.upper() and "RETURNING" in sql.upper():
            sql = sql.split("RETURNING")[0]
        cur.execute(sql, params)
        return cur.lastrowid if "INSERT" in sql.upper() else None
    else:
        cur.execute(sql, params)
        if "RETURNING" in sql.upper():
            return cur.fetchone()[0]
        return None

def save_to_db(data, user_id, extracted_text=None, summary=None):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        name = data.get("Name") if data.get("Name") and data.get("Name") != "Not Found" else None
        dob = data.get("Date") if data.get("Date") and data.get("Date") != "Not Found" else None
        email = data.get("Email") if data.get("Email") and data.get("Email") != "Not Found" else None
        phone = data.get("Phone") if data.get("Phone") and data.get("Phone") != "Not Found" else None
        organization = data.get("Organization") if data.get("Organization") and data.get("Organization") != "Not Found" else None
        doc_type = data.get("Document Type") if data.get("Document Type") else None

        import json
        structured_data_json = json.dumps(data)

        sql = """
            INSERT INTO IDPtable (name, dob, email, phone, organization, document_type, user_id, extracted_text, summary, structured_data, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id
        """
        params = (name, dob, email, phone, organization, doc_type, user_id, extracted_text, summary, structured_data_json)
        new_id = execute_query(conn, cur, sql, params)
        
        conn.commit()
        cur.close()
        conn.close()
        return new_id
    except Exception as e:
        print(f"Database Error: {e}")
        return None

def save_to_json(data, user_id, username):
    try:
        file_path = "IDP.json"
        
        cleaned_data = {}
        for k in ["Name", "Date", "Email", "Phone", "Organization", "Document Type"]:
            val = data.get(k)
            cleaned_data[k] = "" if not val or val == "Not Found" else val
                
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try:
                    file_data = json.load(f)
                except:
                    file_data = []
        else:
            file_data = []
            
        user_entry = next((u for u in file_data if u.get("user_id") == user_id), None)
        if user_entry:
            user_entry["documents"].append(cleaned_data)
        else:
            file_data.append({
                "user_id": user_id,
                "username": username,
                "documents": [cleaned_data]
            })
        
        with open(file_path, "w") as f:
            json.dump(file_data, f, indent=4)
            
    except Exception as e:
        print(f"JSON Storage Error: {e}")

# ------------------------------------------------
# OCR & PREPROCESSING
# ------------------------------------------------
def preprocess_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    processed_path = image_path + "_processed.png"
    cv2.imwrite(processed_path, gray)
    return processed_path

def extract_text_from_file(filepath):
    ext = filepath.split('.')[-1].lower()
    extracted_text = ""
    try:
        if ext == 'pdf':
            pages = convert_from_path(filepath)
            for i, page in enumerate(pages):
                temp_page_path = f"{filepath}_page_{i}.png"
                page.save(temp_page_path, 'PNG')
                processed_img = preprocess_image(temp_page_path)
                if processed_img:
                    extracted_text += pytesseract.image_to_string(Image.open(processed_img))
                    os.remove(processed_img)
                os.remove(temp_page_path)
        elif ext in ['png', 'jpg', 'jpeg']:
            processed_img = preprocess_image(filepath)
            if processed_img:
                extracted_text = pytesseract.image_to_string(Image.open(processed_img))
                os.remove(processed_img)
    except Exception as e:
        print(f"OCR Error: {e}")
        
    return extracted_text.strip()

# ------------------------------------------------
# SMART DOCUMENT-AWARE EXTRACTION & SUMMARY (RULE-BASED + NLP)
# ------------------------------------------------
def clean_text(text):
    # Keep alphanumeric characters, spaces, and basic punctuation
    text = re.sub(r'[^\w\s\.,@:/\-₹]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def detect_document_type(text):
    text_lower = text.lower()
    
    # 1. PAN CARD
    if re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', text) or "income tax" in text_lower or "permanent account number" in text_lower:
        return "PAN Card"
        
    # 2. AADHAAR CARD
    if re.search(r'\b\d{4}\s\d{4}\s\d{4}\b', text) or "government of india" in text_lower or "aadhaar" in text_lower or "uidai" in text_lower:
        return "Aadhaar Card"
        
    # 3. RESUME
    resume_keywords = ["education", "skills", "experience", "projects"]
    if sum(1 for kw in resume_keywords if kw in text_lower) >= 2:
        return "Resume"
        
    # 4. INVOICE
    invoice_keywords = ["invoice", "bill", "amount", "total"]
    if sum(1 for kw in invoice_keywords if kw in text_lower) >= 2:
        return "Invoice"
        
    # 5. FORM
    form_keywords = ["name:", "dob:", "address:"]
    if sum(1 for kw in form_keywords if kw in text_lower) >= 2:
        return "Form"
        
    # 6. OTHERWISE
    return "Other"

def extract_structured_data(text, doc_type):
    doc = nlp(text)
    data = {
        "Name": "Not Found",
        "Date": "Not Found",
        "PAN Number": "Not Found",
        "Aadhaar Number": "Not Found",
        "Email": "Not Found",
        "Phone": "Not Found",
        "Organization": "Not Found",
        "Total Amount": "Not Found"
    }
    
    # Regex Extractions
    email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    if email_match: data["Email"] = email_match.group(0)
        
    phone_match = re.search(r'\+91[- ]?\d{10}|\b\d{10}\b|\b\d{5}[- ]?\d{5}\b', text)
    if phone_match: data["Phone"] = phone_match.group(0).replace(" ", "").replace("-", "")
        
    date_match = re.search(r'\b\d{2}[/-]\d{2}[/-]\d{4}\b', text)
    if date_match: data["Date"] = date_match.group(0)
        
    pan_match = re.search(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', text)
    if pan_match: data["PAN Number"] = pan_match.group(0)
        
    aadhaar_match = re.search(r'\b\d{4}\s\d{4}\s\d{4}\b', text)
    if aadhaar_match: data["Aadhaar Number"] = aadhaar_match.group(0)
    
    amount_match = re.search(r'(?:Rs\.?|INR|₹)\s*([\d,]+\.?\d*)', text, re.IGNORECASE)
    if amount_match: data["Total Amount"] = amount_match.group(1)
        
    # SpaCy Extractions
    persons = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
    orgs = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
    if orgs: data["Organization"] = orgs[0]
        
    # 1. Label-based Name Extraction
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    for line in lines:
        lower_line = line.lower()
        if "name:" in lower_line or "full name:" in lower_line or "applicant name:" in lower_line:
            parts = line.split(':', 1)
            if len(parts) > 1 and len(parts[1].strip()) > 2:
                data["Name"] = parts[1].strip()
                break
                
    # Keep positional extraction rules for PAN and Aadhaar as fallback for label
    if data["Name"] == "Not Found":
        if doc_type == "Aadhaar Card":
            for i, line in enumerate(lines):
                if "dob" in line.lower() or "date of birth" in line.lower() or "year of birth" in line.lower():
                    if i > 0:
                        data["Name"] = lines[i-1]
                    break
        elif doc_type == "PAN Card":
            for i, line in enumerate(lines):
                if "income tax" in line.lower() or "department" in line.lower() or "govt" in line.lower() or "government" in line.lower():
                    if i + 1 < len(lines):
                        potential_name = lines[i+1]
                        if "name" in potential_name.lower() and len(potential_name) < 6:
                            if i + 2 < len(lines):
                                data["Name"] = lines[i+2]
                        else:
                            data["Name"] = potential_name
                    break

    # 2. SpaCy PERSON
    if data["Name"] == "Not Found" or len(data["Name"]) <= 2:
        if persons:
            clean_person = re.sub(r'[^a-zA-Z\s]', '', persons[0]).strip()
            if len(clean_person) > 2:
                data["Name"] = clean_person
                
    # 3. Rule-based Fallback (ALL CAPS heuristic)
    if data["Name"] == "Not Found" or len(data["Name"]) <= 2:
        ignore_words = ["GOVT", "INDIA", "INCOME", "TAX", "DEPARTMENT", "ADDRESS", "FATHER", "DOB", "SIGNATURE", "PAN", "NAME"]
        for line in lines:
            line_upper = line.upper()
            if line.isupper() and re.match(r'^[A-Z]{2,}(?:\s[A-Z]{2,}){1,3}$', line):
                if not any(word in line_upper for word in ignore_words):
                    data["Name"] = line
                    break
                    
    # Clean Output
    if data["Name"] != "Not Found":
        cleaned_name = re.sub(r'[^a-zA-Z\s]', '', data["Name"])
        cleaned_name = re.sub(r'\s+', ' ', cleaned_name).strip()
        if len(cleaned_name) > 2:
            data["Name"] = cleaned_name.title()
        else:
            data["Name"] = "Not Found"
            
    filtered_data = {k: v for k, v in data.items() if v != "Not Found" and v != ""}
    return filtered_data

def generate_smart_summary(text, doc_type, data):
    name = data.get("Name", "Not Found")
    if name == "Unknown" or name == "Not Found" or not name:
        name = "an unidentified individual"
        
    org = data.get("Organization", "Not Found")
    
    if doc_type == "PAN Card":
        return f"This document appears to be a PAN Card belonging to {name}, issued by the Income Tax Department."
    elif doc_type == "Aadhaar Card":
        return f"This document appears to be an Aadhaar Card associated with {name}, issued by the Government of India."
    elif doc_type == "Resume":
        return f"This document appears to be a Resume of {name} highlighting skills and experience."
    elif doc_type == "Invoice":
        issued_by = org if org and org != "Not Found" else "XYZ Company"
        return f"This document appears to be an Invoice issued by {issued_by} with billing details."
    else:
        name_part = f"associated with {name}" if name != "an unidentified individual" else "an unidentified individual"
        return f"This document falls under 'Other' category and is {name_part}."

# ------------------------------------------------
# ROUTES
# ------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/health')
def health_check():
    return {"status": "healthy", "database": "connected" if os.environ.get('DATABASE_URL') else "local"}, 200

@app.route('/')
def index():
    if "demo_count" not in session:
        session["demo_count"] = 0
    return render_template('index.html')

@app.route('/demo', methods=['GET', 'POST'])
def demo():
    if "demo_count" not in session:
        session["demo_count"] = 0
        
    if session["demo_count"] >= 5:
        flash("Free demo limit reached. Please login to continue.")
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file uploaded")
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash("No selected file")
            return redirect(request.url)
            
        filename = str(uuid.uuid4()) + "_" + file.filename.replace(" ", "_")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        extracted_text = extract_text_from_file(filepath)
        cleaned_text = clean_text(extracted_text)
        
        doc_type = detect_document_type(cleaned_text)
        data_dict = extract_structured_data(cleaned_text, doc_type)
        summary = generate_smart_summary(cleaned_text, doc_type, data_dict)
        
        # Increment demo count
        session["demo_count"] += 1
        
        # Create a mock doc for the result template
        class DBObject:
            pass
        doc = DBObject()
        doc.id = int(time.time())
        doc.filename = "Demo_" + file.filename
        doc.document_type = doc_type
        doc.priority = "Demo"
        doc.created_at = datetime.now()
        doc.summary = summary
        doc.extracted_text = extracted_text
        
        structured_data = {k: v for k, v in data_dict.items() if v and v != "Not Found"}
        
        return render_template('demo_result.html', doc=doc, data=structured_data, remaining=5 - session["demo_count"])
        
    return render_template('demo.html', remaining=5 - session["demo_count"])

@app.route('/demo_status')
def demo_status():
    if "demo_count" not in session:
        session["demo_count"] = 0
    return {"remaining": 5 - session["demo_count"]}

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            hashed_pw = generate_password_hash(password)
            execute_query(conn, cur, "INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed_pw))
            conn.commit()
            cur.close()
            conn.close()
            flash("Registration successful. Please login.")
            return redirect(url_for('login'))
        except Exception as e:
            if "UNIQUE" in str(e) or (hasattr(e, 'pgcode') and e.pgcode == '23505'):
                flash("Username already exists.")
            else:
                flash(f"An error occurred: {e}")
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cur = conn.cursor()
        execute_query(conn, cur, "SELECT id, password_hash FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            return redirect(url_for('dashboard'))
            
        flash("Invalid username or password.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Dashboard only shows 8 recent docs
    execute_query(conn, cur, "SELECT id, name, document_type, created_at FROM IDPtable WHERE user_id = %s ORDER BY created_at DESC LIMIT 8", (session['user_id'],))
    user_docs = cur.fetchall()
    
    execute_query(conn, cur, "SELECT COUNT(*) FROM IDPtable WHERE user_id = %s", (session['user_id'],))
    total_docs = cur.fetchone()[0]
    
    execute_query(conn, cur, "SELECT document_type, COUNT(*) FROM IDPtable WHERE user_id = %s GROUP BY document_type", (session['user_id'],))
    type_counts = cur.fetchall()
    
    labels = []
    data = []
    for row in type_counts:
        labels.append(row[0] if row[0] else 'Other')
        data.append(row[1])
        
    most_common_type = labels[data.index(max(data))] if data else "N/A"
    
    execute_query(conn, cur, "SELECT name FROM IDPtable WHERE user_id = %s ORDER BY created_at DESC LIMIT 1", (session['user_id'],))
    latest_doc_row = cur.fetchone()
    latest_doc = latest_doc_row[0] if latest_doc_row and latest_doc_row[0] else "No files yet"
    cur.close()
    conn.close()
        
    return render_template('dashboard.html', user_docs=user_docs, total_docs=total_docs, labels=labels, data=data, most_common_type=most_common_type, latest_doc=latest_doc)

@app.route('/api/dashboard')
@login_required
def api_dashboard():
    conn = get_db_connection()
    cur = conn.cursor()
    execute_query(conn, cur, "SELECT id, name, document_type, created_at FROM IDPtable WHERE user_id = %s ORDER BY created_at DESC LIMIT 8", (session['user_id'],))
    user_docs = cur.fetchall()
    execute_query(conn, cur, "SELECT COUNT(*) FROM IDPtable WHERE user_id = %s", (session['user_id'],))
    total_docs = cur.fetchone()[0]
    execute_query(conn, cur, "SELECT document_type, COUNT(*) FROM IDPtable WHERE user_id = %s GROUP BY document_type", (session['user_id'],))
    type_counts = cur.fetchall()
    labels = [row[0] if row[0] else 'Other' for row in type_counts]
    data = [row[1] for row in type_counts]
    most_common_type = labels[data.index(max(data))] if data else "N/A"
    execute_query(conn, cur, "SELECT name FROM IDPtable WHERE user_id = %s ORDER BY created_at DESC LIMIT 1", (session['user_id'],))
    latest_doc_row = cur.fetchone()
    latest_doc = latest_doc_row[0] if latest_doc_row else "None"
    def format_date(d):
        if not d: return "Unknown"
        if isinstance(d, str):
            try:
                d = datetime.strptime(d.split('.')[0], '%Y-%m-%d %H:%M:%S')
            except:
                return d
        return d.strftime('%Y-%m-%d %H:%M')

    formatted_docs = [{"id": d[0], "name": d[1], "type": d[2], "date": format_date(d[3])} for d in user_docs]
    cur.close()
    conn.close()
    return {"total_docs": total_docs, "most_common_type": most_common_type, "latest_doc": latest_doc, "docs": formatted_docs, "chart_labels": labels, "chart_data": data, "username": session.get('username', 'User')}

@app.route('/documents')
@login_required
def documents_page():
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = request.args.get('q', '')
    doc_type = request.args.get('type', '')
    
    base_query = "SELECT id, name, document_type, created_at FROM IDPtable WHERE user_id = %s"
    params = [session['user_id']]
    
    if doc_type:
        base_query += " AND document_type = %s"
        params.append(doc_type)
        
    if query:
        base_query += " AND (name ILIKE %s OR document_type ILIKE %s)"
        params.extend([f"%{query}%", f"%{query}%"])
        
    base_query += " ORDER BY created_at DESC"
    
    execute_query(conn, cur, base_query, tuple(params))
    user_docs = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('documents.html', user_docs=user_docs, query=query, doc_type=doc_type)

@app.route('/search_suggestions')
@login_required
def search_suggestions():
    keyword = request.args.get('q', '')
    if not keyword:
        return {"suggestions": []}
        
    conn = get_db_connection()
    cur = conn.cursor()
    execute_query(conn, cur, "SELECT name, document_type FROM IDPtable WHERE user_id = %s AND name ILIKE %s LIMIT 5", (session['user_id'], f"%{keyword}%"))
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    suggestions = [{"name": row[0], "type": row[1]} for row in results if row[0]]
    return {"suggestions": suggestions}

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        business_name = request.form.get('business_name')
        company_type = request.form.get('company_type')
        
        execute_query(conn, cur, """
            UPDATE users 
            SET full_name = %s, email = %s, phone = %s, address = %s, business_name = %s, company_type = %s
            WHERE id = %s
        """, (full_name, email, phone, address, business_name, company_type, session['user_id']))
        conn.commit()
        flash("Profile updated successfully!")
        
    execute_query(conn, cur, "SELECT username, full_name, email, phone, address, business_name, company_type FROM users WHERE id = %s", (session['user_id'],))
    user_data = cur.fetchone()
    cur.close()
    conn.close()
    
    return render_template('profile.html', user=user_data)

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@app.route('/delete/<int:doc_id>', methods=['POST'])
@login_required
def delete_document(doc_id):
    conn = get_db_connection()
    cur = conn.cursor()
    execute_query(conn, cur, "DELETE FROM IDPtable WHERE id = %s AND user_id = %s", (doc_id, session['user_id']))
    conn.commit()
    cur.close()
    conn.close()
    flash("Document deleted successfully.")
    return redirect(url_for('dashboard'))

@app.route('/clear_all', methods=['POST'])
@login_required
def clear_all():
    conn = get_db_connection()
    cur = conn.cursor()
    execute_query(conn, cur, "DELETE FROM IDPtable WHERE user_id = %s", (session['user_id'],))
    conn.commit()
    cur.close()
    conn.close()
    flash("All documents cleared.")
    return redirect(url_for('dashboard'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part")
            return redirect(request.url)
            
        files = request.files.getlist('file')
        if not files or files[0].filename == '':
            flash("No selected file")
            return redirect(request.url)
            
        processed_ids = []
        user_id = session["user_id"]
        username = session.get("username", "Unknown")
        
        for file in files:
            if file and file.filename != '':
                filename = str(uuid.uuid4()) + "_" + file.filename.replace(" ", "_")
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                extracted_text = extract_text_from_file(filepath)
                cleaned_text = clean_text(extracted_text)
                
                # Smart Offline Processing
                doc_type = detect_document_type(cleaned_text)
                data_dict = extract_structured_data(cleaned_text, doc_type)
                extracted_data = json.dumps(data_dict)
                summary = generate_smart_summary(cleaned_text, doc_type, data_dict)
                
                # Save to Database and JSON
                structured_data = data_dict.copy()
                structured_data["Document Type"] = doc_type
                
                db_id = save_to_db(structured_data, user_id, extracted_text=extracted_text, summary=summary)
                save_to_json(structured_data, user_id, username)
                
                priority = "High" if doc_type in ["Invoice", "PAN Card", "Aadhaar Card"] else "Medium"
                    
                new_doc = Document(
                    filename=file.filename,
                    document_type=doc_type,
                    extracted_text=extracted_text,
                    structured_data=extracted_data,
                    priority=priority,
                    summary=summary,
                    user_id=user_id,
                    doc_id=db_id
                )
                
                documents.append(new_doc)
                processed_ids.append(new_doc.id)
                
        if processed_ids:
            return redirect(url_for('result', doc_id=processed_ids[0]))
            
    return render_template('upload.html')

@app.route('/result/<int:doc_id>')
@login_required
def result(doc_id):
    print(f"DEBUG: Viewing Document - USER_ID: {session.get('user_id')}, DOC_ID: {doc_id}")
    
    conn = get_db_connection()
    cur = conn.cursor()
    execute_query(conn, cur, "SELECT id, name, document_type, created_at, dob, email, phone, organization, extracted_text, summary FROM IDPtable WHERE id = %s AND user_id = %s", (doc_id, session['user_id']))
    doc_row = cur.fetchone()
    cur.close()
    conn.close()
    
    if not doc_row:
        print(f"DEBUG: Document {doc_id} NOT FOUND for user {session.get('user_id')}")
        flash("Document not found or access denied.")
        return redirect(url_for('dashboard'))
        
    doc_id_db, name, doc_type, created_at, dob, email, phone, org, db_text, db_summary = doc_row
    
    # Try to find corresponding in-memory doc for summary/text (as fallback)
    in_memory_doc = None
    for d in documents:
        if d.id == doc_id:
            in_memory_doc = d
            break
                
    summary = db_summary if db_summary else (in_memory_doc.summary if in_memory_doc else f"This is a {doc_type} record. AI Summary is securely stored in logs.")
    text = db_text if db_text else (in_memory_doc.extracted_text if in_memory_doc else "Raw text is archived.")
    
    class DBObject:
        pass
        
    doc = DBObject()
    doc.id = doc_id_db
    doc.filename = name if name else "Uploaded Document"
    doc.document_type = doc_type
    doc.priority = "High" if doc_type in ["Invoice", "PAN Card", "Aadhaar Card"] else "Medium"
    # Handle SQLite returning dates as strings
    if isinstance(created_at, str):
        try:
            # Common SQLite format: 2026-05-01 04:00:00
            created_at = datetime.strptime(created_at.split('.')[0], '%Y-%m-%d %H:%M:%S')
        except:
            created_at = datetime.now()

    doc.created_at = created_at
    doc.summary = summary
    doc.extracted_text = text
    
    structured_data = {
        "Name": name,
        "DOB": dob,
        "Email": email,
        "Phone": phone,
        "Organization": org
    }
    structured_data = {k: v for k, v in structured_data.items() if v and v != "Not Found"}
    
    return render_template('result.html', doc=doc, data=structured_data)

@app.route('/api/document/<int:doc_id>')
@login_required
def api_document(doc_id):
    conn = get_db_connection()
    cur = conn.cursor()
    execute_query(conn, cur, "SELECT name, document_type, dob, email, phone, organization, extracted_text, summary, structured_data FROM IDPtable WHERE id = %s AND user_id = %s", (doc_id, session['user_id']))
    doc_row = cur.fetchone()
    cur.close()
    conn.close()
    
    if not doc_row:
        return {"error": "Not found"}, 404
        
    name, doc_type, dob, email, phone, org, db_text, db_summary, db_structured = doc_row
    
    return {
        "id": doc_id,
        "name": name,
        "document_type": doc_type,
        "summary": db_summary,
        "extracted_text": db_text,
        "structured_data": db_structured if db_structured else {},
        "entities": {
            "Name": name,
            "Date": dob,
            "Email": email,
            "Phone": phone,
            "Organization": org
        }
    }

@app.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    doc_type = request.args.get('type', '')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    base_query = "SELECT id, name, document_type, created_at FROM IDPtable WHERE user_id = %s"
    params = [session['user_id']]
    
    if doc_type:
        base_query += " AND document_type = %s"
        params.append(doc_type)
        
    if query:
        base_query += " AND (name ILIKE %s OR document_type ILIKE %s)"
        params.extend([f"%{query}%", f"%{query}%"])
        
    base_query += " ORDER BY created_at DESC"
    
    execute_query(conn, cur, base_query, tuple(params))
    db_docs = cur.fetchall()
    cur.close()
    conn.close()
    
    # Format to match template expectations if search template differs
    # The search template currently loops over object properties (d.filename, d.document_type)
    # We should pass objects with those attributes
    class DBDoc:
        def __init__(self, id, filename, document_type, created_at):
            self.id = id
            self.filename = filename if filename else "Unknown"
            self.document_type = document_type
            self.created_at = created_at
            self.priority = "Medium"
            self.extracted_text = ""
            self.summary = ""

    docs = [DBDoc(row[0], row[1], row[2], row[3]) for row in db_docs]
    
    return render_template('search.html', docs=docs, query=query, doc_type=doc_type)

@app.route('/download/<int:doc_id>/<format>')
@login_required
def download(doc_id, format):
    doc = next((d for d in documents if d.id == doc_id and getattr(d, 'user_id', None) == session["user_id"]), None)
    if not doc:
        abort(404)
    
    if format == 'txt':
        fd, path = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(f"Filename: {doc.filename}\n")
            f.write(f"Type: {doc.document_type}\n")
            f.write(f"Priority: {doc.priority}\n\n")
            f.write("=== SUMMARY ===\n")
            f.write(f"{doc.summary.replace('<mark>', '').replace('</mark>', '').replace('<b>', '').replace('</b>', '')}\n\n")
            f.write("=== STRUCTURED DATA ===\n")
            f.write(f"{doc.structured_data}\n\n")
            f.write("=== EXTRACTED TEXT ===\n")
            f.write(f"{doc.extracted_text}\n")
        return send_file(path, as_attachment=True, download_name=f"intellidoc_{doc_id}.txt")
        
    elif format == 'pdf':
        fd, path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd) 
        
        # We need a fallback mechanism if reportlab is not there
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from reportlab.lib.utils import simpleSplit
        except ImportError:
            abort(500, "Reportlab not installed for PDF generation.")
            
        c = canvas.Canvas(path, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, f"INTELLIDOC Report - {doc.filename}")
        
        c.setFont("Helvetica", 12)
        c.drawString(50, 720, f"Type: {doc.document_type}  |  Priority: {doc.priority}")
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 680, "Summary:")
        c.setFont("Helvetica", 12)
        
        y_position = 660
        clean_summary = doc.summary.replace('<mark>', '').replace('</mark>', '').replace('<b>', '').replace('</b>', '')
        lines = simpleSplit(clean_summary, "Helvetica", 12, 500)
        for line in lines:
            c.drawString(50, y_position, line)
            y_position -= 20
            
        y_position -= 20
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "Structured Data:")
        y_position -= 20
        c.setFont("Helvetica", 12)
        
        try:
            parsed_data = json.loads(doc.structured_data)
            for k, v in parsed_data.items():
                c.drawString(50, y_position, f"{k.capitalize()}: {v}")
                y_position -= 20
        except:
            pass
            
        y_position -= 20
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "Extracted Text Snippet:")
        y_position -= 20
        c.setFont("Helvetica", 10)
        snippet_lines = simpleSplit(doc.extracted_text[:1000] + "...", "Helvetica", 10, 500)
        for line in snippet_lines:
            if y_position < 50:
                c.showPage()
                y_position = 750
            c.drawString(50, y_position, line)
            y_position -= 15
            
        c.save()
        return send_file(path, as_attachment=True, download_name=f"intellidoc_{doc_id}.pdf")

    return redirect(url_for('result', doc_id=doc_id))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
