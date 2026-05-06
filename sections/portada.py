"""Sección Portada — pregunta central, score global y stat strip.

Bloque 1 del narrative flow: plantea la pregunta y responde con el número
clave. Max 2 bloques visuales: headline del score + stat strip de 4 números.
"""
from __future__ import annotations

import streamlit as st

from data_layer import load_coverage_report
from section_data import SectionData


def render_portada(data: SectionData, tokens: dict) -> None:
    """Portada — hero, score headline y 4 stats clave."""
    score = data.mean_score
    status_label = "Óptimo" if score >= 80 else "En Revisión"
    status_color = "excellent" if score >= 80 else "poor"
    score_cls = "nl-stat-strip-number--teal" if score >= 80 else "nl-stat-strip-number--rose"

    coverage = load_coverage_report()
    run_id = (coverage or {}).get("run_id", "")
    if len(run_id) == 15:
        pipeline_ts = (
            f"{run_id[:4]}-{run_id[4:6]}-{run_id[6:8]} "
            f"{run_id[9:11]}:{run_id[11:13]}"
        )
    else:
        pipeline_ts = "desconocida"

    st.markdown(f"""
<section id="portada" aria-labelledby="portada-title">
  <header class="editorial-header fade-up">
    <div class="eyebrow">Gobernanza de Datos · Nuevo León 2026</div>
    <h1 id="portada-title" class="editorial-title">
      ¿Qué tan confiables son los datos del Estado?
    </h1>
    <p class="hero-subtitle">
      Un análisis independiente de los datos publicados en el portal oficial,
      evaluados con el estándar internacional ISO/IEC 25012.
    </p>
    <div class="nl-hero-ctas">
      <a href="#hallazgos" class="stitch-btn-primary">
        <span class="material-symbols-outlined" aria-hidden="true">insights</span>
        Ver hallazgos
      </a>
      <a href="#metodologia" class="stitch-btn-ghost">
        <span class="material-symbols-outlined" aria-hidden="true">menu_book</span>
        Metodología
      </a>
    </div>
  </header>

  <div class="nl-hero-stat-block nl-reveal nl-reveal-d1">
    <p class="nl-hero-stat-prose">El catálogo obtiene
      <span class="nl-hero-stat-score nl-hero-stat-score--{status_color}">
        {score:.1f}%
      </span>
      en ISO/IEC 25012.</p>
    <span class="nl-hero-stat-label">{status_label}</span>
  </div>

  <div class="nl-stat-strip nl-reveal nl-reveal-d2">
    <div class="nl-stat-strip-item">
      <span class="nl-stat-strip-number {score_cls}">{score:.1f}%</span>
      <span class="nl-stat-strip-label">Score promedio</span>
    </div>
    <div class="nl-stat-strip-item">
      <span class="nl-stat-strip-number">{data.n_datasets}</span>
      <span class="nl-stat-strip-label">Datasets evaluados</span>
    </div>
    <div class="nl-stat-strip-item">
      <span class="nl-stat-strip-number">{data.n_orgs}</span>
      <span class="nl-stat-strip-label">Dependencias</span>
    </div>
    <div class="nl-stat-strip-item">
      <span class="nl-stat-strip-number nl-stat-strip-number--rose">{data.n_critical}</span>
      <span class="nl-stat-strip-label">Datasets críticos</span>
    </div>
  </div>

  <p class="nl-portada-timestamp nl-reveal">
    Última evaluación: {pipeline_ts} · catalogodatos.nl.gob.mx
  </p>
</section>
""", unsafe_allow_html=True)
