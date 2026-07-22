@echo off
REM CanvasGen Streamlit Web App Launcher Script

echo =========================================================
echo              CanvasGen Streamlit Web Studio
echo =========================================================

if exist "venv\Scripts\python.exe" (
    echo [INFO] Menjalankan CanvasGen dari lingkungan virtual venv...
    .\venv\Scripts\python.exe -m streamlit run app.py
) else (
    echo [INFO] Menjalankan CanvasGen Streamlit Web Application...
    python -m streamlit run app.py
)

pause
