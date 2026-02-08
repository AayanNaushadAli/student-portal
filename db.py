import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import json
import streamlit as st

# 1. Load keys (Try local .env first)
load_dotenv()

def get_db_connection():
    try:
        # 1. First, check if we have a Cloud Link (Supabase) from .env
        database_url = os.getenv("DATABASE_URL")
        
        # 2. If that failed, try Streamlit Cloud Secrets
        if not database_url:
            try:
                database_url = st.secrets["DATABASE_URL"]
            except:
                pass
        
        if database_url:
            return psycopg2.connect(database_url)
            
        # 2. If no Cloud Link, try the old Local way (Fallback)
        else:
            return psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT")
            )
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None

# ... (The rest of your functions: login_user, save_file_record etc. are fine!) ...

# --- NEW FUNCTIONS FOR THE APP ---

def login_user(email):
    """Simple login: If email exists, return user. If not, create new one."""
    conn = get_db_connection()
    if not conn: return None
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # 1. Check if user exists
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        
        if not user:
            # 2. Create new user if not found
            cur.execute(
                "INSERT INTO users (email, full_name, xp) VALUES (%s, %s, %s) RETURNING *",
                (email, email.split('@')[0], 0)
            )
            user = cur.fetchone()
            conn.commit()
            
    conn.close()
    return user

def save_file_record(file_hash, filename, text_content):
    """Saves the file record to the DB"""
    conn = get_db_connection()
    if not conn: return False

    with conn.cursor() as cur:
        # Check for duplicates
        cur.execute("SELECT file_hash FROM master_files WHERE file_hash = %s", (file_hash,))
        if cur.fetchone():
            return True 

        # FIX: Wrap the raw text in a real JSON object
        json_data = json.dumps({"content": text_content})

        cur.execute(
            """INSERT INTO master_files (file_hash, file_name, syllabus_data, ai_status) 
               VALUES (%s, %s, %s, 'completed')""",
            (file_hash, filename, json_data) # Now sending valid JSON
        )
        conn.commit()
    conn.close()
    return True

def get_all_files():
    """Fetch all uploaded files to show in the UI"""
    conn = get_db_connection()
    if not conn: return []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM master_files ORDER BY created_at DESC")
        files = cur.fetchall()
    conn.close()
    return files

def update_ai_analysis(file_hash, analysis_text):
    """Updates the database with the AI's generated report"""
    conn = get_db_connection()
    if not conn: return False
    
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE master_files SET ai_analysis = %s, ai_status = 'analyzed' WHERE file_hash = %s",
            (analysis_text, file_hash)
        )
        conn.commit()
    conn.close()
    return True

def get_leaderboard():
    """Fetch top 10 students by XP"""
    conn = get_db_connection()
    if not conn: return []
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Get top 10 users, sorted by XP (Highest first)
        cur.execute("SELECT full_name, xp FROM users ORDER BY xp DESC LIMIT 10")
        leaders = cur.fetchall()
    conn.close()
    return leaders

def get_file_content(file_hash):
    """Fetch the raw text content of a file for the Chatbot"""
    conn = get_db_connection()
    if not conn: return None
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT syllabus_data FROM master_files WHERE file_hash = %s", (file_hash,))
        result = cur.fetchone()
        
    conn.close()
    
    if result and result['syllabus_data']:
        # The text is stored inside a JSON object: {"content": "..."}
        data = result['syllabus_data']
        # Handle cases where it might be a string or a dict depending on how it was saved
        if isinstance(data, str):
            import json
            data = json.loads(data)
        return data.get("content", "")
    return None

def save_document_sections(file_hash, sections):
    """Saves chunks and their embeddings to the document_sections table"""
    conn = get_db_connection()
    if not conn: return False
    
    with conn.cursor() as cur:
        # Clear existing sections for this hash to avoid duplicates if re-indexed
        cur.execute("DELETE FROM document_sections WHERE file_hash = %s", (file_hash,))
        
        for content, embedding in sections:
            cur.execute(
                "INSERT INTO document_sections (file_hash, content, embedding) VALUES (%s, %s, %s)",
                (file_hash, content, embedding)
            )
        conn.commit()
    conn.close()
    return True

def match_document_sections(file_hash, query_embedding, match_threshold=0.3, match_count=5):
    """Performs vector search using the match_document_sections RPC function"""
    conn = get_db_connection()
    if not conn: return []
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Calling the RPC function we created in Supabase
        cur.execute(
            "SELECT content, similarity FROM match_document_sections(%s, %s, %s, %s)",
            (query_embedding, match_threshold, match_count, file_hash)
        )
        results = cur.fetchall()
    conn.close()
    return [r['content'] for r in results]

    