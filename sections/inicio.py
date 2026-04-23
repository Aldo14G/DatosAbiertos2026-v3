"""
Sección Inicio · Hero central + scroll narrativo.
NL 2026 Design System — Midnight/Teal/Gold/Rose tokens.
Zero inline styles — all visuals via global_css.py classes.
"""
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data_layer import load_coverage_report

# ══════════════════════════════════════════════════════════════════════════════
# HELPERS DE RENDERIZADO (CSS-only, no inline styles)
# ══════════════════════════════════════════════════════════════════════════════

def _divider(label: str) -> None:
    """Divisor visual con etiqueta de sección (usa tokens del design system)."""
    st.markdown(f"""
    <div class="inicio-divider">
        <span class="inicio-divider-label">{label}</span>
        <div class="inicio-divider-line"></div>
    </div>
    """, unsafe_allow_html=True)


def _kpi_block(value: str, label: str, delta: str = "", tier: str = "neutral") -> None:
    """Card KPI individual usando tokens del design system."""
    delta_html = (
        f'<div class="kpi-delta up">'
        f'<span class="material-symbols-outlined" aria-hidden="true" style="font-size:14px">trending_up</span>'
        f' {delta}</div>'
        if delta else ""
    )
    st.markdown(f"""
    <div class="kpi-card kpi-card--left {tier} fade-up">
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def _activity_row(name: str, org: str, date: str, fmt: str = "") -> None:
    """Fila de actividad reciente usando badge del design system."""
    fmt_badge = (
        f'<span class="badge">{fmt}</span>'
        if fmt else ""
    )
    st.markdown(f"""
    <div class="inicio-activity-item">
        <div class="inicio-activity-name">{name}</div>
        <div class="inicio-activity-meta">
            <span class="inicio-activity-org">{org}</span>
            <span class="d-flex gap-2 align-center">
                {fmt_badge}
                <span class="inicio-activity-date">{date}</span>
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _health_bar(label: str, pct: float, tier: str = "teal") -> None:
    """Barra de progreso de salud usando bar tokens del design system."""
    pct_clean = max(0, min(100, round(pct, 1)))

    fill_class = {
        "teal": "bar-fill",
        "gold": "bar-fill bar-fill-gold",
        "rose": "bar-fill bar-fill-rose",
    }.get(tier, "bar-fill")

    st.markdown(f"""
    <div class="mb-4">
        <div class="inicio-health-label">
            <span class="inicio-health-name">{label}</span>
            <span class="inicio-health-pct">{pct_clean}%</span>
        </div>
        <div class="bar-track" role="progressbar" aria-label="{label}" aria-valuenow="{pct_clean}" aria-valuemin="0" aria-valuemax="100">
            <div class="{fill_class}" style="width:{pct_clean}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# BLOQUES DE CONTENIDO
# ══════════════════════════════════════════════════════════════════════════════

def _render_bienvenida() -> None:
    """Bloque 0 · Editorial Header and Introduction."""
    st.markdown("""
    <header class="editorial-header fade-up">
        <div class="eyebrow">Investigación Ciudadana · Nuevo León</div>
        <h1 class="editorial-title">¿Qué tan confiables son los datos del Estado?</h1>
    </header>

    <div class="editorial-container fade-up-d1">
        <p>
            Los datos públicos solo sirven si son exactos y actuales. <strong>Gobernanza Pro</strong> es un motor automático que revisa diariamente el portal oficial para medir qué tan bien se está publicando la información.
        </p>
        <p>
            Evaluamos la <strong>salud de los datos</strong> basándonos en reglas internacionales de calidad. Aquí puedes ver quién publica mejor y qué conjuntos de datos necesitan corrección inmediata.
        </p>
        <div class="mt-4">
            <a href="#datasets" class="stitch-btn-primary">
                <span class="material-symbols-outlined">explore</span>
                Ver Catálogo de Salud
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_hero(stats: dict) -> None:
    """Bloque 1 · Summary health score with minimal noise."""
    health_metrics = stats.get("health_metrics", {})
    vals = [v for v in health_metrics.values() if not pd.isna(v)]
    total_score = sum(vals) / len(vals) if len(vals) > 0 else 0

    st.markdown(f"""
    <div class="editorial-container fade-up-d2">
        <h2 class="section-title">Estado General: {'Óptimo' if total_score >= 80 else 'En Revisión'}</h2>
        <p>
            Actualmente, la salud del catálogo completo es de 
            <span class="kpi-value" style="font-size: 1.5rem; color: var(--teal-light); vertical-align: baseline;">{total_score:.1f}%</span>.
            Analizamos {stats.get('total_datasets', '—')} conjuntos de datos de {stats.get('total_orgs', '—')} dependencias gubernamentales.
        </p>
    </div>
    """, unsafe_allow_html=True)



def _render_kpis(stats: dict) -> None:
    """Omitted in editorial layout. KPIs are now inline text."""
    pass


def _render_actividad_y_orgs(stats: dict) -> None:
    """Omitted to speed up initial load. Data is in 'Organizaciones' tab."""
    pass


def _render_salud_catalogo(stats: dict) -> None:
    """Bloque 4 · Human-readable dimensions."""
    health_metrics = stats.get("health_metrics", {})
    if not health_metrics:
        health_metrics = {
            "Datos Completos": 0.0, "Información Exacta": 0.0, "Consistencia": 0.0, "Registros Únicos": 0.0,
        }

    # Map technical names to citizen-friendly names
    mapping = {
        "Completitud": "Datos Completos",
        "Exactitud": "Información Exacta",
        "Consistencia": "Datos Congruentes",
        "Unicidad": "Sin Duplicados"
    }

    st.markdown("""
    <div class="editorial-container fade-up-4">
        <h2>¿Cómo medimos la calidad?</h2>
        <p>
            No solo revisamos que el archivo exista. Analizamos el contenido registro por registro para asegurar:
        </p>
        <div class="mt-4">
    """, unsafe_allow_html=True)

    for tech_label, pct in health_metrics.items():
        label = mapping.get(tech_label, tech_label)
        tier = "teal" if pct >= 80 else "gold" if pct >= 60 else "rose"
        _health_bar(label, pct, tier=tier)

    st.markdown("</div></div>", unsafe_allow_html=True)


def _render_antes_vs_ahora(
    coverage: dict | None, df: pd.DataFrame,
) -> None:
    """Bloque comparativo Antes vs Ahora inline narrative."""
    if coverage is None:
        return

    ahora_datasets = coverage.get("procesados_exitosos", 0)
    ahora_cobertura = coverage.get("cobertura_pct", 0)
    ahora_tiempo = coverage.get("elapsed_total_s")

    st.markdown(f"""
    <div class="editorial-container mt-5">
        <h2>Evolución del Pipeline</h2>
        <p>
            El nuevo pipeline de auditoría automatizado ha expandido significativamente el área de evaluación. Ahora cubre el <strong>{ahora_cobertura:.1f}%</strong> del catálogo público (evaluando {ahora_datasets} datasets), ejecutando el análisis completo en solo <strong>{ahora_tiempo:.0f}s</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)


def _render_resource_clarity() -> None:
    """Bloque que aclara la diferencia recursos evaluados vs datasets unicos."""
    pass


def _render_inicio_footer() -> None:
    """Cierre visual de la sección con data breadcrumbs."""
    st.markdown(f"""
    <div class="editorial-container mt-5 mb-5" style="border-top: 1px solid var(--card-border); padding-top: 2rem; color: var(--muted); font-size: 0.85rem; font-family: 'DM Mono', monospace;">
      <p>Data sourced from catalogodatos.nl.gob.mx. Rendered at {datetime.now().strftime('%Y-%m-%d %H:%M')}. Processed with PyArrow.</p>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PREPARACIÓN DE DATOS LOCALES
# ══════════════════════════════════════════════════════════════════════════════

def _build_stats_from_df(df: pd.DataFrame) -> dict:
    """Extrae las estadísticas del df real para inyectar a la vista."""
    if df.empty:
        return _demo_stats()

    total_datasets = str(len(df))
    total_orgs = str(df["organizacion"].nunique()) if "organizacion" in df.columns else "0"

    calidad_media = "0.0%"
    if "score_global" in df.columns:
        calidad_media = f"{df['score_global'].mean():.1f}%"

    # Total de filas evaluadas, formateado con comas
    filas_eval = "0"
    if "filas" in df.columns:
        filas_eval_sum = int(df["filas"].sum())
        filas_eval = f"{filas_eval_sum:,}"

    # Recent datasets (Top 6)
    if "dataset" in df.columns:
        if "modificado" in df.columns:
            df_recent = df.sort_values(by="modificado", ascending=False).head(6)
        else:
            df_recent = df.head(6)

        recent_df = df_recent.rename(columns={
            "dataset": "title",
            "organizacion": "organization"
        })[["title", "organization"]].copy()

        if "modificado" in df_recent.columns:
            recent_df["metadata_modified"] = df_recent["modificado"]
        else:
            recent_df["metadata_modified"] = "N/A"

        # Use real format from data if available
        if "formato" in df_recent.columns:
            recent_df["format"] = df_recent["formato"].values
        else:
            recent_df["format"] = "CSV"
    else:
        recent_df = pd.DataFrame()

    # Top orgs
    if "organizacion" in df.columns:
        top_orgs = df["organizacion"].value_counts().head(7)
    else:
        top_orgs = pd.Series()

    # Formatos cubiertos (Fase 5)
    total_formatos = "1"
    if "formato" in df.columns:
        total_formatos = str(df["formato"].nunique())

    # Health metrics (ISO 25012 — 7 dimensiones)
    health = {}
    mapping = {
        "Completitud"   : "comp_completitud_global_pct",
        "Exactitud"     : "acc_score_accuracy_pct",
        "Consistencia"  : "cons_score_consistency_pct",
        "Unicidad"      : "uniq_score_uniqueness_pct",
        "Puntualidad"   : "time_score_timeliness_pct",
        "Documentación" : "doc_score_documentation_pct",
        "Apertura"      : "open_score_openness_pct",
    }

    for lbl, col in mapping.items():
        if col in df.columns:
            val = df[col].dropna()
            if not val.empty:
                health[lbl] = float(val.mean())

    if not health:
        health = {"Evaluación Global": 0.0}

    return {
        "total_datasets" : total_datasets,
        "delta_datasets" : "",
        "total_orgs"     : total_orgs,
        "delta_orgs"     : "",
        "total_formatos" : total_formatos,
        "calidad_media"  : calidad_media,
        "actualizados"   : filas_eval,
        "delta_act"      : "",
        "recent_datasets": recent_df,
        "top_orgs"       : top_orgs,
        "health_metrics" : health,
    }

def _demo_stats() -> dict:
    """Fallback por si falla o viene vacío."""
    return {
        "total_datasets" : "0",
        "total_orgs"     : "0",
        "total_formatos" : "0",
        "calidad_media"  : "0.0%",
        "actualizados"   : "0",
        "recent_datasets": None,
        "top_orgs"       : None,
        "health_metrics" : {
            "Completitud" : 0.0,
            "Exactitud"   : 0.0,
            "Consistencia": 0.0,
            "Unicidad"    : 0.0,
        },
    }

# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def render_inicio(df: pd.DataFrame, tokens: dict) -> None:
    """
    Orquestador de la sección Inicio para DatosAbiertos2026.
    Usa tokens semánticos del design system NL 2026.
    """
    with st.spinner(""):
        stats = _build_stats_from_df(df)
    coverage = load_coverage_report()

    _render_bienvenida()
    _render_hero(stats)
    _render_kpis(stats)
    _render_antes_vs_ahora(coverage, df)
    _render_resource_clarity()
    _render_actividad_y_orgs(stats)
    _render_salud_catalogo(stats)
    _render_inicio_footer()
