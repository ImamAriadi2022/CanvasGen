#!/usr/bin/env bash
# CanvasGen Linux/macOS Environment Setup Script

set -e

echo "========================================================="
echo "             CanvasGen Environment Setup                 "
echo "========================================================="

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 could not be found. Please install Python 3.9+."
    exit 1
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "[INFO] Creating Python virtual environment in ./venv..."
    python3 -m venv venv
else
    echo "[INFO] Virtual environment ./venv already exists."
fi

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source venv/bin/activate

echo "[INFO] Upgrading pip..."
pip install --upgrade pip --quiet

echo "[INFO] Installing requirements from requirements.txt..."
pip install -r requirements.txt

# Copy .env.example if missing
if [ ! -f ".env" ]; then
    echo "[INFO] Creating .env from .env.example..."
    cp .env.example .env
fi

echo "========================================================="
echo "[SUCCESS] CanvasGen Environment setup complete!"
echo "To activate environment run: source venv/bin/activate"
echo "To run tests run: python scripts/run_tests.py"
echo "To run Streamlit app run: streamlit run app.py"
echo "========================================================="
