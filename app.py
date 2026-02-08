import streamlit as st
import hashlib
from db import (
    login_user, save_file_record, get_all_files, update_ai_analysis, 
    get_leaderboard, get_db_connection, get_file_content,
    save_document_sections, match_document_sections
)
from utils import extract_text_from_pdf, ask_gemini, ask_gemini_chat, generate_embedding

st.set_page_config(page_title="Student Portal", layout="wide")

def apply_custom_css():
    st.markdown("""
        <style>
            /* 1. Main Background & Font */
            .stApp {
                background-color: #0E1117;
                font-family: 'Segoe UI', sans-serif;
            }
            
            /* 2. Sidebar styling */
            [data-testid="stSidebar"] {
                background-color: #161B22;
                border-right: 1px solid #30363D;
            }
            
            /* 3. Cards for the Files */
            div.stButton > button {
                width: 100%;
                border-radius: 8px;
                border: 1px solid #30363D;
                background-color: #21262D;
                color: #C9D1D9;
                transition: all 0.3s;
            }
            div.stButton > button:hover {
                background-color: #30363D;
                border-color: #8B949E;
                color: #FFFFFF;
            }
            
            /* 4. Chat Message Bubbles */
            .stChatMessage {
                background-color: #161B22;
                border: 1px solid #30363D;
                border-radius: 10px;
                padding: 10px;
            }
            
            /* 5. Headers */
            h1, h2, h3 {
                color: #58A6FF !important;
            }
            
            /* 6. Tabs */
            .stTabs [data-baseweb="tab-list"] {
                gap: 10px;
            }
            .stTabs [data-baseweb="tab"] {
                background-color: #161B22;
                border-radius: 5px;
                padding: 10px 20px;
                border: 1px solid #30363D;
            }
            .stTabs [aria-selected="true"] {
                background-color: #238636 !important;
                color: white !important;
            }
        </style>
    """, unsafe_allow_html=True)

# CALL THE FUNCTION IMMEDIATELY
apply_custom_css()

# --- SIDEBAR: LOGIN ---
with st.sidebar:
    st.title("🎓 Student Portal")
    if "user" not in st.session_state:
        email = st.text_input("Enter Email to Login")
        if st.button("Start Studying"):
            if email:
                user = login_user(email)
                if user:
                    st.session_state["user"] = user
                    st.rerun()
                else:
                    st.error("❌ Login failed: Connection to database failed. Please try again later.")
    else:
        user = st.session_state.get("user")
        if not user:
            del st.session_state["user"]
            st.rerun()
            
        st.write(f"👤 **{user['full_name']}**")
        st.write(f"🔥 XP: {user['xp']}")
        if st.button("Logout"):
            del st.session_state["user"]
            st.rerun()
    # ... existing sidebar code ...
    
    # 👇 ADD THIS "DEV TOOLS" SECTION AT THE BOTTOM
    st.markdown("---")
    st.subheader("🛠️ Dev Tools")
    if st.button("🗑️ Wipe All Files (Reset DB)"):
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE master_files CASCADE;")
                # Also truncate document_sections if it exists
                cur.execute("TRUNCATE TABLE document_sections CASCADE;")
                conn.commit()
            conn.close()
            st.success("Database Wiped! Please refresh.")
            st.rerun()
        else:
            st.error("Failed to connect to database.")

# --- DIALOGS ---
@st.dialog("📄 Note Analysis", width="large")
def show_analysis(file_name, analysis):
    st.markdown(f"### {file_name}")
    st.markdown(analysis)
    if st.button("Close"):
        st.rerun()

