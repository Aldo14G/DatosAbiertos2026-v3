"""Sección Dashboards y Métricas — wrapper que compone los gráficos reales.

Reutiliza render_calidad_pro (pipeline + heatmaps + sunburst + tabla maestra),
render_organizaciones (heatmap org × dim + top orgs), y render_alertas
(panel de fallos + datasets bajo umbral). Todo conectado a data_layer,
sin datos simulados.
"""

from __future__ import annotations

import html as _html

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
    """Sección Dashboards — compone métricas live del pipeline."""
    from sections.calidad_pro import render_calidad_pro
    from sections.datasets import render_alertas
    from sections.organizaciones import render_organizaciones

    # Métricas derivadas para los insights
    has_score = "score_global" in df.columns and not df.empty
    score_mean   = float(df["score_global"].mean()) if has_score else 0.0
    n_total      = len(df)
    n_below      = int((df["score_global"] < UMBRAL_GOBERNANZA).sum()) if has_score else 0
    n_above      = n_total - n_below
    pct_above    = (n_above / n_total * 100) if n_total else 0.0

    n_orgs = int(df["organizacion"].nunique()) if "organizacion" in df.columns else 0

    dim_cols = [
        ("comp_completitud_global_pct", "Completitud"),
        ("acc_score_accuracy_pct",      "Exactitud"),
        ("cons_score_consistency_pct",  "Consistencia"),
        ("uniq_score_uniqueness_pct",   "Unicidad"),
        ("time_score_timeliness_pct",   "Puntualidad"),
        ("doc_score_documentation_pct", "Documentación"),
        ("open_score_openness_pct",     "Apertura"),
    ]
    weak_label = "N/A"
    weak_val   = 0.0
    for col, label in dim_cols:
        if col in df.columns:
            mean = float(df[col].mean())
            if mean < weak_val or weak_label == "N/A":
                weak_label, weak_val = label, mean

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

    _chart_insight(
        "insights",
        f"El catálogo registra un score promedio de <strong>{score_mean:.1f}%</strong>. "
        f"<strong>{n_above}</strong> de {n_total} datasets ({pct_above:.0f}%) superan el "
        f"umbral de gobernanza. La dimensión con mayor oportunidad de mejora es "
        f"<strong>{_html.escape(weak_label)}</strong> ({weak_val:.1f}% promedio).",
    )

    # ── Bloque 2 — Organizaciones (heatmap + top orgs) ──────────────────
    st.markdown(
        '<div class="nl-section-break" role="separator" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )
    render_organizaciones(df, tokens)

    _chart_insight(
        "apartment",
        f"El catálogo agrupa datasets de <strong>{n_orgs}</strong> organizaciones distintas. "
        f"El heatmap superior identifica qué dependencias concentran las dimensiones de mayor "
        f"riesgo — priorizando ahí los esfuerzos de remediación se obtiene el mayor impacto "
        f"marginal sobre el score global.",
    )

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

    if n_below > 0:
        _chart_insight(
            "warning",
            f"<strong>{n_below}</strong> datasets están por debajo del umbral de gobernanza "
            f"({UMBRAL_GOBERNANZA:.0f}%). Cada tarjeta incluye recomendaciones específicas "
            f"por dimensión para orientar la remediación.",
        )

    render_alertas(df, tokens)
