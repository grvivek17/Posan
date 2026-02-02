# 🔧 Razorpay Payment Integration - Configuration Guide

## ❌ Current Issue

You're getting **"Failed to initiate payment. Please try again."** because the Razorpay credentials are not properly configured.

---

## 🔍 Root Cause

The `.env` file had:
```env
RAZORPAY_APIKEY=rzp_test_S2HY7uXgl2Np5D  # ❌ Wrong variable name
```

But the code expects:
```env
RAZORPAY_KEY_ID=rzp_test_...     # ✅ Correct
RAZORPAY_KEY_SECRET=...          # ✅ Missing!
```

---

## ✅ Solution: Configure Razorpay Credentials

### **Step 1: Get Your Razorpay Credentials**

1. **Login to Razorpay Dashboard**: https://dashboard.razorpay.com/
2. **Go to Settings** → **API Keys**
3. **Generate Test Mode Keys** (or use Production keys if ready)
4. You'll get:
   - **Key ID**: `rzp_test_XXXXX...`
   - **Key Secret**: `XXXXXXXXXX...` (keep this secret!)

### **Step 2: Update `.env` File**

Open `backend/.env` and update:

```env
# Razorpay Payment Gateway
RAZORPAY_KEY_ID=rzp_test_S2HY7uXgl2Np5D
RAZORPAY_KEY_SECRET=YOUR_ACTUAL_SECRET_HERE
```

**⚠️ IMPORTANT:**
- Replace `YOUR_ACTUAL_SECRET_HERE` with your real Razorpay Secret
- Never commit real secrets to Git!
- Use Test mode keys for development

### **Step 3: Restart Backend Server**

The environment variables are loaded when the server starts:

```bash
# Stop all servers (Ctrl+C in terminals)
# Then restart:
cd backend
.\venv_new\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **Step 4: Verify Configuration**

Check the console output when server starts:

**✅ Success:**
```
✅ Razorpay client initialized
```

**❌ Failure:**
```
⚠️  WARNING: Razorpay credentials not configured
```

---

## 🧪 Testing Payment Flow

### **Test Razorpay in Test Mode:**

1. **Go to** `http://localhost:5173/homework`
2. **Click** "Upgrade to Pro" (if you're a free user)
3. **Razorpay modal** should open
4. **Use Razorpay Test Cards:**

```
Card Number: 4111 1111 1111 1111
CVV: Any 3 digits
Expiry: Any future date
```

For more test cards: https://razorpay.com/docs/payments/payments/test-card-details/

---

## 📋 Complete .env Template

Here's what your `.env` should look like:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@host/database

# JWT Configuration
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application Settings
APP_NAME=POSAN
DEBUG=True
API_V1_PREFIX=/api/v1

# CORS Settings
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# File Upload Settings
MAX_UPLOAD_SIZE=10485760
UPLOAD_DIR=uploads

# HuggingFace AI
HUGGINGFACE_TOKEN=hf_...

# Email Service (Resend)
RESEND_API_KEY=re_...

# Razorpay Payment Gateway
RAZORPAY_KEY_ID=rzp_test_YOUR_KEY_ID
RAZORPAY_KEY_SECRET=YOUR_SECRET_KEY_HERE
```

---

## 🔒 Security Best Practices

### **1. Use Test Mode for Development**
```
Test Key ID: rzp_test_...
Test Secret: Starts with test mode indicator
```

### **2. Use Production Mode for Live App**
```
Live Key ID: rzp_live_...
Live Secret: Real production secret
```

### **3. Never Commit Secrets**

Add to `.gitignore`:
```gitignore
.env
.env.local
.env.*.local
```

### **4. Use Environment Variables in Production**

Deployment platforms (Vercel, Railway, etc.) allow setting env vars securely without committing them.

---

## 🚨 Common Errors & Solutions

### **Error: "Failed to initiate payment"**

**Causes:**
1. ❌ `RAZORPAY_KEY_SECRET` not set
2. ❌ Wrong variable names in `.env`
3. ❌ Server not restarted after updating `.env`
4. ❌ Invalid credentials

**Solution:**
1. ✅ Set both `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET`
2. ✅ Use exact variable names (case-sensitive!)
3. ✅ Restart backend server
4. ✅ Copy credentials carefully from Razorpay dashboard

### **Error: "Razorpay not configured"**

**Cause:**
- Environment variables not loaded

**Solution:**
```bash
# Verify .env is in correct location:
ls backend/.env  # Should exist

# Check if variables are loaded:
python -c "from app.core.config import settings; print(settings.RAZORPAY_KEY_ID)"
```

### **Error: "Invalid API key"**

**Cause:**
- Using production key in test mode or vice versa

**Solution:**
- Match key type with Razorpay dashboard mode (Test/Live)
- Regenerate keys if needed

---

## 📊 Payment Flow Diagram

```
User Clicks "Upgrade to Pro"
    ↓
Frontend: Opens UpgradeModal
    ↓
Calls: POST /api/v1/subscription/razorpay/create-order
    {tier: "pro"}
    ↓
Backend: Creates Razorpay Order
    - Uses RAZORPAY_KEY_ID + SECRET
    - Returns order_id, amount, key_id
    ↓
Frontend: Opens Razorpay Checkout
    - User enters card details
    - Razorpay processes payment
    ↓
Frontend: Calls POST /api/v1/subscription/razorpay/verify-payment
    {order_id, payment_id, signature}
    ↓
Backend: Verifies Payment
    - Validates signature
    - Upgrades subscription
    - Returns success
    ↓
User: Now has Pro subscription! 🎉
```

---

## 🛠️ Alternative: Test Mode Bypass

For development/testing, you can bypass Razorpay and upgrade directly:

### **Using Test Subscription Page:**

1. Go to `http://localhost:5173/test-subscription`
2. Click "Test Upgrade to Pro"
3. Instant upgrade without payment!

###**Using API Directly:**

```bash
curl -X POST http://localhost:8000/api/v1/subscription/upgrade \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tier": "pro"}'
```

---

## 📁 Files Modified

✅ `backend/.env` - Added correct Razorpay credentials  
✅ `RAZORPAY_CONFIG.md` - This documentation

---

## 🎯 Quick Fix Checklist

- [ ] Get Razor pay Key ID and Secret from dashboard
- [ ] Update `backend/.env` with both values
- [ ] Restart backend server
- [ ] Verify "Razorpay client initialized" in console
- [ ] Test payment flow
- [ ] Use Razorpay test cards for testing

---

## 🆘 Still Not Working?

### **Debug Steps:**

1. **Check Console Output:**
```bash
# Look for this when backend starts:
✅ Razorpay client initialized
```

2. **Test API Endpoint:**
```bash
curl -X POST http://localhost:8000/api/v1/subscription/razorpay/create-order \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tier": "pro"}'
```

3. **Check Browser Console:**
- Press F12
- Look for network errors
- Check API response

4. **Verify Credentials:**
- Login to Razorpay dashboard
- Regenerate keys if unsure
- Copy-paste carefully (no extra spaces!)

---

## 📞 Support

**Razorpay Documentation:**
- https://razorpay.com/docs/
- https://razorpay.com/docs/payments/server-integration/python/

**Test Environment:**
- Dashboard: https://dashboard.razorpay.com/
- Test Cards: https://razorpay.com/docs/payments/payments/test-card-details/

---

**Status:** ⚠️ Needs Configuration  
**Priority:** High  
**Impact:** Blocks payment functionality

**Next Step:** Add your Razorpay Secret to `.env` and restart the server!
