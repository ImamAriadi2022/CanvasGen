@echo off
REM CanvasGen Windows Environment Setup Script

echo =========================================================
echo              CanvasGen Environment Setup
echo =========================================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to PATH!
    exit /b 1
)

REM Create virtual environment if it does not exist
if not exist "venv" (
    echo [INFO] Creating Python virtual environment in .\venv...
    python -m venv venv
) else (
    echo [INFO] Virtual environment .\venv already exists.
)

REM Activate virtual environment and install requirements
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Upgrading pip...
python -m pip install --upgrade pip --quiet

echo [INFO] Installing requirements from requirements.txt...
pip install -r requirements.txt

REM Copy .env.example to .env if not present
if not exist ".env" (
    echo [INFO] Copying .env.example to .env...
    copy .env.example .env
)

echo =========================================================
echo [SUCCESS] CanvasGen Environment setup complete!
echo To activate environment run: venv\Scripts\activate.bat
echo To run tests run: python scripts\run_tests.py
echo To run Streamlit app run: streamlit run app.py
echo =========================================================
