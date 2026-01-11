# Password Reset - Testing Guide

## ✅ Password Reset Feature is Working!

The password reset feature has been implemented and is ready to test.

---

## 🧪 How to Test:

### Step 1: Go to Login Page
Navigate to: `http://localhost:5173/login`

### Step 2: Click "Forgot password?" Link
You'll see the link below the password field.

### Step 3: Enter Your Email
Use one of these existing emails from your database:
- `grvivek17@gmail.com`
- `grvivek@gmail.com`
- `abc@gmail.com`
- `user123@abc.com`
- `harthi410@gmail.com`
- `test123@gmail.com`
- `user1@gmail.com`

### Step 4: Click "Send Reset Link 📧"
The system will:
1. Generate a secure reset token
2. Show you a success message
3. **For testing:** Display the reset link directly on screen

### Step 5: Click the Reset Link
The link will look like:
```
http://localhost:5173/reset-password?token=...
```

### Step 6: Enter New Password
- Minimum 6 characters
- Enter it twice to confirm

### Step 7: Click "Reset Password 🔐"
The password will be updated in the database.

### Step 8: Login with New Password
You'll be redirected to the login page.
Try logging in with your new password!

---

## 🔍 Debugging Steps:

If the password isn't updating, check:

### 1. Browser Console (F12)
Look for these logs:
```
Resetting password with token: ...
New password length: ...
Password reset response: ...
```

### 2. Backend Terminal
Look for these logs:
```
Updating password for user: email@example.com (ID: X)
Password updated successfully for user: email@example.com
```

### 3. Backend API Request
Check if the request reaches the backend:
```
INFO:     127.0.0.1:XXXXX - "POST /api/v1/auth/reset-password?token=...&new_password=... HTTP/1.1" 200 OK
```

---

## 🐛 Common Issues & Solutions:

### Issue 1: "Invalid reset token"
**Solution:** The token may have expired (1 hour limit). Request a new reset link.

### Issue 2: "Passwords do not match"
**Solution:** Make sure both password fields match exactly.

### Issue 3: Password not updating
**Possible causes:**
1. Database connection issue
2. Session not committing
3. Wrong user being updated

**Check:**
- Backend logs for "Password updated successfully"
- Browser console for API response
- Try logging in with the NEW password

### Issue 4: "Token has expired"
**Solution:** Tokens expire after 1 hour. Request a new one.

---

## 🔧 Manual Database Check:

To verify the password was actually updated, run this in the backend directory:

```bash
python -c "from app.core.database import SessionLocal; from app.models.user import User; db = SessionLocal(); user = db.query(User).filter(User.email == 'YOUR_EMAIL').first(); print(f'Password hash: {user.hashed_password[:50]}...'); db.close()"
```

Replace `YOUR_EMAIL` with the email you used.

The hash should change after password reset.

---

## 📊 What Happens Behind the Scenes:

1. **Forgot Password Request:**
   ```
   POST /api/v1/auth/forgot-password?email=user@example.com
   ```
   - Finds user by email
   - Generates secure token
   - Returns token (in testing mode)

2. **Token Verification:**
   ```
   POST /api/v1/auth/verify-reset-token?token=...
   ```
   - Decodes token
   - Checks expiration
   - Returns validity status

3. **Password Reset:**
   ```
   POST /api/v1/auth/reset-password?token=...&new_password=...
   ```
   - Validates token
   - Hashes new password
   - Updates user record
   - Commits to database

4. **Login with New Password:**
   ```
   POST /api/v1/auth/login
   ```
   - Verifies new password hash
   - Returns access token

---

## ✅ Success Indicators:

You'll know it worked when:
1. ✅ Success message appears: "Password successfully reset"
2. ✅ Redirect to login page after 2 seconds
3. ✅ Can login with NEW password
4. ✅ Cannot login with OLD password
5. ✅ Backend logs show "Password updated successfully"

---

## 🔒 Security Features Implemented:

- ✅ Secure token generation
- ✅ 1-hour token expiration
- ✅ Password hashing (bcrypt)
- ✅ No email enumeration
- ✅ Token validation
- ✅ Database transaction safety

---

## 📝 Next Steps if Still Not Working:

1. **Check backend logs** - Look for any errors
2. **Check browser console** - Look for API errors
3. **Verify database connection** - Ensure DB is accessible
4. **Test with curl** - Direct API test:
   ```bash
   # Request reset
   curl -X POST "http://localhost:8000/api/v1/auth/forgot-password?email=grvivek17@gmail.com"
   
   # Use the token from response
   curl -X POST "http://localhost:8000/api/v1/auth/reset-password?token=TOKEN_HERE&new_password=newpass123"
   ```

5. **Check database directly** - Verify the hash changed

---

## 🎯 Test Checklist:

- [ ] Can access forgot password page
- [ ] Can enter email and submit
- [ ] Receives success message
- [ ] Reset link is displayed
- [ ] Can click reset link
- [ ] Token is verified successfully
- [ ] Can enter new password
- [ ] Passwords match validation works
- [ ] Submit button works
- [ ] Success message appears
- [ ] Redirects to login
- [ ] Can login with NEW password
- [ ] Cannot login with OLD password

---

**If all checks pass, the feature is working correctly!** ✅

If you're still having issues, please share:
1. The email you're using
2. Browser console logs
3. Backend terminal logs
4. Any error messages you see
