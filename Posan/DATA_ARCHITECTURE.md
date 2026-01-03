# 📊 Data Storage & Loading Architecture - POSAN Application

## Overview
This document explains how data is stored and loaded across the POSAN application, covering both backend database storage and frontend data management.

---

## 🗄️ **Backend - Data Storage**

### **1. Database: Neon PostgreSQL**

**Location**: Cloud-hosted PostgreSQL database
- **Provider**: Neon DB (Serverless PostgreSQL)
- **Connection**: Configured via environment variable `DATABASE_URL` in `backend/.env`
- **Type**: Relational database (PostgreSQL)

**Configuration Path**: `backend/app/core/database.py`

```python
# Database URL is loaded from .env file
DATABASE_URL = "postgresql+psycopg2://[connection-string]"

# SQLAlchemy engine configured for serverless
engine = create_engine(
    database_url,
    pool_pre_ping=True,  # Verify connections
    pool_size=1,         # Small pool for serverless
    max_overflow=2,
    pool_recycle=300     # Recycle every 5 minutes
)
```

### **2. Data Models (Tables)**

All database tables are defined in `backend/app/models/`:

#### **User Management** (`models/user.py`)
- **User**: Stores user accounts (username, email, password_hash, role)
- **ParentAccount**: Links parents to their accounts
- **ChildProfile**: Stores child profiles with age, preferences, parent linkage

#### **Content** (`models/content.py`)
- **Magazine**: Digital magazines with title, description, cover images
- **Article**: Individual articles within magazines
- **Quiz**: Interactive quizzes with questions and answers

#### **Puzzles** (`models/puzzle.py`)
- **Puzzle**: Stores puzzle data (word search, crossword, sudoku, jigsaw)
- **PuzzleCompletion**: Tracks user puzzle completion history

#### **Gamification** (`models/gamification.py`)
- **Badge**: Available badges and achievements
- **UserAchievement**: User's earned badges
- **UserPoints**: Points system for each user

### **3. API Endpoints**

Data is exposed via REST API endpoints in `backend/app/api/`:

**Endpoints Structure**:
```
/api/v1/auth/*          # Authentication (register, login)
/api/v1/users/*         # User management
/api/v1/content/*       # Magazines, articles, quizzes
/api/v1/puzzles/*       # Puzzle data and submissions
/api/v1/gamification/*  # Badges, achievements, leaderboard
/api/v1/ai-content/*    # AI-generated content
```

### **4. Data Population**

**SQL Scripts**: `backend/scripts/`
- `populate_magazines.sql` - Sample magazine data
- `populate_articles.sql` - Sample article data

**How to populate**:
```bash
psql $DATABASE_URL -f backend/scripts/populate_magazines.sql
```

---

## 🌐 **Frontend - Data Loading**

### **1. API Client** (`frontend/src/services/api.js`)

**Configuration**:
- **Base URL**: `http://localhost:8000/api/v1` (development)
- **Authentication**: JWT tokens stored in `localStorage`
- **Library**: Axios for HTTP requests

**Key Features**:
```javascript
// Automatically adds auth token to all requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});
```

### **2. Data Loading in Pages**

Each page component fetches data from the backend:

#### **Home Page** (`pages/Home.jsx`)
- **Static Data**: Featured content defined in component state
- **User Data**: Username from `localStorage.getItem('username')`
- **Authentication**: Token from `localStorage.getItem('access_token')`

#### **Magazine/Library Page** (`pages/MagazinePage.jsx`)
```javascript
useEffect(() => {
    fetchMagazines();
}, []);

const fetchMagazines = async () => {
    const response = await contentAPI.getMagazines({ published_only: true });
    setMagazines(response.data);  // Stores in React state
};
```

**Data Flow**:
1. Component mounts
2. Calls `contentAPI.getMagazines()`
3. API sends GET request to `/api/v1/content/magazines`
4. Backend queries PostgreSQL database
5. Returns JSON data
6. Frontend stores in React state (`useState`)
7. Component re-renders with data

#### **Homework Page** (`pages/HomeworkPage.jsx`)
- **Static Data**: Subjects, quiz questions (hardcoded for now)
- **Future**: Will fetch from `/api/v1/content/homework`

#### **Profile Page** (`pages/ProfilePage.jsx`)
- **User Data**: Username, level from `localStorage`
- **Created Content**: Static for demo, will fetch from API

#### **Puzzle Page** (`pages/PuzzlePage.jsx`)
```javascript
const fetchPuzzles = async () => {
    const response = await puzzlesAPI.getPuzzles({ type: puzzleType });
    setPuzzles(response.data);
};
```

### **3. Local Storage (Frontend)**

**What's Stored**:
```javascript
localStorage.setItem('access_token', 'jwt_token_here');
localStorage.setItem('refresh_token', 'refresh_token_here');
localStorage.setItem('user_id', '123');
localStorage.setItem('username', 'Alex');
```

**When It's Used**:
- **Authentication**: Every API request includes the token
- **User Info**: Display username without API call
- **Session Management**: Check if user is logged in

**When It's Cleared**:
- User logs out
- Token expires (401 error)
- User clears browser data

---

## 🔄 **Data Flow Diagram**

