# AI Not Working in Production - Debugging Guide

## Issue
AI features work locally but fail in production (Render deployment).

## Systematic Debugging Checklist

### ✅ Step 1: Verify HuggingFace Token in Render

**Go to Render Dashboard:**
1. Select your `posan-backend` service
2. Click **Environment** tab
3. Look for `HUGGINGFACE_TOKEN`

**Check:**
- [ ] Variable exists
- [ ] Variable name is exactly `HUGGINGFACE_TOKEN` (case-sensitive)
- [ ] Value starts with `hf_`
- [ ] No quotes around the value
- [ ] No extra spaces

**Should look like:**
```
HUGGINGFACE_TOKEN = hf_AbCdEfGhIjKlMnOpQrStUvWxYz1234567890
```

**NOT like:**
```
❌ "hf_AbCdEf..."  (has quotes)
❌  hf_AbCdEf...   (has leading space)
❌ HUGGING_FACE_TOKEN (wrong name)
```

---

### ✅ Step 2: Check Render Deployment Logs

**In Render Dashboard:**
1. Go to your service
2. Click **Logs** tab
3. Look for startup messages

**What to look for:**

**✅ Success:**
```
✅ HuggingFace token loaded: hf_xxxxxxx...
Starting uvicorn...
Application startup complete
```

**❌ Problem:**
```
⚠️  WARNING: HUGGINGFACE_TOKEN not set - AI features may not work
```

**If you see the warning:**
→ Token is NOT being read! Go back to Step 1.

---

### ✅ Step 3: Check API Response

**Test your production API directly:**

**Open Terminal and run:**
```bash
curl -X POST https://your-backend.onrender.com/api/v1/ai/generate/story \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "age_group": "6-8",
    "topic": "space",
    "length": "short"
  }'
```

**Replace:**
- `your-backend.onrender.com` with your actual Render URL
- `YOUR_JWT_TOKEN` with a valid token (get from login)

**Expected Response:**
```json
{
  "story": "Once upon a time...",
  "title": "Space Adventure"
}
```

**Error Responses & Fixes:**

**401 Unauthorized:**
```json
{"detail": "Not authenticated"}
```
→ JWT token is invalid or missing

**500 Internal Server Error:**
```json
{"detail": "Error generating..."}
```
→ HuggingFace token issue or API error

**Check the error message for clues!**

---

### ✅ Step 4: Check Frontend Configuration

**Check if frontend knows about your backend:**

**Look in browser console (F12):**
- Network tab
- Look for API calls
- Check the URL being called

**Should be:**
```
https://your-backend.onrender.com/api/v1/ai/...
```

**NOT:**
```
http://localhost:8000/api/v1/ai/...  ❌
```

**Fix if needed:**
Set environment variable in your frontend deployment (Vercel/Netlify):
```
VITE_API_URL=https://your-backend.onrender.com/api/v1
```

---

### ✅ Step 5: Check CORS Settings

**Symptoms of CORS issue:**
- Browser console shows: "CORS policy" error
- Request fails before reaching backend
- OPTIONS request fails

**Fix:**
In Render Environment, set:
```
ALLOWED_ORIGINS=https://your-frontend-url.vercel.app,http://localhost:5173
```

**Replace** `your-frontend-url.vercel.app` with your actual frontend URL!

---

### ✅ Step 6: Verify Token is Valid

**Test your HF token directly:**

1. Go to: https://huggingface.co/settings/tokens
2. Find your token
3. Check status (should be "Active")
4. Check permissions (needs at least "Read")

**Test the token:**
```bash
curl https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-1B-Instruct \
  -H "Authorization: Bearer hf_YOUR_TOKEN_HERE"
```

**Should NOT return:**
```json
{"error": "Invalid token"}
```

---

### ✅ Step 7: Check Specific Error Messages

**Look in Render Logs for these:**

**Error 1: "Failed inference"**
```
huggingface_hub.utils._errors.HfHubHTTPError: 401 Client Error
```
→ Token is invalid or expired

