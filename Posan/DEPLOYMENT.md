# Deploying POSAN to Vercel

## ✅ Yes! You can deploy both frontend and backend to Vercel

Your application is now configured for Vercel deployment with both:
- **Frontend**: React + Vite
- **Backend**: FastAPI (as serverless functions)

---

## 📋 What Was Set Up

### Files Created:
1. **`vercel.json`** - Deployment configuration
2. **`package.json`** (root) - Build script for frontend
3. **`backend/vercel_app.py`** - Serverless handler for FastAPI
4. **`.vercelignore`** - Files to exclude from deployment

---

## 🚀 Deployment Steps

### Option 1: Using Vercel CLI (Recommended)

```bash
# Install Vercel CLI globally
npm install -g vercel

# Login to Vercel
vercel login

# Deploy from project root
cd c:\Users\grviv\projects\Pratices\Posan
vercel

# Follow the prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? posan (or your choice)
# - Directory? ./ (current directory)
# - Override settings? No

# For production deployment:
vercel --prod
```

### Option 2: Using Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Click **"Add New Project"**
3. Import your Git repository (GitHub/GitLab/Bitbucket)
4. Vercel will auto-detect the configuration from `vercel.json`
5. Click **"Deploy"**

---

## ⚙️ Environment Variables

Add these in Vercel Dashboard (Settings → Environment Variables):

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | Your PostgreSQL URL | Database connection string |
| `SECRET_KEY` | Your secret key | JWT signing key |
| `HUGGINGFACE_API_KEY` | Your HF API key | For AI content generation |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token expiration |

---

## 🔧 How It Works

### Architecture:
```
User Request
    ↓
Vercel Edge Network
    ↓
    ├─→ /api/* → FastAPI Serverless Function (backend/vercel_app.py)
    └─→ /* → Static Files (frontend/dist)
```

### Build Process:
1. **Frontend**: Vite builds React app → `frontend/dist/`
2. **Backend**: Python dependencies installed → Serverless function created
3. **Routing**: `/api/*` goes to backend, everything else to frontend

---

## ⚠️ Important Limitations

### Database Considerations:
- Vercel serverless functions are **stateless**
- Each request creates a new database connection
- Use **connection pooling** for PostgreSQL:

```python
# In backend/app/core/database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=1,  # Small pool for serverless
    max_overflow=0,
    pool_pre_ping=True  # Verify connections
)
```

### Cold Starts:
- First request after inactivity may be slow (2-5 seconds)
- Subsequent requests are fast

### Alternatives if Issues Arise:
- **Frontend**: Vercel ✅
- **Backend**: Railway, Render, or Fly.io (better for persistent connections)

---

## 🧪 Testing Deployment

After deployment, test these endpoints:

```bash
# Replace YOUR_VERCEL_URL with your actual URL

# Health check
curl https://YOUR_VERCEL_URL/api/health

# API docs
https://YOUR_VERCEL_URL/api/docs

# Frontend
https://YOUR_VERCEL_URL/
```

---

## 📝 Framework Answer for Vercel

When Vercel asks for framework:
- **Framework Preset**: `Other` or `Vite`
- **Build Command**: `npm run build`
- **Output Directory**: `frontend/dist`
- **Install Command**: `npm install`

---

## 🎯 Summary

✅ **Frontend**: Vite (React)  
✅ **Backend**: FastAPI (Python serverless)  
✅ **Both deployed to Vercel**: Yes!  
✅ **Configuration**: Done!  

Ready to deploy! 🚀
