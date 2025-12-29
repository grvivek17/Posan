# Vercel Deployment Guide for POSAN Frontend

## 🚀 Quick Setup

### Backend URL
Your backend is deployed at: **https://posan-backend-po1f.onrender.com**

---

## 📝 Configure Environment Variables in Vercel

### Step 1: Access Vercel Dashboard
1. Go to https://vercel.com/dashboard
2. Select your **Posan** project
3. Click on **Settings** tab

### Step 2: Add Environment Variable
1. Click **Environment Variables** in the left sidebar
2. Add the following:

   **Name**: `VITE_API_URL`  
   **Value**: `https://posan-backend-po1f.onrender.com/api/v1`  
   **Environments**: ✅ Production, ✅ Preview, ✅ Development

3. Click **Save**

### Step 3: Redeploy
1. Go to **Deployments** tab
2. Click the **"..."** menu on your latest deployment
3. Select **"Redeploy"**
4. Wait for deployment to complete

---

## 🧪 Testing

After redeployment, test your frontend:

1. **Visit your Vercel URL** (e.g., https://your-app.vercel.app)
2. **Try logging in/registering**
3. **Check browser console** (F12) for any API errors
4. **Verify API calls** are going to `https://posan-backend-po1f.onrender.com/api/v1`

---

## 🔍 Troubleshooting

### Issue: CORS Errors
If you see CORS errors in the browser console:

1. Check backend CORS settings in `backend/app/core/config.py`
2. Ensure your Vercel domain is in `ALLOWED_ORIGINS`
3. Update if needed and redeploy backend

### Issue: 404 Errors
- Verify the `VITE_API_URL` is set correctly in Vercel
- Check that backend is running: https://posan-backend-po1f.onrender.com/
- Verify API endpoints exist in backend Swagger docs

### Issue: Environment Variable Not Working
- Make sure you selected all environments (Production, Preview, Development)
- Redeploy after adding environment variables
- Clear browser cache and try again

---

## 📱 Local Development

For local development, create a `.env` file in the `frontend` folder:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

This will use your local backend instead of the production one.

---

## 🔐 Important Notes

- **Never commit `.env` files** to Git (they're in `.gitignore`)
- **Use `.env.example`** as a template for what variables are needed
- **Environment variables** starting with `VITE_` are exposed to the frontend
- Changes to environment variables **require a redeploy** to take effect

---

## ✅ Checklist

- [ ] Added `VITE_API_URL` environment variable in Vercel
- [ ] Redeployed the application
- [ ] Tested login/registration
- [ ] Verified API calls in browser console
- [ ] Checked that backend CORS allows your Vercel domain

---

## 📚 Resources

- **Backend API**: https://posan-backend-po1f.onrender.com
- **Backend Docs**: https://posan-backend-po1f.onrender.com/docs
- **Vercel Docs**: https://vercel.com/docs/environment-variables
