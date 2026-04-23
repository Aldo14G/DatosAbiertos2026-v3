# Scoring Sensitivity Analysis — Robustez de los pesos ISO 25012

**Pesos actuales ([config.py:15-23](../../../config.py#L15-L23)):**
```
completeness  = 0.30
accuracy      = 0.25
consistency   = 0.15
uniqueness    = 0.08
timeliness    = 0.05
documentation = 0.10
openness      = 0.07
```

**Pregunta:** ¿Cambiaría el ranking de datasets si moviéramos los pesos? ¿Son los pesos "justificables" o "arbitrarios"?

---

## Blocker: dataset v1 insuficiente

El pipeline ISO 25012 de 7 dimensiones (`data_layer.compute_quality_scores`) actualmente produce **n = 1** dataset en [resultados_calidad_datos_nl.csv](../../../resultados_calidad_datos_nl.csv) y [.antigravity/team/shared/quality_results.json](../../../.antigravity/team/shared/quality_results.json).

Con n = 1 **no se puede calcular** correlación de Spearman (requiere ≥3 observaciones para ranking no trivial). El pipeline v1 debe ejecutarse a full scale antes de un análisis empírico de robustez para la escala 7D.

---

## Análisis ejecutado sobre pipeline AVANZADO (n = 272)

**Fuente:** [.antigravity/team/shared/advanced_quality_results.json](../../../.antigravity/team/shared/advanced_quality_results.json) — 272 reportes del pipeline "agentic" ([pipeline/evaluator_v1.py](../../../pipeline/evaluator_v1.py)).

**Dimensiones disponibles (5 de 7):**
- completitud ← usada como `completeness`
- conformidad ← usada como proxy de `accuracy`
- comprensibilidad ← usada como proxy de `consistency`
- unicidad ← `uniqueness`
- trazabilidad ← usada como proxy de `documentation`

**Timeliness y openness no existen en este dataset** → análisis parcial.

### Variantes de pesos evaluadas

| Variante | completeness | accuracy | consistency | uniqueness | documentation |
|---|---|---|---|---|---|
| **Baseline** (actual renorm) | 0.341 | 0.284 | 0.170 | 0.091 | 0.114 |
| Uniforme (1/5) | 0.200 | 0.200 | 0.200 | 0.200 | 0.200 |
| Completeness-heavy | 0.500 | 0.200 | 0.100 | 0.100 | 0.100 |
| Accuracy-heavy | 0.200 | 0.500 | 0.100 | 0.100 | 0.100 |
| Metadata-heavy | 0.200 | 0.200 | 0.100 | 0.100 | 0.400 |

### Matriz de correlación de Spearman (rho)

| | Baseline | Uniforme | Comp-heavy | Acc-heavy | Meta-heavy |
|---|---|---|---|---|---|
| **Baseline** | 1.0000 | 0.9950 | 0.9997 | 0.9987 | 0.9987 |
| **Uniforme** | 0.9950 | 1.0000 | 0.9932 | 0.9985 | 0.9985 |
| **Comp-heavy** | 0.9997 | 0.9932 | 1.0000 | 0.9977 | 0.9977 |
| **Acc-heavy** | 0.9987 | 0.9985 | 0.9977 | 1.0000 | 1.0000 |
| **Meta-heavy** | 0.9987 | 0.9985 | 0.9977 | 1.0000 | 1.0000 |

### Interpretación

- **rho > 0.99 en todas las combinaciones** → los 272 datasets ordenan casi idéntico bajo cualquier variante de pesos.
- La cercanía entre Acc-heavy y Meta-heavy (rho = 1.0) evidencia que **accuracy y documentation casi no varían** entre datasets del advanced pipeline (ver distribución abajo) → sus pesos no discriminan.

### Distribución real de las 5 dimensiones

| Dimensión | Mean | Min | Max | Varianza real |
|---|---|---|---|---|
| completeness | 91.3 | 0.2 | 100.0 | **Alta** |
| accuracy (conformidad) | 93.3 | 93.3 | 93.3 | **Cero** |
| consistency (comprensibilidad) | 100.0 | 100.0 | 100.0 | **Cero** |
| uniqueness | 94.3 | 0.7 | 100.0 | Alta |
| documentation (trazabilidad) | 100.0 | 100.0 | 100.0 | **Cero** |

**Hallazgo crítico:** 3 de las 5 dimensiones en el pipeline avanzado tienen **varianza cero** — todos los datasets reciben el mismo score. Esto inflaría artificialmente el `score_promedio_catalogo` (95.45% reportado) y reduce el análisis a una función efectiva de completeness + uniqueness.

---

## Conclusiones

### A · Robustez de pesos — indeterminada sin datos v1 completos

El análisis muestra **robustez ficticia alta**. La ρ ≈ 1.0 no indica que los pesos estén "bien elegidos"; indica que el pipeline avanzado devuelve valores casi constantes en 3 de 5 dimensiones, haciendo que cualquier ponderación produzca ranking similar.

**Bloquea Fase 2:** Sí, para validación formal de pesos.

### B · Detector de "dimensiones muertas"

El pipeline avanzado debe auditarse: ¿por qué `conformidad`, `comprensibilidad` y `trazabilidad` son constantes (≈100) para 272 datasets? Posibles causas:
1. El evaluador aplica un score por defecto cuando no puede medir (saturación artificial).
2. Los umbrales son tan permisivos que todos aprueban.
3. Bug: no se invoca la evaluación real y devuelve el default de `umbral_aceptable`.

### C · Recomendaciones Fase 2

1. **Ejecutar pipeline v1 a full scale** (no solo 1 dataset en CSV) para habilitar análisis empírico de los 7 pesos reales (completeness, accuracy, consistency, uniqueness, **timeliness**, documentation, **openness**).
2. **Auditar dimensiones saturadas** — revisar `pipeline/evaluator_v1.py` para detectar early-returns o defaults que estén anulando la medición real.
3. **Sensibilidad formal:** repetir este análisis con la función de scoring real `data_layer.compute_quality_scores()` cuando haya ≥30 datasets procesados.
4. **Justificación académica:** documentar en `docs/methodology.md` por qué 0.30/0.25/0.15/0.08/0.05/0.10/0.07 — referencia Wang & Strong 1996 (citada en [config.py:25-26](../../../config.py#L25-L26)) pero no demostrada.
5. **Sensitivity gate en CI (Fase 3):** rechazar PR que cambie `QUALITY_WEIGHTS` si ρ < 0.85 con baseline (= cambio fundamental de ranking).

---

## Apéndice — Script de reproducción

Ejecutable sin dependencias externas (Python stdlib):

```python
# scripts/sensitivity.py (Fase 2)
import json
from collections import defaultdict

def spearman(xs, ys):
    def rank(arr):
        sp = sorted(enumerate(arr), key=lambda x: x[1])
        ranks = [0.0] * len(arr)
        i = 0
        while i < len(arr):
            j = i
            while j+1 < len(arr) and sp[j+1][1] == sp[i][1]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j+1):
                ranks[sp[k][0]] = avg
            i = j+1
        return ranks
    rx, ry = rank(xs), rank(ys)
    n = len(xs)
    mx, my = sum(rx)/n, sum(ry)/n
    num = sum((rx[i]-mx)*(ry[i]-my) for i in range(n))
    dx = sum((r-mx)**2 for r in rx)**0.5
    dy = sum((r-my)**2 for r in ry)**0.5
    return num / (dx*dy) if dx and dy else float('nan')

# ... ver auditoría para reproducir
```

Ejecución: `python scripts/sensitivity.py` — output determinístico ante mismos datos.
