#!/usr/bin/env bash
# CanvasGen Streamlit Web App Launcher Script

set -e

echo "========================================================="
echo "             CanvasGen Streamlit Web Studio              "
echo "========================================================="

if [ -d "venv" ]; then
    echo "[INFO] Activating virtual environment..."
    source venv/bin/activate
fi

echo "[INFO] Launching CanvasGen Streamlit Web Application..."
streamlit run app.py
