# Dokumentasi Submisi Dicoding CanvasGen

Dokumen ini menjelaskan spesifikasi dan arsitektur pengemasan berkas submisi Dicoding di dalam direktori `submit/`.

---

## 1. Arsitektur Folder Submisi (`submit/`)

Folder `submit/` didesain secara independen agar dapat di-zip dan diunggah langsung ke platform penilaian Dicoding tanpa merusak struktur proyek utama.

```
CanvasGen/
└── submit/
    ├── Pipeline_submission_BFGAI_Imam.ipynb   # Laporan pipeline AI
    ├── Streamlit_submission_BFGAI_Imam.ipynb  # Laporan aplikasi Streamlit
    ├── requirements.txt                       # Spesifikasi pustaka
    ├── README.md                              # Dokumentasi penyerahan
    └── submission_checklist.md                # Tabel verifikasi kriteria
```

---

## 2. Prosedur Pembuatan Arsip Submisi (.zip)

Untuk mengompresi folder `submit/` menjadi file ZIP yang siap diunggah ke Dicoding:

### Pada Windows:
```cmd
powershell Compress-Archive -Path submit\* -DestinationPath submit_CanvasGen_Imam.zip
```

### Pada Linux / macOS:
```bash
zip -r submit_CanvasGen_Imam.zip submit/
```

---

## 3. Sinkronisasi dengan Proyek Utama

Setiap pembaruan pada modul `engine/`, `services/`, atau `utils/` secara otomatis terekfleksikan pada notebook di `submit/`. Verifikasi struktur submission diuji secara otomatis melalui `tests/test_structure.py`.
