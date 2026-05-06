"""Sección Metodología — Cómo se construye el score + dimensiones ISO activas.

Bloque 5 del narrative flow: responde "¿cómo se mide esto?" con el pipeline
de 4 etapas, las 7 dimensiones con su estado actual y los pesos del modelo.
"""
from __future__ import annotations

import html as _html

import streamlit as st

from section_data import SectionData
from sections.dimensions import CITIZEN_LABELS as _CITIZEN_LABELS

_PIPELINE_STEPS: list[tuple[str, str, str]] = [
    (
        "travel_explore", "Descubrimiento",
        "Consulta la API CKAN pública del portal. Recolecta metadatos y URLs "
        "de cada recurso publicado respetando límites de tamaño y SSRF.",
    ),
    (
        "download", "Extracción",
        "Descarga cada recurso validando formato real vs declarado. "
        "Soporta CSV, JSON, XLSX, GeoJSON y XML.",
    ),
    (
        "fact_check", "Evaluación ISO 25012",
        "Calcula 7 dimensiones por dataset con pesos ponderados "
        "y genera el score global en escala 0–100.",
    ),
    (
        "hub", "Agregación",
        "Cachea resultados, produce agregaciones por organización y categoría, "
        "y expone APIs de filtrado a la interfaz.",
    ),
]

_WEIGHTS: list[tuple[str, float]] = [
    ("Completitud",   0.30),
    ("Exactitud",     0.25),
    ("Consistencia",  0.15),
    ("Documentación", 0.10),
    ("Unicidad",      0.08),
    ("Apertura",      0.07),
    ("Puntualidad",   0.05),
]


def _health_bar(label: str, pct: float, tier: str = "teal", desc: str = "") -> None:
    pct_clean = max(0, min(100, round(pct, 1)))
    fill_class = {
        "teal": "bar-fill",
        "gold": "bar-fill bar-fill-gold",
        "rose": "bar-fill bar-fill-rose",
    }.get(tier, "bar-fill")
    desc_html = f'<p class="health-mini-card-desc">{desc}</p>' if desc else ""
    st.markdown(f"""
<div class="health-mini-card">
  <div class="health-mini-card-header">
    <span class="health-mini-card-label">{label}</span>
    <span class="health-mini-card-pct">{pct_clean}%</span>
  </div>
  {desc_html}
  <div class="bar-track" role="progressbar" aria-label="{label}"
       aria-valuenow="{pct_clean}" aria-valuemin="0" aria-valuemax="100">
    <div class="{fill_class}" style="width:{pct_clean}%"></div>
  </div>
</div>
""", unsafe_allow_html=True)


def render_metodologia(data: SectionData, tokens: dict) -> None:
    """Metodología — pipeline de 4 etapas + estado actual de las 7 dimensiones ISO."""
    st.markdown("""
<section id="metodologia" aria-labelledby="metodologia-title">
  <div class="nl-section-intro nl-reveal">
    <span class="eyebrow">Cómo funciona</span>
    <h2 id="metodologia-title" class="section-title">¿Cómo se mide la calidad?</h2>
    <p class="section-subtitle">
      Cuatro etapas automáticas evalúan cada dataset contra las
      7 dimensiones del estándar ISO/IEC 25012.
    </p>
  </div>
</section>
""", unsafe_allow_html=True)

    steps_html = "".join(
        f'<article class="nl-pipeline-step stitch-card">'
        f'<span class="material-symbols-outlined nl-pipeline-icon" aria-hidden="true">{icon}</span>'
        f'<h3 class="section-title nl-pipeline-title">{_html.escape(title)}</h3>'
        f'<p class="section-subtitle nl-pipeline-body">{_html.escape(body)}</p>'
        f'</article>'
        for icon, title, body in _PIPELINE_STEPS
    )
    st.markdown(
        f'<div class="nl-pipeline-grid nl-reveal">{steps_html}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("""
<div class="nl-section-intro nl-reveal">
  <span class="eyebrow">Dimensiones ISO/IEC 25012</span>
  <h3 class="section-title">Estado actual del catálogo</h3>
  <p class="section-subtitle">
    Promedio real de cada dimensión. Verde ≥80%, dorado ≥60%, rojo necesita atención.
  </p>
</div>
<div class="nl-center-measure nl-reveal">
""", unsafe_allow_html=True)

    health_metrics: dict[str, float] = data.dim_means or {}
    for tech_label, pct in health_metrics.items():
        entry = _CITIZEN_LABELS.get(tech_label, (tech_label, ""))
        label, desc = entry if isinstance(entry, tuple) else (entry, "")
        tier = "teal" if pct >= 80 else "gold" if pct >= 60 else "rose"
        _health_bar(label, pct, tier=tier, desc=desc)

    st.markdown("</div>", unsafe_allow_html=True)

    weights_html = "".join(
        f'<div class="nl-weight-row">'
        f'<div class="nl-weight-head">'
        f'<span class="nl-weight-label">{_html.escape(dim)}</span>'
        f'<span class="nl-weight-value">{int(round(w * 100))}%</span>'
        f'</div>'
        f'<div class="bar-track" role="progressbar"'
        f' aria-label="Peso de {_html.escape(dim)}"'
        f' aria-valuenow="{int(round(w * 100))}" aria-valuemin="0" aria-valuemax="40">'
        f'<div class="bar-fill nl-weight-fill" style="width:{min(int(w * 100) * 3, 100)}%"></div>'
        f'</div>'
        f'</div>'
        for dim, w in _WEIGHTS
    )
    st.markdown(f"""
<div class="nl-criteria-card nl-reveal">
  <div class="eyebrow mb-3">Pesos del modelo</div>
  {weights_html}
</div>
""", unsafe_allow_html=True)
