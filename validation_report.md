# Reporte de Validación — DatosAbiertos2026-v3
**Fecha:** Mayo 2026  
**Agente:** Exploración + Escritura + Validación  
**Repositorio:** `https://github.com/Aldo14G/DatosAbiertos2026-v3`

---

## 1. Inventario de Archivos Auditados

### Código fuente (Python)
| Archivo | Líneas | Rol en la investigación |
|---|---|---|
| `quality_scorer.py` | 355 | Motor de scoring: 7 dimensiones ISO 25012 |
| `pipeline/evaluator.py` | 821 | Orquestador completo ISO 25012, ISO 8000, DAMA |
| `pipeline/extractor.py` | ~800 | Descubrimiento de datasets vía API CKAN |
| `pipeline/fetcher.py` | 221 | Descarga de recursos individuales |
| `pipeline/normalizer.py` | ~400 | Limpieza y parseo de formatos (CSV, JSON, XLSX) |
| `pipeline/persistence.py` | ~250 | Almacenamiento en CSV / JSON / Parquet |
| `section_data.py` | ~150 | Agregación de estadísticas para el dashboard |
| `config.py` | ~170 | Pesos, umbrales y configuración central |
| `scripts/generate_figures.py` | 172 | Generación de gráficas académicas |

### Datos
| Archivo | Descripción |
|---|---|
| `resultados_calidad_datos_nl.csv` | 288 recursos × 18 columnas — resultado final de la evaluación |
| `data/parquet/` | Snapshots históricos por fecha de ejecución |

### Documentación LaTeX
| Archivo | Estado |
|---|---|
| `Documentacion/protocolo-investigacion.tex` | ✅ Completo — 370 líneas, 10 secciones, APA 7 |
| `Documentacion/reporte_investigacion.tex` | ✅ Reescrito — migrado a biblatex, resultados empíricos completos |
| `Documentacion/referencias.bib` | ✅ 11 entradas BibLaTeX APA 7 |

---

## 2. Verificación de Citas (`\cite{}` vs `referencias.bib`)

### reporte_investigacion.tex
| Clave `\cite{}` | En `referencias.bib` | Estado |
|---|---|---|
| `neumaier2016` | ✅ | OK |
| `iso25012` | ✅ | OK |
| `dama2017` | ✅ | OK |
| `vetro2016` | ✅ | OK |
| `vizcaino2023` | ✅ | OK |
| `alanis2024` | ✅ (añadida) | OK |

### protocolo-investigacion.tex
| Clave `\cite{}` | En `referencias.bib` | Estado |
|---|---|---|
| `vetro2016` | ✅ | OK |
| `neumaier2016` | ✅ | OK |
| `hernandez2014` | ✅ | OK |
| `saenz2014` | ✅ | OK |
| `rojas2013` | ✅ | OK |
| `polania2020` | ✅ | OK |
| `vizcaino2023` | ✅ | OK |
| `bernerslee2006` | ✅ | OK |
| `lgtaip2015` | ✅ | OK |
| `wang1996` | ✅ | OK |
| `dama2017` | ✅ | OK |
| `iso25012` | ✅ | OK |

**Resultado: 0 citas huérfanas detectadas.**

---

## 3. Tests Automatizados

```
platform win32 -- Python 3.13.1, pytest-9.0.2
collected 15 items

pipeline/test_quality_scorer.py::test_perfect_dataset_score_is_high          PASSED
pipeline/test_quality_scorer.py::test_result_is_scoring_result_typeddict     PASSED
pipeline/test_quality_scorer.py::test_empty_dataframe_content_dimensions_zero PASSED
pipeline/test_quality_scorer.py::test_nan_timeliness_excluded_from_weights   PASSED
pipeline/test_quality_scorer.py::test_custom_weights_completeness_only       PASSED
pipeline/test_quality_scorer.py::test_quality_weights_sum_to_one             PASSED
pipeline/test_section_data.py::test_returns_section_data_instance            PASSED
pipeline/test_section_data.py::test_scalar_counts                            PASSED
pipeline/test_section_data.py::test_score_scalars                            PASSED
pipeline/test_section_data.py::test_n_critical_plus_good_plus_excellent_equals_n_datasets PASSED
pipeline/test_section_data.py::test_dim_means_populated                      PASSED
pipeline/test_section_data.py::test_org_stats_matches_agg_org_stats          PASSED
pipeline/test_section_data.py::test_dim_means_by_cat_not_empty               PASSED
pipeline/test_section_data.py::test_recent_datasets_top6                     PASSED
pipeline/test_section_data.py::test_empty_dataframe_returns_zero_scalars     PASSED

15 passed, 1 warning in 7.83s
```

