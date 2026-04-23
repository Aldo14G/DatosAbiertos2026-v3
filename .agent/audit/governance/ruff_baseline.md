# Ruff Baseline — V2.1 (2026-04-16)

Capturado con `ruff check .` tras crear `pyproject.toml` (GOV-07 Semana 1).

```
ruff check .  # desde raíz del proyecto
```

## Resumen

| Regla | Descripción | Cant | Auto-fix? |
|---|---|---|---|
| W293 | blank-line-with-whitespace | 145 | No |
| F541 | f-string-missing-placeholders | 25 | Sí |
| I001 | unsorted-imports | 15 | Sí |
| F401 | unused-import | 11 | Sí |
| UP015 | redundant-open-modes | 8 | Sí |
| F841 | unused-variable | 7 | No |
| W291 | trailing-whitespace | 7 | Sí |
| UP009 | utf8-encoding-declaration | 6 | Sí |
| E402 | module-import-not-at-top-of-file | 2 | No |
| SIM102 | collapsible-if | 2 | No |
| SIM105 | suppressible-exception | 2 | No |
| SIM108 | if-else-block-instead-of-if-exp | 2 | No |
| UP017 | datetime-timezone-utc | 2 | Sí |
| B904 | raise-without-from-inside-except | 1 | No |
| B905 | zip-without-explicit-strict | 1 | No |
| E701 | multiple-statements-on-one-line-colon | 1 | No |
| UP045 | non-pep604-annotation-optional | 1 | Sí |
| **Total** | | **238** | **212 (89%)** |

## Notas

- La mayoría de W293 (145) provienen de archivos en `.agent/skills/` (generados externamente).
- F541 son f-strings sin placeholders en HTML markdown de Streamlit — falsos positivos en algunos casos (el string se embebe en otro f-string).
- F401/I001 prioritarios en `sections/` y `data_layer.py`.
- `pipeline/*` excluido por `pyproject.toml` (`per-file-ignores = ["ALL"]`).
- E402 en `sections/` ignorado por `pyproject.toml` (`sections/* = ["E402"]`).

## Próximo paso (Semana 2)

```bash
ruff check . --fix   # aplica 212 auto-fixes
ruff check .         # verificar residual ~26 errores manuales
```

Target Fase 2: `ruff check .` = 0 errores en CI gate.
