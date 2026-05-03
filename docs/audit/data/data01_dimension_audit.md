# DATA-01 — Auditoría de Dimensiones con Varianza Cero

**Fecha:** 2026-04-16  
**Fuente analizada:** [pipeline/evaluator_v1.py](../../../pipeline/evaluator_v1.py) · [advanced_quality_results.json](../../../.antigravity/team/shared/advanced_quality_results.json) (n = 272)  
**Regla aplicada:** Solo diagnóstico — NO se modifica `pipeline/`.

---

## Hallazgo

3 de 5 dimensiones del pipeline avanzado (`SkillEvaluadorDatos`) tienen varianza cero en los 272 datasets:

| Dimensión (JSON) | Proxy de | Valor constante | Causa |
|---|---|---|---|
| `conformidad` | accuracy | 93.3 | Fallback por ausencia de columnas tipadas |
| `comprensibilidad` | consistency | 100.0 | Saturación: todos los datasets tienen nombres de columna "buenos" |
| `trazabilidad` | documentation | 100.0 | Stub vacío + DAMA saturado |

---

## Análisis por dimensión

### 1 · Conformidad = 93.3 (accuracy proxy)

**Método:** [`_evaluar_conformidad`](../../../pipeline/evaluator_v1.py#L219-L293) en `AnalizadorISO25012`.

Dos ramas:
- **Rama A** (columnas con tokens detectables): busca `curp`, `rfc`, `cp`, `telefono`, `email`, `fecha`, `cve_mun` en nombres de columna → score = media de compliance regex por columna.
- **Rama B** (fallback): cuando ninguna columna tiene token reconocible → cuenta columnas "mixtas" (object dtype + ≥30% valores numéricos) → `score = 100.0 − (mixed / total) * 100.0`.

**Causa de la constante 93.3:**  
La mayoría de los 272 datasets del catálogo NL no tienen columnas con esos tokens → todos caen en Rama B.  
El fallback produce scores similares porque los datasets tienden a tener ~1 columna mixta en ~15 totales:  
`100 − (1/15) × 100 ≈ 93.3`.

**Naturaleza:** diseño, no bug. La Rama B es un proxy débil para conformidad cuando el catálogo no usa las convenciones de nombre esperadas.

---

### 2 · Comprensibilidad = 100.0 (consistency proxy)

**Método:** [`_evaluar_comprensibilidad`](../../../pipeline/evaluator_v1.py#L295-L344) en `AnalizadorISO25012`.

Marca un nombre de columna como "pobre" si:
- longitud < 3 chars
- empieza por `unnamed`
- no tiene vocales
- es solo letra + dígitos (`A1`, `B2`)

`score = (1 − nombres_pobres / total) × 100`

**Causa de la constante 100.0:**  
Los datasets del catálogo NL usan sistemáticamente nombres descriptivos en snake_case con vocales. El criterio es demasiado permisivo para este corpus → `nombres_pobres = 0` en casi todos → score 100.0.

**Naturaleza:** saturación de métrica. No es un bug; el criterio simplemente no discrimina para este catálogo.

---

### 3 · Trazabilidad = 100.0 (documentation proxy)

**Método:** [`_evaluar_trazabilidad`](../../../pipeline/evaluator_v1.py#L405-L407) en `AnalizadorISO8000`.

```python
def _evaluar_trazabilidad(self, df, metadata, dataset_id, recurso_id):
    metricas, problemas = [], []
    return metricas, problemas   # ← STUB. Sin implementación.
```

**Causa:** `_evaluar_trazabilidad` es un stub completamente vacío — nunca añade métricas.  
Los valores `trazabilidad = 100.0` en `advanced_quality_results.json` vienen de dos métricas `DAMA-DMBOK` con `categoria = "trazabilidad"`:
- `gobernanza` — chequea metadatos CKAN (author, maintainer, license, organization, state)
- `calidad_metadatos` — evalúa title, notes, tags, license_id, frequency

El catálogo NL tiene metadatos CKAN completos para la mayoría de datasets → `gobernanza + calidad_metadatos ≈ 100` → promedio = 100.0.

**Naturaleza:** dos bugs distintos:
1. `_evaluar_trazabilidad` es stub — ISO 8000 trazabilidad sin implementar.
2. Las métricas DAMA que sí se calculan están saturadas para este corpus.

---

## Impacto en score_promedio_catalogo

El pipeline calcula `score_global` de cada dataset como:

```python
score_global = mean([score_iso25012, score_iso8000, score_dama])
```

Con 3 dimensiones muertas (constantes en ~93-100), el `score_promedio_catalogo = 95.45%` está artificialmente inflado.  
La **información discriminante real** del pipeline avanzado viene únicamente de:
- `completitud` (varianza alta: 0.2 → 100.0)
- `unicidad` (varianza alta: 0.7 → 100.0)

Los rankings actuales de datasets son esencialmente ordenados por `completitud + unicidad`.

---

## Qué NO está roto

- Los datos de `completitud` y `unicidad` son válidos y discriminan correctamente.
- La arquitectura del evaluador es correcta — el problema es de implementación incompleta y saturación de métricas.
- El `score_promedio_catalogo` no es **falso** per se — refleja lo que el evaluador mide; el problema es que el evaluador no mide lo que debería en 3 dimensiones.

---

## Recomendaciones para Fase 2

> **Regla:** no modificar `pipeline/` sin sign-off. Estas son propuestas para evaluación.

| # | Acción | Dimensión afectada | Esfuerzo |
|---|---|---|---|
| R1 | Implementar `_evaluar_trazabilidad` (ISO 8000) con criterios de linaje, hash de datos, versión de schema | trazabilidad | M |
| R2 | Refinar `_evaluar_comprensibilidad`: añadir criterios semánticos (columnas sin descripción de diccionario, nombres ambiguos) | comprensibilidad | M |
| R3 | Ampliar detectores de conformidad a patrones NL reales (ID_TRAMITE, FOLIO, CVE_DEPENDENCIA) en Rama A | conformidad | S |
| R4 | Comunicar score real = `completitud × 0.5 + unicidad × 0.5` (proxy ejecutivo) hasta Fase 2 completa | — | S |
| R5 | Ejecutar pipeline v1 (DATA-02) a full scale para habilitar análisis de los 7 pesos originales | todos | M |

---

## Evidencia de no-regresión

El diagnóstico fue **solo lectura**. Verificación:

```bash
git diff pipeline/
# (sin cambios)
```

Commit de audit: este archivo + `GAP_ANALYSIS.md` actualizado.
