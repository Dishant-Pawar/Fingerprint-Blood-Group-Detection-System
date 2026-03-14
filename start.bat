@echo off
REM Fingerprint Blood Group Detection System - Windows Startup Script
REM This script sets up and runs the entire system

setlocal enabledelayedexpansion

echo.
echo ========================================
echo Fingerprint Blood Group Detection System
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://www.python.org
    echo Download from: https://www.python.org/downloads/
    echo.
    echo During installation, MAKE SURE to check:
    echo [X] Add Python to PATH
    echo.
    pause
    exit /b 1
)

echo [1/5] Python detected ✓
python --version
echo.

REM Check if virtual environment exists
if not exist "backend\venv" (
    echo [2/5] Creating virtual environment...
    cd backend
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    cd ..
) else (
    echo [2/5] Virtual environment found ✓
)
echo.

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call backend\venv\Scripts\activate.bat
echo Virtual environment activated ✓
echo.

REM Install dependencies
echo [4/5] Installing Python dependencies...
echo This may take 1-2 minutes...
cd backend
echo Upgrading pip and setuptools...
python -m pip install --upgrade pip setuptools wheel
echo Installing packages...
pip install Flask Flask-CORS numpy Werkzeug Pillow
echo Installing OpenCV...
pip install opencv-python
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    echo.
    echo Try running this manually:
    echo   cd backend
    echo   venv\Scripts\activate
    echo   pip install --upgrade pip setuptools wheel
    echo   pip install Flask Flask-CORS numpy Werkzeug opencv-python
    echo.
    pause
    exit /b 1
)
cd ..
echo.
echo Dependencies installed ✓
echo.

REM Initialize database
echo [5/5] Initializing database...
cd backend
python database.py
if errorlevel 1 (
    echo ERROR: Failed to initialize database
    pause
    exit /b 1
)
cd ..
echo.

REM Start the frontend (static) server
echo ========================================
echo Starting Frontend Server...
echo ========================================
echo.
echo Frontend will run on: http://localhost:8000
echo.
cd frontend
start "" cmd /c "python -m http.server 8000"
cd ..
echo Frontend server started in a new window (if available).
echo.

REM Start the backend (Flask) server
echo ========================================
echo Starting Backend (Flask) Server...
echo ========================================
echo.
echo Backend API will run on: http://127.0.0.1:5000
echo.
echo LINKS:
echo   Frontend: http://localhost:8000
echo   Register: http://localhost:8000/register.html
echo   Verify  : http://localhost:8000/verify.html
echo   API Base: http://127.0.0.1:5000
echo.
echo Press Ctrl+C in this window to stop the backend server.
echo (Close the other window to stop the frontend server.)
echo.
echo ========================================
echo.

cd backend
python app.py
