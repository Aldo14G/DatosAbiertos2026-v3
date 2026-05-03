"""
Sección Inicio · Hero central + scroll narrativo.
NL 2026 Design System — Midnight/Teal/Gold/Rose tokens.
Zero inline styles — all visuals via global_css.py classes.
"""
import streamlit as st

from data_layer import load_coverage_report
from section_data import SectionData
from sections.dimensions import CITIZEN_LABELS as _CITIZEN_LABELS

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


def _health_bar(label: str, pct: float, tier: str = "teal", desc: str = "") -> None:
    """Mini-card con barra de progreso de salud y descripción ciudadana."""
    pct_clean = max(0, min(100, round(pct, 1)))

    fill_class = {
        "teal": "bar-fill",
        "gold": "bar-fill bar-fill-gold",
        "rose": "bar-fill bar-fill-rose",
    }.get(tier, "bar-fill")

    desc_html = f'<p class="health-mini-card-desc">{desc}</p>' if desc else ""

    st.markdown(f"""
    <div class="health-mini-card">
        <div class="health-mini-card-header">
            <span class="health-mini-card-label">{label}</span>
            <span class="health-mini-card-pct">{pct_clean}%</span>
        </div>
        {desc_html}
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

    <div class="nl-ctx-img-wrap fade-up-d1">
        <img
            src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=1400"
            alt="Panel de analítica de datos gubernamentales con métricas de calidad en tiempo real"
            class="nl-ctx-img"
            loading="eager"
        >
    </div>

    <div class="editorial-container fade-up-d1">
        <p>
            Los datos públicos solo sirven si son exactos y actuales. <strong>Gobernanza Pro</strong> es un motor automático que revisa diariamente el portal oficial para medir qué tan bien se está publicando la información.
        </p>
        <p>
            Evaluamos la <strong>salud de los datos</strong> basándonos en reglas internacionales de calidad. Aquí puedes ver quién publica mejor y qué conjuntos de datos necesitan corrección inmediata.
        </p>
        <div class="mt-4">
            <a href="#dashboards" class="stitch-btn-primary">
                <span class="material-symbols-outlined">explore</span>
                Ver Catálogo de Salud
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_hero(stats: dict) -> None:
    """Bloque 1 · Score como enunciado editorial, no tarjeta aislada."""
    total_score = stats.get("score_global_mean", 0.0)
    n_datasets = stats.get("total_datasets", "—")
    n_orgs = stats.get("total_orgs", "—")
    status_label = "Óptimo" if total_score >= 80 else "En Revisión"
    status_color = "excellent" if total_score >= 80 else "poor"

    st.markdown(f"""
<div class="nl-hero-stat-block nl-reveal nl-reveal-d1">
<p class="nl-hero-stat-prose">El catálogo obtiene
  <span class="nl-hero-stat-score nl-hero-stat-score--{status_color}">{total_score:.1f}%</span>
  en ISO/IEC 25012.</p>
<span class="nl-hero-stat-label">{status_label} · {n_datasets} datasets · {n_orgs} dependencias</span>
</div>
""", unsafe_allow_html=True)



def _render_salud_catalogo(stats: dict) -> None:
    """Bloque 4 · Human-readable dimensions."""
    health_metrics = stats.get("health_metrics", {})
    if not health_metrics:
        health_metrics = {
            "Datos Completos": 0.0, "Información Exacta": 0.0, "Consistencia": 0.0, "Registros Únicos": 0.0,
        }

    st.markdown("""
<div class="editorial-container fade-up-4 nl-reveal nl-reveal-d1">
<h2 class="section-title">¿Cómo medimos la calidad?</h2>
<p>No solo revisamos que el archivo exista. Analizamos el contenido registro por registro para asegurar:</p>
</div>

<div class="nl-ctx-img-wrap nl-reveal nl-reveal-d1">
    <img
        src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&q=80&w=1400"
        alt="Analista revisando métricas de calidad de datos en múltiples pantallas"
        class="nl-ctx-img"
        loading="lazy"
    >
</div>

<div class="editorial-container nl-reveal">
<div class="mt-4 nl-center-measure">
""", unsafe_allow_html=True)

    for tech_label, pct in health_metrics.items():
        entry = _CITIZEN_LABELS.get(tech_label, (tech_label, ""))
        label, desc = entry if isinstance(entry, tuple) else (entry, "")
        tier = "teal" if pct >= 80 else "gold" if pct >= 60 else "rose"
        _health_bar(label, pct, tier=tier, desc=desc)

    st.markdown("</div></div>", unsafe_allow_html=True)


def _render_inicio_footer(coverage: dict | None) -> None:
    """Cierre visual de la sección con data breadcrumbs."""
    run_id = coverage.get("run_id", "") if coverage is not None else ""
    if len(run_id) == 15:  # "20260423_163006"
        pipeline_ts = f"{run_id[:4]}-{run_id[4:6]}-{run_id[6:8]} {run_id[9:11]}:{run_id[11:13]}"
    else:
        pipeline_ts = "desconocida"
    st.markdown(f"""
<div class="editorial-footer mb-5">
<p>Datos provenientes de <strong>catalogodatos.nl.gob.mx</strong> · Pipeline ejecutado: {pipeline_ts} · Procesado con PyArrow.</p>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def render_inicio(data: SectionData, _tokens: dict) -> None:
    """Orquestador de la sección Inicio para DatosAbiertos2026."""
    stats = {
        "total_datasets"   : str(data.n_datasets),
        "delta_datasets"   : "",
        "total_orgs"       : str(data.n_orgs),
        "delta_orgs"       : "",
        "total_formatos"   : str(data.n_formats),
        "calidad_media"    : f"{data.mean_score:.1f}%",
        "score_global_mean": data.mean_score,
        "actualizados"     : f"{data.total_rows:,}",
        "delta_act"        : "",
        "recent_datasets"  : data.recent_datasets,
        "top_orgs"         : data.top_orgs_by_count,
        "health_metrics"   : data.dim_means if data.dim_means else {"Evaluación Global": 0.0},
    }
    coverage = load_coverage_report()

    _render_bienvenida()
    _render_hero(stats)
    _render_salud_catalogo(stats)
    _render_inicio_footer(coverage)
