# Railway Deployment Fix Guide

## What Was Fixed

✅ **Updated Procfile** - Changed from `python` to `python3`  
✅ **Added Dockerfile** - Proper Docker build configuration for Railway  
✅ **Created requirements.txt** in root directory  
✅ **Fixed Flask app.py** - Now reads PORT from environment and uses 0.0.0.0 for production  
✅ **Added railway.json** - Railway configuration file  

---

## How to Redeploy on Railway

### **Step 1: Go to Railway Dashboard**
https://railway.app/dashboard

### **Step 2: Navigate to Your Deployment**
- Click on your project
- Click on the **web** service

### **Step 3: Redeploy**
There are two ways:

#### **Option A: Manual Redeploy (Easiest)**
1. Go to **Deployments** tab
2. Click the three dots (⋯) next to your latest deployment
3. Click **Redeploy**
4. Wait for deployment to complete

#### **Option B: GitHub Auto-Deploy (Recommended)**
Since code is pushed to GitHub:
1. Go to **Settings** tab
2. Under "GitHub Integration", make sure it's connected
3. Enable "Redeploy on Push" (if available)
4. Any future pushes to `main` branch will auto-deploy

### **Step 4: Monitor Logs**
After deployment:
1. Click on **Deployments** tab
2. Click on the active deployment
3. You should see:
   ```
   Building application image...
   Starting container...
   * Running on http://0.0.0.0:5000
   ```

### **Step 5: Get Your Backend URL**
1. Go back to the project
2. Click **web** service
3. You should see a URL like: `https://web-production-xxxx.up.railway.app`

### **Step 6: Update Frontend Config**
Update `frontend/js/config.js`:
```javascript
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000'
    : 'https://web-production-xxxx.up.railway.app';  // YOUR RAILWAY URL
```

Then:
```bash
git add frontend/js/config.js
git commit -m "Update Railway backend URL"
git push origin main
```

---

## Common Issues & Solutions

### Issue: "python: command not found"
**Status:** ✅ FIXED in latest deployment

### Issue: Port Already in Use
Railway automatically assigns PORT via environment variable.
**Status:** ✅ FIXED - app now reads from `$PORT`

### Issue: Cannot Connect to Backend
Make sure:
1. Railway service is **Running** (green status)
2. Check logs for errors: `Deployments` → Click deployment
3. Update `config.js` with correct Railway URL
4. Clear browser cache (Ctrl+Shift+Delete)

### Issue: 503 Bad Gateway
Wait 2-3 minutes for container to fully start.

---

## Verifying Deployment

### Test Backend is Running
Visit: `https://your-railway-url/` in browser

You should see:
```json
{
  "status": "success",
  "message": "Fingerprint Blood Group Detection API is running!",
  "version": "2.0.0"
}
```

### Test API Endpoint
```bash
curl -X GET https://your-railway-url/api/users
```

---

## Environment Variables (Optional)

If you need to set environment variables on Railway:

1. Go to **Settings** tab
2. Click **Variables**
3. Add any needed variables (none required for basic setup)

Common variables:
```
FLASK_ENV=production
DEBUG=False
```

---

## Database Persistence

⚠️ **Important:** SQLite database (`database.db`) is stored in the container.

**Problem:** When Railway restarts, the database is lost (containers are ephemeral).

**Solution Options:**

### Option 1: Use PostgreSQL on Railway (Recommended)
1. Add a PostgreSQL database from Railway
2. Modify `database.py` to use PostgreSQL instead of SQLite
3. Redeploy

### Option 2: Mount External Storage
1. Use Railway's "Volumes" feature
2. Mount storage to `/app/backend/database.db`

### Option 3: Keep SQLite (For Testing Only)
- Data resets on each redeploy
- Fine for testing
- Not suitable for production

---

## Next Steps

1. ✅ Redeploy on Railway (follow Step 1-4 above)
2. ✅ Get your Railway URL
3. ✅ Update `frontend/js/config.js` with Railway URL
4. ✅ Deploy frontend to Vercel
5. ✅ Test registration and verification

---

## Still Having Issues?

Check:
1. **Build Logs:** Deployments → Click latest → "Build Logs"
2. **Deploy Logs:** Deployments → Click latest → "Deploy Logs"
3. **HTTP Logs:** Deployments → Click latest → "HTTP Logs"

All logs are at: https://railway.app/dashboard → Your Project → Logs

---

## Quick Commands

```bash
# View current deployment
railway status

# Check logs locally
railway logs

# Set environment variable
railway variables set FLASK_ENV=production

# Redeploy
railway deploy
```

---

**Your Backend Should Now Work on Railway! 🚀**
