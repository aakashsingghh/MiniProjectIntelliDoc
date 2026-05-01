import os
import psycopg2
import sqlite3

def init_database():
    db_url = os.environ.get('DATABASE_URL')
    
    conn = None
    cur = None
    is_sqlite = False
    
    # Try to initialize PostgreSQL if URL is present
    if db_url:
        try:
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
            conn = psycopg2.connect(db_url, connect_timeout=3)
            cur = conn.cursor()
            print("📡 [Backend] Initializing Render PostgreSQL...")
        except Exception as e:
            print(f"📡 [Backend] Render DB unreachable ({e}). Using local SQLite for initialization.")
            db_url = None

    if not db_url:
        conn = sqlite3.connect("intellidoc.db")
        cur = conn.cursor()
        is_sqlite = True
        print("🏠 [Backend] Initializing local SQLite (intellidoc.db)...")

    # Define table creation SQL
    user_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            business_name TEXT,
            company_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """ if is_sqlite else """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            business_name TEXT,
            company_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """

    idp_table_sql = """
        CREATE TABLE IF NOT EXISTS IDPtable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            dob TEXT,
            email TEXT,
            phone TEXT,
            organization TEXT,
            document_type TEXT,
            user_id INTEGER REFERENCES users(id),
            extracted_text TEXT,
            summary TEXT,
            structured_data JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """ if is_sqlite else """
        CREATE TABLE IF NOT EXISTS IDPtable (
            id SERIAL PRIMARY KEY,
            name TEXT,
            dob TEXT,
            email TEXT,
            phone TEXT,
            organization TEXT,
            document_type TEXT,
            user_id INTEGER REFERENCES users(id),
            extracted_text TEXT,
            summary TEXT,
            structured_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """

    try:
        cur.execute(user_table_sql)
        cur.execute(idp_table_sql)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ [Backend] Database tables created or verified successfully.")
    except Exception as e:
        print(f"❌ [Backend] Table creation error: {e}")
