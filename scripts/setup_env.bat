@echo off
REM Script Setup Lingkungan Windows CanvasGen

echo =========================================================
echo              Setup Lingkungan CanvasGen
echo =========================================================

REM Periksa apakah Python terinstal
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan atau belum ditambahkan ke PATH!
    exit /b 1
)

REM Buat virtual environment jika belum ada
if not exist "venv" (
    echo [INFO] Membuat Python virtual environment di .\venv...
    python -m venv venv
) else (
    echo [INFO] Virtual environment .\venv sudah ada.
)

REM Aktifkan virtual environment dan pasang dependensi
echo [INFO] Mengaktifkan virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Memperbarui pip...
python -m pip install --upgrade pip --quiet

echo [INFO] Memasang dependensi dari requirements.txt...
pip install -r requirements.txt

REM Salin .env.example ke .env jika belum ada
if not exist ".env" (
    echo [INFO] Menyalin .env.example ke .env...
    copy .env.example .env
)

echo =========================================================
echo [SUKSES] Setup lingkungan CanvasGen selesai!
echo Untuk mengaktifkan venv jalankan: venv\Scripts\activate.bat
echo Untuk menjalankan pengujian jalankan: python scripts\run_tests.py
echo Untuk menjalankan aplikasi web jalankan: streamlit run app.py
echo =========================================================
