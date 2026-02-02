# 🌟 Supabase Database Setup Guide

Your QR Code Generator is configured to use **Supabase** - a powerful cloud PostgreSQL database!

## ✅ What You Have

The backend is already configured to connect to your Supabase database:
- **Host**: `db.nzrsksoyalnoayvhscou.supabase.co`
- **Port**: `5432`
- **Database**: `postgres`
- **User**: `postgres`

---

## 🚀 Quick Setup (1 Minute)

### Step 1: Get Your Password

1. Go to your Supabase project dashboard: https://supabase.com/dashboard
2. Navigate to **Settings** → **Database**
3. Find the **Database Password** section
4. Copy your password (or reset it if needed)

### Step 2: Update the .env File

Open `backend/.env` and replace `[YOUR-PASSWORD]` with your actual password:

**Before:**
```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.nzrsksoyalnoayvhscou.supabase.co:5432/postgres
```

**After:**
```env
DATABASE_URL=postgresql://postgres:YourActualPassword123@db.nzrsksoyalnoayvhscou.supabase.co:5432/postgres
```

### Step 3: Start the Backend

That's it! When you start the backend, tables will be created automatically:

```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

---

## 🎯 Advantages of Using Supabase

✅ **No Local Setup** - No need to install PostgreSQL locally  
✅ **Cloud Hosted** - Access from anywhere  
✅ **Auto Backups** - Your data is automatically backed up  
✅ **Free Tier** - Generous free tier for development  
✅ **Dashboard** - Visual database management  
✅ **Scalable** - Easily scale as your app grows  
✅ **Secure** - Built-in security and SSL  

---

## 🔑 Finding Your Connection Details in Supabase

1. **Go to Dashboard**: https://supabase.com/dashboard
2. **Select Your Project**: Click on your QR Code project
3. **Settings → Database**: Find all connection details
4. **Connection String**: You can also copy the full connection string from here

Your connection details:
```
Host: db.nzrsksoyalnoayvhscou.supabase.co
Database: postgres
Port: 5432
User: postgres
Password: [Your password from dashboard]
```

---

## 📊 Viewing Your Data

### Option 1: Supabase Table Editor (Recommended)
1. Go to your Supabase dashboard
2. Click **Table Editor** in the sidebar
3. Select the `qrcodes` table
4. View, edit, or delete records

### Option 2: SQL Editor
1. Go to **SQL Editor** in Supabase dashboard
2. Run queries like:
```sql
-- View all QR codes
SELECT * FROM qrcodes ORDER BY created_at DESC;

-- Count total QR codes
SELECT COUNT(*) FROM qrcodes;

-- View QR codes with most scans
SELECT title, url, scans FROM qrcodes ORDER BY scans DESC LIMIT 10;
```

### Option 3: API (FastAPI)
When your backend is running, visit:
- **API Docs**: http://localhost:8000/docs
- **Get All QR Codes**: http://localhost:8000/api/qrcodes/

---

## 🔒 Security Tips

### Password Security
- ✅ **Never commit** `.env` file with real password to GitHub
- ✅ **Use strong passwords** - mix of letters, numbers, symbols
- ✅ **Reset password** if you suspect it's been compromised

### Supabase Security Settings
1. Go to **Settings** → **Database**
2. Check **SSL enforcement** is enabled (it should be by default)
3. Review **Connection pooling** settings

---

## 🛠️ Troubleshooting

### "Connection refused" or "Cannot connect"
- ✅ Check your password in `backend/.env` is correct
- ✅ Make sure you have internet connection
- ✅ Verify your Supabase project is active (not paused)
- ✅ Check if you need to reset your database password

### "Password authentication failed"
- ✅ Copy the password directly from Supabase dashboard
- ✅ Make sure there are no extra spaces in `.env` file
- ✅ If password has special characters, they might need URL encoding:
  - `@` → `%40`
  - `#` → `%23`
  - `%` → `%25`

### "SSL connection required"
- This is automatically handled by `psycopg2-binary`
- If you see this error, ensure you have `psycopg2-binary` installed (it's in requirements.txt)

### Database Tables Not Created
- Make sure the backend started successfully
- Check backend logs for errors
- The tables are created automatically on first run by SQLAlchemy

### "Too many connections"
- Supabase free tier has connection limits
- Make sure you're not running multiple instances
- Check **Settings** → **Database** → **Connection pooling**

---

## 📈 Database Schema

The backend automatically creates this table:

```sql
CREATE TABLE qrcodes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200),
    url TEXT NOT NULL,
    description TEXT,
    qr_code_image TEXT NOT NULL,  -- Base64 encoded PNG
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scans INTEGER DEFAULT 0
);
```

You can view this in Supabase Table Editor after starting the backend once.

---

## 🔄 Resetting Your Database

If you want to start fresh:

### Option 1: Delete All Records (Keep Table)
In Supabase SQL Editor:
```sql
DELETE FROM qrcodes;
ALTER SEQUENCE qrcodes_id_seq RESTART WITH 1;
```

### Option 2: Drop and Recreate Table
```sql
DROP TABLE IF EXISTS qrcodes;
-- Then restart your backend to recreate the table
```

---

## 📊 Monitoring

### In Supabase Dashboard:
1. Go to **Database** → **Extensions**
2. Enable **pg_stat_statements** for performance monitoring
3. View query performance in **Database** → **Query Performance**

### View Database Size:
```sql
SELECT pg_size_pretty(pg_database_size('postgres'));
```

### View Table Size:
```sql
SELECT pg_size_pretty(pg_total_relation_size('qrcodes'));
```

---

## 💡 Pro Tips

1. **Bookmark Your Dashboard**: Save your Supabase project URL for quick access
2. **Enable Row Level Security (RLS)**: For production, enable RLS in Table Editor
3. **Set Up Backups**: Configure automatic backups in Settings
4. **Use Connection Pooling**: Enable in Settings → Database for better performance
5. **Monitor Usage**: Check your usage in Settings to stay within free tier limits

---

## 🌐 Alternative: Use Local PostgreSQL

If you prefer to use a local PostgreSQL database instead of Supabase:

1. Install PostgreSQL locally
2. Create database: `CREATE DATABASE qrcode_db;`
3. Update `backend/.env`:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/qrcode_db
```

See `backend/SETUP_DATABASE.md` for more details.

---

## ✅ Checklist

Before starting your app:
- [ ] Copied Supabase password from dashboard
- [ ] Updated `backend/.env` with actual password
- [ ] No brackets `[` or `]` around password in .env
- [ ] Saved the .env file
- [ ] Internet connection is working

---

## 📞 Need Help?

- **Supabase Docs**: https://supabase.com/docs
- **Supabase Support**: https://supabase.com/support
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

---

**You're ready to go!** 🚀

Start the backend and your database connection will be established automatically.

```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

If you see "Application startup complete", you're connected! 🎉
