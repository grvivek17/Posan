# 🔍 Debugging "Upgrade failed" Error

## What I've Fixed

1. ✅ Updated pricing display: ₹99/month (Pro), ₹999/year (Premium)
2. ✅ Added better error logging in console
3. ✅ Error messages now show the actual error from backend

## How to Debug

### **Step 1: Open Browser Console**

1. Press **F12** to open Developer Tools
2. Go to the **Console** tab
3. Click "Upgrade to Pro" button
4. Watch for error messages

### **Step 2: What to Look For**

**If you see:**
```
❌ Upgrade failed: {detail: "...some error..."}
```

This tells you the exact error from the backend!

**Common Errors:**

1. **"Unauthorized" / "Could not validate credentials"**
   - Cause: Not logged in or token expired
   - Solution: Logout and login again

2. **"User not found"**
   - Cause: Token is invalid
   - Solution: Clear localStorage and login again

3. **"Invalid subscription tier"**
   - Cause: Backend doesn't recognize tier
   - Solution: Check if you're selecting "pro" or "premium"

### **Step 3: Check Network Tab**

1. Open **Network** tab in Developer Tools
2. Click "Upgrade to Pro"
3. Look for the request to `/subscription/upgrade`
4. Check:
   - Status code (should be 200)
   - Response body (shows error reason)
   - Request headers (check if Authorization header exists)

### **Step 4: Verify Authentication**

Open Console and run:
```javascript
console.log('Token:', localStorage.getItem('token'));
console.log('Email:', localStorage.getItem('email'));
```

**Expected:** Should show a long JWT token

**If null:** You need to login first!

## Quick Test Steps

### **Test 1: Using Test Subscription Page**

1. Go to: `http://localhost:5173/test-subscription`
2. Click "Test Upgrade to Pro"
3. Check console for errors

This bypasses the modal and directly calls the API.

### **Test 2: Using Browser Console**

```javascript
// Run this in browser console
const
 token = localStorage.getItem('token');

fetch('http://localhost:8000/api/v1/subscription/upgrade', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
        tier: 'pro',
        payment_provider: 'test',
        payment_id: `test_${Date.now()}`
    })
})
.then(res => res.json())
.then(data => console.log('✅ Response:', data))
.catch(err => console.error('❌ Error:', err));
```

**Expected Success:**
```json
{
  "message": "Successfully upgraded to pro",
  "tier": "pro",
  "expires_at": "2026-02-26T..."
}
```

**Expected Failure (with reason):**
```json
{
  "detail": "Could not validate credentials"
}
```

## Common Fixes

### **Fix 1: Authentication Issue**

If getting "Unauthorized" error:

1. **Logout:**
```javascript
localStorage.clear();
window.location.href = '/login';
```

2. **Login again** with valid credentials

3. **Try upgrade again**

### **Fix 2: Backend Not Running**

Check if backend is accessible:
```javascript
fetch('http://localhost:8000/health')
    .then(res => res.json())
    .then(data => console.log('Backend status:', data));
```

Expected: `{status: "healthy"}`

### **Fix 3: CORS Issue**

If seeing CORS errors:

1. Check backend `.env` has:
```env
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

2. Restart backend server

## What to Report

If still failing, please share:

1. **Console error messages** (copy full text)
2. **Network tab response** (screenshot or copy JSON)
3. **Authentication status** (do you see token in localStorage?)
4. **Which button you clicked** (Test mode or Razorpay?)

## Updated Files

✅ `UpgradeModal.jsx` - Better error handling
✅ Pricing now shows ₹99 and ₹999
✅ Console logs added for debugging

## Next Steps

1. **Clear browser cache** (Ctrl + Shift + Delete)
2. **Refresh the page** (Ctrl + F5)
3. **Open browser console** (F12)
4. **Try upgrade again**
5. **Check console for specific error**

The error message should now tell you **exactly** what's wrong!
