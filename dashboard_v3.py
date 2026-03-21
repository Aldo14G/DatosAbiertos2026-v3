# dashboard_v3.py
# Ensamblaje final del dashboard replicando el diseño Stitch completo.

import streamlit as st
import pandas as pd
import json
from pathlib import Path

# ── Configuración de página ─────────────────────────────────
st.set_page_config(
    page_title = "NL 2026 — Gobernanza de Datos",
    page_icon  = "📊",
    layout     = "wide",
    initial_sidebar_state = "expanded",
)

# ── Inyectar CSS del sistema Stitch ─────────────────────────
from styles.global_css import inject_stitch_design_system
st.markdown(inject_stitch_design_system(), unsafe_allow_html=True)

# ── Cargar datos ─────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    from data_layer import load_results
    return load_results("resultados_calidad_datos_nl.csv")

df = load_data()

# ── SIDEBAR — réplica exacta del aside de Stitch ─────────────
with st.sidebar:
    # Logo + versión (replicar estructura Stitch)
    st.markdown("""
    <div style="padding:0 0 24px">
        <div style="font-family:'Plus Jakarta Sans',sans-serif;
                    font-size:15px;font-weight:700;color:#1a1b1e">
            Gobernanza Pro
        </div>
        <div style="font-size:11px;color:#9aa0a6;text-transform:uppercase;
                    letter-spacing:0.08em">v2.0.26</div>
    </div>
    """, unsafe_allow_html=True)

    # Navegación (replicar nav items de Stitch con iconos Material)
    nav = st.radio(
        "nav", [
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

    st.markdown("<hr style='border:none;border-top:1px solid #dadce0;margin:16px 0'>",
                unsafe_allow_html=True)

    # Metadata (replicar bottom section de Stitch)
    st.markdown(f"""
    <div style="font-size:11px;color:#9aa0a6;line-height:2;padding:8px 16px">
        <div>🗓️ Análisis: 2026-03-19</div>
        <div>📦 Script v3.0 · Stitch M3</div>
        <div>📁 {len(df)} datasets</div>
    </div>
    """, unsafe_allow_html=True)

    # CTA Button (replicar "Abrir Portal →" de Stitch)
    st.markdown("""
    <div style="padding:8px 16px">
        <a href="https://catalogodatos.nl.gob.mx" target="_blank"
           style="display:block;text-align:left;color:#005bbf;
                  font-weight:700;font-size:13px;text-decoration:none">
            Abrir Portal →
        </a>
    </div>
    """, unsafe_allow_html=True)

# ── NAVBAR — replicar topnav de Stitch ──────────────────────
st.markdown("""
<div style="display:flex;justify-content:space-between;align-items:center;
            margin-bottom:32px;padding-top:16px;">
    <div style="font-size:21px;font-weight:700;letter-spacing:-0.02em;
                font-family:'Plus Jakarta Sans',sans-serif;color:#1a1b1e">
        NL 2026
    </div>
    <div style="display:flex;gap:16px;align-items:center">
        <button style="padding:8px 16px;font-size:14px;font-weight:600;
                       color:#005bbf;background:transparent;border:none;
                       border-radius:8px;cursor:pointer">
            Descargar CSV
        </button>
        <a href="https://catalogodatos.nl.gob.mx" target="_blank"
           style="padding:8px 20px;font-size:14px;font-weight:600;
                  background:#1a73e8;color:white;border-radius:9999px;
                  text-decoration:none">
            Ver Portal NL
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Enrutamiento de secciones ────────────────────────────────
section = nav.split("  ")[1]

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

# ── Footer — replicar footer de Stitch ──────────────────────
st.markdown("""
<footer style="border-top:1px solid #f1f0f4;background:white;
               padding:48px 0;margin-top:48px;
               display:flex;justify-content:space-between;align-items:center">
    <span style="font-size:18px;font-weight:900;color:#9aa0a6">NL 2026</span>
    <p style="font-family:'Plus Jakarta Sans',sans-serif;font-size:13px;color:#5f6368;margin:0">
        © 2026 Gobierno de Nuevo León - Datos Abiertos
    </p>
    <div style="display:flex;gap:24px">
        <a href="#" style="color:#5f6368;font-size:13px;text-decoration:none">Privacidad</a>
        <a href="#" style="color:#5f6368;font-size:13px;text-decoration:none">Términos</a>
        <a href="#" style="color:#5f6368;font-size:13px;text-decoration:none">Contacto</a>
        <a href="#" style="color:#5f6368;font-size:13px;text-decoration:none">Accesibilidad</a>
    </div>
</footer>
""", unsafe_allow_html=True)
