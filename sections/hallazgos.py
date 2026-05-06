"""Sección Hallazgos — Distribución + treemap + auditoría maestra.

Bloque 2 del narrative flow: responde al "panorama completo" con la
distribución de calidad y el treemap interactivo de todos los datasets.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from section_data import SectionData
from sections.charts_calidad import (
    chart_calidad_por_categoria,
    chart_dimensiones_promedio,
    chart_distribucion_clasi,
)


def render_hallazgos(data: SectionData, df: pd.DataFrame, tokens: dict) -> None:
    """Hallazgos — barras de dimensiones + distribución + calidad por categoría + treemap."""
    from sections.calidad_pro import render_calidad_pro

    theme = tokens.get("theme", "dark")

    st.markdown("""
<section id="hallazgos" aria-labelledby="hallazgos-title">
  <div class="nl-section-intro nl-reveal">
    <span class="eyebrow">Panorama del catálogo</span>
    <h2 id="hallazgos-title" class="section-title">¿Cuál es el estado real?</h2>
    <p class="section-subtitle">
      Distribución de calidad dataset por dataset.
      Verde es confiable, rojo requiere intervención.
    </p>
  </div>
</section>
""", unsafe_allow_html=True)

    # ── Bloque de barras: análisis de ciencia de datos ──────────────────────
    st.markdown("""
<div class="nl-section-intro nl-reveal">
  <span class="eyebrow">Análisis de dimensiones</span>
  <h3 class="section-title">¿Dónde está el problema?</h3>
  <p class="section-subtitle">
    Desglose por dimensión ISO, nivel de calidad y categoría temática.
  </p>
</div>
""", unsafe_allow_html=True)

    col_dim, col_dist = st.columns([3, 2])
    with col_dim:
        st.plotly_chart(
            chart_dimensiones_promedio(df, theme),
            use_container_width=True,
        )
    with col_dist:
        st.plotly_chart(
            chart_distribucion_clasi(df, theme),
            use_container_width=True,
        )

    st.plotly_chart(
        chart_calidad_por_categoria(df, theme),
        use_container_width=True,
    )

    # ── Treemap + auditoría completa ────────────────────────────────────────
    render_calidad_pro(data, df, tokens)
