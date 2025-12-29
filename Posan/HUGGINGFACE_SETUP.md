# HuggingFace API Token Setup Guide

## 🔑 Where to Set HuggingFace Token

The HuggingFace token is a **BACKEND** secret. Here's where it goes:

---

## 🌐 **For Production (Render) - REQUIRED**

### Step 1: Get Your HuggingFace Token

1. **Visit HuggingFace**: https://huggingface.co/
2. **Sign in** (or create account)
3. **Go to Settings** → **Access Tokens**: https://huggingface.co/settings/tokens
4. **Click "New token"**
5. **Configure**:
   - Name: `Posan Production`
   - Type: **Read** (sufficient for inference)
6. **Copy the token** (starts with `hf_...`)

### Step 2: Add to Render

1. **Go to Render Dashboard**: https://dashboard.render.com/
2. **Select your service**: Click `posan-backend`
3. **Go to Environment tab** (left sidebar)
4. **Find or Add**:
   ```
   Key:   HUGGINGFACE_TOKEN
   Value: hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
5. **Click "Save Changes"**
6. **Wait for auto-redeploy** (or manually redeploy)

---

## 💻 **For Local Backend Development (Optional)**

If you want to run the backend locally and test AI features:

### Create `backend/.env` file:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/posan

# JWT Security
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
APP_NAME=POSAN
DEBUG=True
API_V1_PREFIX=/api/v1

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# HuggingFace AI
HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

⚠️ **Note**: The `backend/.env` file is gitignored and should NEVER be committed!

---

## ✅ **Verification**

### Check if Token is Set on Render:

1. Go to: https://dashboard.render.com/
2. Select: `posan-backend`
3. Click: **Environment** tab
4. Look for: `HUGGINGFACE_TOKEN`
5. Should show: `••••••••••••` (hidden for security)

### Test AI Endpoints:

Visit: https://posan-backend-po1f.onrender.com/docs

Try these AI endpoints:
- `POST /api/v1/ai/generate/story` - Generate a story
- `POST /api/v1/ai/generate/article` - Generate an article
- `POST /api/v1/ai/generate/quiz` - Generate quiz questions
- `GET /api/v1/ai/generate/fun-fact` - Generate a fun fact
- `GET /api/v1/ai/generate/riddle` - Generate a riddle

---

## 🚨 **Important Notes**

### ❌ **DO NOT** put HuggingFace token in:
- ❌ Frontend `.env` file
- ❌ Git commits
- ❌ Public repositories
- ❌ Frontend code

### ✅ **DO** put HuggingFace token in:
- ✅ Render Environment Variables (production)
- ✅ `backend/.env` (local development only, gitignored)

---

## 🔍 **Troubleshooting**

### Issue: AI endpoints return errors

**Check backend logs on Render**:
1. Go to Render Dashboard
2. Select `posan-backend`
3. Click **Logs** tab
4. Look for HuggingFace-related errors

**Common errors**:
- `HUGGINGFACE_TOKEN not set` → Add token in Render Environment
- `Invalid token` → Get a new token from HuggingFace
- `Rate limit exceeded` → Wait or upgrade HuggingFace plan

### Issue: Token not working

1. **Verify token is active**: https://huggingface.co/settings/tokens
2. **Check token permissions**: Must have "Read" access
3. **Redeploy backend** after adding token
4. **Check environment variable name**: Must be exactly `HUGGINGFACE_TOKEN`

---

## 📊 **Current Configuration**

### Backend expects:
- **Variable name**: `HUGGINGFACE_TOKEN`
- **Location**: `backend/app/core/config.py` (line 30)
- **Usage**: `backend/app/services/ai_content.py` (line 10)

### Render configuration:
- **File**: `render.yaml` (line 25-26)
- **Sync**: `false` (must be manually set in dashboard)

---

## 🎯 **Quick Checklist**

- [ ] Created HuggingFace account
- [ ] Generated API token (Read access)
- [ ] Added `HUGGINGFACE_TOKEN` to Render Environment
- [ ] Saved changes in Render
- [ ] Backend redeployed (automatic or manual)
- [ ] Tested AI endpoints at `/docs`
- [ ] AI features working in application

---

## 📚 **Related Files**

- `render.yaml` - Lines 25-26 (declares the env var)
- `backend/app/core/config.py` - Line 30 (defines the setting)
- `backend/app/services/ai_content.py` - Line 6-10 (uses the token)
- `backend/.env.example` - Template for local development

---

## 🆘 **Need Help?**

- **HuggingFace Docs**: https://huggingface.co/docs/hub/security-tokens
- **Render Docs**: https://render.com/docs/environment-variables
- **Backend API Docs**: https://posan-backend-po1f.onrender.com/docs
