# 🚨 Project Issues & Improvements

This document lists the identified problems in the current Streamlit application and proposes future enhancements, including a migration to a React frontend.

---

## 🔴 Critical Issues

### 1. **No Password Authentication**
- **Problem**: Login only requires an email. Anyone who knows an email can log in as that user.
- **Impact**: Zero security. User accounts can be hijacked.
- **Fix**: Implement password hashing (e.g., `bcrypt`) and proper session management.

### 2. **Files are Globally Visible**
- **Problem**: `get_all_files()` returns ALL files from the database, regardless of who uploaded them.
- **Impact**: User A can see and chat with files uploaded by User B. **Privacy violation.**
- **Fix**: Add a `user_id` foreign key to `master_files` table. Filter queries by `user_id`.

---

## 🟠 Medium Issues

### 3. **XP Can Be Abused**
- **Problem**: The "Mark as Mastered" button can be clicked repeatedly on the same file. There's no check.
- **Impact**: Users can farm infinite XP.
- **Fix**: Add a `user_file_progress` table to track which files a user has "mastered". Disable button if already claimed.

### 4. **Chat History is Shared Across Files**
- **Problem**: `st.session_state.messages` is a single global list. If you switch to a different PDF, it still shows the old chat.
- **Impact**: Confusing UX. Irrelevant AI responses.
- **Fix**: Key the chat history by `file_hash`: `st.session_state.messages[selected_hash] = [...]`

### 5. **No Email Validation**
- **Problem**: Any string can be entered as an email. No format check. No verification.
- **Impact**: Fake accounts, garbage data.
- **Fix**: Add regex validation for email format. Optionally, send a verification email.

### 6. **Hardcoded Global Rank**
- **Problem**: The "Global Rank" metric in Tab 1 is hardcoded to `#5`.
- **Impact**: Misleading information.
- **Fix**: Query the database to calculate the user's actual rank based on XP.

---

## 🟡 UI/UX Improvements

### 7. **"Open" Button Does Nothing Useful**
- **Problem**: In the new card layout, the "Open" button only shows a toast. It doesn't actually open the analysis.
- **Fix**: Expand the file view to show the AI analysis or navigate to a detail page.

### 8. **Streamlit Limited Interactivity**
- **Problem**: Streamlit has a limited component model. Complex animations, real-time updates, and mobile responsiveness are hard.
- **Fix**: Migrate to a **React Frontend** with a Python (FastAPI/Flask) backend API.

---

## 🔵 Future: React Migration Plan

| Layer | Current (Streamlit) | Future (React + FastAPI) |
|-------|---------------------|--------------------------|
| **Frontend** | `app.py` (Python) | React (Vite + TypeScript) |
| **Backend API** | None (DB calls in Streamlit) | FastAPI (Python) |
| **Database** | Supabase PostgreSQL | Supabase PostgreSQL (no change) |
| **Auth** | Email-only | Supabase Auth (JWT) |

### Benefits of React:
- ✅ Full control over UI/UX
- ✅ Animations, transitions, mobile-first design
- ✅ Proper state management (Zustand, Redux)
- ✅ Scalable component architecture

---

## Summary Table

| # | Issue | Severity | Status |
|---|-------|----------|--------|
| 1 | No Password Authentication | 🔴 Critical | Open |
| 2 | Files Globally Visible | 🔴 Critical | Open |
| 3 | XP Abuse | 🟠 Medium | Open |
| 4 | Chat History Shared | 🟠 Medium | Open |
| 5 | No Email Validation | 🟠 Medium | Open |
| 6 | Hardcoded Rank | 🟡 Low | Open |
| 7 | "Open" Button Incomplete | 🟡 Low | Open |
| 8 | Streamlit Limitations | 🔵 Enhancement | Planned |
