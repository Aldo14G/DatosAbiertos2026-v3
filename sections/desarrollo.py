"""Sección Desarrollo — Metodología, proceso y enfoque técnico.

Explica cómo se construye el score ISO/IEC 25012:2008, qué hace cada etapa
del pipeline, y caracteriza el universo de datasets analizado. Consume
datos reales desde data_layer (coverage_report + df agregado) — nada estático.
"""

from __future__ import annotations

import html as _html

import pandas as pd
import streamlit as st

from config import QUALITY_WEIGHTS, UMBRAL_GOBERNANZA
from data_layer import DIM_LABEL_MAP, load_coverage_report

# ══════════════════════════════════════════════════════════════
# Contenido estático pedagógico (metodología)
# ══════════════════════════════════════════════════════════════

_PIPELINE_STEPS: list[tuple[str, str, str]] = [
    (
        "travel_explore", "Descubrimiento (Fetcher)",
        "Consulta la API CKAN pública del Portal NL. Itera sobre todos los "
        "paquetes publicados, recolecta metadatos y URLs de recursos. "
        "Respeta SSRF y límites de tamaño.",
    ),
    (
        "download", "Extracción (Extractor)",
        "Descarga cada recurso validando formato declarado vs real. Soporta "
        "CSV, JSON, XLSX, GeoJSON, XML. Detecta encoding automáticamente; "
        "normaliza delimitadores y tipos.",
    ),
    (
        "fact_check", "Evaluación (Evaluator ISO 25012)",
        "Calcula 7 dimensiones por dataset: Completitud, Exactitud, Consistencia, "
        "Unicidad, Puntualidad, Documentación, Apertura. Aplica pesos ponderados y "
        "genera el score global.",
    ),
    (
        "hub", "Agregación (Data Layer)",
        "Cachea los resultados, produce agregaciones por organización y categoría, "
        "y expone APIs de filtrado para la UI. Integra overlay de pipeline avanzado "
        "(ISO 8000 + DAMA) si está disponible.",
    ),
]

_DIM_DESCRIPTIONS: dict[str, str] = {
    "Completitud":   "% de celdas no nulas ponderadas por la criticidad de la columna.",
    "Exactitud":     "Validación de tipos, rangos y formatos contra el esquema declarado.",
    "Consistencia":  "Coherencia cross-columna y detección de outliers (IQR robusto, n≥30).",
    "Unicidad":      "Ratio de registros únicos vs totales; penaliza duplicación lógica.",
    "Puntualidad":   "Latencia entre última actualización y frecuencia declarada.",
    "Documentación": "Completitud de metadatos CKAN: descripción, licencia, contactos.",
    "Apertura":      "Grado de apertura del formato según Open Data Charter.",
}


# ══════════════════════════════════════════════════════════════
# Helpers privados
# ══════════════════════════════════════════════════════════════

def _divider(label: str) -> None:
    st.markdown(f"""
    <div class="inicio-divider">
        <span class="inicio-divider-label">{_html.escape(label)}</span>
        <div class="inicio-divider-line"></div>
    </div>
    """, unsafe_allow_html=True)


def _pipeline_card(icon: str, title: str, body: str) -> str:
    return f"""
    <article class="nl-pipeline-step stitch-card">
        <span class="material-symbols-outlined nl-pipeline-icon" aria-hidden="true">{icon}</span>
        <h3 class="section-title nl-pipeline-title">{_html.escape(title)}</h3>
        <p class="section-subtitle nl-pipeline-body">{_html.escape(body)}</p>
    </article>
    """


def _weight_row(dim_label: str, weight: float, description: str) -> str:
    pct = int(round(weight * 100))
    width = min(max(pct * 3, 8), 100)
    return f"""
    <div class="nl-weight-row">
        <div class="nl-weight-head">
            <span class="nl-weight-label">{_html.escape(dim_label)}</span>
            <span class="nl-weight-value">{pct}%</span>
        </div>
        <div class="bar-track" role="progressbar"
             aria-label="Peso de {_html.escape(dim_label)}"
             aria-valuenow="{pct}" aria-valuemin="0" aria-valuemax="40">
            <div class="bar-fill nl-weight-fill" data-width="{width}"></div>
        </div>
        <p class="nl-weight-desc">{_html.escape(description)}</p>
    </div>
    """


# ══════════════════════════════════════════════════════════════
# Render principal
# ══════════════════════════════════════════════════════════════