**Error 2: "Model is loading"**
```
Model is currently loading
```
→ Wait 2-3 minutes and try again (HF cold start)

**Error 3: "Rate limit exceeded"**
```
Rate limit exceeded
```
→ Too many requests, wait or upgrade HF plan

**Error 4: "Authentication failed"**
```
Authentication token not found
```
→ Token not being read from environment

---

## 🔍 Quick Diagnosis

### Run This Command in Render Shell

**In Render Dashboard:**
1. Go to your service
2. Click **Shell** tab
3. Run:

```python
python3 -c "import os; print('Token exists:', bool(os.getenv('HUGGINGFACE_TOKEN'))); print('Token value:', os.getenv('HUGGINGFACE_TOKEN')[:20] if os.getenv('HUGGINGFACE_TOKEN') else 'NOT SET')"
```

**Expected Output:**
```
Token exists: True
Token value: hf_AbCdEfGhIjKlMnOp
```

**If you see:**
```
Token exists: False
Token value: NOT SET
```
→ Environment variable is NOT set in Render!

---

## 🛠️ Most Common Fixes

### Fix 1: Redeploy After Setting Token
After adding `HUGGINGFACE_TOKEN`:
1. Render auto-redeploys
2. Wait for deployment to complete
3. Check logs for success message

### Fix 2: Clear Build Cache
Sometimes Render needs a fresh start:
1. In Render Dashboard
2. Click **Manual Deploy**
3. Select **Clear build cache & deploy**

### Fix 3: Check Token Format
Make sure token:
- Starts with `hf_`
- Has no spaces before/after
- Has no quotes
- Is the full token (not truncated)

### Fix 4: Generate New Token
If token might be compromised:
1. Go to HuggingFace settings
2. Revoke old token
3. Create new token
4. Update in Render
5. Redeploy

---

## 📊 Debugging Workflow

```
1. Check Render Environment Variables
   ↓
   Problem? → Add/Fix HUGGINGFACE_TOKEN
   ↓
2. Check Render Logs
   ↓
   See warning? → Token not loading
   ↓
3. Manual Redeploy
   ↓
   Still failing? → Check token validity
   ↓
4. Test API Directly
   ↓
   Error? → Read error message carefully
   ↓
5. Check Frontend URL
   ↓
   Wrong backend? → Set VITE_API_URL
   ↓
6. Check CORS
   ↓
   CORS error? → Set ALLOWED_ORIGINS
```

---

## 🎯 Immediate Actions

### Do These RIGHT NOW:

1. **Check Render Environment Tab**
   - Is `HUGGINGFACE_TOKEN` there?
   - Copy the first 10 chars, verify it's correct

2. **Check Render Logs**
   - Do you see "✅ HuggingFace token loaded"?
   - Or "⚠️  WARNING: HUGGINGFACE_TOKEN not set"?

3. **Test API Endpoint**
   - Use curl or Postman
   - Try calling your AI endpoint directly
   - What error do you get?

4. **Check Browser Console**
   - What URL is frontend calling?
   - Any CORS errors?
   - What's the exact error message?

---

## 📝 Information Needed to Help Debug

If still not working, provide:
1. ✅ Screenshot of Render Environment tab (blur token value)
2. ✅ Last 20 lines of Render deployment logs
3. ✅ Error message from browser console
4. ✅ Response when testing API with curl
5. ✅ Your Render backend URL
6. ✅ Your frontend URL

---

## 🚨 Emergency Checklist

- [ ] `HUGGINGFACE_TOKEN` exists in Render Environment
- [ ] Token value starts with `hf_`
- [ ] Logs show "✅ HuggingFace token loaded"
- [ ] Service has redeployed since adding token
- [ ] Token is valid on HuggingFace website
- [ ] Frontend is calling correct backend URL
- [ ] ALLOWED_ORIGINS includes frontend URL
- [ ] No CORS errors in browser console

**If ALL checked and still not working:**
→ Share the specific error message you're getting!

