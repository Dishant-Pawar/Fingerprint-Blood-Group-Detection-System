# Deployment Guide - Vercel + Heroku

## **Option 1: Frontend on Vercel + Backend on Heroku (Recommended)**

### **Step 1: Deploy Frontend to Vercel**

1. **Sign up at [vercel.com](https://vercel.com)** (free)

2. **Connect your Git repository:**
   - Push your code to GitHub, GitLab, or Bitbucket
   - Go to Vercel → New Project → Import repository
   - Select the repository
   - Set Build Command: (leave empty)
   - Set Output Directory: `frontend`

3. **Deploy:**
   - Click "Deploy"
   - Vercel will give you a URL: `https://your-app.vercel.app`

4. **Update backend URL in config.js:**
   ```javascript
   // frontend/js/config.js
   const API_BASE_URL = window.location.hostname === 'localhost' 
       ? 'http://localhost:5000'
       : 'https://your-heroku-backend.herokuapp.com';  // Update after backend deployed
   ```

---

### **Step 2: Deploy Backend to Heroku**

1. **Install Heroku CLI:**
   ```bash
   npm install -g heroku
   ```

2. **Login to Heroku:**
   ```bash
   heroku login
   ```

3. **Create Heroku app:**
   ```bash
   cd d:\RFingerPrint
   heroku create your-app-name
   ```

4. **Set environment variables (if needed):**
   ```bash
   heroku config:set FLASK_ENV=production
   ```

5. **Deploy:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push heroku main
   ```

6. **Monitor logs:**
   ```bash
   heroku logs --tail
   ```

7. **Get your Heroku URL:**
   ```bash
   heroku domains
   ```
   Your URL will be: `https://your-app-name.herokuapp.com`

8. **Update config.js with your Heroku URL**

---

## **Option 2: Full Stack on Vercel with Serverless Functions (Advanced)**

### **Requirements:**
- Need to move from SQLite to cloud database (MongoDB, PostgreSQL, etc.)
- Convert Flask routes to serverless functions

**File structure:**
```
api/
├── register.py
├── verify.py
└── users.py
frontend/
├── index.html
├── register.html
├── verify.html
├── manage.html
└── js/
    ├── config.js
    ├── script.js
    └── style.css
vercel.json
```

### **Create vercel.json:**
```json
{
  "buildCommand": "pip install -r requirements.txt",
  "outputDirectory": "frontend",
  "functions": {
    "api/**/*.py": {
      "memory": 3008,
      "maxDuration": 30
    }
  },
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1.py"
    },
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ]
}
```

---

## **Option 3: Docker Deployment (Railway, Render, Fly.io)**

### **1. Create Dockerfile:**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "backend/app.py"]
```

### **2. Deploy to Railway:**
- Go to [railway.app](https://railway.app)
- Click "New Project" → "Deploy from GitHub"
- Select your repository
- Add environment variables
- Deploy

---

## **Recommended: Option 1 (Vercel + Heroku)**

**Pros:**
- ✅ Free tier available for both
- ✅ Easy to set up
- ✅ Good performance
- ✅ SQLite works fine on Heroku

**Cons:**
- Heroku free tier is being deprecated (paid tier required soon)

**Better Alternative: Vercel + Railway/Render**
- Vercel: Free frontend hosting
- Railway/Render: Free tier for backend

---

## **After Deployment:**

1. **Update config.js** with production URLs
2. **Test all endpoints:**
   - Register: `https://your-app.vercel.app/register.html`
   - Verify: `https://your-app.vercel.app/verify.html`
   - Manage: `https://your-app.vercel.app/manage.html`

3. **Enable CORS** in backend for your Vercel domain:
   ```python
   # backend/app.py
   CORS(app, resources={
       r"/api/*": {
           "origins": ["https://your-app.vercel.app", "http://localhost:3000"]
       }
   })
   ```

---

## **Questions?**

Let me know which option you prefer, and I'll set it up for you!
