import os
import requests
from dotenv import load_dotenv

# 1. Load your key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Error: API Key not found in .env")
    exit()

# 2. Ask Google directly via URL (No SDK)
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
print(f"🔍 Contacting Google API directly...")

try:
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ YOUR AVAILABLE MODELS:")
        found_any = False
        for m in data.get('models', []):
            # Only show models that can generate text
            if "generateContent" in m.get('supportedGenerationMethods', []):
                # Clean up the name (remove 'models/' prefix)
                clean_name = m['name'].replace('models/', '')
                print(f" - {clean_name}")
                found_any = True
        
        if not found_any:
            print("⚠️ No text-generation models found. This is weird.")
            
    else:
        print(f"\n❌ Server Error: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"\n❌ Connection Error: {e}")