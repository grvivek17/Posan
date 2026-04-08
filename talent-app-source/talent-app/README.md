# Talent Manager — AI-Powered Talent Platform

A full-stack talent management application with AI-powered resume parsing, semantic profile matching, requirements management, and Twilio-integrated telecalling.

## Features

### 1. Resume Upload & AI Skill Matrix
- Upload PDF/DOC/DOCX resumes
- Auto-generates categorized skill matrices (Frontend, Backend, Database, Cloud/DevOps, Testing, etc.)
- Extracts name, email, phone, experience, education, and certifications

### 2. Talent Finder (RAG-powered Chat)
- Neural semantic search using `sentence-transformers/all-MiniLM-L6-v2` (384-dim embeddings)
- FAISS vector similarity search for fast profile matching
- Natural language queries like "I need a cloud infrastructure designer"

### 3. Requirements Manager
- Create/edit/delete hiring requirements with auto-generated IDs (REQ-001, REQ-002, etc.)
- Track skills needed, team size, and status (open, in-progress, filled, closed)
- **Profile Matching**: Click the match icon to find profiles ranked by similarity to the requirement's skills

### 4. Telecaller
- Manual call scripts with custom screening questions
- Twilio integration for automated voice calls with TTS and speech recognition
- Call history with recorded responses

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python) |
| Frontend | React + TypeScript + Tailwind CSS + shadcn/ui |
| Database | SQLite (aiosqlite) |
| Vector Search | FAISS + sentence-transformers |
| Voice Calls | Twilio Voice API |
| Build Tool | Vite |

## Project Structure

```
talent-app/
├── talent-backend/          # FastAPI backend
│   ├── app/
│   │   ├── main.py          # FastAPI app entry point
│   │   ├── database.py      # SQLite database initialization
│   │   ├── vector_store.py  # FAISS + sentence-transformers
│   │   ├── ai_helper.py     # AI/LLM helper functions
│   │   ├── twilio_service.py # Twilio voice call integration
│   │   └── routers/
│   │       ├── profiles.py
│   │       ├── requirements.py
│   │       ├── talent_finder.py
│   │       └── telecaller.py
│   ├── pyproject.toml
│   └── poetry.lock
├── talent-frontend/         # React frontend
│   ├── src/
│   │   ├── App.tsx
│   │   ├── lib/api.ts       # API client
│   │   └── pages/
│   │       ├── ResumeUpload.tsx
│   │       ├── TalentFinder.tsx
│   │       ├── Requirements.tsx
│   │       └── Telecaller.tsx
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## Setup

### Backend

```bash
cd talent-backend
pip install poetry
poetry install

# Set environment variables
export DATABASE_PATH=./talent.db
export VECTOR_STORE_PATH=./vector_index.json

# Optional: Twilio integration
export TWILIO_ACCOUNT_SID=your_sid
export TWILIO_AUTH_TOKEN=your_token
export TWILIO_PHONE_NUMBER=+1XXXXXXXXXX

# Run
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd talent-frontend
npm install

# Set backend URL
echo "VITE_API_URL=http://localhost:8000" > .env

# Development
npm run dev

# Production build
npm run build
npx serve dist -l 5173 -s
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/profiles/upload` | Upload resume and generate skill matrix |
| GET | `/api/profiles/` | List all profiles |
| POST | `/api/talent-finder/search` | Semantic search for matching profiles |
| GET | `/api/requirements/` | List all requirements |
| POST | `/api/requirements/` | Create a new requirement (auto-generates REQ-XXX ID) |
| GET | `/api/requirements/{id}/match-profiles` | Find matching profiles for a requirement |
| POST | `/api/telecaller/calls` | Create a call record |
| POST | `/api/telecaller/twilio-call` | Initiate a Twilio voice call |

## License

MIT
