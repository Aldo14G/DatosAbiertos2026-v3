# sections/datasets.py
import streamlit as st
import pandas as pd
from data_layer import apply_filters

_DISPLAY_COLS = {
    "dataset"                     : "Dataset",
    "categoria"                   : "Categoría",
    "organizacion"                : "Organización",
    "filas"                       : "Filas",
    "comp_completitud_global_pct" : "Completitud",
    "acc_score_accuracy_pct"      : "Exactitud",
    "cons_score_consistency_pct"  : "Consistencia",
    "uniq_score_uniqueness_pct"   : "Unicidad",
    "time_score_timeliness_pct"   : "Puntualidad",
    "score_global"                : "Score",
}

_PROGRESS_COLS = {
    "Completitud", "Exactitud", "Consistencia", "Unicidad", "Puntualidad",
}


def render_datasets(df: pd.DataFrame, tokens: dict):
    """Pantalla 3: Explorador de Datasets."""

    st.markdown("""
    <h2 style="font-size:40px;font-weight:800;letter-spacing:-0.02em;
               font-family:'Plus Jakarta Sans',sans-serif;color:#1a1b1e;margin-bottom:8px">
        Explorador de Datasets
    </h2>
    <p style="color:#414754;max-width:640px;margin-bottom:32px">
        Visualiza y analiza la integridad de los activos de datos abiertos del Estado de NL.
    </p>
    """, unsafe_allow_html=True)

    # ── Barra de filtros ──────────────────────────────────────
    st.markdown(
        '<div style="background:#f4f3f7;border-radius:12px;padding:20px 24px;'
        'border:1px solid rgba(193,198,214,0.3);margin-bottom:20px">',
        unsafe_allow_html=True,
    )
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        cats       = ["Todas"] + sorted(df["categoria"].dropna().unique().tolist())
        cat_filter = st.selectbox("Categoría", cats)
    with fc2:
        orgs       = ["Todas"] + sorted(df["organizacion"].dropna().unique().tolist())
        org_filter = st.selectbox("Organización", orgs)
    with fc3:
        score_min  = st.slider("Score mínimo", 0, 100, 0)
    with fc4:
        search     = st.text_input("Buscar", placeholder="Nombre del dataset…",
                                   label_visibility="collapsed")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Aplicar filtros ───────────────────────────────────────
    df_f = apply_filters(
        df,
        categorias     = [cat_filter] if cat_filter != "Todas" else None,
        organizaciones = [org_filter] if org_filter != "Todas" else None,
        score_min      = score_min,
    )
    if search:
        mask = df_f["dataset"].str.contains(search, case=False, na=False)
        df_f = df_f[mask]

    # ── Conteo de resultados ──────────────────────────────────
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px">
        <span style="font-size:18px;font-weight:700;color:#1a1b1e">{len(df_f)}</span>
        <span style="color:#414754;font-weight:500">datasets encontrados</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabla ──────────────────────────────────────────────────
    cols_ok  = [c for c in _DISPLAY_COLS if c in df_f.columns]
    df_show  = df_f[cols_ok].rename(columns=_DISPLAY_COLS)

    col_config: dict = {
        "Score": st.column_config.ProgressColumn(
            "Score Global", min_value=0, max_value=100, format="%.1f%%",
        ),
        "Filas": st.column_config.NumberColumn(format="%d"),
    }
    for dim in _PROGRESS_COLS:
        if dim in df_show.columns:
            col_config[dim] = st.column_config.ProgressColumn(
                dim, min_value=0, max_value=100, format="%.1f%%",
            )

    if df_show.empty:
        st.info("No se encontraron datasets con los filtros seleccionados.")
    else:
        st.dataframe(
            df_show,
            use_container_width=True,
            height=520,
            column_config=col_config,
            hide_index=True,
        )

    # ── Barra de exportación ──────────────────────────────────
    st.markdown(
        "<hr style='border:none;border-top:1px solid rgba(193,198,214,0.3);"
        "margin:24px 0'>",
        unsafe_allow_html=True,
    )
    bc1, bc2, _ = st.columns([1, 1, 3])
    with bc1:
        st.download_button(
            "⬇ Descargar CSV",
            df_f.to_csv(index=False).encode("utf-8"),
            "datasets_nl_2026.csv",
            "text/csv",
        )
    with bc2:
        st.download_button(
            "⬇ Descargar JSON",
            df_f.to_json(orient="records", force_ascii=False, indent=2).encode("utf-8"),
            "datasets_nl_2026.json",
            "application/json",
        )