```
┌─────────────────────────────────────────────────────────────┐
│                        USER BROWSER                          │
│  ┌────────────────────────────────────────────────────┐     │
│  │          React Components (Pages)                   │     │
│  │  - Home.jsx, MagazinePage.jsx, etc.                │     │
│  │                                                     │     │
│  │  State: [magazines, puzzles, user]                 │     │
│  └──────────────────┬──────────────────────────────────┘     │
│                     │                                        │
│                     │ useState/useEffect                     │
│                     ▼                                        │
│  ┌────────────────────────────────────────────────────┐     │
│  │         API Service (api.js)                        │     │
│  │  - contentAPI.getMagazines()                        │     │
│  │  - puzzlesAPI.getPuzzles()                          │     │
│  │  - authAPI.login()                                  │     │
│  └──────────────────┬──────────────────────────────────┘     │
│                     │                                        │
│                     │ HTTP Requests (Axios)                  │
└─────────────────────┼────────────────────────────────────────┘
                      │
                      │ localhost:8000/api/v1/*
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND SERVER                            │
│  ┌────────────────────────────────────────────────────┐     │
│  │         FastAPI Application                         │     │
│  │  main.py - Routes and endpoints                    │     │
│  └──────────────────┬──────────────────────────────────┘     │
│                     │                                        │
│                     ▼                                        │
│  ┌────────────────────────────────────────────────────┐     │
│  │         API Routes (/api/v1/*)                      │     │
│  │  - /content/magazines                              │     │
│  │  - /puzzles/puzzles                                │     │
│  │  - /auth/login                                     │     │
│  └──────────────────┬──────────────────────────────────┘     │
│                     │                                        │
│                     ▼                                        │
│  ┌────────────────────────────────────────────────────┐     │
│  │    SQLAlchemy ORM (database.py)                    │     │
│  │  - Models: User, Magazine, Puzzle, etc.            │     │
│  │  - SessionLocal for DB queries                     │     │
│  └──────────────────┬──────────────────────────────────┘     │
│                     │                                        │
│                     │ SQL Queries                            │
└─────────────────────┼────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│               NEON POSTGRESQL DATABASE                       │
│                                                              │
│  Tables:                                                     │
│  - users                                                     │
│  - parent_accounts                                          │
│  - child_profiles                                           │
│  - magazines                                                │
│  - articles                                                 │
│  - puzzles                                                  │
│  - puzzle_completions                                       │
│  - badges                                                   │
│  - user_achievements                                        │
│  - user_points                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 **Example: Loading Magazines**

### **Step-by-Step Flow**:

1. **User navigates to `/magazines`**
   - React Router loads `MagazinePage.jsx`

2. **Component mounts**
   ```javascript
   useEffect(() => {
       fetchMagazines();
   }, []);
   ```

3. **API call is made**
   ```javascript
   const response = await contentAPI.getMagazines({ published_only: true });
   ```

4. **Axios sends HTTP request**
   ```
   GET http://localhost:8000/api/v1/content/magazines?published_only=true
   Headers: { Authorization: "Bearer jwt_token" }
   ```

5. **Backend receives request**
   - Route: `backend/app/api/content.py`
   - Function: `get_magazines()`

6. **Database query**
   ```python
   magazines = db.query(Magazine).filter(Magazine.published == True).all()
   ```

7. **Response sent**
   ```json
   {
       "data": [
           {
               "id": 1,
               "title": "Space Adventure",
               "description": "Explore the cosmos",
               "cover_image_url": "...",
               "issue_number": 42
           }
       ]
   }
   ```

8. **Frontend updates state**
   ```javascript
   setMagazines(response.data);
   ```

9. **UI re-renders** with magazine cards

---

## 🔐 **Authentication Flow**

### **Login Process**:

1. User enters credentials in `Login.jsx`
2. `authAPI.login({ username, password })` called
3. Backend validates credentials against `users` table
4. JWT token generated and returned
5. Frontend stores tokens:
   ```javascript
   localStorage.setItem('access_token', data.access_token);
   localStorage.setItem('user_id', data.user_id);
   localStorage.setItem('username', username);
   ```
6. All subsequent API calls include token in headers

---

## 💾 **Current Data State**

### **Backend** ✅
- Database: Connected to Neon PostgreSQL
- Models: Defined and ready
- API: Running on `http://localhost:8000`
- Docs: Available at `http://localhost:8000/docs`

### **Frontend** ✅
- Running on `http://localhost:5173`
- API Client: Configured to connect to backend
- Auth: Using localStorage for tokens

### **Data Population**
⚠️ **Note**: You may need to populate the database with sample data using the SQL scripts in `backend/scripts/`

---

## 🔧 **Environment Variables**

### **Backend** (`backend/.env`)
```env
DATABASE_URL=postgresql://[your-neon-connection-string]
SECRET_KEY=your-secret-key
HUGGINGFACE_TOKEN=your-hf-token
```

### **Frontend** (`frontend/.env`)
```env
VITE_API_URL=http://localhost:8000/api/v1
```

---

## 🚀 **Quick Commands**

### **Backend**
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### **Frontend**
```bash
cd frontend
npm run dev
```

### **Populate Database**
```bash
psql $DATABASE_URL -f backend/scripts/populate_magazines.sql
```

---

## 📌 **Summary**

| Component | Storage Type | Location | Access Method |
|-----------|-------------|----------|---------------|
| **User Data** | PostgreSQL | Neon DB Cloud | SQLAlchemy ORM |
| **Magazine Content** | PostgreSQL | Neon DB Cloud | REST API |
| **Puzzles** | PostgreSQL | Neon DB Cloud | REST API |
| **Authentication** | localStorage | Browser | Direct access |
| **User Session** | localStorage | Browser | JWT tokens |
| **Frontend State** | React useState | Memory | Component state |
| **API Responses** | Cache/Memory | Browser | Axios |

The application follows a classic **3-tier architecture**:
1. **Presentation Layer**: React (Frontend)
2. **Application Layer**: FastAPI (Backend)
3. **Data Layer**: PostgreSQL (Database)
