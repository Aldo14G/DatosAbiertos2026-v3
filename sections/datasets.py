# sections/datasets.py
# INSTRUCCIONES AL AGENTE:
# La tabla de Stitch tiene estas columnas con estilo exacto:
#   - Dataset: font-bold, hover→color primary, subtítulo "Actualizado X"
#   - Categoría: badge pill (bg surface-highest, border outline-variant)
#   - Score: barra mini (w-12 h-1.5) + número bold
#   - Filas: font-mono, text-right

import streamlit as st
import pandas as pd
from data_layer import apply_filters

def render_score_bar_html(score: float) -> str:
    """
    Barra inline de score del Explorador (extraída de Stitch):
    """
    from sections.categorias import score_to_color
    color = score_to_color(score)
    return f"""
    <div style="display:flex;align-items:center;justify-content:center;gap:8px">
        <div style="width:48px;height:6px;background:rgba(193,198,214,0.3);
                    border-radius:9999px;overflow:hidden">
            <div style="width:{min(score,100):.0f}%;height:100%;background:{color}"></div>
        </div>
        <span style="font-size:12px;font-weight:700;color:#1a1b1e">{score:.0f}</span>
    </div>"""


def render_datasets(df: pd.DataFrame, tokens: dict):
    """
    Pantalla 3: Explorador de Datasets
    Fuente Stitch: 03_explorador-de-datasets_desktop.html

    REGLA: usar st.dataframe con column_config para replicar el estilo.
    El filter bar va arriba con st.columns(), igual que en Stitch.
    """
    st.markdown("""
    <h2 style="font-size:40px;font-weight:800;letter-spacing:-0.02em;
               font-family:'Plus Jakarta Sans',sans-serif;color:#1a1b1e;margin-bottom:8px">
        Explorador de Datasets
    </h2>
    <p style="color:#414754;max-width:640px;margin-bottom:32px">
        Visualiza y analiza la integridad de los activos de datos abiertos del Estado de NL.
    </p>
    """, unsafe_allow_html=True)

    # ── Filter Bar (replicar grid de Stitch) ─────────────────
    with st.container():
        st.markdown('<div style="background:#f4f3f7;border-radius:12px;padding:24px;border:1px solid rgba(193,198,214,0.3)">', unsafe_allow_html=True)
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1:
            cats = ["Todas"] + sorted(df["categoria"].dropna().unique().tolist())
            cat_filter = st.selectbox("Categoría", cats, label_visibility="visible")
        with fc2:
            orgs = ["Todas"] + sorted(df["organizacion"].dropna().unique().tolist())
            org_filter = st.selectbox("Organización", orgs, label_visibility="visible")
        with fc3:
            score_range = st.slider("Score Mínimo", 0, 100, 0,
                                    label_visibility="visible")
        with fc4:
            search = st.text_input("Buscar dataset...", label_visibility="collapsed",
                                   placeholder="Buscar dataset...")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Aplicar filtros ───────────────────────────────────────
    df_f = apply_filters(df, 
                         categorias=[cat_filter] if cat_filter != "Todas" else None, 
                         organizaciones=[org_filter] if org_filter != "Todas" else None, 
                         score_min=score_range)
    if search:
        df_f = df_f[df_f["dataset"].str.contains(search, case=False, na=False)]

    # ── Result count ──────────────────────────────────────────
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;
                align-items:center;margin-bottom:20px;margin-top:20px">
        <div style="display:flex;align-items:center;gap:8px">
            <span style="font-size:18px;font-weight:700;color:#1a1b1e">{len(df_f)}</span>
            <span style="color:#414754;font-weight:500">datasets encontrados</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabla (replicar estilo Stitch con column_config) ──────
    display_cols = {
        "dataset"                     : "Dataset",
        "categoria"                   : "Categoría",
        "organizacion"                : "Organización",
        "filas"                       : "Filas",
        "comp_completitud_global_pct" : "Completitud",
        "acc_score_accuracy_pct"      : "Exactitud",
        "cons_score_consistency_pct"  : "Consistencia",
        "uniq_score_uniqueness_pct"   : "Unicidad",
        "score_global"                : "Score",
    }
    cols_ok = [c for c in display_cols.keys() if c in df_f.columns]
    df_show = df_f[cols_ok].rename(columns=display_cols)

    # Aplicamos format %.1f a las columnas numéricas que correspondan para no romper
    if not df_show.empty:
        st.dataframe(
            df_show,
            use_container_width=True,
            height=520,
            column_config={
                "Score": st.column_config.ProgressColumn(
                    "Score Global",
                    min_value=0, max_value=100,
                    format="%.1f%%",
                ),
                "Filas": st.column_config.NumberColumn(format="%d"),
            },
            hide_index=True,
        )

    # ── Bottom Bar (replicar export row de Stitch) ─────────────
    st.markdown("<hr style='border:none;border-top:1px solid rgba(193,198,214,0.3);margin:24px 0'>", unsafe_allow_html=True)
    bc1, bc2, bc3 = st.columns([1, 1, 3])
    with bc1:
        csv_data = df_f.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Descargar CSV",
            csv_data,
            "datasets_nl_2026.csv", "text/csv",
        )
    with bc2:
        if st.button("Copiar JSON"):
            st.toast("JSON visualizado o copiado internamente")
