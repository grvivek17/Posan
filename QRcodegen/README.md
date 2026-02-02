# QR Code Generator Application

A full-stack application to generate QR codes that redirect to websites, built with Next.js, FastAPI, and PostgreSQL.

## Features

- 🎯 Generate QR codes for any URL
- 💾 Save QR code data to PostgreSQL database
- 📊 View all generated QR codes
- 🎨 Beautiful, modern UI with Next.js
- ⚡ Fast API with FastAPI
- 🔍 Track QR code usage and analytics

## Tech Stack

- **Frontend**: Next.js 14 with TypeScript
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **QR Code Generation**: qrcode library (Python)

## Architecture

![Architecture Diagram](https://raw.githubusercontent.com/grvivek17/QRcodegen/main/architecture_diagram.png)

The application follows a three-tier architecture:

1. **Frontend (Next.js)**: Modern, responsive UI built with React and Tailwind CSS
2. **Backend (FastAPI)**: RESTful API handling business logic and QR code generation
3. **Database (PostgreSQL)**: Persistent storage for QR code metadata and analytics

## Project Structure

```
QRcodegen/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── database.py
│   │   └── routers/
│   ├── requirements.txt
│   └── .env
├── frontend/         # Next.js frontend
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── lib/
│   ├── package.json
│   └── .env.local
└── README.md
```

## Setup Instructions

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- Supabase account (free tier available) - **No local PostgreSQL installation needed!**

### Database Setup

This project uses **Supabase** as the cloud PostgreSQL database.

1. Get your Supabase database password from your dashboard
2. Update `backend/.env` with your password:
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.nzrsksoyalnoayvhscou.supabase.co:5432/postgres
```

**See [SUPABASE_SETUP.md](./SUPABASE_SETUP.md) for detailed setup instructions.**

> **Note**: Database tables are created automatically when you start the backend!

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the backend directory:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/qrcode_db
```

5. Run the backend:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env.local` file:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Run the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## API Endpoints

- `POST /api/qrcodes` - Generate a new QR code
- `GET /api/qrcodes` - Get all QR codes
- `GET /api/qrcodes/{id}` - Get a specific QR code
- `DELETE /api/qrcodes/{id}` - Delete a QR code

## Usage

1. Enter a URL in the input field
2. Optionally add a title/description
3. Click "Generate QR Code"
4. Download or view your QR code
5. View all generated QR codes in the gallery

## License

MIT
