# 🚨 Production Podcast Issue Fix

## **Problem:**
- Weekly Highlights Podcast not working in production
- AI Podcast generation failing with "Failed to generate content"
- Works locally but not on Vercel (frontend) + Render (backend)

---

## **Root Causes:**

### 1. **Missing Environment Variable**
The `HUGGINGFACE_TOKEN` is likely not set in your Render backend deployment.

### 2. **Frontend API Configuration**
The frontend may not be correctly pointing to your Render backend URL.

### 3. **CORS Issues**
Render backend might not allow requests from your Vercel frontend domain.

---

## **Fix Steps:**

### 🔧 **Step 1: Set Environment Variables in Render**

1. Go to your **Render Dashboard** → Your backend service
2. Click **"Environment"** tab
3. Add these variables:

```bash
HUGGINGFACE_TOKEN=hf_YOUR_TOKEN_HERE
DEBUG=False
ALLOWED_ORIGINS=https://your-app.vercel.app,https://posan.vercel.app
DATABASE_URL=postgresql://your-neon-db-url
SECRET_KEY=your-production-secret-key
API_V1_PREFIX=/api/v1
```

4. Click **"Save Changes"**
5. Render will automatically redeploy

---

### 🔧 **Step 2: Configure Frontend for Production**

**In your Vercel deployment:**

1. Go to **Vercel Dashboard** → Your project → **Settings** → **Environment Variables**
2. Add:

```bash
VITE_API_URL=https://your-backend.onrender.com/api/v1
```

3. **Redeploy** your frontend

**Alternative: Update frontend/.env.production**

Create `frontend/.env.production`:
```bash
VITE_API_URL=https://your-backend.onrender.com/api/v1
```

Then commit and push.

---

### 🔧 **Step 3: Verify CORS Configuration**

Check `backend/app/main.py`:

```python
# CORS should include your Vercel domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://your-app.vercel.app",  # ADD THIS
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 🔧 **Step 4: Add Error Handling & Logging**

I'll create an improved version of the podcast service with better error messages.

---

## **Quick Verification:**

### **Test Backend API Directly:**

Visit in your browser:
```
https://your-backend.onrender.com/health
```

Should return: `{"status": "healthy"}`

### **Test Podcast Endpoint:**

Use curl or Postman:
```bash
curl -X POST https://your-backend.onrender.com/api/v1/podcasts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "dinosaurs",
    "age_group": "8-12",
    "duration": "short",
    "style": "fun"
  }'
```

---

## **Common Error Messages & Fixes:**

| Error | Cause | Fix |
|-------|-------|-----|
| "Failed to generate content" | HUGGINGFACE_TOKEN missing | Add to Render env vars |
| "Network error" | Wrong API URL | Check VITE_API_URL |
| "CORS error" | Domain not allowed | Add to ALLOWED_ORIGINS |
| "500 Internal Server Error" | Backend crash | Check Render logs |

---

## **How to Check Render Logs:**

1. Go to Render Dashboard
2. Click your backend service
3. Click **"Logs"** tab
4. Look for errors when you trigger the podcast

---

## **Fallback Solution:**

If HuggingFace API keeps failing, the service will use template-based generation (lines 159-213 in `podcast_service.py`). This means podcasts WILL work, but they'll use pre-made templates instead of AI-generated content.

---

## **Next Steps:**

1. ✅ Add HUGGINGFACE_TOKEN to Render
2. ✅ Add VITE_API_URL to Vercel
3. ✅ Update CORS allowed origins
4. ✅ Test the endpoint directly
5. ✅ Check Render logs for errors

Once you complete these steps, **both Weekly Highlights and AI Podcasts should work in production!** 🎉
