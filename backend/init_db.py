import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def init_database():
    db_url = os.environ.get('DATABASE_URL')
    
    # On Render/Production, DATABASE_URL is provided and DB is already created
    if not db_url:
        print("Running locally. Checking/Creating database 'intellidoc'...")
        try:
            conn = psycopg2.connect(
                user=os.environ.get("DB_USER", "postgres"), 
                password=os.environ.get("DB_PASSWORD", "your_password"), 
                host=os.environ.get("DB_HOST", "localhost"), 
                port=os.environ.get("DB_PORT", "5432")
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur = conn.cursor()
            
            cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'intellidoc'")
            exists = cur.fetchone()
            
            if not exists:
                cur.execute("CREATE DATABASE intellidoc;")
                print("✅ Database 'intellidoc' created successfully.")
            else:
                print("⚡ Database 'intellidoc' already exists.")
                
            cur.close()
            conn.close()
        except Exception as e:
            print(f"⚠️ Warning during database creation: {e}")
            
    # Connect to the database to create tables
    try:
        if db_url:
            conn = psycopg2.connect(db_url)
        else:
            conn = psycopg2.connect(
                dbname="intellidoc", 
                user=os.environ.get("DB_USER", "postgres"), 
                password=os.environ.get("DB_PASSWORD", "your_password"), 
                host=os.environ.get("DB_HOST", "localhost"), 
                port=os.environ.get("DB_PORT", "5432")
            )
        
        cur = conn.cursor()
        
        # Create Users Table
        cur.execute("""
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
        """)
        
        # Create IDPtable with all required columns
        cur.execute("""
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
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Database tables created or verified successfully.")
    except Exception as e:
        print(f"❌ Table creation error: {e}")

if __name__ == "__main__":
    init_database()
