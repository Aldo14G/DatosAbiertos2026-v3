# sections/categorias.py
import streamlit as st
import pandas as pd


def _score_color(score: float) -> str:
    if score >= 90: return "#1e8e3e"
    if score >= 70: return "#e37400"
    return "#d93025"


def _score_tier(score: float) -> str:
    if score >= 90: return "excellent"
    if score >= 70: return "good"
    return "poor"


# Dimensiones en orden de visualización
_DIM_MAP = {
    "Completitud":  "comp_completitud_global_pct",
    "Exactitud":    "acc_score_accuracy_pct",
    "Consistencia": "cons_score_consistency_pct",
    "Unicidad":     "uniq_score_uniqueness_pct",
    "Puntualidad":  "time_score_timeliness_pct",
    "Score Global": "score_global",
}


def render_heatmap_table(df_agg: pd.DataFrame, counts: pd.Series) -> str:
    """
    Tabla HTML heatmap replicando el diseño Stitch.
    Incluye columna de recuento y dimensión de Puntualidad.
    Solo muestra columnas disponibles en el DataFrame.
    """
    dim_ok = {k: v for k, v in _DIM_MAP.items() if v in df_agg.columns}

    # ── Header ────────────────────────────────────────────────
    col_names = ["Categoría", "Datasets"] + list(dim_ok.keys())
    headers = ""
    for col in col_names:
        is_score  = col == "Score Global"
        is_left   = col in ("Categoría", "Datasets")
        width_css = "width:240px;" if col == "Categoría" else ""
        bg_css    = "background:#efedf1;" if is_score else ""
        headers += (
            f'<th style="padding:16px 24px;font-size:13px;font-weight:700;'
            f'color:#414754;text-transform:uppercase;letter-spacing:0.06em;'
            f'text-align:{"left" if is_left else "center"};{width_css}{bg_css}">'
            f'{col}</th>'
        )

    # ── Rows ──────────────────────────────────────────────────
    rows_html = ""
    sort_col  = "score_global" if "score_global" in df_agg.columns else df_agg.columns[-1]
    for _, row in df_agg.sort_values(sort_col, ascending=False).iterrows():
        cat   = row["categoria"]
        count = int(counts.get(cat, 0))

        cells = (
            f'<td style="padding:16px 24px;font-weight:700;color:#1a1b1e;'
            f'font-size:14px">{cat}</td>'
            f'<td style="padding:16px 24px;text-align:center">'
            f'<span style="background:#f4f3f7;padding:2px 10px;border-radius:9999px;'
            f'font-size:12px;font-weight:600;color:#414754">{count}</span></td>'
        )

        for col_name, col_key in dim_ok.items():
            val   = float(row.get(col_key, 0) or 0)
            color = _score_color(val)

            if col_name == "Score Global":
                tier = _score_tier(val)
                t_color = {"excellent": "#005bbf", "good": "#1a1b1e", "poor": "#ba1a1a"}[tier]
                bg_col  = {"excellent": "rgba(26,115,232,0.05)",
                           "good":      "#f4f3f7",
                           "poor":      "#ffdad6"}[tier]
                cells += (
                    f'<td style="padding:16px 24px;text-align:center;'
                    f'font-size:18px;font-weight:900;color:{t_color};'
                    f'background:{bg_col}">{val:.1f}</td>'
                )
            else:
                cells += f"""
                <td style="padding:4px">
                    <div style="height:40px;display:flex;align-items:center;
                                justify-content:center;border-radius:4px;
                                background:{color};color:white;font-weight:700;
                                font-size:13px;transition:transform 0.2s;cursor:default"
                         onmouseover="this.style.transform='scale(1.05)'"
                         onmouseout="this.style.transform='scale(1)'">
                        {val:.0f}%
                    </div>
                </td>"""

        rows_html += (
            f'<tr style="border-bottom:1px solid rgba(193,198,214,0.1)">'
            f'{cells}</tr>'
        )

    return f"""
    <div style="background:white;border-radius:16px;
                border:1px solid rgba(193,198,214,0.4);overflow:hidden">
        <div style="overflow-x:auto">
            <table style="width:100%;border-collapse:collapse;text-align:left">
                <thead>
                    <tr style="background:#f4f3f7">{headers}</tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
    </div>
    """


def render_categorias(df: pd.DataFrame, tokens: dict):
    """Pantalla 2: Rendimiento por Categoría Temática."""

    col_title, col_legend = st.columns([2, 1])
    with col_title:
        st.markdown("""
        <h2 style="font-size:32px;font-weight:700;letter-spacing:-0.02em;
                   font-family:'Plus Jakarta Sans',sans-serif;color:#1a1b1e">
            Rendimiento por Categoría Temática
        </h2>
        <p style="color:#414754;margin-top:8px">
            Calidad de datos segmentada por pilares de gobernanza institucional.
        </p>
        """, unsafe_allow_html=True)

    with col_legend:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:20px;padding:12px 16px;
                    background:#f4f3f7;border-radius:12px;
                    border:1px solid rgba(193,198,214,0.2);float:right;margin-top:8px">
            <span style="display:flex;align-items:center;gap:6px;font-size:12px;
                         font-weight:500;color:#414754">
                <span style="width:10px;height:10px;border-radius:50%;
                             background:#d93025;display:inline-block"></span>&lt;70
            </span>
            <span style="display:flex;align-items:center;gap:6px;font-size:12px;
                         font-weight:500;color:#414754">
                <span style="width:10px;height:10px;border-radius:50%;
                             background:#e37400;display:inline-block"></span>70–89
            </span>
            <span style="display:flex;align-items:center;gap:6px;font-size:12px;
                         font-weight:500;color:#414754">
                <span style="width:10px;height:10px;border-radius:50%;
                             background:#1e8e3e;display:inline-block"></span>≥90
            </span>
        </div>
        """, unsafe_allow_html=True)

    # ── Filtros ───────────────────────────────────────────────
    fc1, fc2, fc3 = st.columns([3, 1, 1])
    with fc1:
        cats = sorted(df["categoria"].dropna().unique().tolist())
        selected = st.multiselect(
            "Filtrar", cats,
            placeholder="Todas las categorías",
            label_visibility="collapsed",
        )
    with fc3:
        only_alerts = st.toggle("Solo críticos (<70)", value=False)

    # ── Aplicar filtros ───────────────────────────────────────
    df_f = df.copy()
    if selected:
        df_f = df_f[df_f["categoria"].isin(selected)]
    if only_alerts:
        df_f = df_f[df_f["score_global"] < 70]

    if df_f.empty or "categoria" not in df_f.columns:
        st.info("No hay datos para los filtros seleccionados.")
        return

    # ── Agregar ───────────────────────────────────────────────
    dim_cols = [v for v in _DIM_MAP.values() if v in df_f.columns]
    counts   = df_f.groupby("categoria")["score_global"].count()
    df_agg   = df_f.groupby("categoria")[dim_cols].mean().round(1).reset_index()

    st.markdown(render_heatmap_table(df_agg, counts), unsafe_allow_html=True)
