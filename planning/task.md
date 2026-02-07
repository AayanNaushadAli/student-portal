# Master To-Do List

## Phase 1: The Foundation (Database & Setup)
- [ ] **Create Supabase Project**: User to set up a free project on Supabase.
- [ ] **Setup Environment**: Create `.env` file and install dependencies.
- [ ] **Create Tables**: Run SQL to create `users`, `classrooms`, `master_files`, `topics`.
- [ ] **Setup Storage Bucket**: Create `raw_uploads` bucket.
- [ ] **Connect Python**: Create `db.py` to test connection.

## Phase 2: The "Brain" (AI Pipeline)
- [ ] **PDF Text Extractor**: Implement `utils.py` to extract text from PDFs.
- [ ] **Syllabus Parser**: Create Gemini prompt for extracting Units/Topics.
- [ ] **Note Generator**: Implement loop for Topic + PYQ -> AI Markdown.

## Phase 3: The Interface (Streamlit UI)
- [ ] **Login Screen**: Implement email/password auth using Supabase.
- [ ] **The Dashboard**: Dropdown for College/Class selection.
- [ ] **Upload Zone**: Drag-and-drop for Syllabus/PYQs.
- [ ] **Study View**: Sidebar for Units, Main area for Topics.
- [ ] **Content Renderer**: Display AI Markdown with formatting.

## Phase 4: The Game Layer
- [ ] **Mark as Done**: Add "Complete" button.
- [ ] **XP Logic**: Update user XP on completion.
- [ ] **Leaderboard**: Display user rankings.
