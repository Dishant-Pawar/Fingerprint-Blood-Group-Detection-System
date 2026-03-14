# QUICK START GUIDE

## Prerequisites
- Python 3.7+
- Any modern web browser

## Installation (5 minutes)

### Step 1: Setup Backend Environment

**Windows:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python database.py
python app.py
```

**macOS/Linux:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python database.py
python app.py
```

### Step 2: Open Frontend

Open any of these URLs in your browser:

**Option 1: Direct File (Simplest)**
```
Double-click: frontend/index.html
```

**Option 2: Python HTTP Server**
```bash
cd frontend
python -m http.server 8000
```
Then open: `http://localhost:8000`

**Option 3: VS Code Live Server**
- Install "Live Server" extension
- Right-click on `index.html` → "Open with Live Server"

## Testing the System

### 1. Register a Fingerprint
- Go to Register page
- Fill in: Name, Blood Group
- Upload any image as "fingerprint"
- Click Register

### 2. Verify Fingerprint
- Go to Verify page
- Upload the **exact same image**
- See your blood group displayed

## URLs

| Page | URL |
|------|-----|
| Home | http://localhost:8000 or frontend/index.html |
| Register | http://localhost:8000/register.html |
| Verify | http://localhost:8000/verify.html |
| API | http://localhost:5000 |

## Key Files

- `backend/app.py` - Main Flask server
- `backend/database.py` - Database operations
- `backend/fingerprint.py` - Image processing
- `frontend/index.html` - Home page
- `frontend/register.html` - Registration
- `frontend/verify.html` - Verification

## API Endpoints

```
GET  http://localhost:5000/              # API Status
POST http://localhost:5000/api/register   # Register user
POST http://localhost:5000/api/verify     # Verify fingerprint
GET  http://localhost:5000/api/users      # Get all users
```

## Common Issues

| Issue | Solution |
|-------|----------|
| ModuleNotFoundError | Ensure venv is activated and `pip install -r requirements.txt` is run |
| API not found | Make sure backend is running: `python app.py` |
| CORS error | Backend not running or frontend not opened via HTTP server |
| Port 5000 in use | Change port in `app.py`: `app.run(port=5001)` |

## Next Steps

1. Read the full README.md for detailed information
2. Customize the UI in `frontend/css/style.css`
3. Add more features from the "Future Enhancements" section
4. Deploy to production with proper security measures

---

**Everything set up? Try the system now!**
