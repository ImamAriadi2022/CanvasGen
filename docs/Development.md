# CanvasGen Developer Guide

This guide details environment setup, local development guidelines, coding standards, testing instructions, and quality control procedures for developers working on **CanvasGen**.

---

## 1. Prerequisites & Environment Setup

### System Requirements
- **Python**: 3.9, 3.10, or 3.11
- **GPU Hardware (Recommended)**: NVIDIA GPU with CUDA 11.8+ or CUDA 12.x support (minimum 6GB VRAM recommended)
- **RAM**: Minimum 8GB (16GB recommended)

### Quickstart Setup Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ImamAriadi2022/CanvasGen.git
   cd CanvasGen
   ```

2. **Run setup environment script**:
   - **Windows**:
     ```cmd
     scripts\setup_env.bat
     ```
   - **Linux / macOS**:
     ```bash
     chmod +x scripts/setup_env.sh
     ./scripts/setup_env.sh
     ```

3. **Configure Environment File**:
   Copy `.env.example` to `.env` and set your optional HuggingFace token:
   ```bash
   cp .env.example .env
   ```

---

## 2. Running Local Web Application

Launch the Streamlit web app interface:
```bash
streamlit run app.py
```

---

## 3. Running Automated Tests

Run the complete pytest test suite:
```bash
pytest tests/ -v
```

Or execute the custom python test compiler:
```bash
python scripts/run_tests.py
```

---

## 4. Code Standards & Style Guidelines

- **PEP8 Compliance**: All code must conform to standard PEP8 formatting (4 spaces indentation, maximum line length 88-100 characters).
- **Type Hinting**: All function parameters and return types must include explicit type annotations.
- **Docstrings**: All modules, classes, and public methods must include Google-style Python docstrings.
- **Error Handling & Logging**: Use `utils.logger.get_logger(__name__)` instead of bare `print()` statements. Avoid silent `except Exception: pass` blocks.
