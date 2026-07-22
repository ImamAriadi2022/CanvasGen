# Alur Kerja Git & Tahapan Staging CanvasGen

Dokumen ini menjelaskan strategi branching Git, panduan kontribusi, integrasi QA otomatis, dan roadmap pengembangan multi-tahap untuk **CanvasGen**.

---

## 1. Strategi Branching Git

CanvasGen mengikuti alur kerja branching GitFlow:

- **`main`**: Rilis stabil produksi. Seluruh commit harus diberi tag versi semver (misalnya `v1.0.0`).
- **`develop`**: Branch integrasi untuk rilis mendatang dan pencapaian milestone tahap.
- **`feature/<nama-fitur>`**: Branch fitur khusus yang dibuat dari `develop` (misalnya `feature/inpainting-ui`).
- **`bugfix/<nama-masalah>`**: Branch perbaikan bug yang menargetkan masalah tertentu.

---

## 2. Standar Pesan Commit

Seluruh commit wajib mengikuti format Conventional Commits:

- `feat: add DPMSolver scheduler support`
- `fix: resolve VRAM memory leak on batch generation`
- `docs: update Architecture.md diagrams`
- `test: add unit test for OutpaintPipeline canvas expansion`

---

## 3. Roadmap Pengembangan Multi-Tahap

```mermaid
timeline
    title Roadmap Tahapan CanvasGen
    Tahap 1 : Arsitektur Utama & Skeleton : Kebutuhan & Lingkungan : Suite Pengujian & Verifikasi : Setup Google Colab
    Tahap 2 : Integrasi Diffusers : Generasi Text-to-Image : Generasi Batch & Komparasi Scheduler : Engine Inpainting & Outpainting
    Tahap 3 : UI Lengkap Streamlit : Progress Bar & Galeri Gambar : Pengunduh Model & Pengelola Preset : Pengemasan Final & Rilis
```

### Daftar Periksa Kesiapan Transisi Tahap

Untuk bertransisi dari Tahap 1 ke Tahap 2:
- [x] Seluruh skeleton modul engine utama telah didefinisikan dengan PEP8, type hints, dan docstring.
- [x] Suite pengujian unit lulus dengan tingkat keberhasilan 100% pada impor, struktur direktori, dan pengujian asap.
- [x] Manajemen konfigurasi memuat file `.env` dengan bersih.
- [x] Notebook Google Colab (`colab.ipynb`) telah dibuat dan diverifikasi.
