# 🛠️ Solutions & Implementation Guide

This document provides detailed solutions for each issue identified in `project_issues.md`.

---

## 🔴 Critical: Issue #1 – Password Authentication

### Database Changes
```sql
-- Add password column to users table
ALTER TABLE users ADD COLUMN password_hash VARCHAR(255);
```

### Code Changes (`db.py`)
```python
import bcrypt

def register_user(email, password, full_name):
    """Register a new user with password hashing"""
    conn = get_db_connection()
    if not conn: return None
    
    # Hash the password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.salt(12))
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "INSERT INTO users (email, password_hash, full_name, xp) VALUES (%s, %s, %s, %s) RETURNING *",
            (email, password_hash.decode('utf-8'), full_name, 0)
        )
        user = cur.fetchone()
        conn.commit()
    conn.close()
    return user

def login_user(email, password):
    """Login with email + password verification"""
    conn = get_db_connection()
    if not conn: return None
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
    conn.close()
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        return user
    return None
```

### UI Changes (`app.py`)
```python
# In sidebar
email = st.text_input("Email")
password = st.text_input("Password", type="password")
if st.button("Login"):
    user = login_user(email, password)
    if user:
        st.session_state["user"] = user
        st.rerun()
    else:
        st.error("Invalid credentials")
```

---

## 🔴 Critical: Issue #2 – User-Specific Files

### Database Changes
```sql
-- Add user_id foreign key to master_files
ALTER TABLE master_files ADD COLUMN user_id INTEGER REFERENCES users(id);
```

### Code Changes (`db.py`)
```python
def save_file_record(file_hash, filename, text_content, user_id):
    """Saves the file record linked to a specific user"""
    # ... existing code ...
    cur.execute(
        """INSERT INTO master_files (file_hash, file_name, syllabus_data, ai_status, user_id) 
           VALUES (%s, %s, %s, 'completed', %s)""",
        (file_hash, filename, json_data, user_id)
    )

def get_user_files(user_id):
    """Fetch only files uploaded by this user"""
    conn = get_db_connection()
    if not conn: return []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT * FROM master_files WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,)
        )
        files = cur.fetchall()
    conn.close()
    return files
```

### UI Changes (`app.py`)
```python
# Replace get_all_files() with:
files = get_user_files(st.session_state["user"]["id"])
```

---

## 🟠 Medium: Issue #3 – Prevent XP Abuse

### Database Changes
```sql
-- Create progress tracking table
CREATE TABLE user_file_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    file_hash VARCHAR(64),
    mastered BOOLEAN DEFAULT FALSE,
    mastered_at TIMESTAMP,
    UNIQUE(user_id, file_hash)
);
```

### Code Changes (`db.py`)
```python
def is_file_mastered(user_id, file_hash):
    """Check if user already mastered this file"""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT mastered FROM user_file_progress WHERE user_id = %s AND file_hash = %s",
            (user_id, file_hash)
        )
        result = cur.fetchone()
    conn.close()
    return result and result[0]

def mark_as_mastered(user_id, file_hash):
    """Mark file as mastered and award XP (only once)"""
    if is_file_mastered(user_id, file_hash):
        return False  # Already claimed
    
    conn = get_db_connection()
    with conn.cursor() as cur:
        # Insert progress record
        cur.execute(
            "INSERT INTO user_file_progress (user_id, file_hash, mastered, mastered_at) VALUES (%s, %s, TRUE, NOW())",
            (user_id, file_hash)
        )
        # Award XP
        cur.execute("UPDATE users SET xp = xp + 100 WHERE id = %s", (user_id,))
        conn.commit()
    conn.close()
    return True
```

---

## 🟠 Medium: Issue #4 – Per-File Chat History

### Code Changes (`app.py`)
```python
# Initialize chat history per file
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}

# Get/create history for selected file
if selected_hash not in st.session_state.chat_histories:
    st.session_state.chat_histories[selected_hash] = []

messages = st.session_state.chat_histories[selected_hash]

# Use 'messages' for display and append
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# When adding new messages:
st.session_state.chat_histories[selected_hash].append({"role": "user", "content": prompt})
```

---

## 🟠 Medium: Issue #5 – Email Validation

### Code Changes (`app.py`)
```python
import re

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# In sidebar
email = st.text_input("Email")
if st.button("Login"):
    if not is_valid_email(email):
        st.error("Please enter a valid email address")
    else:
        # proceed with login
```

---

## 🟡 Low: Issue #6 – Calculate Real Rank

### Code Changes (`db.py`)
```python
def get_user_rank(user_id):
    """Calculate user's global rank based on XP"""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) + 1 as rank
            FROM users u1
            WHERE u1.xp > (SELECT xp FROM users WHERE id = %s)
        """, (user_id,))
        result = cur.fetchone()
    conn.close()
    return result[0] if result else 0
```

### UI Changes (`app.py`)
```python
# Replace hardcoded #5
rank = get_user_rank(st.session_state["user"]["id"])
st.metric(label="Global Rank", value=f"#{rank}")
```

---

## 🟡 Low: Issue #7 – Make "Open" Button Work

### Code Changes (`app.py`)
```python
# Store which file is "open"
if "selected_file" not in st.session_state:
    st.session_state.selected_file = None

# In the card loop
if st.button("Open", key=f"btn_{file['file_hash']}"):
    st.session_state.selected_file = file

# Below the cards, show the selected file's analysis
if st.session_state.selected_file:
    f = st.session_state.selected_file
    st.markdown(f"### 🧠 Analysis for {f['file_name']}")
    st.write(f.get('ai_analysis', 'No analysis available'))
```

---

## 📦 Dependencies to Add

```txt
# requirements.txt
bcrypt==4.1.2
```

---

## 🔵 React Migration (Future)

For React frontend, create a new project:
```bash
npx create-vite@latest frontend --template react-ts
cd frontend
npm install axios zustand @supabase/supabase-js
```

Backend API structure (FastAPI):
```
backend/
├── main.py          # FastAPI app
├── routes/
│   ├── auth.py      # Login/Register endpoints
│   ├── files.py     # File upload/list endpoints
│   └── chat.py      # Chat endpoints
├── models/
│   └── schemas.py   # Pydantic models
└── requirements.txt
```

---

## ✅ Implementation Priority

| Priority | Issue | Effort |
|----------|-------|--------|
| 1 | Files Globally Visible (#2) | 🟢 Easy |
| 2 | Password Authentication (#1) | 🟡 Medium |
| 3 | Per-File Chat History (#4) | 🟢 Easy |
| 4 | XP Abuse (#3) | 🟡 Medium |
| 5 | Email Validation (#5) | 🟢 Easy |
| 6 | Real Rank (#6) | 🟢 Easy |
| 7 | Open Button (#7) | 🟢 Easy |
