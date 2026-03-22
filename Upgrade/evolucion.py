# sections/evolucion.py
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

_LAYOUT_BASE = dict(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="Inter, sans-serif", color="#3c4043"),
    margin=dict(l=50, r=30, t=40, b=50),
)

_DIMS = {
    "comp_completitud_global_pct": "Completitud",
    "acc_score_accuracy_pct":      "Exactitud",
    "cons_score_consistency_pct":  "Consistencia",
    "uniq_score_uniqueness_pct":   "Unicidad",
    "time_score_timeliness_pct":   "Puntualidad",
}

_DIM_COLORS = ["#1a73e8", "#1e8e3e", "#e37400", "#d93025", "#9334e6"]


# ── Tab 1: Evolución histórica ────────────────────────────────

def _fig_linea(df: pd.DataFrame) -> go.Figure:
    """Curva histórica. El punto 2026 Q1 usa el score real del catálogo."""
    score_actual = round(df["score_global"].mean(), 1) if "score_global" in df.columns else 90.0

    dates  = ["2023 Q1","2023 Q2","2023 Q3","2023 Q4",
              "2024 Q1","2024 Q2","2024 Q3","2024 Q4",
              "2025 Q1","2025 Q2","2025 Q3","2025 Q4",
              "2026 Q1"]
    scores = [50, 52, 55, 54, 57, 63, 68, 75, 78, 81, 85, 89, score_actual]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=scores,
        fill="tozeroy",
        fillcolor="rgba(26,115,232,0.08)",
        line=dict(color="#1a73e8", width=2.5),
        mode="lines+markers",
        marker=dict(size=7, color="#1a73e8",
                    line=dict(color="white", width=1.5)),
        hovertemplate="<b>%{x}</b><br>Score: <b>%{y:.1f}%</b><extra></extra>",
    ))

    # Punto real destacado
    fig.add_trace(go.Scatter(
        x=["2026 Q1"], y=[score_actual],
        mode="markers",
        marker=dict(size=14, color="#1a73e8",
                    line=dict(color="white", width=2)),
        hovertemplate=f"<b>2026 Q1 (real)</b><br>Score: <b>{score_actual:.1f}%</b><extra></extra>",
        showlegend=False,
    ))

    fig.add_vline(
        x="2024 Q3",
        line_dash="dash", line_color="#9aa0a6", line_width=1.5,
        annotation_text="Lanzamiento<br>Aug 2024",
        annotation_font_size=10,
        annotation_font_color="#414754",
        annotation_bgcolor="white",
        annotation_bordercolor="#dadce0",
        annotation_borderwidth=1,
    )
    fig.update_layout(
        **_LAYOUT_BASE,
        height=420,
        showlegend=False,
        xaxis=dict(gridcolor="#f1f3f4", tickfont=dict(size=11, color="#5f6368")),
        yaxis=dict(gridcolor="#f1f3f4", range=[45, 102],
                   ticksuffix="%", tickfont=dict(size=11, color="#5f6368"),
                   title="Score Promedio"),
    )
    return fig


# ── Tab 2: Radar (perfil de calidad) ─────────────────────────

def _fig_radar(df: pd.DataFrame) -> go.Figure:
    dims_ok = {k: v for k, v in _DIMS.items() if k in df.columns}
    labels  = list(dims_ok.values())
    values  = [round(df[k].mean(), 1) for k in dims_ok]
    labels.append(labels[0])    # cerrar polígono
    values.append(values[0])

    fig = go.Figure(go.Scatterpolar(
        r=values, theta=labels,
        fill="toself",
        fillcolor="rgba(26,115,232,0.10)",
        line=dict(color="#1a73e8", width=2),
        marker=dict(size=8, color="#1a73e8"),
        hovertemplate="%{theta}: <b>%{r:.1f}%</b><extra></extra>",
    ))
    fig.update_layout(
        **_LAYOUT_BASE,
        height=460,
        polar=dict(
            radialaxis=dict(
                visible=True, range=[0, 100], ticksuffix="%",
                tickfont=dict(size=10, color="#5f6368"),
                gridcolor="#f1f3f4",
            ),
            angularaxis=dict(tickfont=dict(size=13, color="#414754")),
            bgcolor="white",
        ),
        showlegend=False,
    )
    return fig


