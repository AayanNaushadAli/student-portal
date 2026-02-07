# Implementation Plan - Class Note Generator MVP

## Goal Description
Create a web application that takes Syllabus and Past Year Questions (PYQs) as PDFs, extracts topics, and generates AI-written study notes. Includes a gamification layer with XP and a leaderboard.

## User Review Required
> [!IMPORTANT]
> **Credentials Needed**:
> 1. **Supabase URL & Key**: You need to create a project on [Supabase](https://supabase.com/) and provide the credentials.
> 2. **Gemini API Key**: For the AI generation.

## Proposed Changes

### Configuration
#### [NEW] [planning/master_plan.md](file:///c:/Users/aayan/OneDrive/Desktop/This%20Pc/P-dashboard/idk/planning/master_plan.md)
- detailed breakdown of the 4 phases.

#### [NEW] [planning/suggestions.md](file:///c:/Users/aayan/OneDrive/Desktop/This%20Pc/P-dashboard/idk/planning/suggestions.md)
- Additional items needed like `.env` setup, `requirements.txt`, and deployment strategy.

### Phase 1: Foundation (Database & Setup)
#### [NEW] [db.py](file:///c:/Users/aayan/OneDrive/Desktop/This%20Pc/P-dashboard/idk/db.py)
- Supabase connection logic.

#### [NEW] [requirements.txt](file:///c:/Users/aayan/OneDrive/Desktop/This%20Pc/P-dashboard/idk/requirements.txt)
- `streamlit`, `supabase`, `python-dotenv`, `google-generativeai`, `pypdf`.

### Phase 2: AI Pipeline
#### [NEW] [utils.py](file:///c:/Users/aayan/OneDrive/Desktop/This%20Pc/P-dashboard/idk/utils.py)
- PDF extraction and Gemini interaction functions.

### Phase 3 & 4: UI & Gamification
#### [NEW] [app.py](file:///c:/Users/aayan/OneDrive/Desktop/This%20Pc/P-dashboard/idk/app.py)
- Main Streamlit application with Login, Dashboard, Study View, and Leaderboard.

## Verification Plan
### Automated Tests
- None planned for MVP (manual verification preferred).
### Manual Verification
- **DB Connection**: Run `db.py` to check Supabase connectivity.
- **Upload**: Upload a PDF and check text extraction.
- **Generation**: specific prompts to Gemini and check output.
- **UI**: Click through the Streamlit interface.
