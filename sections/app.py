"""Orquestador de la página única scrollable.

Invoca las 5 secciones verticales en orden. Cada render_* produce un
<section id="..."> que la topbar referencia vía anchors (#inicio,
#desarrollo, #dashboards, #conclusiones, #footer).
"""

from __future__ import annotations

import pandas as pd
import streamlit as st


def render(df: pd.DataFrame, tokens: dict) -> None:
    """Renderiza la página completa en orden vertical."""
    from sections.conclusiones import render_conclusiones
    from sections.dashboards import render_dashboards
    from sections.desarrollo import render_desarrollo
    from sections.footer import render_footer
    from sections.inicio import render_inicio

    # 1 · Inicio (hero + KPIs + salud del catálogo)
    st.markdown('<a id="inicio" class="nl-anchor"></a>', unsafe_allow_html=True)
    render_inicio(df, tokens)

    # 2 · Desarrollo (metodología + pipeline + universo)
    st.markdown(
        '<div class="nl-section-break" role="separator" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )
    render_desarrollo(df, tokens)

    # 3 · Dashboards y Métricas (visualizaciones live)
    st.markdown(
        '<div class="nl-section-break" role="separator" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )
    render_dashboards(df, tokens)

    # 4 · Conclusiones (hallazgos + recomendaciones derivadas)
    st.markdown(
        '<div class="nl-section-break" role="separator" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )
    render_conclusiones(df, tokens)

    # 5 · Footer (docs + referencias + créditos)
    render_footer(tokens)
