# dashboard_v3.py
# Orquestador principal del dashboard NL 2026.
# Ejecutar con: streamlit run dashboard_v3.py

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="NL 2026 — Gobernanza de Datos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inyectar sistema de diseño Stitch ────────────────────────
from styles.global_css import inject_stitch_design_system
st.markdown(inject_stitch_design_system(), unsafe_allow_html=True)


# ── Carga de datos ────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data() -> pd.DataFrame:
    from data_layer import load_results
    return load_results()


try:
    df = load_data()
except (FileNotFoundError, ValueError, KeyError) as e:
    st.error(
        f"**Error al cargar los datos:** {e}\n\n"
        "Verifica que exista `resultados_calidad_datos_nl.csv` o "
        "`.antigravity/team/shared/quality_results.json`."
    )
    st.stop()

if df.empty:
    st.warning("El archivo de resultados existe pero no contiene datos.")
    st.stop()


# ── Métricas de cabecera para el sidebar ─────────────────────
_n_alertas  = int((df["score_global"] < 70).sum()) if "score_global" in df.columns else 0
_score_prom = df["score_global"].mean()             if "score_global" in df.columns else 0


# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:0 0 20px">
        <div style="font-family:'Plus Jakarta Sans',sans-serif;
                    font-size:15px;font-weight:700;color:#1a1b1e">
            Gobernanza Pro
        </div>
        <div style="font-size:11px;color:#9aa0a6;text-transform:uppercase;
                    letter-spacing:0.08em">v2.1 · Stitch M3</div>
    </div>
    """, unsafe_allow_html=True)

    nav = st.radio(
        "nav",
        [
            "dashboard  Resumen",
            "explore  Categorías",
            "table_view  Datasets",
            "notifications  Alertas",
            "show_chart  Evolución",
            "insights  Avanzado",
        ],
        label_visibility="collapsed",
        format_func=lambda x: x.split("  ")[1],
    )

    st.markdown(
        "<hr style='border:none;border-top:1px solid #dadce0;margin:16px 0'>",
        unsafe_allow_html=True,
    )

    # Badge de alertas (rojo si hay críticos)
    alert_color = "#d93025" if _n_alertas > 0 else "#1e8e3e"
    alert_icon  = "⚠️" if _n_alertas > 0 else "✓"
    st.markdown(f"""
    <div style="font-size:11px;color:#9aa0a6;line-height:2.2;padding:4px 16px">
        <div>🗓️ Análisis: 2026-03-19</div>
        <div>📁 {len(df)} datasets procesados</div>
        <div>📊 Score promedio: <strong style="color:#1a1b1e">{_score_prom:.1f}%</strong></div>
        <div style="color:{alert_color};font-weight:600">
            {alert_icon} {_n_alertas} alertas críticas
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<hr style='border:none;border-top:1px solid #dadce0;margin:12px 0'>",
        unsafe_allow_html=True,
    )

    st.markdown("""
    <div style="padding:4px 16px 8px">
        <a href="https://catalogodatos.nl.gob.mx" target="_blank"
           style="color:#005bbf;font-weight:700;font-size:13px;text-decoration:none">
            Abrir Portal →
        </a>
    </div>
    """, unsafe_allow_html=True)


# ── NAVBAR ────────────────────────────────────────────────────
section = nav.split("  ")[1]

nc1, nc2 = st.columns([1, 2])
with nc1:
    st.markdown("""
    <div style="font-size:21px;font-weight:700;letter-spacing:-0.02em;
                font-family:'Plus Jakarta Sans',sans-serif;color:#1a1b1e;
                padding-top:16px;margin-bottom:8px">
        NL 2026
    </div>
    """, unsafe_allow_html=True)
with nc2:
    # Botón de descarga global disponible en todas las secciones
    _, btn_col = st.columns([3, 1])
    with btn_col:
        st.download_button(
            "⬇ CSV completo",
            df.to_csv(index=False).encode("utf-8"),
            "resultados_nl_2026.csv",
            "text/csv",
            key="nav_dl",
        )

st.markdown("<div style='margin-bottom:24px'></div>", unsafe_allow_html=True)


# ── ENRUTAMIENTO ──────────────────────────────────────────────
if section == "Resumen":
    from sections.resumen import render_resumen
    render_resumen(df, {})

elif section == "Categorías":
    from sections.categorias import render_categorias
    render_categorias(df, {})

elif section == "Datasets":
    from sections.datasets import render_datasets
    render_datasets(df, {})

elif section == "Alertas":
    from sections.alertas import render_alertas
    render_alertas(df, {})

elif section == "Evolución":
    from sections.evolucion import render_evolucion
    render_evolucion(df, {})

elif section == "Avanzado":
    from sections.avanzado import render_avanzado
    render_avanzado(df, {})


# ── FOOTER ────────────────────────────────────────────────────
st.markdown("""
<footer style="border-top:1px solid #f1f0f4;padding:32px 0;margin-top:56px;
               display:flex;justify-content:space-between;align-items:center;
               flex-wrap:wrap;gap:16px">
    <span style="font-size:18px;font-weight:900;color:#9aa0a6">NL 2026</span>
    <p style="font-family:'Plus Jakarta Sans',sans-serif;font-size:13px;
              color:#5f6368;margin:0">
        © 2026 Gobierno de Nuevo León — Datos Abiertos
    </p>
    <div style="display:flex;gap:24px">
        <a href="https://datosabiertos.nl.gob.mx"  target="_blank"
           style="color:#5f6368;font-size:13px;text-decoration:none">Portal</a>
        <a href="https://catalogodatos.nl.gob.mx"  target="_blank"
           style="color:#5f6368;font-size:13px;text-decoration:none">Catálogo</a>
        <a href="https://nl.gob.mx/transparencia" target="_blank"
           style="color:#5f6368;font-size:13px;text-decoration:none">Transparencia</a>
    </div>
</footer>
""", unsafe_allow_html=True)
