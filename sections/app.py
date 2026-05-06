"""Orquestador de la página única scrollable — 6 secciones narrativas.

Orden: Portada → Hallazgos → Organizaciones → Alertas → Metodología → Conclusiones → Footer.
Cada sección tiene un único propósito y máximo 3 bloques visuales.
Cada render_* produce un <section id="..."> que la topbar referencia vía anchors.
Error boundary activo: un fallo en una sección no rompe el resto de la página.
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


def _sep() -> None:
    st.markdown(
        '<div class="nl-band-sep" role="separator" aria-hidden="true">'
        '<span class="nl-band-sep-dot"></span>'
        '<span class="nl-band-sep-dot"></span>'
        '<span class="nl-band-sep-dot"></span>'
        '</div>',
        unsafe_allow_html=True,
    )


def render(data: SectionData, df: pd.DataFrame, tokens: dict) -> None:
    """Renderiza la página completa en orden narrativo vertical."""
    from sections.alertas import render_alertas_section
    from sections.conclusiones import render_conclusiones
    from sections.footer import render_footer
    from sections.hallazgos import render_hallazgos
    from sections.metodologia import render_metodologia
    from sections.organizaciones import render_organizaciones
    from sections.portada import render_portada

    # 1 · Portada
    _render_boundary("portada", "Portada", render_portada, data, tokens)

    # 2 · Hallazgos
    _sep()
    _render_boundary("hallazgos", "Hallazgos", render_hallazgos, data, df, tokens)

    # 3 · Alertas
    _sep()
    _render_boundary("alertas", "Alertas", render_alertas_section, data, df, tokens)

    # 4 · Organizaciones
    _sep()
    _render_boundary("organizaciones", "Organizaciones", render_organizaciones, data, tokens)

    # 5 · Conclusiones
    _sep()
    _render_boundary("conclusiones", "Conclusiones", render_conclusiones, df, tokens)

    # 6 · Metodología
    _sep()
    _render_boundary("metodologia", "Metodología", render_metodologia, data, tokens)

    # Footer
    _render_boundary("footer", "Footer", render_footer, tokens)
