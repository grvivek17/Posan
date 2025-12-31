# Troubleshooting: HuggingFace Token in Render Production

## Issue
HuggingFace token not being loaded properly in Render production deployment.

## Root Cause
Pydantic Settings needs to be configured to read from system environment variables (not just `.env` files) in production.

## Solution Applied

### 1. Updated `config.py`
Added better environment variable handling and debug logging:

```python
# Initialize settings - will load from system env vars first, then .env if exists
settings = Settings()

# Log if HuggingFace token is loaded (for debugging)
if settings.HUGGINGFACE_TOKEN:
    print(f"✅ HuggingFace token loaded: {settings.HUGGINGFACE_TOKEN[:10]}...")
else:
    print("⚠️  WARNING: HUGGINGFACE_TOKEN not set - AI features may not work")
```

## Verification Steps

### Step 1: Check Render Environment Variables
1. Go to Render Dashboard
2. Select **posan-backend** service
3. Click **Environment** tab
4. Verify `HUGGINGFACE_TOKEN` exists and has a value

**Expected:**
```
HUGGINGFACE_TOKEN = hf_xxxxxxxxxxxxxxxxxxxxx
```

### Step 2: Check Deployment Logs
After redeploying, check logs for:

**Success:**
```
✅ HuggingFace token loaded: hf_xxxxxxx...
```

**Failure:**
```
⚠️  WARNING: HUGGINGFACE_TOKEN not set - AI features may not work
```

### Step 3: Force Redeploy
1. In Render dashboard, click **Manual Deploy**
2. Select **Clear build cache & deploy**
3. Wait for deployment to complete
4. Check logs again

## Common Issues & Fixes

### Issue 1: Token Not Set in Render
**Symptom:** Warning message in logs
**Fix:**
1. Render Dashboard → Environment
2. Add environment variable:
   - Key: `HUGGINGFACE_TOKEN`
   - Value: Your HF token (starts with `hf_`)
3. Save
4. Service will auto-redeploy

### Issue 2: Token Has Wrong Name
**Symptom:** Token set but not loading
**Fix:** Ensure exact name match:
- ✅ Correct: `HUGGINGFACE_TOKEN`
- ❌ Wrong: `HUGGING_FACE_TOKEN`
- ❌ Wrong: `HF_TOKEN`
- ❌ Wrong: `HUGGINGFACE_API_KEY`

### Issue 3: Token Has Spaces/Quotes
**Symptom:** Token set but API calls fail
**Fix:** 
- Remove any quotes around the token
- Remove any leading/trailing spaces
- Should be: `hf_AbCdEfGhIj...`
- Not: `"hf_AbCdEfGhIj..."` or ` hf_AbCdEfGhIj... `

### Issue 4: Token Expired or Invalid
**Symptom:** API calls return 401 errors
**Fix:**
1. Go to https://huggingface.co/settings/tokens
2. Check if token is still active
3. Generate new token if needed
4. Update in Render

## Testing After Deploy

### Test 1: Check Startup Logs
```bash
# In Render logs, you should see:
✅ HuggingFace token loaded: hf_xxxxxxx...
```

### Test 2: Test AI Endpoint
Make a request to your AI content endpoint:
```bash
curl -X POST https://your-app.onrender.com/api/v1/ai/generate/story \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "age_group": "6-8",
    "topic": "space",
    "length": "short"
  }'
```

**Expected:** Story content generated
**Error:** Check if HF token is the issue

### Test 3: Check from Frontend
1. Log in to your app
2. Go to AI Content Generator
3. Try generating a story
4. Check browser console for errors

## Environment Variable Priority

Pydantic Settings loads in this order:
1. **System environment variables** (Render sets these)
2. `.env` file (only exists locally)
3. Default values in code

In production (Render), only #1 applies.

## Render Environment Setup Checklist

### Required Variables:
- [x] `DATABASE_URL` - Your Neon/Supabase database URL
- [x] `SECRET_KEY` - Random secret for JWT
- [x] `HUGGINGFACE_TOKEN` - Your HF token
- [x] `ALGORITHM` - HS256 (auto-set in render.yaml)
- [x] `DEBUG` - False (auto-set in render.yaml)

### Optional Variables:
- [ ] `ALLOWED_ORIGINS` - Add your frontend URL
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` - Default: 30
- [ ] `UPLOAD_DIR` - Default: uploads

## Getting Your HuggingFace Token

1. Visit: https://huggingface.co/settings/tokens
2. Log in with your account
3. Click **"New token"**
4. Settings:
   - Name: `POSAN Production`
   - Type: **Read**
   - Click **Generate token**
5. Copy the token (starts with `hf_`)
6. Paste in Render environment variables

## Debugging Commands

### Check if token is loaded (in Python shell):
```python
from app.core.config import settings
print(settings.HUGGINGFACE_TOKEN)
```

### Check environment variable directly:
```python
import os
print(os.getenv("HUGGINGFACE_TOKEN"))
```

### Test HuggingFace connection:
```python
from huggingface_hub import InferenceClient
from app.core.config import settings

client = InferenceClient(token=settings.HUGGINGFACE_TOKEN)
# If this doesn't error, token is valid
```

## Quick Fix Checklist

1. ✅ Token added to Render Environment tab
2. ✅ Token value starts with `hf_`
3. ✅ No quotes or spaces around token
4. ✅ Variable name is exactly `HUGGINGFACE_TOKEN`
5. ✅ Service redeployed after adding token
6. ✅ Logs show "✅ HuggingFace token loaded"
7. ✅ AI endpoints return content (not errors)

## Still Not Working?

### Check Render Logs:
```
Settings → Logs → Look for:
- Build logs
- Deploy logs
- Runtime logs
```

### Look for:
- ✅ "HuggingFace token loaded" message
- ❌ Any errors mentioning "HUGGINGFACE_TOKEN"
- ❌ API authentication errors
- ❌ Pydantic validation errors

### If you see validation errors:
The token might not be loading. Try:
1. Delete the environment variable
2. Re-add it (copy-paste token directly)
3. Redeploy

## Contact Support

If still having issues, collect:
1. Screenshot of Render Environment tab
2. Deployment logs (last 50 lines)
3. Error messages from API calls
4. First 10 characters of your HF token (for verification)

---

**Status**: Configuration updated for proper environment variable loading
**Next Step**: Redeploy on Render and check logs for success message
