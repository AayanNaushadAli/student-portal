# Suggestions & Missing Items

While the MVP specification is solid, here are a few technical necessities and suggestions to ensure smooth implementation:

## 1. Environment Configuration (.env)
We need a secure way to store credentials.
**Action**: Create a `.env` file (and add to .gitignore) with:
```
SUPABASE_URL="your_supabase_url"
SUPABASE_KEY="your_supabase_anon_key"
GEMINI_API_KEY="your_gemini_api_key"
```

## 2. Dependencies (requirements.txt)
To ensure the environment can be reproduced.
**Action**: Create `requirements.txt`:
```
streamlit
supabase
google-generativeai
python-dotenv
pypdf
```

## 3. Error Handling
- **PDF Extraction**: what if the PDF is scanned images (no text)? We might need OCR (Tesseract) or use Gemini 1.5 Pro's native document understanding if simple text extraction fails.
- **AI Failures**: Retry logic if the API call fails or returns malformed JSON.

## 4. Session State Management
Streamlit reruns the script on every interaction. We need to persist user login state and selected topics using `st.session_state`.

## 5. Deployment strategy
Where will this run?
- **Local**: `streamlit run app.py`
- **Cloud**: Streamlit Cloud is the easiest free option (requires a GitHub repo).

## 6. Database Schema Refinements
- **Users**: Need to link `users` to `auth.users` in Supabase for security, or just use a simple custom table if security isn't critical for MVP.
- **Topics**: Need a `status` field (e.g., 'pending', 'generated') to track generation progress.
