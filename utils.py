import os
import requests
import json
import streamlit as st
from pypdf import PdfReader
from dotenv import load_dotenv

# 1. Load keys (Try local .env first)
load_dotenv()

# 2. Smart Key Retrieval
# Try to get it from the OS (Local .env)
api_key = os.getenv("GEMINI_API_KEY")

# If that failed, try to get it from Streamlit Cloud Secrets
if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except:
        pass

# If BOTH fail, then crash
if not api_key:
    raise ValueError("❌ Missing GEMINI_API_KEY! Check your .env (Local) or Streamlit Secrets (Cloud).")

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        return None

def ask_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "maxOutputTokens": 8192,
            "temperature": 0.3
        }
    }

    try:
        # We generally don't need verify=False on the cloud, but you can add it if needed.
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"❌ Server Error {response.status_code}: {response.text}"
            
    except Exception as e:
        return f"❌ Connection Error: {e}"