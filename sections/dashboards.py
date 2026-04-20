"""Sección Dashboards y Métricas — wrapper que compone los gráficos reales.

Reutiliza render_calidad_pro (pipeline + heatmaps + sunburst + tabla maestra),
render_organizaciones (heatmap org × dim + top orgs), y render_alertas
(panel de fallos + datasets bajo umbral). Todo conectado a data_layer,
sin datos simulados.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st


def render_dashboards(df: pd.DataFrame, tokens: dict) -> None:
    """Sección Dashboards — compone métricas live del pipeline."""
    from sections.calidad_pro import render_calidad_pro
    from sections.datasets import render_alertas
    from sections.organizaciones import render_organizaciones

    st.markdown("""
    <section id="dashboards" class="nl-section" aria-labelledby="dashboards-title">
        <span class="eyebrow">03 · Dashboards y Métricas</span>
        <h2 id="dashboards-title" class="hero-title nl-section-title">
            Visualización <em>live</em> del pipeline
        </h2>
        <p class="hero-subtitle nl-section-subtitle">
            Cobertura, dimensiones, organizaciones y alertas críticas — todo
            alimentado desde la última ejecución del pipeline.
        </p>
    </section>
    """, unsafe_allow_html=True)

    # ── Bloque 1 — Calidad Pro (cobertura + dimensiones + radial + tabla) ─
    render_calidad_pro(df, tokens)

    # ── Bloque 2 — Organizaciones (heatmap + top orgs) ──────────────────
    st.markdown(
        '<div class="nl-section-break" role="separator" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )
    render_organizaciones(df, tokens)

    # ── Bloque 3 — Alertas críticas + fallos de extracción ─────────────
    st.markdown(
        '<div class="nl-section-break" role="separator" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )
    st.markdown("""
    <header class="nl-subsection-header">
        <span class="eyebrow">03.3</span>
        <h3 class="section-title">Alertas críticas & trazabilidad del pipeline</h3>
    </header>
    """, unsafe_allow_html=True)
    render_alertas(df, tokens)
