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
Documentation y Openness portados del estudio NL 2024."""

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
PUERTO: int = 8503
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
    (60.0, "Deficiente"),
]
CLASIFICACION_DEFAULT: str = "Critico"
"""Umbrales para derivar etiquetas de clasificacion desde score_global.
Replica los rangos de evaluator.py para coherencia con el pipeline avanzado."""
