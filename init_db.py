import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def init_database():
    # 1. Connect to default 'postgres' database to create 'intellidoc'
    try:
        conn = psycopg2.connect(user="postgres", password="your_password", host="localhost", port="5432")
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Check if db exists
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
        print("Make sure PostgreSQL is running and the password 'your_password' is correct.")

    # 2. Connect to 'intellidoc' to create table
    try:
        conn = psycopg2.connect(dbname="intellidoc", user="postgres", password="your_password", host="localhost", port="5432")
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS IDPtable (
                id SERIAL PRIMARY KEY,
                name TEXT,
                dob TEXT,
                email TEXT,
                phone TEXT,
                organization TEXT,
                document_type TEXT,
                created_at TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Table 'IDPtable' created or verified successfully.")
    except Exception as e:
        print(f"❌ Table creation error: {e}")

if __name__ == "__main__":
    init_database()
