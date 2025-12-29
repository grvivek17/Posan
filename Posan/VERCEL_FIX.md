# 🔧 FIX: Vercel Deployment Error

## Error: `sh: line 1: vite: command not found`

This happens because Vercel is looking for Vite in the root directory, but it's installed in the `frontend` folder.

---

## ✅ SOLUTION: Configure Root Directory in Vercel

### Step-by-Step Fix:

1. **Go to your Vercel project settings**
   - Open [vercel.com/dashboard](https://vercel.com/dashboard)
   - Select your project (Posan)
   - Go to **Settings** → **General**

2. **Update Root Directory**
   - Find the **"Root Directory"** section
   - Click **"Edit"**
   - Enter: `frontend`
   - Click **"Save"**

3. **Redeploy**
   - Go to **Deployments** tab
   - Click **"Redeploy"** on the latest deployment

---

## 📋 Correct Vercel Configuration

When setting up (or in Project Settings):

| Setting | Value |
|---------|-------|
| **Root Directory** | `frontend` ← **IMPORTANT!** |
| **Framework Preset** | `Vite` |
| **Build Command** | `npm run build` (or leave default) |
| **Output Directory** | `dist` (or leave default) |
| **Install Command** | `npm install` (or leave default) |

---

## 🎯 Why This Works

```
Your Project Structure:
Posan/
├── frontend/          ← Vercel should use THIS as root
│   ├── package.json   ← Vite is here
│   ├── src/
│   └── dist/ (output)
└── backend/           ← Deploy separately to Railway/Render
```

By setting `frontend` as the root directory, Vercel will:
1. Run `npm install` in the `frontend` folder
2. Find Vite in `frontend/node_modules`
3. Build successfully with `vite build`

---

## 🚀 Alternative: Deploy Frontend Only (Recommended)

Since the backend won't work well on Vercel anyway (needs persistent server), deploy them separately:

### **Frontend** → Vercel
- Root Directory: `frontend`
- Framework: Vite

### **Backend** → Railway/Render
- Use the `backend` folder
- Better for FastAPI + PostgreSQL

---

## 📝 Quick Fix Checklist

- [ ] Go to Vercel project settings
- [ ] Set Root Directory to `frontend`
- [ ] Save changes
- [ ] Redeploy
- [ ] ✅ Should work now!

---

## 💡 If Still Not Working

Delete the current Vercel project and create a new one with these settings from the start:

1. Import your GitHub repo
2. **BEFORE deploying**, configure:
   - Root Directory: `frontend`
   - Framework: Vite
3. Deploy

---

**TL;DR**: In Vercel settings, set **Root Directory = `frontend`** and redeploy! 🎯
