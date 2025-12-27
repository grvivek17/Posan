# 🎨 POSAN - Kids Magazine & Puzzle Web Application

An interactive digital platform for children featuring magazines, puzzles, and educational games.

## 🛠️ Tech Stack

- **Backend**: Python FastAPI
- **Frontend**: ReactJS
- **Database**: Neon DB (PostgreSQL)
- **Authentication**: JWT-based

## 📁 Project Structure

```
Posan/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Config, security, database
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── main.py         # FastAPI app
│   ├── tests/
│   ├── requirements.txt
│   └── .env
├── frontend/               # ReactJS frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API clients
│   │   ├── hooks/          # Custom React hooks
│   │   ├── styles/         # CSS/styling
│   │   └── App.jsx
│   ├── public/
│   └── package.json
└── README.md
```

## 🚀 Quick Start

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend will run on `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will run on `http://localhost:5173`

## 📖 Features

- ✅ Digital Magazine with illustrated stories
- ✅ Audio narration for younger kids
- ✅ Interactive puzzles (Word Search, Crossword, Jigsaw, Sudoku)
- ✅ Gamification (Points, Badges, Leaderboards)
- ✅ Parent/Child account management
- ✅ Age-based content filtering
- ✅ Mobile-first responsive design

## 🔒 Environment Variables

Create a `.env` file in the `backend/` directory:

```env
DATABASE_URL=postgresql://neondb_owner:npg_NnJ5sICAUpa7@ep-empty-cake-a4z84d12-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

## 📝 License

MIT License
