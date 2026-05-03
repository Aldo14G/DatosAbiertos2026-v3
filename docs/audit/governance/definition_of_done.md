# Definition of Done — DatosAbiertos2026

**Propósito:** criterios objetivos para declarar una PR "lista para merge" según el tipo de cambio. Complementa [UX_QA_CHECKLIST.md](../../../UX_QA_CHECKLIST.md).

**Principio rector:** una PR no está lista si alguien más del equipo tiene que adivinar si está lista.

---

## Tipos de cambio y DoD

### 1 · Cambios CSS / design tokens (`styles/global_css.py`)

| # | Criterio | Verificación |
|---|---|---|
| 1.1 | Nueva clase definida solo si no hay clase existente que cumpla la función | Cruzar con [component_inventory.md](../ux/component_inventory.md) |
| 1.2 | Usa tokens de `_TOKENS_DARK` / `_TOKENS_LIGHT`, sin hex hardcodeado | `grep -E "#[0-9a-fA-F]{6}" styles/global_css.py` en diff |
| 1.3 | Paridad dark/light (mismos tokens existen en ambos bloques) | Inspección visual |
| 1.4 | Ningún `style="..."` inline ≥30 chars añadido en `sections/*.py` o `dashboard_v3.py` | `grep -c 'style="'` antes/después |
| 1.5 | Respeta `prefers-reduced-motion` si añade animación | Cada `@keyframes` nuevo aparece también bajo `@media (prefers-reduced-motion: reduce)` |
| 1.6 | Contraste ≥4.5:1 texto normal / ≥3:1 grande | Manual con devtools |
| 1.7 | Focus ring visible (usa `--focus-ring`) | Test Tab navigation |
| 1.8 | No rompe breakpoints 1200 / 992 / 768 / 600 | Resize browser |

### 2 · Nueva sección Streamlit (`sections/*.py`)

| # | Criterio | Verificación |
|---|---|---|
| 2.1 | Imports y firmas consistentes con secciones existentes (`def render(ctx: ...)`) | Code review |
| 2.2 | Todos los `<span class="material-symbols-outlined">` llevan `aria-hidden="true"` si son decorativos, o `aria-label` si son informativos | Grep del diff |
| 2.3 | Todo `.bar-track`/`.bar-fill` expone `role="progressbar" aria-valuenow aria-valuemin aria-valuemax` | Grep |
| 2.4 | SVGs informativos tienen `<title>` + `role="img"` | Inspección |
| 2.5 | Ningún `onmouseover`/`onmouseout` sin equivalente `:hover, :focus` en CSS | Grep |
| 2.6 | Sin secretos, URLs hardcodeadas, ni datos sensibles en HTML | Revisión manual |
| 2.7 | Si lee datos: usa `data_layer.*`, no I/O directo | Code review |
| 2.8 | Dashboard arranca sin errores de consola: `bash run_local.sh` | Smoke test local |
| 2.9 | Responsive 1200 → 600 sin overflow horizontal | Resize browser |
| 2.10 | Tests visuales manuales de estados: **loading (skeleton) · empty · error · success** | UX_QA_CHECKLIST.md |

### 3 · Cambios en `data_layer.py`

| # | Criterio | Verificación |
|---|---|---|
| 3.1 | No se modifican archivos en `pipeline/` | `git diff pipeline/` vacío |
| 3.2 | `_validate_schema` actualizado si `_REQUIRED_COLS` cambia | Ambos diffs presentes |
| 3.3 | Nueva dimensión ISO: actualizar `DIM_LABEL_MAP`, `QUALITY_WEIGHTS`, docstring, test | 4 diffs en misma PR |
| 3.4 | Logs con `logging` no `print()` en código nuevo | Grep diff |
| 3.5 | Funciones puras preferidas (no mutación de DataFrames de entrada) | Code review |
| 3.6 | Tests pytest pasan: `pytest pipeline/test_data_layer.py` (si existen) | CI |
| 3.7 | Documentar cambios breaking en `MIGRATION_2026.md` / `CHANGELOG.md` | PR body |

### 4 · Cambios en `pipeline/*` (bypass de regla dura)

**Regla por defecto:** NO modificar `pipeline/*`.

**Si excepcionalmente se requiere** (ej. bugfix crítico):

| # | Criterio | Verificación |
|---|---|---|
| 4.1 | Sign-off explícito del owner del pipeline en el PR | Comment con aprobación |
| 4.2 | Cambio aislado: una sola función, sin refactor colateral | Diff minimal |
| 4.3 | Test de regresión añadido en `pipeline/test_*.py` | Ambos diffs presentes |
| 4.4 | `run_id` + `pipeline_version` del JSON output bumped si cambia la semántica del score | Diff en metadata |
| 4.5 | Reportes existentes (CSV/JSON) siguen deserializando | Smoke test: `python -c "import data_layer; data_layer.load_results()"` |

### 5 · Audit / docs (`.agent/audit/**`, `*.md`)

| # | Criterio | Verificación |
|---|---|---|
| 5.1 | Referencias a archivos usan formato `[path](relative)` markdown, clickables | Render preview |
| 5.2 | Claims con cifras citan la línea fuente: `[data_layer.py:42](...)` | Grep del diff |
| 5.3 | "Bloquea Fase 2" es explícito (sí/no) cuando aplica | Presencia en tabla |
| 5.4 | Sin emojis salvo acordado explícitamente | Grep unicode |
| 5.5 | Si propone código: bloque ```python o ```html fenced + testeado mentalmente | Revisión |

### 6 · Config (`config.py`, `config/thresholds.toml`)

| # | Criterio | Verificación |
|---|---|---|
| 6.1 | Cambios en `QUALITY_WEIGHTS` justificados con ref. Wang & Strong u otro marco | PR body |
| 6.2 | Sensitivity analysis re-ejecutado si pesos cambian; ρ ≥ 0.85 con baseline | Script `scripts/sensitivity.py` (Fase 2) |
| 6.3 | Thresholds `gold/silver/bronze` cambian → actualizar `calidad_pro.py` labels | Diff conjunto |

### 7 · Dependencias (`requirements.txt`)

| # | Criterio | Verificación |
|---|---|---|
| 7.1 | Versión pinneada (`==X.Y.Z`) no `>=` ni `~=` sin razón | Grep |
| 7.2 | Justificación 1-línea en PR body: "añadido X para Y" | PR |
| 7.3 | `pip-audit` sin vulnerabilidades High/Critical | CI (Fase 2) |
| 7.4 | `pip install -r requirements.txt` en venv limpio funciona | Local test |

---

## Checklist universal (aplica a toda PR)

- [ ] Título sigue Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, `test:`).
- [ ] `git diff pipeline/` vacío **o** excepción 4.x aprobada.
- [ ] `git diff` no añade comentarios "what" redundantes con el código.
- [ ] No se añaden archivos >1 MB sin LFS.
- [ ] No se commitea `.venv/`, `__pycache__/`, `*.ipynb_checkpoints/`, `data/*.csv` >1 MB.
- [ ] Co-Authored-By footer si hubo asistencia AI.
- [ ] PR tiene descripción: qué, por qué, cómo probar, capturas si aplica.

---

## Cuando dudes

Si el cambio no encaja en ninguna categoría anterior, aplicar el **Checklist universal** + el más cercano y documentar en el PR por qué se eligió ese conjunto.

Si un criterio no aplica, escribir `N/A — razón`. Nunca omitir silenciosamente.
