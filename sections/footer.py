"""Sección Footer — Créditos, documentación y contacto (single-page layout).

Reemplaza el footer inline de dashboard_v3.py. Zero inline styles ≥30 chars;
todos los tokens vía clases CSS definidas en styles/global_css.py.
"""

from __future__ import annotations

import datetime

import streamlit as st

from config import VERSION

# ══════════════════════════════════════════════════════════════
# Estructura de enlaces (fuente de verdad)
# ══════════════════════════════════════════════════════════════

_DOCS_LINKS: list[tuple[str, str]] = [
    ("Portal Datos Abiertos NL",    "https://datosabiertos.nl.gob.mx"),
    ("Catálogo CKAN",               "https://catalogodatos.nl.gob.mx"),
    ("API CKAN (v3)",               "https://catalogodatos.nl.gob.mx/api/3/action/package_list"),
    ("ISO/IEC 25012:2008",          "https://www.iso.org/standard/35736.html"),
]

_REFS_LINKS: list[tuple[str, str]] = [
    ("ISO 8000 — Data Quality",                 "https://www.iso.org/standard/50798.html"),
    ("DAMA-DMBOK 2.0",                          "https://www.dama.org/cpages/body-of-knowledge"),
    ("Open Data Charter",                       "https://opendatacharter.net/principles/"),
    ("W3C Data on the Web Best Practices",      "https://www.w3.org/TR/dwbp/"),
]

_CONTACT_LINKS: list[tuple[str, str]] = [
    ("LABNL",                       "https://labnl.mx"),
    ("Coordinación Ejecutiva NL",   "https://www.nl.gob.mx/coordinacion-ejecutiva"),
    ("GitHub del Proyecto",         "https://github.com/aldogp/DatosAbiertos2026"),
]


# ══════════════════════════════════════════════════════════════
# Render principal
# ══════════════════════════════════════════════════════════════

def render_footer(tokens: dict | None = None) -> None:
    """Renderiza el footer con documentación, referencias, contacto y créditos."""
    year = datetime.date.today().year

    def _links_html(items: list[tuple[str, str]]) -> str:
        return "".join(
            f'<a class="nl-footer-link" href="{url}" target="_blank" '
            f'rel="noopener noreferrer">{label}</a>'
            for label, url in items
        )

    st.markdown(f"""
    <section id="footer" class="nl-footer" aria-labelledby="footer-title">
        <div class="nl-footer-top">
            <div class="nl-footer-brand">
                <span class="nl-footer-logo" aria-hidden="true">NL 2026</span>
                <p class="nl-footer-tagline">
                    Sistema de Calidad de Datos del Estado de Nuevo León
                    conforme a ISO/IEC 25012:2008.
                </p>
            </div>

            <nav class="nl-footer-col" aria-label="Documentación">
                <h3 class="nl-footer-col-title">Documentación</h3>
                {_links_html(_DOCS_LINKS)}
            </nav>

            <nav class="nl-footer-col" aria-label="Referencias técnicas">
                <h3 class="nl-footer-col-title">Referencias</h3>
                {_links_html(_REFS_LINKS)}
            </nav>

            <nav class="nl-footer-col" aria-label="Contacto y créditos">
                <h3 class="nl-footer-col-title">Contacto</h3>
                {_links_html(_CONTACT_LINKS)}
            </nav>
        </div>

        <div class="nl-footer-bottom">
            <span class="nl-footer-copy">
                © {year} Gobierno de Nuevo León — Datos Abiertos · {VERSION}
            </span>
            <span class="nl-footer-meta">
                Construido con Streamlit · Plotly · Pandas
            </span>
        </div>
    </section>
    """, unsafe_allow_html=True)
