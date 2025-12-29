# 🚀 Deploy POSAN to Render

## Why Render for Backend?
✅ Free tier includes PostgreSQL database  
✅ Better for long-running FastAPI apps  
✅ Automatic deploys from GitHub  
✅ No serverless limitations  

---

## 📋 Step-by-Step Deployment

### Step 1: Deploy Backend to Render

1. **Go to [render.com](https://render.com)** and sign up/login

2. **Create PostgreSQL Database First**
   - Click **"New +"** → **"PostgreSQL"**
   - Name: `posan-db`
   - Database: `posan`
   - User: `posan`
   - Region: Choose closest to you
   - Instance Type: **Free**
   - Click **"Create Database"**
   - **⚠️ IMPORTANT**: Copy the **"Internal Database URL"** (starts with `postgresql://`)

3. **Create Web Service**
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub account
   - Select repository: **`grvivek17/Posan`**
   
4. **Configure the Web Service:**
   
   | Setting | Value |
   |---------|-------|
   | **Name** | `posan-backend` (or your choice) |
   | **Region** | Same as your database |
   | **Branch** | `main` |
   | **Root Directory** | `backend` |
   | **Runtime** | `Python 3` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
   | **Instance Type** | `Free` |

5. **Add Environment Variables:**
   
   Click **"Advanced"** → **"Add Environment Variable"** and add these:
   
   | Key | Value | Example |
   |-----|-------|---------|
   | `DATABASE_URL` | Paste the Internal Database URL from Step 2 | `postgresql://posan:pass@...` |
   | `SECRET_KEY` | Any random string (32+ characters) | Generate at [randomkeygen.com](https://randomkeygen.com) |
   | `ALGORITHM` | `HS256` | Just type this |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Just type this |
   | `DEBUG` | `False` | Production setting |
   | `APP_NAME` | `POSAN API` | Your app name |
   | `API_V1_PREFIX` | `/api/v1` | API prefix |
   | `HUGGINGFACE_API_KEY` | Your Hugging Face API key | Get from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |

6. **Click "Create Web Service"**
   - Render will start building and deploying
   - Wait 3-5 minutes for first deployment
   - Once deployed, you'll see a green "Live" status
   - **Copy your backend URL** (e.g., `https://posan-backend.onrender.com`)

---

### Step 2: Update Frontend on Vercel

1. **Go to [vercel.com/dashboard](https://vercel.com/dashboard)**
2. Click on your **Posan** project
3. Go to **Settings** → **Environment Variables**
4. Add a new variable:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://your-render-url.onrender.com/api/v1`
     - ⚠️ Replace with YOUR actual Render URL
     - ⚠️ Don't forget `/api/v1` at the end!
   - **Environment**: All (Production, Preview, Development)
5. Click **"Save"**
6. Go to **Deployments** tab
7. Click **"Redeploy"** on the latest deployment

---

### Step 3: Test Your Deployment

1. **Test Backend API:**
   - Open: `https://your-render-url.onrender.com/docs`
   - You should see the FastAPI Swagger docs
   - Try the health check: `https://your-render-url.onrender.com/health`

2. **Test Frontend:**
   - Open: `https://your-vercel-url.vercel.app`
   - Try to register/login
   - Should work from desktop AND mobile! 🎉

---

## ⚠️ Important Notes

### Free Tier Limitations:
- **Render Free tier**: Service spins down after 15 minutes of inactivity
- **First request after inactivity**: May take 30-60 seconds (cold start)
- **Database**: 90 days free, then $7/month

### To Keep Service Awake (Optional):
Use a service like [UptimeRobot](https://uptimerobot.com) to ping your API every 10 minutes:
- Add monitor: `https://your-render-url.onrender.com/health`
- Interval: Every 5-10 minutes

---

## 🔧 Environment Variables Reference

### Backend (Render):
```
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=your-very-long-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=False
APP_NAME=POSAN API
API_V1_PREFIX=/api/v1
HUGGINGFACE_API_KEY=hf_xxxxxxxxxxxxx
```

### Frontend (Vercel):
```
VITE_API_URL=https://posan-backend.onrender.com/api/v1
```

---

## 📱 Mobile Login Fix

After completing these steps:
- ✅ Mobile will be able to login
- ✅ Desktop will work
- ✅ All API calls will go to your public Render backend

---

## 🆘 Troubleshooting

### Backend not starting?
- Check **Logs** tab in Render dashboard
- Common issues:
  - Missing environment variables
  - Database connection error
  - Wrong start command

### Frontend can't connect to backend?
- Check `VITE_API_URL` is correct
- Must include `/api/v1` at the end
- Check CORS settings allow your Vercel domain

### Database connection error?
- Make sure you used the **Internal Database URL**
- Check the database is in the same region as web service

---

## 🎉 That's It!

Your app is now fully deployed:
- **Frontend**: Vercel
- **Backend + Database**: Render

Both free tiers, accessible from anywhere! 🚀

---

**Need help? Check the logs in Render dashboard or let me know!**