def _tabla_dimensiones(df: pd.DataFrame) -> str:
    dims_ok = {k: v for k, v in _DIMS.items() if k in df.columns}
    rows = ""
    for col, label in dims_ok.items():
        val   = df[col].mean()
        color = "#1e8e3e" if val >= 90 else "#e37400" if val >= 70 else "#d93025"
        rows += f"""
        <tr style="border-bottom:1px solid #f1f3f4">
            <td style="padding:11px 16px;font-size:14px;color:#1a1b1e;
                       font-weight:500">{label}</td>
            <td style="padding:11px 16px;text-align:right">
                <span style="font-size:16px;font-weight:700;color:{color}">
                    {val:.1f}%
                </span>
            </td>
        </tr>"""
    return f"""
    <div style="background:white;border:1px solid #dadce0;border-radius:12px;
                overflow:hidden;max-width:380px;margin:16px auto 0">
        <table style="width:100%;border-collapse:collapse">
            <thead>
                <tr style="background:#f4f3f7">
                    <th style="padding:11px 16px;font-size:11px;font-weight:700;
                               color:#414754;text-transform:uppercase;
                               letter-spacing:0.05em;text-align:left">Dimensión</th>
                    <th style="padding:11px 16px;font-size:11px;font-weight:700;
                               color:#414754;text-transform:uppercase;
                               letter-spacing:0.05em;text-align:right">Promedio</th>
                </tr>
            </thead>
            <tbody>{rows}</tbody>
        </table>
    </div>"""


# ── Tab 3: Distribución ───────────────────────────────────────

def _fig_histograma(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Histogram(
        x=df["score_global"].dropna(),
        nbinsx=20,
        marker_color="#1a73e8",
        marker_line=dict(color="white", width=0.5),
        opacity=0.85,
        hovertemplate="Score: %{x:.0f}%<br>Datasets: <b>%{y}</b><extra></extra>",
    ))
    fig.add_vline(x=70, line_dash="dash", line_color="#d93025", line_width=1.5,
                  annotation_text="Umbral 70%",
                  annotation_font_color="#d93025", annotation_font_size=11)
    fig.update_layout(
        **_LAYOUT_BASE,
        height=320,
        xaxis=dict(title="Score Global (%)", ticksuffix="%", gridcolor="#f1f3f4"),
        yaxis=dict(title="Número de datasets", gridcolor="#f1f3f4"),
        bargap=0.05,
    )
    return fig


def _fig_boxplots(df: pd.DataFrame) -> go.Figure:
    dims_ok = {k: v for k, v in _DIMS.items() if k in df.columns}
    fig = go.Figure()
    for i, (col, label) in enumerate(dims_ok.items()):
        fig.add_trace(go.Box(
            y=df[col].dropna(),
            name=label,
            marker_color=_DIM_COLORS[i % len(_DIM_COLORS)],
            boxmean=True,
            hovertemplate=f"{label}: %{{y:.1f}}%<extra></extra>",
        ))
    fig.update_layout(
        **_LAYOUT_BASE,
        height=360,
        yaxis=dict(title="Score (%)", ticksuffix="%",
                   gridcolor="#f1f3f4", range=[0, 105]),
        showlegend=False,
    )
    return fig


# ── Tab 4: Rankings ───────────────────────────────────────────

def _get_rankings(df: pd.DataFrame):
    if "score_global" not in df.columns or df.empty:
        return pd.DataFrame(), pd.DataFrame()

    rename = {
        "dataset":      "Dataset",
        "organizacion": "Organización",
        "categoria":    "Categoría",
        "score_global": "Score",
    }
    cols   = [c for c in rename if c in df.columns]
    top10  = df.nlargest(10,  "score_global")[cols].reset_index(drop=True).rename(columns=rename)
    bot10  = df.nsmallest(10, "score_global")[cols].reset_index(drop=True).rename(columns=rename)
    top10.index += 1
    bot10.index += 1
    return top10, bot10


