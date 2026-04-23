# Audit Report — Fase 1 · Fundación (NL 2026)

**Generado:** 2026-04-15
**Alcance:** Auditoría read-only del dashboard Streamlit NL 2026 previa a Fase 2 (Infraestructura Analítica).
**Regla dura:** Cero modificaciones a `pipeline/*`. Solo lectura + documentación.

## Entregables

### UX
| Archivo | Propósito |
|---|---|
| [ux/heuristic_nielsen.md](ux/heuristic_nielsen.md) | 10 heurísticas Nielsen × 4 secciones × severidad (0-4) |
| [ux/wcag_2_1_aa.md](ux/wcag_2_1_aa.md) | Checklist WCAG 2.1 AA con evidencia file:line |
| [ux/component_inventory.md](ux/component_inventory.md) | Bloques CSS definidos vs consumidos + inline CSS residual |

### Data
| Archivo | Propósito |
|---|---|
| [data/pipeline_audit.md](data/pipeline_audit.md) | 7 dimensiones ISO 25012 × método actual vs Great Expectations |
| [data/data_contracts_gap.md](data/data_contracts_gap.md) | Schemas Pydantic propuestos (diseño, no implementación) |
| [data/scoring_sensitivity.md](data/scoring_sensitivity.md) | Metodología + blocker: dataset insuficiente (n=1) |

### Governance
| Archivo | Propósito |
|---|---|
| [governance/docs_gap.md](governance/docs_gap.md) | CONTRIBUTING, CHANGELOG, ADRs ausentes |
| [governance/definition_of_done.md](governance/definition_of_done.md) | Criterios DoD por tipo de change |
| [governance/ci_baseline.md](governance/ci_baseline.md) | `pyproject.toml` + `.github/workflows/ci.yml` propuestos |

### Consolidado
| Archivo | Propósito |
|---|---|
| [GAP_ANALYSIS.md](GAP_ANALYSIS.md) | Tabla priorizada con `Bloquea Fase 2?` |

## Baseline confirmado

- **Versión app:** V2.1 · NL 2026 SYS ([config.py:40](../../config.py#L40))
- **Python mínimo:** 3.11 ([requirements.txt:3](../../requirements.txt#L3))
- **Secciones activas:** Inicio, Datasets, Calidad Pro ([dashboard_v3.py:60-64](../../dashboard_v3.py#L60-L64))
- **Datasets en CSV:** 1 ([resultados_calidad_datos_nl.csv](../../resultados_calidad_datos_nl.csv)) — dataset de desarrollo, **no producción**
- **Datasets en JSON avanzado:** 272 ([.antigravity/team/shared/advanced_quality_results.json](../../.antigravity/team/shared/advanced_quality_results.json))
- **Pesos ISO 25012:** completeness 0.30, accuracy 0.25, consistency 0.15, uniqueness 0.08, timeliness 0.05, documentation 0.10, openness 0.07 ([config.py:15-23](../../config.py#L15-L23))
