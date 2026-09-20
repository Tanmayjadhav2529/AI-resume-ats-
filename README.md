# AI Resume ATS System

A local FastAPI + Streamlit project for analyzing resumes against a job description, scoring ATS compatibility, and generating structured feedback.

## Project Overview

This application:

- Parses uploaded resumes in PDF and DOCX format
- Extracts resume metadata and keywords with Groq-based parsing
- Compares resume content to a target job description
- Detects location/privacy risk and grammar issues
- Validates skills against project and experience evidence
- Produces an ATS-style score and recommendations
- Stores authenticated user history in Supabase when configured
- Exposes a REST API and a Streamlit dashboard

## Tech Stack

- Backend: FastAPI, Pydantic, Python
- Frontend: Streamlit
- NLP/ML: spaCy, SentenceTransformers
- Parsing: pdfplumber, PyPDF2, python-docx
- Auth/history: Supabase
- LLM parsing: Groq
- PDF export: Jinja2 + WeasyPrint

## Repository Structure

- `backend/` — API, config, services, database logic
- `frontend/` — Streamlit UI and client helpers
- `tests/` — local contract and regression tests
- `requirements.txt` — Python dependencies

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Install spaCy language model(s) if needed:

   ```bash
   python -m spacy download en_core_web_sm
   ```

4. Create a local `.env` file with the required values.

## Required Environment Variables

Add these entries to your local `.env` file before running the app:

```env
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_KEY=your_supabase_service_role_or_anon_key
SUPABASE_JWT_SECRET=your_supabase_jwt_secret_if_using_hs256
SENTENCE_TRANSFORMER_MODEL=all-MiniLM-L6-v2
```

> The app will still start in a degraded mode without a configured Groq or Supabase connection, but external features will behave gracefully or skip optional network actions.

## Run the Backend

```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

## Run the Streamlit Frontend

```bash
streamlit run frontend/streamlit_app.py
```

## Test the Project

```bash
python -m unittest discover -s tests -v
```

## Notes

- The project is intentionally kept local-only and does not require GitHub push or commit actions.
- Auth is email/password-based through Supabase; Google OAuth is not required and is intentionally not used in this client.
- History saving is non-blocking and gracefully skips if Supabase configuration or schema is unavailable.
