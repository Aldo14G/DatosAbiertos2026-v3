# sections/categorias.py

import streamlit as st
import pandas as pd

def score_to_color(score: float) -> str:
    """Mapa de color semántico exacto del diseño Stitch."""
    if score >= 90: return "#1e8e3e"   # --excellent
    if score >= 70: return "#e37400"   # --good
    return "#d93025"                    # --poor

def score_to_tier(score: float) -> str:
    if score >= 90: return "excellent"
    if score >= 70: return "good"
    return "poor"

def render_heatmap_table(df_agg: pd.DataFrame) -> str:
    """
    Genera la tabla HTML del heatmap replicando EXACTAMENTE el diseño Stitch.

    Dimensiones que muestra (extraídas del thead de Stitch):
        Completitud | Exactitud | Consistencia | Unicidad | Score Global
    """
    dim_map = {
        "Completitud":  "comp_completitud_global_pct",
        "Exactitud":    "acc_score_accuracy_pct",
        "Consistencia": "cons_score_consistency_pct",
        "Unicidad":     "uniq_score_uniqueness_pct",
        "Score Global": "score_global",
    }

    # ── Header ────────────────────────────────────────────────
    headers = "".join([
        f'<th style="padding:16px 24px;font-size:13px;font-weight:700;'
        f'color:#414754;text-transform:uppercase;letter-spacing:0.06em;'
        f'text-align:{"left" if col=="Categoría" else "center"};'
        f'{"width:240px;" if col=="Categoría" else ""}'
        f'{"background:#efedf1;" if col=="Score Global" else ""}">'
        f'{col}</th>'
        for col in ["Categoría"] + list(dim_map.keys())
    ])

    # ── Rows ──────────────────────────────────────────────────
    rows_html = ""
    for _, row in df_agg.sort_values("score_global", ascending=False).iterrows():
        cells = f'<td style="padding:16px 24px;font-weight:700;color:#1a1b1e;font-size:14px">{row["categoria"]}</td>'

        for col_name, col_key in dim_map.items():
            val = row.get(col_key, 0) or 0
            color = score_to_color(val)

            if col_name == "Score Global":
                # Columna Score Global tiene estilo especial (ver Stitch)
                tier = score_to_tier(val)
                text_colors = {"excellent":"#005bbf","good":"#1a1b1e","poor":"#ba1a1a"}
                cells += f"""
                <td style="padding:16px 24px;text-align:center;
                           font-size:18px;font-weight:900;
                           color:{text_colors[tier]};
                           background:{'rgba(26,115,232,0.05)' if tier=='excellent' else '#ffdad6' if tier=='poor' else '#f4f3f7'}">
                    {val:.1f}
                </td>"""
            else:
                # Celda heatmap con div coloreado (EXACTO del Stitch)
                cells += f"""
                <td style="padding:4px">
                    <div style="height:40px;display:flex;align-items:center;
                                justify-content:center;border-radius:4px;
                                background:{color};color:white;font-weight:700;
                                font-size:13px;transition:transform 0.2s ease;
                                cursor:default"
                        onmouseover="this.style.transform='scale(1.05)'"
                        onmouseout="this.style.transform='scale(1)'">
                        {val:.0f}%
                    </div>
                </td>"""

        rows_html += f'<tr style="border-bottom:1px solid rgba(193,198,214,0.1)">{cells}</tr>'

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
    """
    Pantalla 2: Rendimiento por Categoría Temática
    Fuente Stitch: 10_rendimiento-por-categoria_desktop.html
    """
    # ── Header (replicar estructura de Stitch) ─────────────────
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
        <div style="display:flex;align-items:center;gap:24px;padding:12px;
                    background:#f4f3f7;border-radius:12px;
                    border:1px solid rgba(193,198,214,0.2);float:right">
            <div style="display:flex;align-items:center;gap:8px">
                <div style="width:12px;height:12px;border-radius:50%;background:#d93025"></div>
                <span style="font-size:12px;font-weight:500;color:#414754">Deficiente</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px">
                <div style="width:12px;height:12px;border-radius:50%;background:#e37400"></div>
                <span style="font-size:12px;font-weight:500;color:#414754">Regular</span>
            </div>
            <div style="display:flex;align-items:center;gap:8px">
                <div style="width:12px;height:12px;border-radius:50%;background:#1e8e3e"></div>
                <span style="font-size:12px;font-weight:500;color:#414754">Excelente</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Filter Bar (replicar filter bar de Stitch) ─────────────
    with st.container():
        fc1, fc2, fc3, fc4 = st.columns([2, 1, 1, 1])
        with fc1:
            cats = sorted(df["categoria"].dropna().unique().tolist())
            selected_cats = st.multiselect(
                "Filtrar por categoría",
                cats,
                placeholder="Todas las categorías",
                label_visibility="collapsed"
            )
        with fc4:
            only_alerts = st.toggle("Solo alertas", value=False)

    # ── Aplicar filtros ────────────────────────────────────────
    df_filtered = df.copy()
    if selected_cats:
        df_filtered = df_filtered[df_filtered["categoria"].isin(selected_cats)]
    if only_alerts:
        df_filtered = df_filtered[df_filtered["score_global"] < 70]

    # ── Agregar por categoría ──────────────────────────────────
    dim_cols = [
        "comp_completitud_global_pct",
        "acc_score_accuracy_pct",
        "cons_score_consistency_pct",
        "uniq_score_uniqueness_pct",
        "score_global",
    ]
    cols_ok = [c for c in dim_cols if c in df_filtered.columns]
    
    if "categoria" in df_filtered.columns and not df_filtered.empty:
        df_agg = (df_filtered.groupby("categoria")[cols_ok]
                              .mean().round(1).reset_index())
        df_agg.columns = ["categoria"] + cols_ok

        # ── Heatmap Table (HTML replicado de Stitch) ───────────────
        st.markdown(render_heatmap_table(df_agg), unsafe_allow_html=True)
    else:
        st.info("No hay datos para las categorías seleccionadas.")
