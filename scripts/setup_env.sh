#!/usr/bin/env bash
# Script Setup Lingkungan Linux/macOS CanvasGen

set -e

echo "========================================================="
echo "             Setup Lingkungan CanvasGen                  "
echo "========================================================="

# Periksa python3
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 tidak ditemukan. Silakan pasang Python 3.9+."
    exit 1
fi

# Buat virtual environment
if [ ! -d "venv" ]; then
    echo "[INFO] Membuat Python virtual environment di ./venv..."
    python3 -m venv venv
else
    echo "[INFO] Virtual environment ./venv sudah ada."
fi

# Aktifkan virtual environment
echo "[INFO] Mengaktifkan virtual environment..."
source venv/bin/activate

echo "[INFO] Memperbarui pip..."
pip install --upgrade pip --quiet

echo "[INFO] Memasang dependensi dari requirements.txt..."
pip install -r requirements.txt

# Salin .env.example jika belum ada
if [ ! -f ".env" ]; then
    echo "[INFO] Menyalin .env.example ke .env..."
    cp .env.example .env
fi

echo "========================================================="
echo "[SUKSES] Setup lingkungan CanvasGen selesai!"
echo "Untuk mengaktifkan venv jalankan: source venv/bin/activate"
echo "Untuk menjalankan pengujian jalankan: python scripts/run_tests.py"
echo "Untuk menjalankan aplikasi web jalankan: streamlit run app.py"
echo "========================================================="
