# sections/organizaciones.py
"""Sección Organizaciones — Heatmap de calidad por dependencia gubernamental.
Refactorizada para minimalismo y responsividad (Google Stitch).
"""

from __future__ import annotations

import html as _html
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config import UMBRAL_EXCELENTE, UMBRAL_GOBERNANZA
from styles.global_css import PLOTLY_THEMES, get_plotly_layout

_DIM_COLS = [
    ("comp_completitud_global_pct", "Completitud"),
    ("acc_score_accuracy_pct",      "Exactitud"),
    ("cons_score_consistency_pct",  "Consistencia"),
    ("uniq_score_uniqueness_pct",   "Unicidad"),
    ("time_score_timeliness_pct",   "Puntualidad"),
    ("doc_score_documentation_pct", "Documentación"),
    ("open_score_openness_pct",     "Apertura"),
]

_MAP_POSITIONS = [
    (22, 45), (30, 58), (18, 32), (38, 42), (14, 55),
    (45, 25), (26, 72), (12, 20), (50, 55), (35, 15),
]

def _tier(val: float) -> str:
    if val >= UMBRAL_EXCELENTE: return "excellent"
    if val >= UMBRAL_GOBERNANZA: return "good"
    return "poor"

def _tier_color_hex(val: float, theme: str = "dark") -> str:
    t = PLOTLY_THEMES.get(theme, PLOTLY_THEMES["dark"])
    if val >= UMBRAL_EXCELENTE: return t["excellent"]
    if val >= UMBRAL_GOBERNANZA: return t["good"]
    return t["poor"]

def _shorten_name(name: str, max_len: int = 40) -> str:
    if len(name) <= max_len: return name
    return name[:max_len - 2].rstrip() + "…"

def _build_org_stats(df: pd.DataFrame) -> pd.DataFrame:
    agg_dict = {"n_datasets": ("dataset", "count"), "score_global": ("score_global", "mean")}
    for col, _ in _DIM_COLS:
        if col in df.columns: agg_dict[col] = (col, "mean")
    stats = df.groupby("organizacion", as_index=False).agg(**agg_dict)
    return stats.sort_values("score_global", ascending=False).reset_index(drop=True).round(1)

def _render_org_kpis(stats: pd.DataFrame) -> None:
    n_orgs = len(stats)
    avg_score = stats["score_global"].mean()
    n_excellent = int((stats["score_global"] >= UMBRAL_EXCELENTE).sum())
    n_poor = int((stats["score_global"] < UMBRAL_GOBERNANZA).sum())

    kpis = [
        ("corporate_fare", "Dependencias", str(n_orgs), "neutral"),
        ("speed", "Salud Promedio", f"{avg_score:.1f}%", _tier(avg_score)),
        ("workspace_premium", "Excelencia", str(n_excellent), "excellent"),
        ("warning", "En Riesgo", str(n_poor), "poor" if n_poor > 0 else "excellent"),
    ]

    cols = st.columns(4)
    for i, (icon, label, value, cls) in enumerate(kpis):
        with cols[i]:
            st.markdown(f'<div class="kpi-card {cls}"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>', unsafe_allow_html=True)

def _render_mapa_visual(stats: pd.DataFrame, theme: str) -> None:
    avg_score = stats["score_global"].mean()
    highlighted = pd.concat([stats.head(4), stats.tail(2)]).reset_index(drop=True)
    overlays_html = ""
    for idx, (_, row) in enumerate(highlighted.iterrows()):
        if idx >= len(_MAP_POSITIONS): break
        top, left = _MAP_POSITIONS[idx]
        name = _html.escape(_shorten_name(str(row["organizacion"]), 18))
        score = row["score_global"]
        color = _tier_color_hex(score, theme)
        overlays_html += f'<div class="map-overlay" style="top:{top}%; left:{left}%;"><div class="map-dot" style="background:{color}"></div><div class="map-tooltip"><strong>{name}</strong><br>{score:.1f}%</div></div>'

    nl_map_url = "https://images.unsplash.com/photo-1564790242166-6a0928c13e9e?w=1400&q=80"
    st.markdown(f"""
    <div class="editorial-container">
        <h2 class="section-title">Distribución de Calidad</h2>
        <p class="section-subtitle">Mapa visual del desempeño por dependencia estatal.</p>
    </div>
    <div class="stitch-map-container fade-up">
        <img src="{nl_map_url}" class="map-bg">
        <div class="map-scrim"></div>
        {overlays_html}
        <div class="map-central-card">
            <div class="kpi-label">Promedio de Salud</div>
            <div class="kpi-value" style="color:var(--teal-light)">{avg_score:.1f}%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_organizaciones(df: pd.DataFrame, tokens: dict) -> None:
    theme = tokens.get("theme", "dark")
    if "organizacion" not in df.columns: return
    stats = _build_org_stats(df)
    
    st.markdown('<div class="editorial-header fade-up"><div class="eyebrow">Instituciones Públicas</div><h1 class="editorial-title">Ranking Organizacional</h1></div>', unsafe_allow_html=True)
    
    _render_org_kpis(stats)
    st.write("")
    _render_mapa_visual(stats, theme)
    
    tab_rank, tab_table = st.tabs(["Ranking Visual", "Tabla Detallada"])
    with tab_rank:
        t = PLOTLY_THEMES.get(theme, PLOTLY_THEMES["dark"])
        top_stats = stats.head(15)
        fig = go.Figure(go.Bar(y=[_shorten_name(n, 30) for n in top_stats["organizacion"]], x=top_stats["score_global"], orientation="h", marker_color=[_tier_color_hex(v, theme) for v in top_stats["score_global"]]))
        fig.update_layout(**get_plotly_layout(theme), height=500, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    with tab_table:
        st.dataframe(stats, use_container_width=True, hide_index=True)
