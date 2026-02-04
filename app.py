import streamlit as st
import hashlib
from db import login_user, save_file_record, get_all_files, update_ai_analysis, get_leaderboard, get_db_connection
from utils import extract_text_from_pdf, ask_gemini

st.set_page_config(page_title="Student Portal", layout="wide")

# --- SIDEBAR: LOGIN ---
with st.sidebar:
    st.title("🎓 Student Portal")
    if "user" not in st.session_state:
        email = st.text_input("Enter Email to Login")
        if st.button("Start Studying"):
            if email:
                user = login_user(email)
                st.session_state["user"] = user
                st.rerun()
    else:
        user = st.session_state["user"]
        st.write(f"👤 **{user['full_name']}**")
        st.write(f"🔥 XP: {user['xp']}")
        if st.button("Logout"):
            del st.session_state["user"]
            st.rerun()
    # ... existing sidebar code ...
    
    st.markdown("---")
    st.subheader("🏆 Hall of Fame")
    
    # Import the function first! (from db import get_leaderboard)
    leaders = get_leaderboard()
    
    if leaders:
        for i, student in enumerate(leaders):
            # i+1 is the rank (1st, 2nd, 3rd...)
            st.write(f"**{i+1}. {student['full_name']}** — {student['xp']} XP")
    else:
        st.write("No competitors yet!")

# --- MAIN APP ---
if "user" in st.session_state:
    st.title("📚 My Study Dashboard")
    
    tab1, tab2 = st.tabs(["📂 My Notes", "🚀 AI Generator"])

    # TAB 1: VIEW NOTES
    # TAB 1: VIEW NOTES
    # TAB 1: VIEW NOTES
    with tab1:
        st.subheader("My Analyzed Papers")
        files = get_all_files()
        
        if not files:
            st.info("No papers analyzed yet. Go to the 'AI Generator' tab!")
            
        for f in files:
            # Show the file name
            with st.expander(f"📄 {f['file_name']} (Uploaded: {f['created_at']})"):
                
                # Check if analysis exists
                if f.get('ai_analysis'):
                    st.markdown("### 🧠 AI Strategy Report")
                    st.write(f['ai_analysis'])
                    
                    st.markdown("---")
                    
                    # --- THE REAL XP BUTTON ---
                    # We use a unique key for every button so Streamlit doesn't get confused
                    btn_key = f"btn_{f['file_hash']}"
                    
                    if st.button(f"🏆 Mark as Mastered (+100 XP)", key=btn_key):
                        # 1. Update Database (The Real Bank Transaction)
                        conn = get_db_connection()
                        with conn.cursor() as cur:
                            cur.execute(
                                "UPDATE users SET xp = xp + 100 WHERE email = %s",
                                (st.session_state["user"]["email"],)
                            )
                            conn.commit()
                        conn.close()
                        
                        # 2. Update the "Live" Session (So you see it instantly)
                        st.session_state["user"]["xp"] += 100
                        
                        # 3. Success Message & Rerun
                        st.toast(f"Boom! XP Added. Total: {st.session_state['user']['xp']}")
                        st.balloons()
                        
                        # Rerun to update the Leaderboard immediately
                        st.rerun()
                        
                else:
                    st.warning("Analysis pending or failed.")
    # TAB 2: UPLOAD & GENERATE
    # TAB 2: UPLOAD & GENERATE
    with tab2:
        st.header("Upload Previous Year Papers")
        # 1. Enable Multiple Files
        uploaded_files = st.file_uploader("Drop 5 years of papers here", type="pdf", accept_multiple_files=True)
        
        if uploaded_files:
            if st.button("⚡ Generate Exam Strategy"):
                
                # Create a progress bar
                progress_bar = st.progress(0)
                total_files = len(uploaded_files)
                
                for index, uploaded_file in enumerate(uploaded_files):
                    with st.status(f"Processing {uploaded_file.name}...", expanded=True) as status:
                        
                        # A. Read PDF
                        st.write("📖 Reading file...")
                        
                        # Fix: Pass the stream directly to pypdf (via utils.py)
                        # No need to save temp files!
                        raw_text = extract_text_from_pdf(uploaded_file)
                        
                        # B. Generate Hash (Unique ID)
                        file_hash = hashlib.md5(raw_text.encode()).hexdigest()
                        
                        # C. Save Raw Input to DB
                        st.write("💾 Saving to Database...")
                        save_file_record(file_hash, uploaded_file.name, raw_text)
                        
                        # D. Ask Gemini (The PRO Prompt)
                        st.write("🤖 AI Analyst is thinking...")
                        
                        prompt = f"""
                        Here is the text content from the uploaded exam paper ({uploaded_file.name}):
                        {raw_text}

                        ---------------------------------------------
                        INSTRUCTIONS:
                        Analyze this exam paper in detail. Your goal is to extract crystal-clear insights.
                        
                        Deliver the analysis in this structure:
                        1️⃣ Repeated Questions Analysis (Frequency & Topics)
                        2️⃣ Important Topics Priority List (High Weightage)
                        3️⃣ Chapter-wise Weightage (%)
                        4️⃣ Difficulty Assessment (Easy/Moderate/Hard)
                        5️⃣ Final Summary: Top 5 Expected Questions

                        Be highly accurate and structured.
                        """
                        
                        ai_response = ask_gemini(prompt)
                        
                        # E. Save AI Output to DB (NEW STEP)
                        update_ai_analysis(file_hash, ai_response)
                        
                        st.success("Analysis Saved!")
                        status.update(label=f"✅ {uploaded_file.name} Complete!", state="complete", expanded=False)
                    
                    # Update progress bar
                    progress_bar.progress((index + 1) / total_files)

                st.balloons()
                st.success("All files processed! Check 'My Notes' tab to view them.")
else:
    st.info("👈 Please log in from the sidebar to continue.")