"""Sección Conclusiones — hallazgos, insights y recomendaciones auto-derivadas.

Se alimenta exclusivamente del DataFrame de resultados y del coverage_report;
no hay texto estático sobre métricas que pueda quedar desfasado. Los bullets
se regeneran en cada carga según el estado real del catálogo.
"""

from __future__ import annotations

import html as _html

import pandas as pd
import streamlit as st

from config import UMBRAL_GOBERNANZA
from sections.dimensions import DIM_COLS as _DIM_COLS

# ══════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════

def _strongest_weakest_dim(df: pd.DataFrame) -> tuple[str, float, str, float]:
    """Devuelve (dim_mejor, score_mejor, dim_peor, score_peor)."""
    scores: list[tuple[str, float]] = []
    for col, label in _DIM_COLS:
        if col in df.columns:
            scores.append((label, float(df[col].mean())))
    if not scores:
        return ("N/A", 0.0, "N/A", 0.0)
    scores.sort(key=lambda x: x[1], reverse=True)
    return (scores[0][0], scores[0][1], scores[-1][0], scores[-1][1])


def _top_organization(df: pd.DataFrame) -> tuple[str, float, int]:
    """Organización con mejor promedio (mínimo 3 datasets)."""
    if "organizacion" not in df.columns or "score_global" not in df.columns:
        return ("N/A", 0.0, 0)
    grouped = df.groupby("organizacion")["score_global"].agg(["mean", "count"])
    qualified = grouped[grouped["count"] >= 3].sort_values("mean", ascending=False)
    if qualified.empty:
        return ("N/A", 0.0, 0)
    top = qualified.iloc[0]
    return (str(qualified.index[0]), float(top["mean"]), int(top["count"]))


def _flip_card(
    color: str,
    icon: str,
    tag: str,
    kpi: str | None,
    back_title: str,
    back_body: str,
    delay: str = "",
    extra_class: str = "",
) -> str:
    """Genera una disclosure card con summary (icon+kpi) y body expandible.

    back_body puede contener <strong> — no se escapa aquí; el llamador es responsable.
    """
    kpi_html = f'<span class="nl-flip-kpi">{_html.escape(kpi)}</span>' if kpi else ""
    cls = f"nl-flip-card nl-flip--{color} nl-reveal {delay} {extra_class}".strip()
    return (
        f'<details class="{cls}">'
        f'<summary class="nl-flip-front">'
        f'<span class="material-symbols-outlined nl-flip-icon" aria-hidden="true">{icon}</span>'
        f'<span class="nl-flip-tag">{_html.escape(tag)}</span>'
        f'{kpi_html}'
        f'<span class="nl-flip-hint">Clic para ver detalle</span>'
        f'</summary>'
        f'<div class="nl-flip-back">'
        f'<h3 class="nl-flip-back-title">{_html.escape(back_title)}</h3>'
        f'<p class="nl-flip-back-text">{back_body}</p>'
        f'</div>'
        f'</details>'
    )


# ══════════════════════════════════════════════════════════════
# Render principal
# ══════════════════════════════════════════════════════════════