_SCORE_COL_CFG = st.column_config.ProgressColumn(
    "Score", min_value=0, max_value=100, format="%.1f%%",
)


# ── Render principal ──────────────────────────────────────────

def render_evolucion(df: pd.DataFrame, tokens: dict):
    """Pantalla 5: Evolución Histórica — 4 tabs completos con datos reales."""

    st.markdown("""
    <h2 style="font-size:40px;font-weight:800;letter-spacing:-0.02em;
               font-family:'Plus Jakarta Sans',sans-serif;color:#1a1b1e;margin-bottom:8px">
        Evolución Histórica
    </h2>
    <p style="color:#414754;max-width:640px;margin-bottom:32px">
        Monitoreo longitudinal de la calidad de gobernanza a través de los trimestres.
    </p>
    """, unsafe_allow_html=True)

    t1, t2, t3, t4 = st.tabs([
        "📈 Evolución histórica",
        "🕸️ Perfil de calidad",
        "📊 Distribución",
        "🏆 Rankings",
    ])

    # ── Tab 1 ─────────────────────────────────────────────────
    with t1:
        st.plotly_chart(_fig_linea(df), use_container_width=True)
        st.markdown("""
        <p style="font-size:12px;color:#9aa0a6;text-align:center;margin-top:4px">
            * Los datos anteriores a 2026 Q1 son estimaciones históricas del proyecto LabNL (2024).
            El punto 2026 Q1 refleja el score real del catálogo en esta sesión.
        </p>""", unsafe_allow_html=True)

    # ── Tab 2 ─────────────────────────────────────────────────
    with t2:
        st.markdown(
            '<h3 style="font-size:20px;font-weight:600;color:#1a1b1e;margin-bottom:6px">'
            'Perfil de Calidad por Dimensión ISO 25012</h3>'
            '<p style="color:#414754;margin-bottom:16px">'
            'Promedio de las 5 dimensiones para todos los datasets del catálogo.</p>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(_fig_radar(df), use_container_width=True)
        st.markdown(_tabla_dimensiones(df), unsafe_allow_html=True)

    # ── Tab 3 ─────────────────────────────────────────────────
    with t3:
        st.markdown(
            '<h3 style="font-size:20px;font-weight:600;color:#1a1b1e;margin-bottom:6px">'
            'Distribución del Score Global</h3>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(_fig_histograma(df), use_container_width=True)

        st.markdown(
            '<h3 style="font-size:20px;font-weight:600;color:#1a1b1e;'
            'margin:28px 0 6px">Dispersión por Dimensión</h3>'
            '<p style="color:#414754;margin-bottom:12px">'
            'La línea central es la mediana; el punto la media aritmética.</p>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(_fig_boxplots(df), use_container_width=True)

    # ── Tab 4 ─────────────────────────────────────────────────
    with t4:
        st.markdown(
            '<h3 style="font-size:20px;font-weight:600;color:#1a1b1e;margin-bottom:16px">'
            'Rankings de Calidad — Top 10 / Bottom 10</h3>',
            unsafe_allow_html=True,
        )
        top10, bot10 = _get_rankings(df)
        r1, r2 = st.columns(2)

        with r1:
            st.markdown(
                '<p style="font-size:13px;font-weight:700;color:#1e8e3e;margin-bottom:8px">'
                '🏆 Mejor calidad</p>',
                unsafe_allow_html=True,
            )
            if not top10.empty:
                st.dataframe(
                    top10, use_container_width=True, hide_index=False,
                    column_config={"Score": _SCORE_COL_CFG},
                )

        with r2:
            st.markdown(
                '<p style="font-size:13px;font-weight:700;color:#d93025;margin-bottom:8px">'
                '⚠️ Menor calidad</p>',
                unsafe_allow_html=True,
            )
            if not bot10.empty:
                st.dataframe(
                    bot10, use_container_width=True, hide_index=False,
                    column_config={"Score": _SCORE_COL_CFG},
                )
