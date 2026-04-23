# AGENTS.md - DatosAbiertos2026

**Purpose**: Provide a concise, agent‑friendly reference for building, linting, testing, and coding standards in this repository. All agents should consult this file before making code changes.

---

## Project Overview
A Python/Streamlit dashboard that evaluates datasets from the Nuevo León open data portal using ISO/IEC 25012:2008 quality dimensions (Completeness, Accuracy, Consistency, Uniqueness, Timeliness) and additional catalog‑level metrics.

---

## Tech Stack
- **Python** 3.13+ (type‑checked, `pyright` compatible)
- **Streamlit** 1.56+
- **Pandas** 3.0+ (Copy‑on‑Write enabled)
- **PyArrow** 23.0+
- **Pydantic** 2.12+ (v2 API)
- **Plotly**
- **pytest**
- **black**, **ruff**, **flake8** (linting/formatting)

---

## Build / Run Commands
```bash
# Install runtime and dev dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt   # contains black, ruff, flake8, pytest

# Run the Streamlit dashboard
streamlit run dashboard_v3.py

# Lint / format the whole codebase
ruff .            # fast linting (ruff)
black . --check   # ensure Black formatting
flake8 .          # legacy style checks

# Auto‑format the whole repository (use with care)
black .
ruff --fix .

# Run the test suite
pytest                       # all tests
pytest -v                    # verbose output
pytest -k "anomaly"         # pattern match
pytest pipeline/test_anomaly_detector.py                # single file
pytest pipeline/test_anomaly_detector.py::test_global_score_anomaly  # single test
```

---

## Directory Structure
```
DatosAbiertos2026/
├─ .github/                 # CI / workflow files
├─ .streamlit/              # Streamlit theme config
├─ .opencode/skills/        # custom skill bundles
├─ config.py                # global constants
├─ dashboard_v3.py          # Streamlit entry point
├─ data_layer.py            # ETL & quality scoring
├─ config/                  # TOML thresholds
├─ pipeline/                # data pipeline & tests
│   ├─ anomaly_detector.py
│   ├─ refresh_engine.py
│   ├─ fetcher.py
│   ├─ extractor_v1.py
│   ├─ evaluator_v1.py
│   └─ test_anomaly_detector.py
├─ sections/                # UI components (Streamlit pages)
│   ├─ inicio.py
│   ├─ datasets.py
│   ├─ calidad_pro.py
│   └─ organizaciones.py
└─ styles/                  # CSS tokens (Material Design 3)
```

---

## Code Style Guidelines
### 1. Imports
- **Three‑block order** (PEP 8): stdlib → third‑party → local
- One import per line; alphabetize within blocks
- Use explicit relative imports for intra‑package modules

### 2. Formatting
- Line length: 88 characters (Black default)
- Trailing commas on multi‑line collections
- Single blank line between top‑level definitions
- Double quotes for strings (except when containing a double quote)
- End files with a single newline

### 3. Naming Conventions
| Element | Convention | Example |
|---------|------------|---------|
| Variables / functions | `snake_case` | `detect_low_global_score` |
| Constants | `UPPER_SNAKE_CASE` | `QUALITY_WEIGHTS` |
| Classes | `PascalCase` | `DatasetEvaluator` |
| Private helpers | leading underscore | `_get_tier` |
| Type variables | `T`, `K`, `V` | `T = TypeVar('T')` |

### 4. Type Hints
- Annotate all public functions (including return types)
- Prefer concrete collection types (`list[dict]`, `dict[str, Any]`)
- Use `|` for Union (PEP 604)

### 5. Docstrings
- Google style for public callables
- First line: summary sentence ending with a period
- Include `Args:` and `Returns:` sections if non‑trivial

### 6. String Formatting
- **f‑strings** exclusively
- Avoid concatenation with `+`

### 7. Error Handling
- Catch specific exceptions only
- Re‑raise with contextual information when appropriate
- For HTTP calls: `response.raise_for_status()` after the request

### 8. Logging / Debugging
- Use `logging` (configured in `dashboard_v3.py`) instead of `print`
- Log at appropriate levels (`debug`, `info`, `warning`, `error`)
- Never log secrets or raw user data

### 9. HTML / CSS in Streamlit
- When `unsafe_allow_html=True`, escape user‑generated strings with `html.escape`
- Prefer CSS custom properties defined in `styles/`
- Keep inline styles minimal; move reusable styles to the CSS token file

### 10. Constants & Configuration
- All magic numbers live in `config.py` (or TOML files under `config/`)
- Use type‑annotated literals for clarity

### 11. Testing Guidelines
- Tests reside in `pipeline/` and follow the pattern `test_*.py`
- Use pytest fixtures for shared data (e.g., mock API responses)
- Each test should be self‑contained and assert concrete outcomes
- Prefer parameterized tests for edge‑case coverage
- Run a single test via `pytest path/to/file.py::test_name`

### 12. Linting / Formatting Rules
- **ruff**: primary linter (`ruff check .`). Enforce `E`, `F`, `W` error codes, ignore `D` (docstring style)
- **black**: formatting (`black .`). Use `--line-length 88`
- **flake8**: legacy compatibility; run after `black` to catch any remaining issues
- CI pipeline runs `ruff`, `black --check`, and `pytest` on every push

---

## Cursor / Copilot Rules
No `.cursor/` or `.github/copilot-instructions.md` files are present in this repository, so no additional rules need to be reproduced here.

---

## Custom Agents & Skills
Refer to the `AGENTS.md` section **Active Agent Workflow** for mandatory trigger agents (data‑quality‑analyst, python‑reviewer, ui‑ux‑pro‑max, etc.). Ensure any new agent respects the conventions defined above.

---

*Last updated: 2026-04-20*