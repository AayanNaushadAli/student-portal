import os
import requests
import json
from pypdf import PdfReader
from dotenv import load_dotenv

# 1. Load keys
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("❌ Missing GEMINI_API_KEY in .env file!")

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
    # We use the raw REST API. This bypasses the buggy SDK.
    # We are using 'gemini-flash-latest' which appeared in your available list.
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        # ADD THIS BLOCK to allow long responses
        "generationConfig": {
            "maxOutputTokens": 8192,  # Huge limit so it doesn't cut off
            "temperature": 0.3        # Lower temp = More analytical/precise, less creative
        }
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            result = response.json()
            # Dig through the JSON to find the text answer
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"❌ Server Error {response.status_code}: {response.text}"
            
    except Exception as e:
        return f"❌ Connection Error: {e}"

# --- TEST AREA ---
if __name__ == "__main__":
    print("🤖 Testing Direct Connection (No SDK)...")
    reply = ask_gemini("Are you online?")
    print(f"\n💬 Gemini says: {reply}")