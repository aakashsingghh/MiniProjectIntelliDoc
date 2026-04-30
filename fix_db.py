import psycopg2
from config import DB_CONFIG

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Get a valid user ID (the first user created)
    cur.execute("SELECT id FROM users ORDER BY created_at ASC LIMIT 1;")
    user_row = cur.fetchone()
    
    if user_row:
        valid_user_id = user_row[0]
        cur.execute("UPDATE IDPtable SET user_id = %s WHERE user_id IS NULL", (valid_user_id,))
        conn.commit()
        print(f"Successfully updated {cur.rowcount} rows in IDPtable to user_id = {valid_user_id}")
    else:
        print("No users found in the database. Cannot assign user_id.")
        
    cur.close()
    conn.close()
except Exception as e:
    print("Error:", e)
