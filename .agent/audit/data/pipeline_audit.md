# Data Pipeline Audit — 7 dimensiones ISO 25012

**Fuente:** [pipeline/evaluator_v1.py](../../../pipeline/evaluator_v1.py), [data_layer.py](../../../data_layer.py).
**Regla:** NO modificar `pipeline/*`. Solo documentar gaps.

## Síntesis

| Dimensión | Método actual | Fuente | GE equivalent | Gap | Esfuerzo Fase 2 |
|---|---|---|---|---|---|
| **Completitud** | `1 - df.isnull().sum()/df.size` | [data_layer.py:207-220](../../../data_layer.py#L207-L220) | `expect_column_values_to_not_be_null` + `expect_table_row_count_to_be_between` | Medio — falta contrato por columna | M |
| **Exactitud** | Penalización: mixtos ×40, espacios ×15, constantes ×20 | [data_layer.py:223-267](../../../data_layer.py#L223-L267) | `expect_column_values_to_match_regex`, `expect_column_value_lengths_to_be_between` | Alto — heurística sin ground-truth | L |
| **Consistencia** | IQR outliers (n≥30) + lowercase/strip duplicates | [data_layer.py:270-318](../../../data_layer.py#L270-L318) | `expect_column_values_to_be_unique_when_stripped`, custom expectation para IQR | Medio | M |
| **Unicidad** | `df.duplicated().sum()` | [data_layer.py:321-334](../../../data_layer.py#L321-L334) | `expect_compound_columns_to_be_unique` | Bajo — función simple | S |
| **Puntualidad** | `dias_desde_modificado` vs frecuencia declarada CKAN | [data_layer.py:337-384](../../../data_layer.py#L337-L384) | `expect_column_max_to_be_between` sobre fechas | Medio — depende de metadata CKAN confiable | M |
| **Documentación** | Score por len(descripción) + descripción de recursos + licencia + keywords | [data_layer.py:387-453](../../../data_layer.py#L387-L453) | No aplica — métrica de metadata, no datos | Bajo | S |
| **Apertura** | Formato + licencia abierta + acceso HTTP directo | [data_layer.py:456-521](../../../data_layer.py#L456-L521) | No aplica — métrica de metadata | Bajo | S |

**Esfuerzo:** S = 1-2 días · M = 3-5 días · L = 1-2 semanas.

---

## 1 · Completitud

**Método actual:**
```python
nulos = df.isnull().sum().sum()
completitud = (total - nulos) / total * 100
```
**Fortaleza:** Vectorizado, determinístico, rápido.
**Debilidad:** Trata todas las columnas como equivalentes. Un NULL en `fecha_evento` pesa igual que un NULL en `comentarios_opcionales`.

**Great Expectations sustituto:**
```python
expectation_suite.expect_column_values_to_not_be_null("id")
expectation_suite.expect_column_values_to_not_be_null("fecha_publicacion")
# Columnas opcionales: expect_column_values_to_not_be_null("notas", mostly=0.3)
```

**Gap Fase 2:**
- Definir lista de columnas obligatorias por tipo de dataset (padrón vs serie temporal vs registro administrativo).
- Reportar granularidad por columna en lugar de score agregado.
- No-bloqueante: el método actual sirve para ranking comparativo.

---

## 2 · Exactitud

**Método actual:** Tres detectores heurísticos penalizan el score:
- Columnas de tipo mixto (texto+numérico) → −40×(n/total_cols)
- Columnas con espacios al inicio/fin → −15×(n/total_cols)
- Columnas constantes → −20×(n/total_cols)

**Debilidad:**
1. **Sin ground-truth:** No compara contra valores esperados; penaliza patrones sospechosos.
2. Umbrales fijos (0.05 < pct_numeric < 0.95 en [data_layer.py:251](../../../data_layer.py#L251)) no calibrados.
3. Columna "constante" puede ser legítima (ej. `pais="México"`).
4. Penalización acumulativa puede llevar `score_accuracy` a 0 rápidamente.

**Great Expectations sustituto (por dataset):**
```python
expect_column_values_to_match_regex("cp", r"^\d{5}$")
expect_column_values_to_be_in_set("estado", ["Nuevo León", ...])
expect_column_values_to_be_between("edad", 0, 120)
```

**Gap Fase 2:**
- **Alto:** Migrar a expectations explícitas por dataset (requiere diccionario de datos).
- Alternativa pragmática: mantener heurística actual para "alerta temprana" + GE para validación formal.

---

## 3 · Consistencia

**Método actual:**
- **Outliers numéricos:** IQR (Q3 − Q1) × 1.5, solo columnas con n ≥ 30.
- **Inconsistencia textual:** `nunique(raw) − nunique(lower+strip)` → detecta "Monterrey" vs "monterrey" vs " Monterrey ".
- Score: `100 − pct_outliers×2 − min(incons_txt×0.5, 20)`.

**Fortaleza:** Umbral n≥30 elimina falsos positivos por muestra pequeña (mejora [FIX-2](../../../data_layer.py#L272)).

**Debilidad:**
- IQR × 1.5 asume distribución aproximadamente normal — falla en datos sesgados (presupuestos, población).
- No detecta valores "casi iguales" con typos (Levenshtein).

**Great Expectations sustituto:**
- `expect_column_values_to_be_between` para outliers acotados por dominio (no estadísticos).
- `expect_column_pair_values_to_be_equal` para validar joins.

**Gap Fase 2:** Medio — considerar `dedupe` o `recordlinkage` para typos.

---

## 4 · Unicidad

**Método actual:**
```python
dups = df.duplicated().sum()
score = 100 − pct_dup × 2
```

**Debilidad:** `df.duplicated()` requiere coincidencia exacta en **todas** las columnas. En práctica, duplicados lógicos difieren por timestamp o ID incremental.

**Great Expectations sustituto:**
```python
expect_compound_columns_to_be_unique(["cp", "calle", "num"])  # natural key
```

**Gap Fase 2:** Bajo — definir natural key por dataset (dict en config).

---

## 5 · Puntualidad

**Método actual:**
- Score 100 si `días_transcurridos ≤ frecuencia_declarada`.
- Score 0 si `días ≥ 2× frecuencia`.
- Interpolación lineal entre ambos.
- Si no hay frecuencia: degradación 20%/año.
- Si no hay fecha: `NaN` (no penaliza).

**Fortaleza:** Respeta el contrato CKAN de frecuencia de actualización.

**Debilidad:**
- Depende de `metadata_modified` en CKAN — puede reflejar edición de metadata, no de datos.
- `NaN` excluye la dimensión del score global ([data_layer.py:563-565](../../../data_layer.py#L563-L565)) — introduce varianza sistemática entre datasets con/sin fecha.

**Great Expectations sustituto:** No directo. Mejor: comparar `max(fecha_evento)` con `now()`.

**Gap Fase 2:** Medio — añadir detección de datos "stale" basada en contenido del CSV, no metadatos CKAN.

---

## 6 · Documentación (catálogo)

**Método actual (0-100):**
- Descripción dataset: 30 pts si ≥200 chars · 20 si ≥50 · 10 si >0.
- Descripción de recursos: 30 pts prorrateados.
- Licencia explícita: 20 pts.
- Keywords metodológicos: hasta 20 pts (5×kw, max 4 kws).

**Debilidad:** Pesos hard-coded. Bucket discretos (50/200 chars) insensibles a la calidad real del texto.

**Gap Fase 2:** Bajo — considerar score continuo basado en tokens distintos o LLM-as-judge (Fase 3).

---

## 7 · Apertura (catálogo)

**Método actual (0-100):**
- Formato abierto (CSV/JSON/GeoJSON/XML): 40.
- Licencia abierta (Creative Commons, public domain): 35.
- Acceso sin registro (URL HTTP/HTTPS): 25.

**Fortaleza:** Alineado con principios Open Data (FAIR).

**Debilidad:** No distingue CSV bien-formado de CSV con encoding roto. Un archivo "CSV" de 0 bytes puntúa 40.

**Gap Fase 2:** Bajo — añadir validación de parseabilidad (ya se intenta en `download_csv` pero no se reporta).

---

## Issues transversales

### Testing

✅ Tests en [pipeline/test_data_layer.py](../../../pipeline/test_data_layer.py), [pipeline/test_anomaly_detector.py](../../../pipeline/test_anomaly_detector.py), [pipeline/test_agent_pipeline.py](../../../pipeline/test_agent_pipeline.py).
❌ **No automatizados en CI.**

### Observabilidad

❌ [data_layer.py:159](../../../data_layer.py#L159) usa `print()` no `logging`.
❌ Sin `run_id` ni correlación entre pipeline runs y dashboard re-renders (aunque `pipeline_version` y `run_id` sí existen en el JSON output).

### Reproducibilidad

✅ `pipeline_version` y `run_id` en JSON output.
❌ No se commitea/archiva la versión de datos (CSV) que generó cada reporte.
❌ `fetch_portal_catalog` usa `@lru_cache(maxsize=1)` — cache de proceso, no de disco; no es reproducible entre runs.

### Escalabilidad

✅ Operaciones vectorizadas Pandas (post FIX-1, FIX-2).
⚠ `fetch_portal_catalog` pagina de 100 en 100 con `sleep(1.5s)` → ~272 datasets ≈ 4 minutos de fetch.

---

## Conclusión

El pipeline actual es **funcional y defendible para auditoría pública**, pero opera a nivel "descriptivo + heurístico". Fase 2 debe:

1. **Mantener** las métricas actuales como "alerta temprana".
2. **Añadir** Great Expectations suite por dataset con expectations basadas en diccionario de datos.
3. **Exponer** el reporte GE en el dashboard (nueva tab en Calidad Pro).
4. **Formalizar** schemas Pydantic (ver [data_contracts_gap.md](data_contracts_gap.md)).
