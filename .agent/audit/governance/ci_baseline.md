# CI Baseline — Propuesta Fase 2

**Estado actual:** No hay CI. Tests locales existen ([pipeline/test_data_layer.py](../../../pipeline/test_data_layer.py), [pipeline/test_anomaly_detector.py](../../../pipeline/test_anomaly_detector.py), [pipeline/test_agent_pipeline.py](../../../pipeline/test_agent_pipeline.py)) pero no se ejecutan automatizadamente en push/PR.

**Objetivo:** ganar un gate mínimo (lint + type + tests) que detecte regresiones antes de merge, sin sobre-configurar.

**Regla Fase 1:** solo propuesta — no se crea `.github/workflows/` todavía.

---

## 1 · `pyproject.toml` propuesto

Hoy el proyecto no tiene `pyproject.toml`; toda la configuración vive en `requirements.txt` + convenciones ad-hoc. Mover la config de tooling a un solo archivo facilita onboarding y CI.

```toml
[project]
name = "datos-abiertos-nl-2026"
version = "2.1.0"
description = "Dashboard de calidad de datos abiertos de Nuevo León 2026"
requires-python = ">=3.11"
readme = "README.md"

[tool.ruff]
line-length = 100
target-version = "py311"
extend-exclude = [".venv", "__pycache__", "lecturas_txt", "Lecturas"]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "W",   # pycodestyle warnings
    "I",   # isort
    "B",   # flake8-bugbear
    "UP",  # pyupgrade
    "SIM", # flake8-simplify
]
ignore = [
    "E501",  # line too long (compensado por line-length)
    "B008",  # do not call X in argument defaults (Streamlit lo hace idiomáticamente)
]

[tool.ruff.lint.per-file-ignores]
"pipeline/*" = ["ALL"]  # pipeline es read-only — no auto-format destructivo
"sections/*" = ["E402"]  # streamlit imports a veces condicionales

[tool.mypy]
python_version = "3.11"
strict_optional = true
warn_unused_ignores = true
ignore_missing_imports = true  # streamlit, plotly sin stubs oficiales en algunas versiones
exclude = "(pipeline|.venv|__pycache__)"

[tool.pytest.ini_options]
testpaths = ["pipeline"]
python_files = ["test_*.py"]
addopts = "-v --tb=short"
```

**Justificación:**
- `ruff` >> black+isort+flake8 en velocidad y config única.
- `mypy --ignore-missing-imports` evita romper por falta de stubs de terceros.
- `pipeline/*` en `per-file-ignores` respeta la regla dura "no tocar pipeline".

---

## 2 · `.github/workflows/ci.yml` propuesto

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
      - name: Install
        run: |
          python -m pip install --upgrade pip
          pip install ruff mypy
          pip install -r requirements.txt
      - name: Ruff check
        run: ruff check .
      - name: Ruff format check
        run: ruff format --check .
      - name: Mypy
        run: mypy dashboard_v3.py data_layer.py config.py sections/
        # pipeline/ excluido: read-only

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
      - name: Install
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Pytest
        run: pytest pipeline/ --cov=pipeline --cov-report=term-missing

  smoke:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install
        run: pip install -r requirements.txt
      - name: Import smoke
        run: |
          python -c "import data_layer; import dashboard_v3; print('OK')"
      - name: Streamlit boot (headless 10s)
        run: |
          timeout 10s streamlit run dashboard_v3.py --server.headless true || test $? -eq 124
```

**Justificación por job:**
- `lint`: Detecta imports rotos, sintaxis, formato inconsistente.
- `test`: Ejecuta `pipeline/test_*.py` que ya existen pero no se corren.
- `smoke`: Verifica que el dashboard arranca — barato (~15 s), evita regresiones catastróficas del tipo "ImportError on boot".

---

## 3 · `.pre-commit-config.yaml` propuesto (opcional)

Para atrapar errores antes del push:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-added-large-files
        args: ["--maxkb=1000"]

  - repo: local
    hooks:
      - id: no-pipeline-changes
        name: "Guard: pipeline/ is read-only"
        entry: bash -c 'git diff --cached --name-only | grep -E "^pipeline/" && echo "Pipeline changes need owner sign-off" && exit 1 || exit 0'
        language: system
        pass_filenames: false
```

**Hook local `no-pipeline-changes`:** implementa la regla dura. Se puede bypassear con `git commit --no-verify` cuando el owner aprueba, pero fuerza la consciencia.

---

## 4 · Gates mínimos propuestos (Fase 2)

| Gate | Umbral | Qué rompe si falla |
|---|---|---|
| Ruff lint | 0 errores | PR bloqueado |
| Ruff format | 0 diffs | PR bloqueado |
| Mypy | 0 errores en `dashboard_v3.py`, `data_layer.py`, `sections/` | PR bloqueado |
| Pytest | Todos los tests existentes passing | PR bloqueado |
| Smoke import | `python -c "import dashboard_v3"` sin error | PR bloqueado |
| Coverage pipeline/ | ≥70% líneas (aspiracional — ajustar tras medir baseline) | Warning, no bloqueo |
| pip-audit | 0 vulnerabilidades High/Critical | PR bloqueado (Fase 2) |

---

## 5 · Gates diferidos (Fase 3)

- **Sensitivity gate:** rechazar PR que modifique `QUALITY_WEIGHTS` si ρ < 0.85 con baseline ([scoring_sensitivity.md](../data/scoring_sensitivity.md)).
- **Accessibility gate:** `pa11y-ci` sobre el dashboard renderizado ([wcag_2_1_aa.md](../ux/wcag_2_1_aa.md)).
- **Lighthouse performance:** score ≥80 en categoría accesibilidad.
- **Visual regression:** screenshot diff con tolerancia 5%.

Estos requieren Fase 2 completa antes de ser valiosos.

---

## 6 · Plan de adopción incremental

**Semana 1:** `pyproject.toml` + `ruff check` manual en local para limpiar warnings existentes.

**Semana 2:** `.github/workflows/ci.yml` con solo job `lint` (no blockea merges al principio, modo "informativo").

**Semana 3:** añadir job `test` (primera corrida completa, capturar qué tests no pasan hoy).

**Semana 4:** pasar gates a "required" en branch protection de `main`.

**Mes 2+:** añadir `smoke`, `pip-audit`, `pre-commit` local.

---

## 7 · Costo estimado

- Infraestructura: 0 (GitHub Actions gratis para repos públicos, minutos ~2/PR).
- Setup tiempo dev: ~1 día (configuración) + ~2-3 días (resolver warnings actuales de ruff/mypy).
- Mantenimiento: ~0.5 día/mes actualizando versiones.

**ROI:** una sola regresión evitada en `data_layer.py` o `dashboard_v3.py` paga el setup.

---

## 8 · Qué NO proponer todavía

- **Coverage 100%:** falso sentido de seguridad. Priorizar ramas críticas.
- **Pre-merge review bot obligatorio:** overkill para equipo de ≤3 personas.
- **Semantic release automático:** requiere changelog disciplinado que aún no existe.
- **Docker/containerización:** Streamlit + `requirements.txt` ya es reproducible; contenedor añade complejidad sin ganancia hoy.
- **Dependabot agresivo:** crear spam de PRs en un proyecto con pocas dependencias directas es ruido.

Éstos pueden re-evaluarse en Fase 4.
