# Railway Redeployment Instructions

## The Problem Was Fixed ✅

**Error:** `The executable 'cd' could not be found`

**Root Cause:** Procfile couldn't properly change directories in Railway's container environment

**Solution:**
1. ✅ Created `run.sh` - A proper bash startup script
2. ✅ Updated `Procfile` to use `bash run.sh`
3. ✅ Updated `Dockerfile` to set working directory to `/app/backend`
4. ✅ Added `PYTHONUNBUFFERED=1` for better logging

---

## How to Redeploy on Railway

### Step 1: Go to Railway Dashboard
Visit: https://railway.app/dashboard

### Step 2: Select Your Project
- Click on your **Fingerprint-Blood-Group-Detection-System** project

### Step 3: Select the Web Service
- Click on the **web** service (not the postgres/database service)

### Step 4: Redeploy
Go to **Deployments** tab and:

**Option A: Manual Redeploy (Quick)**
1. Click the **⋮** (three dots) next to your latest deployment
2. Click **Redeploy**
3. Wait ~2-3 minutes for build and deployment

**Option B: View Build Process**
1. Click the latest deployment
2. Watch the real-time logs:
   - "Build" phase (should complete successfully)
   - "Deploy → Create container" phase
   - Look for: `Running on http://0.0.0.0:5000`

### Step 5: Verify Success ✅

When deployment succeeds, you should see:
```
Starting Container
...
Running on http://0.0.0.0:5000
```

(NOT the old error about 'cd' command)

### Step 6: Get Your Backend URL

1. Go back to the **web** service page
2. Look for the URL in the service details (usually shown at top)
3. Format: `https://web-production-[random].up.railway.app`

### Step 7: Update Frontend Config

Edit `frontend/js/config.js`:

```javascript
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:5000'
    : 'https://web-production-af129c.up.railway.app';  // YOUR RAILWAY URL HERE
```

Then push to GitHub:
```bash
git add frontend/js/config.js
git commit -m "Update Railway backend URL"
git push origin main
```

This will auto-redeploy your Vercel frontend with the correct backend URL.

---

## Testing the Backend

### Test API is Running
```bash
curl https://web-production-af129c.up.railway.app/
```

You should get:
```json
{
  "status": "success",
  "message": "Fingerprint Blood Group Detection API is running!",
  "version": "2.0.0"
}
```

### Test Registration Endpoint
```bash
curl https://web-production-af129c.up.railway.app/api/users
```

You should get:
```json
{
  "status": "success",
  "users": [],
  "total_users": 0
}
```

---

## If Still Failing

### Check Build Logs
1. Deployments → Click latest deployment
2. Click **Build** in left sidebar
3. Look for errors related to:
   - Python import errors
   - Missing dependencies
   - OpenCV build issues

### Common Issues

**"ModuleNotFoundError: No module named 'flask'"**
- Requirements weren't installed
- Solution: Redeploy again

**"Address already in use"**
- Another process is using port 5000
- Railway handles this automatically - just redeploy

**"connection refused"**
- Container is still starting
- Wait 1-2 minutes and try again

### View All Logs
Click on deployment → Tabs on left:
- **Build** - Shows build process
- **Deploy** - Shows deployment process
- **HTTP** - Shows API requests
- **Logs** - Combined logs

---

## Fastest Troubleshooting

1. Go to Railway Dashboard
2. Click your project → web service
3. Click latest deployment
4. Scroll down to view "Build Logs" and "Deploy Logs"
5. Look for red text (errors)
6. Take a screenshot and share the error

---

## Everything is Ready!

All code is on GitHub with the latest fixes. Railway will pull the latest code automatically on redeploy.

**Current Status:**
- ✅ GitHub repository updated
- ✅ Dockerfile fixed
- ✅ Procfile fixed
- ✅ Startup script created
- ✅ Ready for redeploy

**Next Step:** Redeploy on Railway (follow steps above) 🚀
