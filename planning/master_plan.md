# The Master To-Do List - Class Note Generator MVP

We will work in `c:\Users\aayan\OneDrive\Desktop\This Pc\P-dashboard\idk`.

## Phase 1: The Foundation (Database & Setup)
- [ ] **Create Supabase Project**: Set up a free project on Supabase.
- [ ] **Create Tables**: Run the SQL to create:
    - `users` (id, email, college, xp)
    - `classrooms` (id, branch, section)
    - `master_files` (hash, file_path, status)
    - `topics` (id, unit, title, content_markdown)
- [ ] **Setup Storage Bucket**: Create a bucket named `raw_uploads` (for PDFs).
- [ ] **Connect Python**: Create a basic `db.py` script to test connection.

## Phase 2: The "Brain" (AI Pipeline)
- [ ] **PDF Text Extractor**: Write a script (`utils.py`) to extract text from an uploaded PDF.
- [ ] **The Syllabus Parser**: Create a prompt for Gemini: "Extract the list of Units and Topics from this text and return JSON."
- [ ] **The Note Generator**: Create the loop:
    - Input: Topic Name + PYQ Context.
    - Prompt: "Write a detailed 3-page study guide for [Topic] focusing on these past questions."
    - Output: Markdown text.

## Phase 3: The Interface (Streamlit UI)
- [ ] **Login Screen**: Simple email/password (handled by Supabase Auth).
- [ ] **The Dashboard**: A dropdown to select College/Class.
- [ ] **Upload Zone**: A drag-and-drop box for Syllabus/PYQs.
- [ ] **Study View**: A sidebar listing "Unit 1... Unit 5". Clicking a Unit shows the list of generated Topics.
- [ ] **Content Renderer**: Display the AI Markdown nicely (with formulas/code blocks).

## Phase 4: The Game Layer
- [ ] **Mark as Done**: Add a "Complete" button at the bottom of a note.
- [ ] **XP Logic**: When clicked, update `users.xp = xp + 100`.
- [ ] **The Leaderboard**: A simple table showing `SELECT name, xp FROM users ORDER BY xp DESC`.
