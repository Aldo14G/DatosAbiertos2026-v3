"""Sección Dashboards y Métricas — wrapper que compone los gráficos reales.

Reutiliza render_calidad_pro (pipeline + heatmaps + sunburst + tabla maestra),
render_organizaciones (heatmap org × dim + top orgs), y render_alertas
(panel de fallos + datasets bajo umbral). Todo conectado a data_layer,
sin datos simulados.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from config import UMBRAL_GOBERNANZA


def _chart_insight(icon: str, text: str) -> None:
    """Renderiza un panel de insight contextual bajo un gráfico."""
    st.markdown(
        f'<div class="nl-chart-insight nl-reveal">'
        f'<span class="material-symbols-outlined nl-chart-insight-icon" aria-hidden="true">{icon}</span>'
        f'<p class="nl-chart-insight-text">{text}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_dashboards(df: pd.DataFrame, tokens: dict) -> None:
    """Sección Dashboards — compone métricas live del pipeline con narrativa ciudadana."""
    from sections.calidad_pro import render_calidad_pro
    from sections.datasets import render_alertas
    from sections.organizaciones import render_organizaciones

    # Métricas derivadas para los insights
    has_score = "score_global" in df.columns and not df.empty
    n_below      = int((df["score_global"] < UMBRAL_GOBERNANZA).sum()) if has_score else 0

    st.markdown("""
    <section id="dashboards" class="nl-section" aria-labelledby="dashboards-title">
        <span class="eyebrow">02 · Calidad en Tiempo Real</span>
        <h2 id="dashboards-title" class="section-title nl-section-title">
            Salud de los Datos Abiertos
        </h2>
    </section>

    <div class="editorial-container fade-up">
        <p>
            El <strong>Score de Calidad</strong> indica qué tan confiable es un dato.
            Buscamos el color <span class="accent-teal">Verde (Óptimo)</span>.
            El <span class="accent-rose">Rojo (Crítico)</span> avisa que el dato tiene fallas que impiden su uso.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Bloque 1 — Calidad Pro (cobertura + dimensiones + radial + tabla) ─
    render_calidad_pro(df, tokens)

    # [CLEANUP] Redundant insight removed as per user request

    # ── Bloque 2 — Organizaciones (heatmap + top orgs) ──────────────────
    st.markdown(
        '<div class="nl-section-break" role="separator" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )

    st.markdown("""
    <header class="nl-subsection-header">
        <span class="eyebrow">02.2 · Organizaciones</span>
        <h3 class="section-title">¿Quiénes publican mejor?</h3>
    </header>
    """, unsafe_allow_html=True)

    render_organizaciones(df, tokens)

    # ── Bloque 3 — Alertas críticas + fallos de extracción ─────────────
    st.markdown(
        '<div class="nl-section-break" role="separator" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )
    st.markdown("""
    <header class="nl-subsection-header">
        <span class="eyebrow">02.3 · Alertas</span>
        <h3 class="section-title">Zonas de Riesgo y Alertas</h3>
    </header>
    <p class="section-subtitle mb-4">Identificamos automáticamente los conjuntos de datos que requieren atención inmediata por parte de las dependencias.</p>
    """, unsafe_allow_html=True)

    if n_below > 0:
        _chart_insight(
            "warning",
            f"Existen <strong>{n_below}</strong> datasets que presentan inconsistencias críticas. Abajo encontrarás las tarjetas con las acciones recomendadas para cada uno.",
        )

    render_alertas(df, tokens)
