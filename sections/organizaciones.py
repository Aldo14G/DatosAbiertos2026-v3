# sections/organizaciones.py
"""Sección Organizaciones — Heatmap de calidad por dependencia gubernamental.
Refactorizada para minimalismo y responsividad (Google Stitch).
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config import UMBRAL_EXCELENTE, UMBRAL_GOBERNANZA
from data_layer import agg_org_stats
from styles.global_css import PLOTLY_THEMES, get_plotly_layout


def _tier(val: float) -> str:
    if val >= UMBRAL_EXCELENTE:
        return "excellent"
    if val >= UMBRAL_GOBERNANZA:
        return "good"
    return "poor"

def _tier_color_hex(val: float, theme: str = "dark") -> str:
    t = PLOTLY_THEMES.get(theme, PLOTLY_THEMES["dark"])
    if val >= UMBRAL_EXCELENTE:
        return t["excellent"]
    if val >= UMBRAL_GOBERNANZA:
        return t["good"]
    return t["poor"]

def _shorten_name(name: str, max_len: int = 40) -> str:
    if len(name) <= max_len:
        return name
    return name[:max_len - 2].rstrip() + "…"


def _render_org_kpis(stats: pd.DataFrame) -> None:
    n_orgs = len(stats)
    avg_score = stats["score_global"].mean()
    n_excellent = int((stats["score_global"] >= UMBRAL_EXCELENTE).sum())
    n_poor = int((stats["score_global"] < UMBRAL_GOBERNANZA).sum())
    tier_cls = _tier(avg_score)
    poor_cls = " rose" if n_poor > 0 else ""

    st.markdown(f"""
<div class="nl-org-summary nl-reveal">
    <div class="nl-org-summary-primary">
        <span class="nl-org-summary-score {tier_cls}">{avg_score:.1f}%</span>
        <span class="nl-org-summary-caption">Salud Promedio</span>
    </div>
    <div class="nl-org-summary-sep" aria-hidden="true"></div>
    <div class="nl-org-summary-stats">
        <div class="nl-org-summary-stat">
            <span class="nl-org-summary-stat-value teal">{n_excellent}</span>
            <span class="nl-org-summary-stat-label">Excelentes</span>
        </div>
        <div class="nl-org-summary-stat">
            <span class="nl-org-summary-stat-value{poor_cls}">{n_poor}</span>
            <span class="nl-org-summary-stat-label">En riesgo</span>
        </div>
        <div class="nl-org-summary-stat">
            <span class="nl-org-summary-stat-value">{n_orgs}</span>
            <span class="nl-org-summary-stat-label">Dependencias</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


def render_organizaciones(df: pd.DataFrame, tokens: dict) -> None:
    theme = tokens.get("theme", "dark")
    if "organizacion" not in df.columns:
        return
    stats = agg_org_stats(df)

    st.markdown('<div class="editorial-header fade-up"><div class="eyebrow">Instituciones Públicas</div><h2 class="editorial-title">Ranking Organizacional</h2></div>', unsafe_allow_html=True)

    _render_org_kpis(stats)
    st.write("")


    tab_rank, tab_table = st.tabs(["Ranking Visual", "Tabla Detallada"])
    with tab_rank:
        chart_height = max(500, len(stats) * 26 + 80)
        fig = go.Figure(go.Bar(
            y=[_shorten_name(n, 35) for n in stats["organizacion"]],
            x=stats["score_global"],
            orientation="h",
            marker_color=[_tier_color_hex(v, theme) for v in stats["score_global"]],
        ))
        fig.update_layout(
            **get_plotly_layout(theme),
            height=chart_height,
            yaxis=dict(autorange="reversed"),
            transition=dict(duration=600, easing="cubic-in-out"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab_table:
        st.dataframe(stats, use_container_width=True, hide_index=True)
