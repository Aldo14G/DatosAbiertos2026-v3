"""Orquestador de la página única scrollable.

Invoca las 5 secciones verticales en orden. Cada render_* produce un
<section id="..."> que la topbar referencia vía anchors (#inicio,
#desarrollo, #dashboards, #conclusiones, #footer).

Cada sección se envuelve en un error boundary: un fallo en una no
rompe la página — se muestra una tarjeta de error en su lugar y el
scroll narrativo continúa.
"""

from __future__ import annotations

import html as _html
import logging
from collections.abc import Callable
from typing import Any

import pandas as pd
import streamlit as st

from section_data import SectionData

_log = logging.getLogger(__name__)


def _render_boundary(
    anchor: str,
    label: str,
    fn: Callable[..., None],
    *args: Any,
    **kwargs: Any,
) -> None:
    """Ejecuta `fn` aislando excepciones; registra traza y muestra aviso local."""
    try:
        fn(*args, **kwargs)
    except Exception as exc:  # noqa: BLE001 — boundary deliberado
        _log.exception("Fallo en sección '%s'", anchor)
        st.markdown(
            f"""
            <section id="{anchor}" class="nl-section-error" role="alert">
                <h3 class="nl-section-error-title">
                    Ocurrió un problema al renderizar "{_html.escape(label)}"
                </h3>
                <p class="nl-section-error-body">
                    {_html.escape(type(exc).__name__)}: {_html.escape(str(exc))}
                </p>
            </section>
            """,
            unsafe_allow_html=True,
        )


def render(data: SectionData, df: pd.DataFrame, tokens: dict) -> None:
    """Renderiza la página completa en orden vertical con iconografía de apoyo."""
    from sections.conclusiones import render_conclusiones
    from sections.dashboards import render_dashboards
    from sections.desarrollo import render_desarrollo
    from sections.footer import render_footer
    from sections.inicio import render_inicio

    # 1 · Inicio
    st.markdown('<a id="inicio" class="nl-anchor"></a>', unsafe_allow_html=True)
    _render_boundary("inicio", "Inicio", render_inicio, data, tokens)

    # 2 · Metodología (cómo medimos)
    st.markdown(
        '<div class="nl-section-break" role="separator" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="nl-section-icon-wrap"><span class="material-symbols-outlined nl-section-icon-xl">history_edu</span></div>', unsafe_allow_html=True)
    _render_boundary("desarrollo", "Metodología", render_desarrollo, df, tokens)

    # 3 · Dashboards (resultados)
    st.markdown(
        '<div class="nl-section-break" role="separator" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="nl-section-icon-wrap"><span class="material-symbols-outlined nl-section-icon-xl">analytics</span></div>', unsafe_allow_html=True)
    _render_boundary("dashboards", "Dashboards", render_dashboards, data, df, tokens)

    # 4 · Conclusiones (síntesis)
    st.markdown(
        '<div class="nl-section-break" role="separator" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="nl-section-icon-wrap"><span class="material-symbols-outlined nl-section-icon-xl">auto_awesome</span></div>', unsafe_allow_html=True)
    _render_boundary("conclusiones", "Conclusiones", render_conclusiones, df, tokens)

    # 5 · Footer
    _render_boundary("footer", "Footer", render_footer, tokens)
