# Panduan Pengembang Lokal CanvasGen

Panduan ini menjelaskan setup lingkungan lokal, panduan pengembangan lokal, standar penulisan kode, instruksi pengujian, dan prosedur kontrol kualitas untuk pengembang yang bekerja pada proyek **CanvasGen**.

---

## 1. Prasyarat & Setup Lingkungan Lokal

### Persyaratan Sistem
- **Python**: Versi 3.9, 3.10, atau 3.11
- **Hardware GPU (Direkomendasikan)**: GPU NVIDIA dengan dukungan CUDA 11.8+ atau CUDA 12.x (direkomendasikan minimal VRAM 6GB)
- **RAM**: Minimal 8GB (direkomendasikan 16GB)

### Langkah Setup Cepat

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ImamAriadi2022/CanvasGen.git
   cd CanvasGen
   ```

2. **Jalankan script setup lingkungan**:
   - **Windows**:
     ```cmd
     scripts\setup_env.bat
     ```
   - **Linux / macOS**:
     ```bash
     chmod +x scripts/setup_env.sh
     ./scripts/setup_env.sh
     ```

3. **Konfigurasi File Environment**:
   Salin `.env.example` menjadi `.env` dan atur token HuggingFace opsional Anda:
   ```bash
   cp .env.example .env
   ```

---

## 2. Menjalankan Aplikasi Web Lokal

Jalankan antarmuka aplikasi web Streamlit:
```bash
streamlit run app.py
```

---

## 3. Menjalankan Pengujian Otomatis

Jalankan seluruh suite pengujian pytest / unittest:
```bash
pytest tests/ -v
```

Atau jalankan verifikator kompilator python kustom:
```bash
python scripts/run_tests.py
```

---

## 4. Standar Kode & Panduan Style

- **Kepatuhan PEP8**: Seluruh kode harus mematuhi format standar PEP8 (indentasi 4 spasi, panjang baris maksimal 88-100 karakter).
- **Type Hinting**: Seluruh parameter fungsi dan tipe kembalian harus menyertakan anotasi tipe data yang jelas.
- **Docstring**: Seluruh modul, kelas, dan metode publik harus menyertakan docstring Python bergaya Google.
- **Penanganan Error & Logging**: Gunakan `utils.logger.get_logger(__name__)` alih-alih `print()`. Hindari blok `except Exception: pass` tanpa penanganan log.
