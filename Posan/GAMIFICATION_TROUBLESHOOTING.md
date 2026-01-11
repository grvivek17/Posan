# Gamification System - Troubleshooting Guide

## Issue: Blank Achievements Page

### ✅ **FIXED** - Root Cause
The API endpoints require a `user_id` parameter, but the frontend wasn't sending it.

### Solution Applied
Updated all frontend API calls to include `user_id` from localStorage:

```javascript
const userId = localStorage.getItem('user_id');
const response = await axios.get('/api/v1/gamification-v2/stats', {
  params: { user_id: parseInt(userId) },
  headers: { Authorization: `Bearer ${token}` }
});
```

---

## Common Issues & Solutions

### 1. **Blank Page / No Data Showing**

**Symptoms:**
- Achievements page shows blank/loading state
- Points not displaying in header
- Console shows 422 errors

**Solution:**
✅ Already fixed! The frontend now sends `user_id` parameter.

**Verify Fix:**
1. Open browser console (F12)
2. Check Network tab
3. Look for `/gamification-v2/stats` request
4. Should see `?user_id=X` in the URL

---

### 2. **"user_id not found in localStorage"**

**Symptoms:**
- Console warning: "No user_id found in localStorage"
- Points display shows "..."

**Solution:**
Make sure you're logged in. The `user_id` is set during login.

**Check:**
```javascript
// In browser console
console.log(localStorage.getItem('user_id'));
// Should return a number like "1" or "2"
```

**Fix:**
1. Logout
2. Login again
3. Check localStorage

---

### 3. **404 Error on API Calls**

**Symptoms:**
- Console error: "404 Not Found"
- Endpoints not working

**Solution:**
Restart the backend server to load new routes:

```bash
# Stop the server (Ctrl+C)
# Then restart
cd backend
uvicorn app.main:app --reload
```

---

### 4. **Database Tables Missing**

**Symptoms:**
- Error: "relation 'user_activities' does not exist"
- 500 errors from API

**Solution:**
Run the migration script:

```bash
cd backend
python migrate_gamification_tables.py
```

---

### 5. **No Badges Showing**

**Symptoms:**
- Badges page shows 0/0
- No badges in database

**Solution:**
Seed the badges:

```bash
cd backend
python seed_badges.py
```

---

### 6. **Points Not Updating**

**Symptoms:**
- Completed puzzle but no points awarded
- Points stuck at 0

**Possible Causes & Solutions:**

**A. Child Profile Missing**
```sql
-- Check if user has child profile
SELECT * FROM child_profiles WHERE user_id = YOUR_USER_ID;
```

If missing, create one through the app or database.

**B. Duplicate Activity Prevention**
The system prevents duplicate point awards. If you already completed that puzzle, you won't get points again.

**C. Check Activity Log**
```sql
-- See if activity was recorded
SELECT * FROM user_activities WHERE user_id = YOUR_USER_ID ORDER BY created_at DESC;
```

---

### 7. **Level Not Updating**

**Symptoms:**
- Points increase but level stays "Bronze"
- Progress bar stuck

**Solution:**
The level updates automatically when points change. If stuck:

```sql
-- Manually trigger level update
DELETE FROM user_levels WHERE user_id = YOUR_USER_ID;
-- System will recreate on next API call
```

---

### 8. **Frontend Not Hot-Reloading**

**Symptoms:**
- Changes not appearing
- Old code still running

**Solution:**
```bash
# Stop frontend (Ctrl+C)
# Clear cache and restart
cd frontend
npm run dev
```

Or hard refresh browser: `Ctrl + Shift + R`

---

## Verification Checklist

After fixing issues, verify everything works:

### Backend
- [ ] Server running on http://localhost:8000
- [ ] `/api/v1/gamification-v2/stats?user_id=1` returns data
- [ ] `/api/v1/gamification-v2/levels` returns 6 levels
- [ ] `/api/v1/gamification/badges` returns 15 badges

### Database
- [ ] `user_activities` table exists
- [ ] `user_levels` table exists
- [ ] `badges` table has 15 rows
- [ ] User has `child_profile` record

### Frontend
- [ ] Server running on http://localhost:5173
- [ ] `/achievements` page loads
- [ ] Points display in header
- [ ] Badges grid shows badges
- [ ] No console errors

---

## Quick Test

1. **Login** to the app
2. **Navigate** to `/achievements`
3. **Check** if you see:
   - Your points and level
   - Progress bar
   - Activity cards
   - Badges grid
4. **Complete** a puzzle
5. **Verify** points increase

---

## Debug Commands

### Check User Data
```sql
-- Get user info
SELECT u.id, u.username, cp.total_points 
FROM users u 
LEFT JOIN child_profiles cp ON cp.user_id = u.id 
WHERE u.id = YOUR_USER_ID;

-- Get user activities
SELECT activity_type, points_earned, created_at 
FROM user_activities 
WHERE user_id = YOUR_USER_ID 
ORDER BY created_at DESC 
LIMIT 10;

-- Get user level
SELECT * FROM user_levels WHERE user_id = YOUR_USER_ID;

-- Get user badges
SELECT b.name, ua.earned_at 
FROM user_achievements ua 
JOIN badges b ON b.id = ua.badge_id 
WHERE ua.user_id = YOUR_USER_ID;
```

### Check API Responses
```bash
# Test stats endpoint (replace USER_ID)
curl "http://localhost:8000/api/v1/gamification-v2/stats?user_id=1"

# Test levels endpoint
curl "http://localhost:8000/api/v1/gamification-v2/levels"

# Test badges endpoint
curl "http://localhost:8000/api/v1/gamification/badges"
```

---

## Still Having Issues?

1. **Check browser console** for errors
2. **Check backend logs** for errors
3. **Verify database** tables exist
4. **Restart both servers**
5. **Clear browser cache**
6. **Check localStorage** has user_id

---

## Status After Fixes

✅ **Frontend Updated**: All API calls now include `user_id`  
✅ **Auto-Reload**: Vite should hot-reload changes  
✅ **Database Ready**: Tables created and seeded  
✅ **Backend Running**: Endpoints available  

**The achievements page should now work!** 🎉

---

**Last Updated**: January 2026  
**Issue**: Blank page fixed  
**Status**: Resolved
