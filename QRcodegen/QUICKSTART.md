# 🎉 Welcome to QR Code Generator!

## What You Have

A **complete, production-ready** QR code generator application featuring:

- ✨ **Beautiful Modern UI** - Dark theme with purple/pink gradients
- ⚡ **Lightning Fast** - Built with Next.js and FastAPI
- 💾 **Database Powered** - PostgreSQL for reliable data storage
- 📱 **Fully Responsive** - Works on desktop, tablet, and mobile
- 🎯 **Feature Complete** - Create, view, download, and delete QR codes

---

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Prerequisites

Make sure you have these installed:
- ✅ **Python 3.9+** - [Download Python](https://www.python.org/downloads/)
- ✅ **Node.js 18+** - [Download Node.js](https://nodejs.org/)
- ✅ **Supabase Account** - [Sign up free](https://supabase.com/) (No local PostgreSQL needed!)

### Step 2: Setup Database (Using Supabase) 🌟

**Good news!** This project is configured to use **Supabase** - a cloud PostgreSQL database. No local installation needed!

Your database is already set up at: `db.nzrsksoyalnoayvhscou.supabase.co`

**All database tables will be created automatically** when you start the backend!

### Step 3: Configure Backend

1. Open the `backend/.env` file
2. Replace `[YOUR-PASSWORD]` with your actual Supabase database password:
   ```
   DATABASE_URL=postgresql://postgres:YOUR_SUPABASE_PASSWORD@db.nzrsksoyalnoayvhscou.supabase.co:5432/postgres
   ```

**To get your Supabase password:**
- Go to your Supabase dashboard
- Navigate to **Settings** → **Database**
- Copy your database password

### Step 4: Start Backend

In the `backend` folder terminal:
```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload
```

You should see: `INFO:     Uvicorn running on http://127.0.0.1:8000`

### Step 5: Start Frontend

Open a **NEW** terminal in the `frontend` folder:
```bash
# Install dependencies
npm install

# Start the dev server
npm run dev
```

You should see: `- Local:   http://localhost:3000`

### Step 6: Open the App!

🎊 Open your browser to: **http://localhost:3000**

---

## 🎯 Try It Out!

1. **Enter a URL** (e.g., `https://github.com`)
2. **Add a title** (e.g., "My GitHub Profile")
3. Click **"Generate QR Code"**
4. **Download** your QR code!
5. **Scan it** with your phone to test!

---

## 📁 What's Inside

```
QRcodegen/
├── backend/              # Python FastAPI backend
│   ├── app/             # Application code
│   ├── .env             # ✅ Already configured!
│   └── requirements.txt
│
├── frontend/            # Next.js frontend
│   ├── app/            # Pages and layouts
│   ├── components/     # React components
│   ├── lib/            # Utilities
│   └── .env.local      # ✅ Already configured!
│
├── README.md           # Documentation
├── QUICKSTART.md       # This guide
├── FEATURES.md         # All features
├── DEPLOYMENT.md       # Deploy to production
└── PROJECT_SUMMARY.md  # Complete overview
```

---

## 🎨 Features You'll Love

### Create QR Codes
- Enter any URL
- Add optional title and description
- Instant QR code generation
- High-quality PNG output

### Manage Your Codes
- View all QR codes in a beautiful gallery
- Download any QR code as PNG
- Delete unwanted QR codes
- Track scan counts

### Beautiful Interface
- Modern dark theme
- Smooth animations
- Responsive design
- Professional look and feel

---

## 🔧 Useful Commands

### Backend
```bash
# Start backend
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload

# View API docs
# Open http://localhost:8000/docs
```

### Frontend
```bash
# Start frontend
cd frontend
npm run dev

# Build for production
npm run build
```

### Database
```sql
-- View all QR codes
SELECT * FROM qrcodes;

-- Delete all QR codes
DELETE FROM qrcodes;

-- Reset auto-increment
ALTER SEQUENCE qrcodes_id_seq RESTART WITH 1;
```

---

## 🌐 Important URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## ❓ Troubleshooting

### "Cannot connect to database"
- Check your Supabase password in `backend\.env`
- Make sure you replaced `[YOUR-PASSWORD]` with your actual password
- Verify your Supabase project is active
- Check your internet connection (Supabase is cloud-based)

### "Port 3000 already in use"
- Close other apps using port 3000
- Or Next.js will suggest port 3001

### "Port 8000 already in use"
- Close other apps using port 8000
- Or change the port in the uvicorn command

### "Module not found"
**Backend:**
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### CORS Errors
- Make sure backend is running on port 8000
- Check `CORS_ORIGINS` in `backend\.env`

---

## 📚 Learn More

- **Full Features**: Read `FEATURES.md`
- **Deployment**: Read `DEPLOYMENT.md`
- **Project Overview**: Read `PROJECT_SUMMARY.md`
- **Main Docs**: Read `README.md`

---

## 🎯 Next Steps

1. ✅ Get the app running (you're almost there!)
2. 🎨 Generate your first QR code
3. 📱 Test it by scanning with your phone
4. 🚀 Deploy to production (see DEPLOYMENT.md)
5. 💡 Customize and make it your own!

---

## 💡 Pro Tips

- **API Docs**: The backend auto-generates interactive API documentation at http://localhost:8000/docs - try it out!
- **Hot Reload**: Both frontend and backend support hot reload - changes appear instantly!
- **Database GUI**: Use pgAdmin or DBeaver to visually explore your database
- **Testing**: Use Postman or the Swagger docs to test API endpoints

---

## 🎊 You're All Set!

Everything is configured and ready to go. Just:

1. Update your Supabase password in `backend\.env`
2. Run backend (Step 4 above)
3. Run frontend (Step 5 above)
4. Create amazing QR codes!

**Need help?** Check the troubleshooting section or the detailed docs.

**Ready to deploy?** See DEPLOYMENT.md for cloud deployment options.

---

**Happy QR Code Generating! 🚀**

Built with ❤️ using Next.js, FastAPI, and PostgreSQL
