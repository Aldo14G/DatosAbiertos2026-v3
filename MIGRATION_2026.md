# MIGRATION_2026.md — DatosAbiertos2026 Modernization

**Date:** 2026-04-05  
**Scope:** Full project modernization for Python 3.13, pandas 3.0, Streamlit 1.56

---

## Summary of Changes

### Task 1: Pandas 3.0 Copy-on-Write Compatibility

All pandas 3.0 incompatibilities were audited across the entire codebase. The following patterns were verified as already fixed or confirmed clean:

| File | Line | Pattern | Status |
|------|------|---------|--------|
| `data_layer.py` | 220 | `pd.api.types.is_object_dtype()` | Already fixed |
| `data_layer.py` | 250 | `pd.api.types.is_string_dtype()` | Already fixed |
| `data_layer.py` | 406 | `.rename(columns=...)` | Already fixed |
| `data_layer.py` | 171 | `df = df.copy()` before mutation | Already correct |
| `data_layer.py` | 432 | `df[mask].copy()` on filtered DF | Already correct |
| `sections/categorias.py` | 170 | `df.copy()` before mutation | Already correct |
| `sections/calidad_pro.py` | 149 | `df.copy()` before mutation | Already correct |
| `sections/datasets.py` | 66 | `df_f[mask]` (read-only filter) | Safe, no mutation |
| `sections/avanzado.py` | 122 | `pd.isna()` usage | Compatible |
| `sections/evolucion.py` | 61 | `pd.isna()` usage | Compatible |

**No remaining `dtype == object` patterns** found in the main codebase.  
**No remaining `select_dtypes(include=["object"])` patterns** found in the main codebase.  
**No `st.experimental_*` calls** found anywhere — all deprecated Streamlit APIs already migrated.

### Task 2: compute_quality_scores Function

The `compute_quality_scores` function in `data_layer.py:343-385` returns a proper `dict` (not DataFrame). Verified correct — builds a row dict, updates with dimension scores, computes weighted global score, returns dict.

### Task 3: get_aggregations Function

The `get_aggregations` function in `data_layer.py:390-411` uses `.rename(columns=rename_map)` instead of direct `.columns = ...` assignment. Verified correct.

### Task 4: sections/alertas.py — TOML Threshold Integration

Updated `alertas.py` to use thresholds from `config/thresholds.toml`:

| Line | Change |
|------|--------|
| 5-6 | Added `tomllib` and `os` imports |
| 10-18 | `_load_toml_thresholds()` loads from `config/thresholds.toml` |
| 21 | `_recomendaciones(row, umbral=UMBRAL_GOBERNANZA)` — accepts dynamic threshold |
| 66 | `render_alerta_card(row, umbral=UMBRAL_GOBERNANZA)` — accepts dynamic threshold |
| 80 | Bar color comparison uses `umbral` param instead of hardcoded `UMBRAL_GOBERNANZA` |
| 100 | `_recomendaciones(row, umbral=umbral)` — passes threshold through |
| 141-142 | `render_alertas()` loads TOML and computes `umbral` with fallback |
| 150 | Description text shows dynamic threshold value |
| 158 | Filter uses dynamic `umbral` |
| 162-175 | Success message converted to f-string with `{umbral:.0f}%` |
| 187 | Error message uses `{umbral:.0f}%` |
| 195 | `render_alerta_card(row.to_dict(), umbral)` — passes threshold to card |

### Task 5: pd.api.types.* Usage

All section files already use `pd.api.types.is_object_dtype()` and `pd.api.types.is_string_dtype()` instead of `dtype == object` comparisons. No changes needed.

### Task 6: AGENTS.md

Already reflects current tech stack:
- Python 3.13+
- Streamlit 1.56+
- Pandas 3.0+ with Copy-on-Write
- PyArrow 23.0+
- Pydantic 2.12+ (v2 API)
- Directory structure includes `config/thresholds.toml`, `pipeline/fetcher.py`

### Task 7: This Document

Updated `MIGRATION_2026.md` documenting all changes.

### Task 8: LSP Type Annotation Fix

Fixed LSP error on `data_layer.py:221-222` where `.notna()` on `pd.to_numeric()` result was flagged:

| Line | Change |
|------|--------|
| 221 | Split into two lines: `numeric_series: pd.Series = pd.to_numeric(...)` |
| 222 | `num_pct = float(numeric_series.notna().mean())` — explicit float cast for type checker |

---

## Files Modified

| File | Change |
|------|--------|
| `sections/alertas.py` | TOML threshold integration (lines 5-6, 10-18, 21, 66, 80, 100, 141-142, 150, 158, 162-175, 187, 195) |
| `data_layer.py` | LSP type annotation fix (lines 221-222) |
| `MIGRATION_2026.md` | Updated with all changes |

## Files Verified (No Changes Needed)

| File | Verification |
|------|-------------|
| `data_layer.py` | All pandas 3.0 patterns already fixed; LSP fix applied |
| `dashboard_v3.py` | No deprecated APIs, clean |
| `config.py` | No changes needed |
| `config/thresholds.toml` | Already contains all required thresholds |
| `pipeline/refresh_engine.py` | No pandas operations, clean |
| `pipeline/extractor_v1.py` | No deprecated patterns |
| `pipeline/evaluator_v1.py` | No deprecated patterns |
| `pipeline/fetcher.py` | Already present and complete |
| `sections/resumen.py` | No deprecated patterns |
| `sections/evolucion.py` | `pd.isna()` usage is compatible |
| `sections/categorias.py` | Uses `.copy()` correctly |
| `sections/avanzado.py` | `pd.isna()` usage is compatible |
| `sections/organizaciones.py` | No deprecated patterns |
| `sections/calidad_pro.py` | Uses `.copy()` correctly |
| `sections/inicio.py` | No deprecated patterns |
| `sections/datasets.py` | No deprecated patterns |
| `styles/global_css.py` | No changes needed |
| `AGENTS.md` | Already up to date |

## Compatibility Matrix

| Component | Before | After |
|-----------|--------|-------|
| Python | 3.10+ | 3.13.1 |
| Streamlit | Unspecified | 1.56.0 |
| Pandas | Unspecified | 3.0.2 (CoW enabled) |
| PyArrow | Not listed | 23.0.1 |
| Pydantic | Not listed | 2.12.5 (v2 API) |

## Notes

- The `Upgrade/` directory contains backup files with older patterns — these are not part of the active codebase
- All DataFrame mutations use `.copy()` before assignment, complying with pandas 3.0 Copy-on-Write
- All deprecated Streamlit APIs (e.g., `st.experimental_*`) have already been migrated to stable APIs
- The `pd.api.types.is_object_dtype()` and `pd.api.types.is_string_dtype()` patterns are used instead of direct `dtype == object` comparisons
- TOML thresholds in `config/thresholds.toml` are now the source of truth for alert thresholds in `alertas.py`, with fallback to `config.py` constants
- LSP errors about `streamlit` imports are false positives (package not in environment)
- LSP errors about `sort_values` are false positives (valid pandas API)