# --- MAIN APP ---
if "user" in st.session_state:
    st.title("📚 My Study Dashboard")
    
    tab1, tab2, tab3 = st.tabs(["📂 My Notes", "🚀 AI Generator", "💬 Chat Assistant"])

    # TAB 1: VIEW NOTES
    # TAB 1: VIEW NOTES
    # TAB 1: VIEW NOTES
    with tab1:
        st.header("📚 My Study Dashboard")
        
        # Define files here!
        files = get_all_files()
        
        # Grid Layout for stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Total Papers", value=len(files))
        with col2:
            st.metric(label="Total XP", value=st.session_state["user"]['xp'])
        with col3:
            st.metric(label="Global Rank", value="#5") # Placeholder for now

        st.divider()
        st.subheader("Your Library")

        if not files:
            st.info("📂 No files uploaded yet. Go to the 'AI Generator' tab to start!")
        else:
            # Display files in a nice grid instead of a list
            for file in files:
                with st.container():
                    # Create a "Card" look using columns
                    c1, c2, c3 = st.columns([0.1, 0.7, 0.2])
                    
                    with c1:
                        st.markdown("📄") # Icon
                    with c2:
                        st.markdown(f"**{file['file_name']}**")
                        st.caption(f"Uploaded: {file['created_at'].strftime('%Y-%m-%d')}")
                    with c3:
                        if st.button("Open", key=f"btn_{file['file_hash']}"):
                            if file.get('ai_analysis'):
                                show_analysis(file['file_name'], file['ai_analysis'])
                            else:
                                st.warning("Analysis not yet generated for this file.")
                    
                    st.divider() # Thin line between items
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
                        
                        # E. Save AI Output to DB
                        update_ai_analysis(file_hash, ai_response)
                        
                        # F. CHUNKING & EMBEDDINGS (NEW: RAG Preparation)
                        st.write("🧠 Indexing for Chat...")
                        # Simple chunking: split by paragraphs or every 1000 chars
                        chunks = [raw_text[i:i+1000] for i in range(0, len(raw_text), 1000)]
                        
                        sections_to_save = []
                        for chunk in chunks:
                            vector = generate_embedding(chunk)
                            if vector:
                                sections_to_save.append((chunk, vector))
                        
                        if sections_to_save:
                            save_document_sections(file_hash, sections_to_save)
                        
                        st.success("Analysis Saved & Indexed!")
                        status.update(label=f"✅ {uploaded_file.name} Complete!", state="complete", expanded=False)
                    
                    # Update progress bar
                    progress_bar.progress((index + 1) / total_files)

                st.balloons()
                st.success("All files processed! Check 'My Notes' tab to view them.")
    # TAB 3: CHAT ASSISTANT
    with tab3:
        st.header("💬 Chat with a Paper")
        
        # 1. Select a File
        files = get_all_files()
        file_options = {f['file_name']: f['file_hash'] for f in files}
        
        selected_file_name = st.selectbox("Choose a paper to discuss:", list(file_options.keys()))
        
        if selected_file_name:
            selected_hash = file_options[selected_file_name]
            
            # Initialize Chat History
            if "messages" not in st.session_state:
                st.session_state.messages = []
            
            # --- CRITICAL FIX: DISPLAY MESSAGES FIRST ---
            # Create a container specifically for the chat history
            chat_container = st.container()
            
            with chat_container:
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
            
            # --- INPUT BOX COMES LAST ---
            # This ensures it stays at the bottom or below the messages
            if prompt := st.chat_input(f"Ask about {selected_file_name}..."):
                
                # 1. Show User Message immediately
                with chat_container: # Write to the container we created above
                    with st.chat_message("user"):
                        st.markdown(prompt)
                
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                # 2. Get AI Response
                with chat_container: # Write to the container
                    with st.chat_message("assistant"):
                        with st.spinner("Searching document..."):
                            # 1. Generate embedding for the question
                            query_vector = generate_embedding(prompt)
                            
                            if query_vector:
                                # 2. Find relevant chunks
                                relevant_chunks = match_document_sections(selected_hash, query_vector)
                                
                                if relevant_chunks:
                                    # 3. Ask Gemini with context
                                    response = ask_gemini_chat(prompt, relevant_chunks)
                                    st.markdown(response)
                                    st.session_state.messages.append({"role": "assistant", "content": response})
                                else:
                                    st.error("I couldn't find any relevant sections in the paper.")
                            else:
                                st.error("Failed to generate embedding for your question.")

else:
    st.info("👈 Please log in from the sidebar to continue.")