"""sections/charts_calidad.py — Gráficas de barras ISO 25012 para el catálogo NL 2026.

Cuatro funciones reutilizables que responden las preguntas clave de ciencia de datos:
- chart_dimensiones_promedio   → ¿Cuál dimensión ISO está peor?
- chart_distribucion_clasi     → ¿Cómo se distribuye la calidad?
- chart_calidad_por_categoria  → ¿Qué categorías temáticas son las más débiles?
- chart_top_bottom_orgs        → ¿Quién lidera y quién está en riesgo?

Chromatic rule: máximo 1 acento por gráfica (excepción: dimensiones usa per-bar tier).
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from config import UMBRAL_EXCELENTE, UMBRAL_GOBERNANZA
from styles.global_css import PLOTLY_THEMES, get_bar_layout

_DIM_COLS: list[tuple[str, str]] = [
    ("comp_completitud_global_pct", "Completitud"),
    ("acc_score_accuracy_pct",      "Exactitud"),
    ("cons_score_consistency_pct",  "Consistencia"),
    ("doc_score_documentation_pct", "Documentación"),
    ("uniq_score_uniqueness_pct",   "Unicidad"),
    ("open_score_openness_pct",     "Apertura"),
    ("time_score_timeliness_pct",   "Temporalidad"),
]

_TIER_ORDER: list[str] = ["Crítico", "Deficiente", "Aceptable", "Bueno", "Excelente"]


def _tier_color(val: float, t: dict) -> str:
    if val >= UMBRAL_EXCELENTE:
        return t["excellent"]
    if val >= UMBRAL_GOBERNANZA:
        return t["good"]
    return t["poor"]


def _shorten(name: str, n: int = 38) -> str:
    return name if len(name) <= n else name[: n - 1].rstrip() + "…"


def chart_dimensiones_promedio(df: pd.DataFrame, theme: str = "dark") -> go.Figure:
    """Barras horizontales: promedio de cada dimensión ISO, coloreadas por tier."""
    t = PLOTLY_THEMES.get(theme, PLOTLY_THEMES["dark"])

    means: list[tuple[str, float]] = [
        (label, float(df[col].mean()))
        for col, label in _DIM_COLS
        if col in df.columns
    ]
    means.sort(key=lambda x: x[1])  # ascendente → mejor queda arriba en horizontal

    labels = [m[0] for m in means]
    values = [m[1] for m in means]
    colors = [_tier_color(v, t) for v in values]

    layout = get_bar_layout(theme)
    layout.update({
        "title": {"text": "Dimensiones ISO — Promedio del Catálogo", "font": {"size": 14}},
        "xaxis": {
            "showgrid": True,
            "gridcolor": t["grid_color"],
            "griddash": "dot",
            "zeroline": False,
            "range": [0, 105],
            "color": t["font_color"],
        },
        "yaxis": {"showgrid": False, "zeroline": False, "color": t["font_color"]},
        "margin": {"l": 120, "r": 70, "t": 50, "b": 40},
        "height": 340,
        "showlegend": False,
    })

    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker_color=colors,
        text=[f"{v:.1f}%" for v in values],
        textposition="outside",
        cliponaxis=False,
    ))
    fig.update_layout(**layout)
    return fig


def chart_distribucion_clasi(df: pd.DataFrame, theme: str = "dark") -> go.Figure:
    """Barras verticales: conteo de datasets por nivel de clasificación."""
    t = PLOTLY_THEMES.get(theme, PLOTLY_THEMES["dark"])

    if "clasificacion" not in df.columns:
        # Devolver figura vacía pero ya con el layout de tema correcto
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor=t["paper_bgcolor"],
            plot_bgcolor=t["plot_bgcolor"],
            font=dict(family=t["font_family"], color=t["font_color"]),
        )
        return fig

    counts = df["clasificacion"].value_counts()
    labels = [lbl for lbl in _TIER_ORDER if lbl in counts.index]
    values = [int(counts[lbl]) for lbl in labels]

    def _cls_color(lbl: str) -> str:
        if lbl in ("Crítico", "Deficiente"):
            return t["poor"]
        if lbl == "Aceptable":
            return t["good"]
        return t["excellent"]

    colors = [_cls_color(lbl) for lbl in labels]

    layout = get_bar_layout(theme)
    layout.update({
        "title": {"text": "Datasets por Nivel de Calidad", "font": {"size": 14}},
        "xaxis": {"showgrid": False, "zeroline": False, "color": t["font_color"]},
        "yaxis": {
            "showgrid": True,
            "gridcolor": t["grid_color"],
            "griddash": "dot",
            "zeroline": False,
            "color": t["font_color"],
        },
        "margin": {"l": 40, "r": 40, "t": 50, "b": 60},
        "height": 340,
        "showlegend": False,
    })

    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker_color=colors,
        text=values,
        textposition="outside",
        cliponaxis=False,
    ))
    fig.update_layout(**layout)
    return fig


def chart_calidad_por_categoria(df: pd.DataFrame, theme: str = "dark") -> go.Figure:
    """Barras horizontales: score promedio por categoría temática — acento teal único."""
    t = PLOTLY_THEMES.get(theme, PLOTLY_THEMES["dark"])

    if "categoria" not in df.columns or "score_global" not in df.columns:
        return go.Figure()

    cat_scores = (
        df.groupby("categoria")["score_global"]
        .mean()
        .sort_values(ascending=True)
        .tail(10)
    )

    layout = get_bar_layout(theme)
    layout.update({
        "title": {"text": "Calidad Promedio por Categoría Temática", "font": {"size": 14}},
        "xaxis": {
            "showgrid": True,
            "gridcolor": t["grid_color"],
            "griddash": "dot",
            "zeroline": False,
            "range": [0, 105],
            "color": t["font_color"],
        },
        "yaxis": {"showgrid": False, "zeroline": False, "color": t["font_color"]},
        "margin": {"l": 170, "r": 70, "t": 50, "b": 40},
        "height": 380,
        "showlegend": False,
    })

    fig = go.Figure(go.Bar(
        x=cat_scores.values.tolist(),
        y=[_shorten(str(c), 42) for c in cat_scores.index],
        orientation="h",
        marker_color=t["excellent"],  # Chromatic rule: acento único
        text=[f"{v:.1f}%" for v in cat_scores.values],
        textposition="outside",
        cliponaxis=False,
    ))
    fig.update_layout(**layout)
    return fig


def chart_top_bottom_orgs(org_stats: pd.DataFrame, theme: str = "dark") -> go.Figure:
    """Barras horizontales: top 5 (teal) y bottom 5 (rose) por score global."""
    t = PLOTLY_THEMES.get(theme, PLOTLY_THEMES["dark"])

    if org_stats.empty or "score_global" not in org_stats.columns:
        return go.Figure()

    sorted_orgs = org_stats.sort_values("score_global", ascending=False).reset_index(drop=True)
    top5 = sorted_orgs.head(5).sort_values("score_global", ascending=True)
    bottom5 = sorted_orgs.tail(5).sort_values("score_global", ascending=True)

    combined = pd.concat([bottom5, top5], ignore_index=True)
    colors = [t["poor"]] * len(bottom5) + [t["excellent"]] * len(top5)

    layout = get_bar_layout(theme)
    layout.update({
        "title": {"text": "Líderes y Organizaciones en Riesgo", "font": {"size": 14}},
        "xaxis": {
            "showgrid": True,
            "gridcolor": t["grid_color"],
            "griddash": "dot",
            "zeroline": False,
            "range": [0, 105],
            "color": t["font_color"],
        },
        "yaxis": {"showgrid": False, "zeroline": False, "color": t["font_color"]},
        "margin": {"l": 190, "r": 70, "t": 50, "b": 40},
        "height": 420,
        "showlegend": False,
        "shapes": [
            # línea separadora entre bottom5 y top5
            dict(
                type="line",
                x0=0, x1=1, xref="paper",
                y0=len(bottom5) - 0.5, y1=len(bottom5) - 0.5,
                yref="y",
                line=dict(color=t["grid_color"], width=1, dash="dash"),
            )
        ],
    })

    fig = go.Figure(go.Bar(
        x=combined["score_global"].tolist(),
        y=[_shorten(str(n)) for n in combined["organizacion"]],
        orientation="h",
        marker_color=colors,
        text=[f"{v:.1f}%" for v in combined["score_global"]],
        textposition="outside",
        cliponaxis=False,
    ))
    fig.update_layout(**layout)
    return fig