def render_desarrollo(df: pd.DataFrame, tokens: dict) -> None:
    """Sección Desarrollo — metodología + pipeline + caracterización del universo."""

    st.markdown("""
    <section id="desarrollo" class="nl-section" aria-labelledby="desarrollo-title">
        <span class="eyebrow">02 · Desarrollo</span>
        <h2 id="desarrollo-title" class="hero-title nl-section-title">
            Cómo construimos el <em>score</em>
        </h2>
        <p class="hero-subtitle nl-section-subtitle">
            Una cadena de cuatro etapas que transforma el catálogo público en
            un índice de calidad auditable bajo ISO/IEC 25012:2008.
        </p>
    </section>
    """, unsafe_allow_html=True)

    # ── Pipeline de 4 etapas ─────────────────────────────────
    _divider("Proceso de análisis")
    cards_html = "".join(_pipeline_card(*step) for step in _PIPELINE_STEPS)
    st.markdown(
        f'<div class="nl-pipeline-grid">{cards_html}</div>',
        unsafe_allow_html=True,
    )

    # ── Pesos ISO 25012 ──────────────────────────────────────
    _divider("Metodología ISO/IEC 25012:2008")

    weight_rows: list[str] = []
    dim_key_to_label = {
        "completeness":  "Completitud",
        "accuracy":      "Exactitud",
        "consistency":   "Consistencia",
        "uniqueness":    "Unicidad",
        "timeliness":    "Puntualidad",
        "documentation": "Documentación",
        "openness":      "Apertura",
    }
    for key, weight in QUALITY_WEIGHTS.items():
        label = dim_key_to_label.get(key, key.title())
        desc  = _DIM_DESCRIPTIONS.get(label, "")
        weight_rows.append(_weight_row(label, weight, desc))

    st.markdown(
        '<div class="nl-weights-grid">' + "".join(weight_rows) + '</div>',
        unsafe_allow_html=True,
    )

    # ── Caracterización del universo analizado ──────────────
    _divider("Datasets analizados")

    coverage = load_coverage_report() or {}
    total_catalogo = int(coverage.get("total_catalogo", len(df)))
    procesados     = int(coverage.get("procesados_exitosos", len(df)))
    fallidos       = int(coverage.get("fallidos", 0))
    elapsed        = float(coverage.get("elapsed_total_s", 0.0) or 0.0)

    n_orgs = int(df["organizacion"].nunique()) if "organizacion" in df.columns else 0
    n_cats = int(df["categoria"].nunique()) if "categoria" in df.columns else 0
    n_fmts = int(df["formato"].dropna().nunique()) if "formato" in df.columns else 0
    filas_total = int(df["filas"].sum()) if "filas" in df.columns else 0
    by_umbral = int((df["score_global"] >= UMBRAL_GOBERNANZA).sum()) if "score_global" in df.columns else 0
    pct_umbral = (by_umbral / len(df) * 100) if len(df) else 0

    stats_cards = [
        ("database",    f"{total_catalogo:,}",          "Datasets en catálogo"),
        ("check_circle", f"{procesados:,}",              "Procesados con éxito"),
        ("error",        f"{fallidos:,}",                "Fallos de extracción"),
        ("timer",        f"{elapsed:.0f}s",              "Tiempo total de evaluación"),
        ("apartment",    f"{n_orgs}",                    "Organizaciones representadas"),
        ("category",     f"{n_cats}",                    "Categorías temáticas"),
        ("description",  f"{n_fmts}",                    "Formatos distintos"),
        ("dataset",      f"{filas_total:,}",             "Filas evaluadas (total)"),
        ("verified",     f"{pct_umbral:.0f}%",           "Sobre umbral de gobernanza"),
    ]
    card_html = "".join(f"""
    <div class="nl-stat-card">
        <span class="material-symbols-outlined nl-stat-icon" aria-hidden="true">{icon}</span>
        <span class="nl-stat-value">{_html.escape(str(value))}</span>
        <span class="nl-stat-label">{_html.escape(label)}</span>
    </div>
    """ for icon, value, label in stats_cards)

    st.markdown(
        f'<div class="nl-stats-grid">{card_html}</div>',
        unsafe_allow_html=True,
    )

    # ── Cierre ─────────────────────────────────────────────────
    st.markdown(f"""
    <div class="nl-section-closure">
        <p class="section-subtitle">
            Fuente: <strong>catalogodatos.nl.gob.mx</strong> (API CKAN v3). Caché local con TTL de 5 min.
            Todos los KPIs de esta sección se derivan dinámicamente del último pipeline ejecutado.
            Dimensiones reportadas: <strong>{len(DIM_LABEL_MAP) - 1}</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)
