#!/bin/bash
# Fingerprint Blood Group Detection System - macOS/Linux Startup Script

echo ""
echo "========================================"
echo "Fingerprint Blood Group Detection System"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.7+ from https://www.python.org"
    exit 1
fi

echo "[1/5] Python detected ✓"
echo ""

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "[2/5] Creating virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
else
    echo "[2/5] Virtual environment found ✓"
fi
echo ""

# Activate virtual environment
echo "[3/5] Activating virtual environment..."
source backend/venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi
echo "Virtual environment activated ✓"
echo ""

# Install dependencies
echo "[4/5] Installing Python dependencies..."
cd backend
pip install -r requirements.txt > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    cd ..
    exit 1
fi
cd ..
echo "Dependencies installed ✓"
echo ""

# Initialize database
echo "[5/5] Initializing database..."
cd backend
python3 database.py
cd ..
echo ""

# Start the server
echo "========================================"
echo "Starting Flask Server..."
echo "========================================"
echo ""
echo "Server will run on: http://127.0.0.1:5000"
echo "Press Ctrl+C to stop the server"
echo ""
echo "To open the frontend:"
echo "1. Open in browser: frontend/index.html"
echo "2. Or use: open frontend/index.html"
echo ""
echo "========================================"
echo ""

cd backend
python3 app.py
