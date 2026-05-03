# config.py
# Configuración centralizada del proyecto DatosAbiertos2026.
# Importar constantes desde aquí en lugar de hardcodearlas.

from __future__ import annotations

# ── Umbrales de calidad ISO 25012 ──────────────────────────────
UMBRAL_GOBERNANZA: float = 70.0
"""Score mínimo aceptable para gobernanza de datos (ISO/IEC 25012:2008)."""

UMBRAL_EXCELENTE: float = 90.0
"""Score a partir del cual un dataset se clasifica como 'excelente'."""

# ── Pesos ISO 25012 + catálogo ─────────────────────────────────
QUALITY_WEIGHTS: dict[str, float] = {
    "completeness":  0.30,
    "accuracy":      0.25,
    "consistency":   0.15,
    "uniqueness":    0.08,
    "timeliness":    0.05,
    "documentation": 0.10,
    "openness":      0.07,
}
"""Pesos ponderados — 7 dimensiones (5 ISO 25012 + 2 catálogo). Suma = 1.0.
Completitud y Exactitud priman (Wang & Strong 1996).
Documentation y Openness portados del estudio NL 2024.
Al cambiar estos valores ejecutar: python scripts/sync_weights.py"""

# ── Defaults de dimensión por contexto ────────────────────────
DIM_ALERT_DEFAULTS: dict[str, float] = {
    "comp_completitud_global_pct" : 0.0,
    "acc_score_accuracy_pct"      : 0.0,
    "cons_score_consistency_pct"  : 0.0,
    "uniq_score_uniqueness_pct"   : 0.0,
    "time_score_timeliness_pct"   : 50.0,
    "doc_score_documentation_pct" : 0.0,
    "open_score_openness_pct"     : 0.0,
}
"""Defaults conservadores para tarjetas de alerta: muestra la barra en rojo si
el dato está ausente, salvo Puntualidad (50) porque ausencia ≠ retraso probado."""

DIM_REC_DEFAULTS: dict[str, float] = {
    "comp_completitud_global_pct" : 100.0,
    "acc_score_accuracy_pct"      : 100.0,
    "cons_score_consistency_pct"  : 100.0,
    "uniq_score_uniqueness_pct"   : 100.0,
    "time_score_timeliness_pct"   :  50.0,
    "doc_score_documentation_pct" : 100.0,
    "open_score_openness_pct"     : 100.0,
}
"""Defaults permisivos para lógica de recomendaciones: si el campo está ausente
no se genera recomendación (evita falsos positivos sobre datos faltantes)."""

# ── Seguridad ──────────────────────────────────────────────────
MAX_DOWNLOAD_MB: int = 50
"""Tamaño máximo de descarga en megabytes para el agente de código."""

DOMINIOS_PERMITIDOS: frozenset[str] = frozenset({
    "catalogodatos.nl.gob.mx",
    "datos.nl.gob.mx",
})
"""Dominios confiables para descarga de datasets."""

# ── Aplicación ─────────────────────────────────────────────────
TITULO_APP: str = "Gobernanza de Datos — Nuevo León 2026"
VERSION: str = "V2.1 · NL 2026 SYS"
PUERTO: int = 8501
COLOR_PRINCIPAL: str = "#0F172A"

# ── Caché ──────────────────────────────────────────────────────
CACHE_TTL_SECONDS: int = 300
"""Tiempo de vida del caché de datos en segundos (5 minutos)."""

# ── Baseline pre-pipeline (referencia "Antes") ────────────────
BASELINE_ANTES: dict[str, str | int | float] = {
    "datasets_evaluados": 1,
    "cobertura_pct": 0.4,
    "dimensiones": 4,
    "tiempo_s": "N/A",
    "score_promedio": "N/A",
    "formatos": 1,
}
"""Valores de referencia pre-pipeline para comparacion Antes vs Ahora.
Fuente: evaluacion manual inicial del catalogo NL (1 dataset, 4 dims)."""

# ── Clasificacion de datasets por score ───────────────────────
CLASIFICACION_THRESHOLDS: list[tuple[float, str]] = [
    (90.0, "Excelente"),
    (80.0, "Bueno"),
    (70.0, "Aceptable"),
    (50.0, "Deficiente"),
]
CLASIFICACION_DEFAULT: str = "Crítico"
"""Umbrales para derivar etiquetas de clasificacion desde score_global.
Fuente de verdad para evaluator.py y el dashboard. Orden descendente obligatorio."""
