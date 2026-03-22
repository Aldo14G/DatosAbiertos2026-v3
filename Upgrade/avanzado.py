# sections/avanzado.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

_DIM_COLS = {
    "comp_completitud_global_pct": "Completitud",
    "acc_score_accuracy_pct":      "Exactitud",
    "cons_score_consistency_pct":  "Consistencia",
    "uniq_score_uniqueness_pct":   "Unicidad",
    "time_score_timeliness_pct":   "Puntualidad",
}

_LAYOUT_BASE = dict(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="Inter, sans-serif", size=12, color="#3c4043"),
    margin=dict(l=50, r=30, t=40, b=50),
)


def _badge(val: float) -> tuple[str, str]:
    """Devuelve (texto_badge, color_class) según el valor del score."""
    if val >= 90: return ("OPTIMAL",  "tertiary")
    if val >= 70: return ("STABLE",   "secondary")
    if val >= 50: return ("REGULAR",  "primary")
    return              ("CRITICAL", "error")


def render_gauge_svg(value: float, label: str,
                     badge_text: str, color_class: str) -> str:
    """
    Gauge SVG circular replicando el diseño Stitch.
    El valor y badge se calculan dinámicamente desde el DataFrame.
    """
    _colors = {
        "tertiary" : ("#006d2a", "rgba(0,109,42,0.10)",  "#006d2a"),
        "secondary": ("#2a5bb3", "rgba(42,91,179,0.10)", "#2a5bb3"),
        "primary"  : ("#005bbf", "rgba(0,91,191,0.10)",  "#005bbf"),
        "error"    : ("#ba1a1a", "rgba(186,26,26,0.10)", "#ba1a1a"),
    }
    stroke, badge_bg, badge_fg = _colors.get(color_class, _colors["primary"])
    dasharray = f"{min(value, 100):.1f}, 100"

    return f"""
    <div style="background:#f4f3f7;border-radius:12px;padding:24px;
                display:flex;flex-direction:column;align-items:center;
                border:1px solid transparent;transition:border-color 0.2s"
         onmouseover="this.style.borderColor='#dadce0'"
         onmouseout="this.style.borderColor='transparent'">
        <span style="font-size:11px;font-weight:700;text-transform:uppercase;
                     letter-spacing:0.1em;color:#414754;margin-bottom:16px;
                     text-align:center">{label}</span>
        <div style="position:relative;width:120px;height:120px;margin-bottom:16px">
            <svg style="width:100%;height:100%;transform:rotate(-90deg)"
                 viewBox="0 0 36 36">
                <circle cx="18" cy="18" r="15.9155"
                    fill="none" stroke="#e3e2e6" stroke-width="3"/>
                <circle cx="18" cy="18" r="15.9155"
                    fill="none" stroke="{stroke}" stroke-width="3"
                    stroke-dasharray="{dasharray}"
                    stroke-linecap="round"/>
            </svg>
            <div style="position:absolute;inset:0;display:flex;align-items:center;
                        justify-content:center">
                <span style="font-size:22px;font-weight:700;color:#1a1b1e">
                    {value:.0f}%
                </span>
            </div>
        </div>
        <span style="padding:4px 12px;border-radius:9999px;font-size:11px;
                     font-weight:700;background:{badge_bg};color:{badge_fg}">
            {badge_text}
        </span>
    </div>
    """


