# 🔧 FIX: Mobile Login Not Working

## Problem
Login doesn't work when accessing from mobile or deployed website because the frontend is trying to connect to `localhost:8000`, which only exists on your development machine.

---

## ✅ Solution Applied

Updated `frontend/src/services/api.js` to use environment variables for the API URL.

---

## 🚀 How to Deploy (Two Options)

### Option 1: Deploy Backend Separately (Recommended)

Since Vercel isn't ideal for the FastAPI backend, deploy them separately:

#### **Step 1: Deploy Backend to Railway/Render**

**Using Railway (Easiest):**
1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `Posan` repository
4. Configure:
   - **Root Directory**: `backend`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `DATABASE_URL` - Your PostgreSQL URL
   - `SECRET_KEY` - Your secret key
   - `HUGGINGFACE_API_KEY` - Your HF key
6. Deploy!
7. **Copy the deployed URL** (e.g., `https://posan-backend.up.railway.app`)

**Using Render:**
1. Go to [render.com](https://render.com)
2. New → Web Service
3. Connect your GitHub repo
4. Configure:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (same as above)
6. Deploy!
7. **Copy the deployed URL**

#### **Step 2: Deploy Frontend to Vercel**

1. Go to [vercel.com](https://vercel.com/dashboard)
2. Your Posan project → Settings
3. **Add Environment Variable**:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://your-backend-url.railway.app/api/v1`
     - Replace with your actual Railway/Render backend URL
     - **IMPORTANT**: Add `/api/v1` at the end!
4. Save
5. Go to Deployments → Redeploy

---

### Option 2: Quick Test with ngrok (Temporary)

For testing mobile access quickly without deploying:

```bash
# In a new terminal, from the backend folder
ngrok http 8000
```

This will give you a public URL like `https://abc123.ngrok.io`

Then in Vercel, set:
- `VITE_API_URL` = `https://abc123.ngrok.io/api/v1`

**Note**: ngrok URLs change every time you restart it (unless you have a paid plan).

---

## 📝 Environment Variables Summary

### Frontend (Vercel):
| Variable | Value | Example |
|----------|-------|---------|
| `VITE_API_URL` | Your backend URL + `/api/v1` | `https://posan-api.railway.app/api/v1` |

### Backend (Railway/Render):
| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT secret key |
| `HUGGINGFACE_API_KEY` | For AI features |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` |

---

## 🧪 Testing

After deployment:

1. **Test from desktop**: `https://your-app.vercel.app`
2. **Test from mobile**: Same URL
3. **Try login**: Should work on both!

---

## 🎯 Current Status

✅ Frontend code updated to support environment variables  
✅ Falls back to `localhost:8000` for local development  
⏳ **Next step**: Deploy backend and add `VITE_API_URL` to Vercel  

---

## 💡 Why This Fixes Mobile Login

**Before:**
- Mobile → Frontend (Vercel) → tries to connect to `localhost:8000` ❌
- `localhost` on mobile = mobile device itself, not your PC

**After:**
- Mobile → Frontend (Vercel) → connects to `https://your-backend.railway.app` ✅
- Public URL works from anywhere!

---

**Ready to deploy!** Let me know if you need help with Railway/Render setup. 🚀
