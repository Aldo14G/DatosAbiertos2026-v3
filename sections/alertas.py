"""Sección Alertas — Datasets bajo umbral que requieren atención inmediata.

Bloque 4 del narrative flow: responde "¿qué está roto ahora mismo?" con
el conteo crítico y tarjetas de alerta con recomendaciones por dimensión.
"""
from __future__ import annotations

import html as _html

import pandas as pd
import streamlit as st

from section_data import SectionData


def render_alertas_section(data: SectionData, df: pd.DataFrame, tokens: dict) -> None:
    """Alertas — conteo crítico y tarjetas accionables."""
    from sections.datasets import render_alertas

    n_below = data.n_critical
    count_html = (
        f'<strong>{_html.escape(str(n_below))}</strong> datasets requieren atención inmediata.'
        if n_below > 0
        else "No se detectaron datasets en estado crítico en esta evaluación."
    )

    st.markdown(f"""
<section id="alertas" aria-labelledby="alertas-title">
  <div class="nl-section-intro nl-reveal">
    <span class="eyebrow">Zonas de riesgo</span>
    <h2 id="alertas-title" class="section-title">¿Qué está roto ahora mismo?</h2>
    <p class="section-subtitle">{count_html}</p>
  </div>
</section>
""", unsafe_allow_html=True)

    render_alertas(data, df, tokens)
