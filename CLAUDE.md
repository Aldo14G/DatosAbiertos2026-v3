# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Summary

Open Data Quality Analyzer for the Nuevo León state government portal (`catalogodatos.nl.gob.mx`). A Python/Streamlit analytics dashboard that scores datasets against ISO/IEC 25012:2008 quality dimensions (Completeness, Accuracy, Consistency, Uniqueness, Timeliness + Documentation + Openness). Accompanied by a Next.js promotional landing page.

---

## Commands

### Python / Streamlit Dashboard

```bash
# Setup
python -m venv .venv && source .venv/Scripts/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt   # black, ruff, flake8, pytest

# Run
streamlit run dashboard_v3.py         # http://localhost:8501

# Lint & format
ruff check .                          # primary linter
ruff format --check .                 # format check
ruff --fix .                          # auto-fix
black . --check                       # format check
black .                               # auto-format

# Tests
pytest                                # full suite
pytest -v
pytest -k "anomaly"                   # filter by name
pytest pipeline/test_anomaly_detector.py::test_global_score_anomaly  # single test
```

### Next.js Landing Page (`landing/`)

```bash
cd landing
npm run dev     # dev server
npm run build   # production build
npm run lint    # ESLint
```

---

## Architecture

### Data Flow

```
CKAN API → fetcher.py → extractor_v1.py → evaluator_v1.py
                                               ↓
                                    anomaly_detector.py
                                               ↓
                                    data_layer.py (cache + aggregations)
                                               ↓
                               dashboard_v3.py (Streamlit orchestrator)
                                               ↓
                          sections/{inicio,datasets,calidad_pro,organizaciones}.py
```

The pipeline produces per-dataset scores across 7 weighted dimensions. `data_layer.py` caches results and exposes them to the UI via `load_results()`. `dashboard_v3.py` routes navigation via URL query parameters (`?section=datasets`), injects the design system, and calls each section module.

### Key Modules

| File | Role |
|------|------|
| `dashboard_v3.py` | Entry point; navigation, CSS injection, section dispatch |
| `data_layer.py` | ETL, quality scoring, caching — **read-only in Phase 1** |
| `config.py` | Single source of truth for thresholds, weights (`QUALITY_WEIGHTS`), security constants |
| `styles/global_css.py` | Design system tokens (Material Design 3); defines all CSS custom properties |
| `pipeline/evaluator_v1.py` | ISO 25012 scoring algorithm — **read-only; requires owner sign-off to modify** |
| `pipeline/fetcher.py` | SSRF-protected CKAN HTTP client |

### Design System (Critical Pattern)

Streamlit's default UI is entirely overridden. The app is structured as a pseudo-SPA using `st.markdown(unsafe_allow_html=True)`. **Never use native Streamlit primitives** (`st.metric()`, `st.success()`, etc.) for new UI — instead, write HTML blocks using the CSS classes and variables defined in `styles/global_css.py`.

All colors must reference CSS custom properties (`var(--midnight)`, `var(--teal)`, `var(--gold)`, `var(--rose)`). Plotly charts must use the hex equivalents (Plotly does not support CSS variables) — these resolved values live in `global_css.py`. Every new section must import and use `_TOKENS_DARK` / `_TOKENS_LIGHT` from that module.

---

## Hard Rules (Non-Negotiable)

- **No modifications to `pipeline/`** without explicit owner sign-off. Regressions here break public data.
- **No inline styles ≥ 30 characters** in generated HTML. Use CSS classes instead.
- **No emojis** in UI or source code.
- **No data files > 1 MB** in commits. Use CKAN fetch or external storage.
- **No hardcoded hex colors** outside of `global_css.py`. Always use design tokens.
- **No `href="#"` placeholder links**. All links must be real.
- **Escape user-generated strings** with `html.escape` whenever `unsafe_allow_html=True`.

---

## Code Conventions

- **Python 3.13+**: use `|` for Union types (PEP 604), annotate all public functions.
- **Pandas 3.0+**: always `.copy()` before mutating a DataFrame (Copy-on-Write compliance). Use `pd.api.types.is_*()` for dtype checks — never `dtype == object`.
- **Strings**: f-strings exclusively; double quotes.
- **Line length**: 88 characters (black default), ruff configured to match.
- **Constants**: all magic numbers go in `config.py` or `config/thresholds.toml`.
- **Logging**: use the `logging` module (configured in `dashboard_v3.py`), not `print`.
- **Tests**: reside in `pipeline/`, named `test_*.py`. Must pass before any PR touching `data_layer.py` or `config.py`.

### Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Variables / functions | `snake_case` | `detect_low_global_score` |
| Constants | `UPPER_SNAKE_CASE` | `QUALITY_WEIGHTS` |
| Classes | `PascalCase` | `DatasetEvaluator` |
| Private helpers | leading underscore | `_get_tier` |
| Type variables | `T`, `K`, `V` | `T = TypeVar('T')` |

### Commit Style (Conventional Commits)

```
feat:     new functionality
fix:      bug fix
docs:     documentation only
refactor: no behavior change
style:    CSS / visual tokens
chore:    deps, CI, maintenance
test:     new or modified tests
```

AI-assisted commits must include:
```
Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

---

## PR Checklist

- `ruff check .` passes with no errors
- `pytest pipeline/` green (if `data_layer.py` or `pipeline/` was touched)
- No hardcoded hex colors — tokens from `_TOKENS_DARK`/`_TOKENS_LIGHT`
- WCAG 2.1 AA: decorative icons have `aria-hidden="true"`, progress bars have `role="progressbar"` + `aria-valuenow/min/max`, SVGs have `role="img"` + `<title>`
- `git diff pipeline/` is empty, or owner sign-off is attached
- `CHANGELOG.md` updated

---

## Further Reading

- [CONTRIBUTING.md](CONTRIBUTING.md) — contribution rules (Spanish)
- [docs/DESIGN.md](docs/DESIGN.md) — design tokens, colors, typography
- [docs/PRODUCT.md](docs/PRODUCT.md) — product context and roadmap
- [.claude/LLM_INIT.md](.claude/LLM_INIT.md) — project context for AI agents
- [docs/audit/GAP_ANALYSIS.md](docs/audit/GAP_ANALYSIS.md) — Phase 2 technical backlog
