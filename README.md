# 🎨 CanvasGen - Engine Generasi Gambar Berbasis AI

**CanvasGen** adalah platform Generasi Gambar AI modular dan siap produksi yang dibangun menggunakan Python. Dirancang untuk skalabilitas, performa tinggi, dan pengalaman pengguna yang mulus, CanvasGen mendukung sintesis Text-to-Image, generasi batch multi-sampel, komparasi scheduler noise secara langsung, inpainting presisi, outpainting vertikal/horizontal, serta aplikasi web interaktif berbasis Streamlit.

---

## 🏗️ Arsitektur Proyek

CanvasGen mengadopsi arsitektur berlapis yang rapi dengan menerapkan prinsip **SOLID**, pemisahan modular, dan kepatuhan PEP8 secara ketat.

```
CanvasGen/
├── app.py                      # Titik masuk utama aplikasi web Streamlit
├── requirements.txt            # Spesifikasi daftar dependensi proyek
├── README.md                   # Dokumentasi lengkap proyek & rencana pengembangan
├── LICENSE                     # Lisensi MIT
├── .gitignore                  # Aturan pengecualian pelacakan Git
├── .env.example                # Template konfigurasi lingkungan (.env)
├── config/                     # Lapisan manajemen konfigurasi
│   ├── __init__.py
│   └── settings.py             # Pemuat lingkungan Pydantic BaseSettings / Dataclass
├── engine/                     # Engine sintesis difusi machine learning
│   ├── __init__.py
│   ├── loader.py               # Pengelola ModelLoader & cache pipeline
│   ├── generator.py            # Engine text-to-image & batch ImageGenerator
│   ├── scheduler.py            # Suite komparator sampler SchedulerManager
│   ├── inpaint.py              # Sintesis gambar bermasker InpaintPipeline
│   └── outpaint.py             # Pemroses ekspansi kanvas OutpaintPipeline
├── services/                   # Lapisan fasad integrasi layanan
│   ├── __init__.py
│   └── generation_service.py   # Koordinator layanan generasi tingkat tinggi
├── utils/                      # Modul utilitas produksi
│   ├── __init__.py
│   ├── image.py                # Resizing gambar PIL, grid, konversi Base64
│   ├── memory.py               # Pembersihan VRAM PyTorch CUDA & pemantau RAM
│   ├── seed.py                 # Pengatur seed deterministik multi-framework
│   ├── logger.py               # Pengaturan pencatatan log terstruktur
│   └── file_manager.py         # Pengelola output artefak berstempel waktu
├── assets/                     # Direktori aset visual bawaan
├── outputs/                    # Direktori output untuk hasil gambar generasi
├── notebooks/                  # Lingkungan notebook interaktif
│   └── colab.ipynb             # Notebook setup Google Colab yang siap dieksekusi
├── tests/                      # Suite pengujian unit dan pengujian asap otomatis
│   ├── __init__.py
│   ├── test_imports.py         # Verifikasi impor modul
│   ├── test_structure.py       # Verifikasi keberadaan file dan direktori
│   └── test_smoke.py           # Pengujian asap logika inti
├── docs/                       # Dokumentasi pengembang
│   ├── Architecture.md         # Desain sistem detail & alur data
│   ├── Development.md          # Setup & panduan coding
│   └── Workflow.md             # Branching Git & roadmap multi-tahap
└── scripts/                    # Script otomatisasi dan setup
    ├── setup_env.bat           # Script pembuka lingkungan Windows
    ├── setup_env.sh            # Script pembuka lingkungan Linux/macOS
    └── run_tests.py            # Verifikator kompilator & penguji otomatis
```

---

## 🚀 Instalasi & Setup Lokal

### 1. Prasyarat Sistem
- **Python**: Versi 3.9+ telah terinstal.
- **Git**: Terinstal dan terkonfigurasi.
- **GPU (Direkomendasikan)**: GPU NVIDIA dengan dukungan CUDA 11.8 atau 12.x.

### 2. Langkah Setup Lokal

#### Pada Windows:
```cmd
git clone https://github.com/ImamAriadi2022/CanvasGen.git
cd CanvasGen
scripts\setup_env.bat
```

#### Pada Linux / macOS:
```bash
git clone https://github.com/ImamAriadi2022/CanvasGen.git
cd CanvasGen
chmod +x scripts/setup_env.sh
./scripts/setup_env.sh
```

---

## 💻 Alur Kerja Pengembang

### Menjalankan Aplikasi Web Streamlit
```bash
streamlit run app.py
```

### Menjalankan Verifikasi & Pengujian Otomatis
```bash
python scripts/run_tests.py
```
atau secara langsung menggunakan pytest:
```bash
pytest tests/ -v
```

---

## ☁️ Eksekusi Google Colab

CanvasGen menyediakan notebook setup Google Colab otomatis di `notebooks/colab.ipynb`.

1. Buka Google Colab dan unggah `notebooks/colab.ipynb`.
2. Pilih Akselerator Hardware GPU di bawah menu `Runtime -> Change runtime type -> T4 GPU`.
3. Jalankan seluruh sel secara berurutan dari atas ke bawah. Notebook secara otomatis akan:
   - Menghubungkan Google Drive (`/content/drive/MyDrive/CanvasGen`).
   - Melakukan klon atau menarik pembaruan repository.
   - Memasang seluruh dependensi dari `requirements.txt`.
   - Memeriksa akselerasi GPU, versi driver CUDA, VRAM, dan RAM Sistem.
   - Menjalankan pengujian otomatis pytest.

---

## 🗺️ Fitur Masa Depan & Rencana Pengembangan

- **Tahap 1 (Selesai)**: Desain arsitektur, struktur direktori, skeleton modul, paket utilitas, suite pengujian, dan integrasi Google Colab.
- **Tahap 2 (Mendatang)**: Integrasi PyTorch & HuggingFace Diffusers, eksekusi Text-to-Image, generasi batch multi-sampel, pergantian scheduler secara langsung, inpainting, dan outpainting.
- **Tahap 3 (Mendatang)**: Kontrol UI Streamlit tingkat lanjut, galeri gambar, riwayat prompt, pemuatan LoRA, integrasi ControlNet, dan pengelola unduhan model.

---

## 🌿 Panduan Kontribusi & Git

1. **Strategi Branching**: Mengikuti alur GitFlow. Buat branch fitur dari `develop` (`feature/nama-fitur` atau `bugfix/nama-masalah`).
2. **Standar Commit**: Gunakan format Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`).
3. **Pull Request**: Pastikan `python scripts/run_tests.py` lulus 100% sebelum membuka Pull Request.

---

## 📜 Lisensi

Diterbitkan di bawah Lisensi MIT. Lihat [LICENSE](file:///c:/programming/CanvasGen/LICENSE) untuk informasi lebih rinci.