def render_conclusiones(df: pd.DataFrame, _tokens: dict) -> None:
    """Sección Conclusiones — hallazgos e insights derivados del estado actual."""
    total        = len(df)
    score_mean   = float(df["score_global"].mean()) if "score_global" in df.columns else 0.0
    gobernables  = int((df["score_global"] >= UMBRAL_GOBERNANZA).sum()) if "score_global" in df.columns else 0
    criticos     = int((df["score_global"] < UMBRAL_GOBERNANZA).sum()) if "score_global" in df.columns else 0
    strong_label, strong_val, weak_label, weak_val = _strongest_weakest_dim(df)
    top_org_name, top_org_score, top_org_n = _top_organization(df)

    pct_gobernables = (gobernables / total * 100) if total else 0
    pct_criticos    = (criticos / total * 100) if total else 0

    st.markdown("""
<section id="conclusiones" aria-labelledby="conclusiones-title">
  <div class="nl-section-intro nl-reveal">
    <span class="eyebrow">¿Qué debo hacer?</span>
    <h2 id="conclusiones-title" class="section-title">Hallazgos y siguientes pasos</h2>
    <p class="section-subtitle">
      El estado actual del catálogo y las acciones concretas de mayor impacto.
      Se recalcula con cada corrida del pipeline.
    </p>
  </div>
</section>
""", unsafe_allow_html=True)

    # ── 1. HALLAZGOS (3 flip cards) ───────────────────────────
    st.markdown('<div class="eyebrow mt-5 mb-3">Hallazgos clave</div>', unsafe_allow_html=True)


    dim_card = (
        f'<details class="nl-flip-card nl-flip--neutral nl-reveal nl-reveal-d2">'
        f'<summary class="nl-flip-front">'
        f'<div class="nl-flip-dim-row">'
        f'<span class="nl-flip-dim-label">{_html.escape(strong_label)}</span>'
        f'<span class="nl-flip-dim-val nl-dim-up-val">{strong_val:.1f}%</span>'
        f'<span class="nl-flip-dim-sep" aria-hidden="true"></span>'
        f'<span class="nl-flip-dim-label">{_html.escape(weak_label)}</span>'
        f'<span class="nl-flip-dim-val nl-dim-down-val">{weak_val:.1f}%</span>'
        f'</div>'
        f'<span class="nl-flip-tag">Dimensiones</span>'
        f'<span class="nl-flip-hint">Clic para ver detalle</span>'
        f'</summary>'
        f'<div class="nl-flip-back">'
        f'<h3 class="nl-flip-back-title">{_html.escape(strong_label)} lidera; {_html.escape(weak_label)} tiene margen</h3>'
        f'<p class="nl-flip-back-text">'
        f'<strong>{strong_val:.1f}%</strong> en promedio para el catálogo completo. '
        f'La que más puede crecer es <strong>{_html.escape(weak_label)}</strong>, con <strong>{weak_val:.1f}%</strong>. '
        f'Mejorarla mueve el indicador global más que cualquier otra dimensión.'
        f'</p>'
        f'</div>'
        f'</details>'
    )

    hallazgos_html = "".join([
        _flip_card(
            "teal", "query_stats", "Catálogo gobernable",
            f"{pct_gobernables:.0f}%",
            "La mayoría del catálogo cumple",
            f"<strong>{gobernables} de {total}</strong> datasets cumplen el umbral de calidad ({UMBRAL_GOBERNANZA:.0f}%). "
            f"Promedio general: <strong>{score_mean:.1f}%</strong>.",
            "nl-reveal-d1",
            "nl-flip-card--primary",
        ),
        dim_card,
        _flip_card(
            "rose", "error", "Datasets críticos",
            str(criticos),
            f"{criticos} datasets no alcanzan el umbral",
            f"El <strong>{pct_criticos:.0f}%</strong> del catálogo no llega al umbral de {UMBRAL_GOBERNANZA:.0f}%. "
            f"Cada uno tiene recomendaciones concretas en la sección de alertas.",
            "nl-reveal-d3",
        ),
    ])

    st.markdown(
        f'<div class="nl-flip-grid">{hallazgos_html}</div>',
        unsafe_allow_html=True,
    )

    # ── 2. RECOMENDACIONES (roadmap numerado) ─────────────────
    st.markdown('<div class="eyebrow mt-6 mb-3">Recomendaciones</div>', unsafe_allow_html=True)

    recomendaciones: list[tuple[str, str]] = [
        (
            f"Empezar por los {criticos} datasets bajo umbral",
            "Tienen recomendaciones concretas por dimensión en la sección de alertas. "
            "Ahí está el impacto más rápido.",
        ),
        (
            f"Mejorar {weak_label}",
            f"{weak_label} es donde cada punto de mejora tiene mayor efecto en el indicador global. "
            "El esquema de pesos ISO 25012 la convierte en la palanca más eficiente.",
        ),
        (
            f"Aprender de {top_org_name[:40]}",
            "Sus prácticas de catalogación, periodicidad y esquemas de datos son concretas "
            "y replicables. Compartirlas con otras dependencias no cuesta mucho.",
        ),
        (
            "Completar los metadatos CKAN faltantes",
            "Los campos groups, license, maintainer_email y update_frequency son los que más faltan. "
            "Hacerlos obligatorios en el proceso de publicación atacaría directamente "
            "el deterioro en Documentación y Puntualidad.",
        ),
    ]

    steps_html = "".join(
        f'<li class="nl-roadmap-step">'
        f'<div class="nl-roadmap-marker" aria-hidden="true">{i}</div>'
        f'<div class="nl-roadmap-body">'
        f'<h4 class="nl-roadmap-title">{_html.escape(title)}</h4>'
        f'<p class="nl-roadmap-text">{_html.escape(body)}</p>'
        f'</div>'
        f'</li>'
        for i, (title, body) in enumerate(recomendaciones, 1)
    )
    st.markdown(
        f'<ol class="nl-roadmap nl-reveal nl-reveal-d2" aria-label="Recomendaciones priorizadas">{steps_html}</ol>',
        unsafe_allow_html=True,
    )