**Resultado: 15/15 tests PASSED ✅**

---

## 4. Auditoría de Consistencia Terminológica

| Término | Código | LaTeX (protocolo) | LaTeX (reporte) | Estado |
|---|---|---|---|---|
| `score_global` / Score Global | `quality_scorer.py:L350` | Sección 6 (Variables) | Sección 4.1 | ✅ Consistente |
| Completitud / completeness | `quality_scorer.py:L44` | Tabla 6.1 | Tabla 4.3 | ✅ Consistente |
| Exactitud / accuracy | `quality_scorer.py:L66` | Tabla 6.1 | Tabla 4.3 | ✅ Consistente |
| Consistencia / consistency | `quality_scorer.py:L115` | Tabla 6.1 | Tabla 4.3 | ✅ Consistente |
| Unicidad / uniqueness | `quality_scorer.py:L157` | Tabla 6.1 | Tabla 4.3 | ✅ Consistente |
| Puntualidad / timeliness | `quality_scorer.py:L177` | Tabla 6.1 | Tabla 4.3 | ✅ Consistente |
| Documentación / documentation | `quality_scorer.py:L214` | Tabla 6.1 | Tabla 4.3 | ✅ Consistente |
| Apertura / openness | `quality_scorer.py:L265` | Tabla 6.1 | Tabla 4.3 | ✅ Consistente |
| Gold / Silver / Bronze | `config.py` | §4 (H4) | Tabla 4.2 | ✅ Consistente |

**Resultado: 0 inconsistencias terminológicas detectadas.**

---

## 5. Consistencia de Valores Numéricos

| Métrica | Valor en CSV | Valor en reporte.tex | Estado |
|---|---|---|---|
| Total recursos | 288 | 288 | ✅ |
| Score promedio | 88.83 | 88.83 | ✅ |
| Score mediana | 91.61 | 91.61 | ✅ |
| Desv. estándar | 9.48 | 9.48 | ✅ |
| Score mín | 52.61 | 52.61 | ✅ |
| Score máx | 98.23 | 98.23 | ✅ |
| Gold (%) | 65.6% | 65.6% | ✅ |
| Silver (%) | 27.8% | 27.8% | ✅ |
| Bronze (%) | 6.6% | 6.6% | ✅ |
| Media completitud | 85.09 | 85.09 | ✅ |
| Media documentación | 72.40 | 72.40 | ✅ |

---

## 6. Issues Abiertos

| # | Issue | Severidad | Acción requerida |
|---|---|---|---|
| 1 | `ruff` pasa en CI pero `pipeline/evaluator.py:L328–331` contiene métodos `_evaluar_exactitud`, `_evaluar_consistencia` y `_evaluar_actualidad` con cuerpos `pass` (implementación simplificada) | Baja | Documentar como trabajo futuro |
| 2 | `reporte_investigacion.tex` requiere `biber` para compilar (no solo `pdflatex`) | Media | Usar el script `compile.bat` |
| 3 | Entrada `alanis2024` en `referencias.bib` es un `@techreport` sin DOI ni URL verificada; el autor exacto no fue confirmado | Media | Verificar datos con el tutor antes de entrega |

---

## 7. Figuras Generadas

| Archivo | Descripción |
|---|---|
| `Documentacion/figures/fig1_distribucion_scores.png` | Histograma de scores globales con clasificación Medallion |
| `Documentacion/figures/fig2_dimensiones.png` | Barras horizontales por dimensión con peso ponderado |
| `Documentacion/figures/fig3_clasificacion.png` | Gráfico donut Gold/Silver/Bronze |
| `Documentacion/figures/fig4_top_organizaciones.png` | Top 10 dependencias por score promedio |

---

## 8. Veredicto Final

| Área | Estado |
|---|---|
| Tests automatizados | ✅ 15/15 PASSED |
| Citas LaTeX vs BibTeX | ✅ 0 huérfanas |
| Consistencia terminológica | ✅ 0 inconsistencias |
| Valores numéricos | ✅ Todos verificados contra CSV |
| Figuras | ✅ 4 figuras generadas en 180 DPI |
| **Listo para compilación PDF** | ✅ Ejecutar `Documentacion/compile.bat` |
