# How to Run the Fingerprint Blood Group Detection System


# Terminal 1 - Backend
cd d:\RFingerPrint\backend
python app.py

# Terminal 2 - Frontend  
cd d:\RFingerPrint\frontend
python -m http.server 8000

## Backend (Flask API)

Open a terminal in the `D:\RFingerPrint` directory and run:

```bash
cd backend
python app.py
```

**Backend will start on:** `http://127.0.0.1:5000`

---

## Frontend (Static Website)

Open **another terminal** in the `D:\RFingerPrint` directory and run:

```bash
cd frontend
python -m http.server 8000
```

**Frontend will start on:** `http://localhost:8000`

---

## Access the Application

Once both are running, open these URLs in your browser:

| Page | URL |
|------|-----|
| **Home** | `http://localhost:8000` |
| **Register** | `http://localhost:8000/register.html` |
| **Verify** | `http://localhost:8000/verify.html` |
| **Manage** | `http://localhost:8000/manage.html` |
| **API Status** | `http://127.0.0.1:5000/` |

---

## Step-by-Step Guide

1. **Terminal 1 (Backend):**
   ```
   cd D:\RFingerPrint
   cd backend
   python app.py
   ```
   Wait for: `Running on http://127.0.0.1:5000`

2. **Terminal 2 (Frontend):**
   ```
   cd D:\RFingerPrint
   cd frontend
   python -m http.server 8000
   ```
   Wait for: `Serving HTTP on :: port 8000`

3. **Browser:**
   Open `http://localhost:8000` and start using the app!

---

## Alternative: Run Everything with One Script

Run the `start.bat` file (Windows only):
```
.\start.bat
```

This will automatically start both backend and frontend and print all the links in the terminal.

---

## Stop the Servers

- **Backend terminal:** Press `Ctrl+C`
- **Frontend terminal:** Press `Ctrl+C`
