# 🔍 Pro Feature Troubleshooting Guide

## Problem
Pro badge and subscription features not showing in the UI.

## Solution Steps

### 1. ✅ Backend is Fixed
The subscription API is now working at: `http://localhost:8000/api/v1/subscription/*`

### 2. 🧪 Test the Subscription System

#### Option A: Use the Test Page (Easiest)
1. **Login to the app** at `http://localhost:5173/login`
2. **Navigate to**: `http://localhost:5173/test-subscription`
3. This page shows:
   - Your current subscription status
   - All subscription features
   - Debug information
   - Button to upgrade to Pro for testing

#### Option B: Upgrade via Command Line
```bash
cd backend
.\venv_new\Scripts\python.exe upgrade_user_to_pro.py <your-username>
```

Example:
```bash
.\venv_new\Scripts\python.exe upgrade_user_to_pro.py User123
```

### 3. 📋 Check Your Current Users
Run this to see all users and their subscription tiers:
```bash
cd backend
.\venv_new\Scripts\python.exe upgrade_user_to_pro.py
```

### 4. 🎯 Where to See Pro Badges

Once upgraded to Pro, you'll see the Pro badge in:

1. **AI Content Creator Page** (`/ai-content`)
   - Top right corner of the page header
   - Only shows if you have Pro/Premium tier

2. **Test Subscription Page** (`/test-subscription`)
   - Shows all subscription details
   - Displays all features and their status

### 5. 🔑 Important: Login Required

The Pro badge only shows when:
- ✅ You are logged in
- ✅ Your account has Pro or Premium tier
- ✅ The subscription is active

### 6. 🎨 How Pro Features Work

The system checks:
1. **Frontend**: `useSubscription()` hook fetches data from `/api/v1/subscription/status`
2. **Backend**: Returns user's subscription tier and features
3. **Display**: Pro badge shows if `tier === 'pro'` or `tier === 'premium'`

### 7. 🐛 Debugging Checklist

If Pro badge still doesn't show:

1. **Open Browser Console** (F12)
   - Check for any errors
   - Look for failed API calls

2. **Verify Login**
   - Check `localStorage.getItem('token')` in console
   - Should have a JWT token

3. **Test API Directly**
   ```javascript
   // In browser console:
   const token = localStorage.getItem('token');
   fetch('http://localhost:8000/api/v1/subscription/status', {
       headers: { 'Authorization': `Bearer ${token}` }
   })
   .then(r => r.json())
   .then(console.log);
   ```

4. **Check Network Tab**
   - Look for call to `/api/v1/subscription/status`
   - Verify it returns 200 OK
   - Check the response data

### 8. 📊 Expected Response

When you have Pro, the API should return:
```json
{
  "tier": "pro",
  "status": "active",
  "is_active": true,
  "features": {
    "ai_image_generation": true,
    "advanced_puzzles": true,
    "unlimited_content": true,
    "no_ads": true
  },
  "expires_at": "2027-01-24T..."
}
```

### 9. ⚡ Quick Test

**Fastest way to see the Pro badge:**

1. Login with username: `User123`
2. Run: `.\venv_new\Scripts\python.exe upgrade_user_to_pro.py user123`
3. Navigate to: `http://localhost:5173/test-subscription`
4. You should see Pro badge and all features enabled!

### 10. 📝 Files Changed

Backend:
- ✅ `backend/app/main.py` - Added subscription router
- ✅ `backend/app/core/security.py` - Added get_current_user function
- ✅ `backend/upgrade_user_to_pro.py` - Script to upgrade users

Frontend:
- ✅ `frontend/src/App.jsx` - Added test subscription route
- ✅ `frontend/src/pages/TestSubscriptionPage.jsx` - New test page
- ✅ `frontend/src/hooks/useSubscription.js` - Already existed
- ✅ `frontend/src/components/subscription/ProBadge.jsx` - Already existed

---

**Need Help?** Navigate to `/test-subscription` while logged in to see all debug information!
