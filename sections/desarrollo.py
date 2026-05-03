"""Sección Desarrollo — Metodología, proceso y enfoque técnico.

Explica cómo se construye el score ISO/IEC 25012:2008, qué hace cada etapa
del pipeline, y caracteriza el universo de datasets analizado. Consume
datos reales desde data_layer (coverage_report + df agregado) — nada estático.
"""

from __future__ import annotations

import html as _html

import pandas as pd
import streamlit as st

# ══════════════════════════════════════════════════════════════
# Contenido estático pedagógico (metodología)
# ══════════════════════════════════════════════════════════════

_PIPELINE_STEPS: list[tuple[str, str, str]] = [
    (
        "travel_explore", "Descubrimiento (Fetcher)",
        "Consulta la API CKAN pública del Portal NL. Itera sobre todos los "
        "paquetes publicados, recolecta metadatos y URLs de recursos. "
        "Respeta SSRF y límites de tamaño.",
    ),
    (
        "download", "Extracción (Extractor)",
        "Descarga cada recurso validando formato declarado vs real. Soporta "
        "CSV, JSON, XLSX, GeoJSON, XML. Detecta encoding automáticamente; "
        "normaliza delimitadores y tipos.",
    ),
    (
        "fact_check", "Evaluación (Evaluator ISO 25012)",
        "Calcula 7 dimensiones por dataset: Completitud, Exactitud, Consistencia, "
        "Unicidad, Puntualidad, Documentación, Apertura. Aplica pesos ponderados y "
        "genera el score global.",
    ),
    (
        "hub", "Agregación (Data Layer)",
        "Cachea los resultados, produce agregaciones por organización y categoría, "
        "y expone APIs de filtrado para la UI. Integra overlay de pipeline avanzado "
        "(ISO 8000 + DAMA) si está disponible.",
    ),
]

_DIM_DESCRIPTIONS: dict[str, str] = {
    "Completitud":   "% de celdas no nulas ponderadas por la criticidad de la columna.",
    "Exactitud":     "Validación de tipos, rangos y formatos contra el esquema declarado.",
    "Consistencia":  "Coherencia cross-columna y detección de outliers (IQR robusto, n≥30).",
    "Unicidad":      "Ratio de registros únicos vs totales; penaliza duplicación lógica.",
    "Puntualidad":   "Latencia entre última actualización y frecuencia declarada.",
    "Documentación": "Completitud de metadatos CKAN: descripción, licencia, contactos.",
    "Apertura":      "Grado de apertura del formato según Open Data Charter.",
}


# ══════════════════════════════════════════════════════════════
# Helpers privados
# ══════════════════════════════════════════════════════════════

def _divider(label: str) -> None:
    st.markdown(f"""
    <div class="inicio-divider">
        <span class="inicio-divider-label">{_html.escape(label)}</span>
        <div class="inicio-divider-line"></div>
    </div>
    """, unsafe_allow_html=True)


def _pipeline_card(icon: str, title: str, body: str) -> str:
    return (
        f'<article class="nl-pipeline-step stitch-card">'
        f'<span class="material-symbols-outlined nl-pipeline-icon" aria-hidden="true">{icon}</span>'
        f'<h3 class="section-title nl-pipeline-title">{_html.escape(title)}</h3>'
        f'<p class="section-subtitle nl-pipeline-body">{_html.escape(body)}</p>'
        f'</article>'
    )


def _weight_row(dim_label: str, weight: float, description: str) -> str:
    pct = int(round(weight * 100))
    width = min(max(pct * 3, 8), 100)
    return (
        f'<div class="nl-weight-row">'
        f'<div class="nl-weight-head">'
        f'<span class="nl-weight-label">{_html.escape(dim_label)}</span>'
        f'<span class="nl-weight-value">{pct}%</span>'
        f'</div>'
        f'<div class="bar-track" role="progressbar"'
        f' aria-label="Peso de {_html.escape(dim_label)}"'
        f' aria-valuenow="{pct}" aria-valuemin="0" aria-valuemax="40">'
        f'<div class="bar-fill nl-weight-fill" style="width:{width}%"></div>'
        f'</div>'
        f'<p class="nl-weight-desc">{_html.escape(description)}</p>'
        f'</div>'
    )


# ══════════════════════════════════════════════════════════════
# Render principal
# ══════════════════════════════════════════════════════════════

def render_desarrollo(df: pd.DataFrame, _tokens: dict) -> None:
    """Sección Desarrollo — Metodología simplificada."""
    n_datasets = len(df)
    n_orgs = df["organizacion"].nunique() if "organizacion" in df.columns else 0

    st.markdown(f"""
<section id="desarrollo" class="nl-section nl-reveal">
<span class="eyebrow">01 · Metodología</span>
<h2 class="section-title nl-section-title">¿Cómo analizamos los datos?</h2>
</section>
<div class="editorial-container fade-up nl-reveal nl-reveal-d1">
<p>Usamos un "analista robot" que entra al portal oficial y revisa cada dataset bajo 4 criterios clave:</p>
<div class="nl-criteria-card">
<ul class="nl-criteria-list">
<li><strong class="accent-teal">1. Existencia:</strong> ¿El archivo se puede descargar o está roto?</li>
<li><strong class="accent-gold">2. Orden:</strong> ¿La estructura es clara o es un caos de celdas?</li>
<li><strong class="accent-rose">3. Verdad:</strong> ¿Los datos tienen sentido (ej. fechas válidas)?</li>
<li><strong class="accent-teal">4. Actualidad:</strong> ¿La información es de hoy o de hace años?</li>
</ul>
</div>
</div>
<div class="editorial-container mt-5 fade-up-2 nl-reveal nl-reveal-d2">
<h2 class="section-title">Universo Analizado</h2>
<p>Procesamos automáticamente <strong class="accent-teal">{n_datasets}</strong> conjuntos de datos de <strong class="accent-teal">{n_orgs}</strong> dependencias gubernamentales para generar los reportes de salud que ves en este sitio.</p>
</div>
""", unsafe_allow_html=True)
