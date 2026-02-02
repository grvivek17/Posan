---
description: Setup and run the QR Code Generator application
---

# QR Code Generator - Setup and Run Workflow

## Prerequisites

Before starting, ensure you have:
- Python 3.9+ installed (check with `python --version`)
- Node.js 18+ and npm installed (check with `node --version`)
- PostgreSQL 14+ installed and running

## Step 1: Setup PostgreSQL Database

First, create the database for the application:

1. Open PostgreSQL command line or PgAdmin
2. Run the following SQL command:
```sql
CREATE DATABASE qrcode_db;
```

## Step 2: Setup Backend (FastAPI)

// turbo
1. Navigate to the backend directory and create a virtual environment:
```bash
cd backend
python -m venv venv
```

2. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On Mac/Linux: `source venv/bin/activate`

// turbo
3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Update the `.env` file in the backend directory with your PostgreSQL credentials:
   - Open `backend\.env`
   - Replace `password` with your actual PostgreSQL password
   - The file should look like:
   ```
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/qrcode_db
   CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   ```

// turbo
5. Start the FastAPI backend server:
```bash
uvicorn app.main:app --reload
```

The backend will be running at http://localhost:8000
API documentation will be available at http://localhost:8000/docs

## Step 3: Setup Frontend (Next.js)

Open a **NEW** terminal window (keep the backend running):

// turbo
1. Navigate to the frontend directory:
```bash
cd frontend
```

// turbo
2. Install Node.js dependencies:
```bash
npm install
```

3. The `.env.local` file has already been created with:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

// turbo
4. Start the Next.js development server:
```bash
npm run dev
```

The frontend will be running at http://localhost:3000

## Step 4: Access the Application

1. Open your browser and go to http://localhost:3000
2. You should see the QR Code Generator interface
3. Test it by:
   - Entering a URL (e.g., https://example.com)
   - Adding an optional title
   - Clicking "Generate QR Code"
   - Downloading your QR code
   - Viewing it in the gallery below

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL service is running
- Verify the database `qrcode_db` exists
- Check that the password in `backend\.env` is correct

### CORS Errors
- Make sure the backend is running on port 8000
- Verify frontend is accessing http://localhost:8000

### Port Already in Use
- Backend (8000): Stop any other process using port 8000
- Frontend (3000): Next.js will automatically suggest port 3001 if 3000 is busy

### Module Import Errors (Python)
- Ensure you activated the virtual environment
- Try reinstalling: `pip install -r requirements.txt`

### Package Not Found (Node.js)
- Delete `node_modules` folder and `package-lock.json`
- Run `npm install` again

## Quick Commands Reference

**Start Backend:**
```bash
cd backend
venv\Scripts\activate  # Windows
uvicorn app.main:app --reload
```

**Start Frontend:**
```bash
cd frontend
npm run dev
```

**Create Database:**
```sql
CREATE DATABASE qrcode_db;
```
