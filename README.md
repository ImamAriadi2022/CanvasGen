# 🎨 CanvasGen - AI Image Generation Engine

**CanvasGen** is a modular, production-ready AI Image Generation platform built in Python. Designed for scalability, high performance, and seamless user experience, CanvasGen supports Text-to-Image synthesis, multi-sample batch generation, live noise scheduler comparisons, precise inpainting, directional outpainting, and an interactive Streamlit web application.

---

## 🏗️ Project Architecture

CanvasGen adopts a clean, layered architecture enforcing **SOLID** principles, modular separation, and strict PEP8 compliance.

```
CanvasGen/
├── app.py                      # Streamlit web application entrypoint
├── requirements.txt            # Project dependency specifications
├── README.md                   # Complete project documentation
├── LICENSE                     # MIT License
├── .gitignore                  # Git tracking exclusion rules
├── .env.example                # Configuration template
├── config/                     # Configuration management layer
│   ├── __init__.py
│   └── settings.py             # Pydantic BaseSettings environment loader
├── engine/                     # Machine learning diffusion synthesis engine
│   ├── __init__.py
│   ├── loader.py               # ModelLoader & pipeline cache manager
│   ├── generator.py            # ImageGenerator text-to-image & batch engine
│   ├── scheduler.py            # SchedulerManager sampler comparative suite
│   ├── inpaint.py              # InpaintPipeline masked image synthesizer
│   └── outpaint.py             # OutpaintPipeline canvas expansion processor
├── services/                   # Service integration facade layer
│   ├── __init__.py
│   └── generation_service.py   # High-level generation service coordinator
├── utils/                      # Production utility modules
│   ├── __init__.py
│   ├── image.py                # PIL Image resizing, grids, Base64 conversion
│   ├── memory.py               # PyTorch CUDA VRAM cleanup & RAM tracking
│   ├── seed.py                 # Multi-framework deterministic seed manager
│   ├── logger.py               # Centralized structured logging setup
│   └── file_manager.py         # Timestamped artifact output manager
├── assets/                     # Default visual assets directory
├── outputs/                    # Output directory for generated images
├── notebooks/                  # Interactive notebook environment
│   └── colab.ipynb             # Fully executable Google Colab setup notebook
├── tests/                      # Automated unit and smoke test suite
│   ├── __init__.py
│   ├── test_imports.py         # Module import verification
│   ├── test_structure.py       # File structure existence verification
│   └── test_smoke.py           # Core logic smoke tests
├── docs/                       # Developer documentation
│   ├── Architecture.md         # Detailed system design & data flow
│   ├── Development.md          # Setup & coding guidelines
│   └── Workflow.md             # Git branching & release roadmap
└── scripts/                    # Automation and setup scripts
    ├── setup_env.bat           # Windows environment bootstrapper
    ├── setup_env.sh            # Linux/macOS environment bootstrapper
    └── run_tests.py            # Verification compiler & test runner
```

---

## 🚀 Installation & Local Setup

### 1. Prerequisites
- **Python**: 3.9+ installed.
- **Git**: Installed and configured.
- **GPU (Recommended)**: NVIDIA GPU with CUDA 11.8 or 12.x.

### 2. Local Setup Steps

#### On Windows:
```cmd
git clone https://github.com/ImamAriadi2022/CanvasGen.git
cd CanvasGen
scripts\setup_env.bat
```

#### On Linux / macOS:
```bash
git clone https://github.com/ImamAriadi2022/CanvasGen.git
cd CanvasGen
chmod +x scripts/setup_env.sh
./scripts/setup_env.sh
```

---

## 💻 Development Workflow

### Running the Streamlit Web Application
```bash
streamlit run app.py
```

### Running Automated Verification & Tests
```bash
python scripts/run_tests.py
```
or via pytest directly:
```bash
pytest tests/ -v
```

---

## ☁️ Google Colab Execution

CanvasGen includes a fully automated Google Colab setup notebook in `notebooks/colab.ipynb`.

1. Open Google Colab and upload `notebooks/colab.ipynb`.
2. Select GPU Hardware Accelerator under `Runtime -> Change runtime type -> T4 GPU`.
3. Run all cells sequentially from top to bottom. The notebook automatically:
   - Mounts Google Drive (`/content/drive/MyDrive/CanvasGen`).
   - Clones or pulls the repository.
   - Installs dependencies from `requirements.txt`.
   - Checks GPU acceleration, CUDA driver version, VRAM, and System RAM.
   - Runs automated pytest verification.

---

## 🗺️ Future Features & Development Roadmap

- **Stage 1 (Complete)**: Architecture design, directory structure, module skeletons, utility packages, test suite, and Google Colab integration.
- **Stage 2 (Upcoming)**: PyTorch & HuggingFace Diffusers integration, Text-to-Image execution, multi-sample batch generation, live scheduler swapping, inpainting, and outpainting logic.
- **Stage 3 (Upcoming)**: Advanced Streamlit UI controls, gallery browser, prompt history, LoRA loading, controlnet integration, and model download manager.

---

## 🌿 Git & Contribution Guidelines

1. **Branching Strategy**: Follow GitFlow. Create topic branches from `develop` (`feature/feature-name` or `bugfix/issue-name`).
2. **Commit Standards**: Use Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`).
3. **Pull Requests**: Ensure `python scripts/run_tests.py` passes 100% cleanly before opening PRs.

---

## 📜 License

Distributed under the MIT License. See [LICENSE](file:///c:/programming/CanvasGen/LICENSE) for more details.