def render_avanzado(df: pd.DataFrame, tokens: dict):
    """Pantalla 6: Análisis de Data Science — gauges dinámicos, correlación, scatter."""

    st.markdown("""
    <h2 style="font-size:40px;font-weight:800;letter-spacing:-0.02em;
               font-family:'Plus Jakarta Sans',sans-serif;color:#1a1b1e;margin-bottom:8px">
        Análisis de Data Science
    </h2>
    <p style="color:#414754;max-width:640px;margin-bottom:32px">
        Diagnóstico estadístico de gobernanza: dispersión, correlaciones y outliers.
    </p>
    """, unsafe_allow_html=True)

    # ── Gauges — valores leídos del DataFrame ─────────────────
    dims_ok = {k: v for k, v in _DIM_COLS.items() if k in df.columns}
    if dims_ok:
        gauge_cols = st.columns(len(dims_ok))
        for i, (col_key, label) in enumerate(dims_ok.items()):
            series = df[col_key].dropna()
            val    = round(series.mean(), 1) if not series.empty else 0.0
            btxt, bclass = _badge(val)
            gauge_cols[i].markdown(
                render_gauge_svg(val, label.upper(), btxt, bclass),
                unsafe_allow_html=True,
            )

    st.markdown(
        "<hr style='border:none;border-top:1px solid rgba(193,198,214,0.3);"
        "margin:40px 0;'>",
        unsafe_allow_html=True,
    )

    # ── Correlación de dimensiones ────────────────────────────
    st.markdown(
        '<h3 style="font-size:20px;font-weight:600;color:#1a1b1e;margin-bottom:6px">'
        'Correlación de Dimensiones ISO 25012</h3>'
        '<p style="color:#414754;margin-bottom:16px">'
        'Relación estadística entre dimensiones. '
        'Rojo = correlación negativa · Azul = correlación positiva.</p>',
        unsafe_allow_html=True,
    )

    quality_cols = [k for k in _DIM_COLS if k in df.columns]
    if "score_global" in df.columns:
        quality_cols.append("score_global")

    if len(quality_cols) > 1:
        rename_map = {**_DIM_COLS, "score_global": "Score Global"}
        df_corr = df[quality_cols].rename(columns=rename_map).corr()

        fig_corr = px.imshow(
            df_corr,
            text_auto=".2f",
            aspect="auto",
            color_continuous_scale="RdBu",
            zmin=-1, zmax=1,
        )
        fig_corr.update_layout(
            **_LAYOUT_BASE,
            height=420,
            coloraxis_colorbar=dict(title="r", tickvals=[-1, -0.5, 0, 0.5, 1]),
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("Se necesitan al menos 2 columnas numéricas para calcular correlaciones.")

    st.markdown(
        "<hr style='border:none;border-top:1px solid rgba(193,198,214,0.3);"
        "margin:40px 0;'>",
        unsafe_allow_html=True,
    )

    # ── Scatter: tamaño del dataset vs score ──────────────────
    st.markdown(
        '<h3 style="font-size:20px;font-weight:600;color:#1a1b1e;margin-bottom:6px">'
        'Tamaño del Dataset vs Score de Calidad</h3>'
        '<p style="color:#414754;margin-bottom:16px">'
        '¿Los datasets más grandes tienen mejor o peor calidad? '
        'Cada punto representa un dataset (escala logarítmica en X).</p>',
        unsafe_allow_html=True,
    )

    if "filas" in df.columns and "score_global" in df.columns:
        df_sc = df[["filas", "score_global", "dataset", "categoria"]].dropna()
        if not df_sc.empty:
            fig_sc = px.scatter(
                df_sc,
                x="filas",
                y="score_global",
                color="categoria",
                hover_data={
                    "dataset":      True,
                    "filas":        True,
                    "score_global": ":.1f",
                    "categoria":    False,
                },
                labels={
                    "filas":        "Número de filas (log)",
                    "score_global": "Score Global (%)",
                    "categoria":    "Categoría",
                },
                log_x=True,
            )
            fig_sc.add_hline(
                y=70,
                line_dash="dash", line_color="#d93025", line_width=1.5,
                annotation_text="Umbral 70%",
                annotation_font_color="#d93025",
                annotation_font_size=11,
            )
            fig_sc.update_layout(
                **_LAYOUT_BASE,
                height=420,
                yaxis=dict(ticksuffix="%", gridcolor="#f1f3f4", range=[0, 105]),
                xaxis=dict(gridcolor="#f1f3f4"),
                legend=dict(title="Categoría", font=dict(size=11)),
            )
            st.plotly_chart(fig_sc, use_container_width=True)
        else:
            st.info("No hay datos suficientes para el gráfico de dispersión.")
    else:
        st.info("Columnas `filas` o `score_global` no disponibles.")
