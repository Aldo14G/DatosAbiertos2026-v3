# GEMINI.md — Gobernanza de Datos Abiertos Nuevo León 2026

## Project Overview
This project is an automated infrastructure for auditing and governing open data from the Nuevo León (Mexico) government portal (`catalogodatos.nl.gob.mx`). It evaluates datasets against international quality standards (**ISO/IEC 25012:2008**, **ISO 8000**, and **DAMA-DMBOK**) and provides a high-fidelity visual dashboard.

The platform consists of two main parts:
1.  **Analytical Dashboard (Streamlit):** A custom-styled Python interface using **Material Design 3 (Google Stitch)** to provide a professional, "pixel-perfect" UI/UX.
2.  **Data Pipeline (Python):** An ETL and scoring engine that extracts metadata, performs quality audits (Completeness, Accuracy, Consistency, Uniqueness), and detects anomalies.
3.  **Landing Page (Next.js):** A modern landing page built with Next.js 15.

## Architecture and Key Modules
- **`dashboard_v3.py`:** Main entry point for the Streamlit application. Orchestrates the single-page scrollable navigation.
- **`pipeline/`:** Core logic for data processing.
    - `evaluator.py`: Scoring engine based on ISO/DAMA standards.
    - `anomaly_detector.py`: Detects statistical deviations in quality scores.
    - `fetcher.py` & `extractor.py`: Data ingestion from CKAN API.
- **`sections/`:** Modular UI components for the dashboard (e.g., `inicio.py`, `datasets.py`, `calidad_pro.py`).
- **`styles/global_css.py`:** The "Design System" hub. Injects custom CSS tokens to override Streamlit's default look and feel.
- **`landing/`:** Next.js 15 project located in the sub-directory for the public-facing site.
- **`.antigravity/`:** Multi-agent system rules and agent definitions for automated code reviews and quality analysis.

## Building and Running

### Python / Streamlit Dashboard
```bash
# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run dashboard_v3.py
```

### Next.js Landing Page
```bash
cd landing
npm install
npm run dev
```

### Testing and Quality
```bash
# Run the test suite (mostly pipeline tests)
pytest

# Linting and Formatting
ruff .
black . --check
```

## Development Conventions

### 1. UI/UX Integrity (Crucial)
- **NEVER** use native Streamlit primitives that break the design (e.g., `st.metric`, `st.success`).
- **ALWAYS** use the custom HTML/CSS blocks defined in `styles/global_css.py` via `st.markdown(..., unsafe_allow_html=True)`.
- Adhere to the **Material Design 3 (Google Stitch)** tokens (Colors: Midnight, Teal, Gold, Rose).

### 2. Coding Standards
- **Python:** Use type hints for all public functions. Follow Google-style docstrings.
- **Imports:** Three-block PEP 8 order (stdlib → third-party → local).
- **Pandas:** Use Copy-on-Write (CoW) where possible (Pandas 3.0+).

### 3. Data Governance
- All quality evaluations must map back to ISO 25012 or DAMA dimensions.
- New metrics should be added to `pipeline/evaluator.py` following the existing `Analizador` class patterns.

### 4. Multi-Agent Workflow
- This project utilizes specialized agents (`data-quality-analyst`, `python-reviewer`, `ui-ux-pro-max`). Consult `AGENTS.md` for specific agent triggers and workflows.
- Always check `.antigravity/rules/` for detailed coding, testing, and security patterns.

---
*This file serves as a foundation for Gemini CLI and other AI agents to maintain project consistency and quality.*
