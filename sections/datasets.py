# sections/datasets.py
"""Explorador de Datasets + Monitor de Alertas Críticas (fusionado).

Fase 2 de la refactorización de navegación:
  - Tab 1: Explorador full-text con filtros y descarga.
  - Tab 2: Alertas críticas (datasets bajo umbral de gobernanza).
    Absorbido desde sections/alertas.py — ya no existe como sección independiente.
"""

import html as _html
import logging
import os
import tomllib

import pandas as pd
import streamlit as st

from config import DIM_ALERT_DEFAULTS, DIM_REC_DEFAULTS, UMBRAL_GOBERNANZA
from data_layer import apply_filters, load_coverage_report
from section_data import SectionData
from sections.dimensions import DIM_COLS as _DIM_COLS

_log = logging.getLogger(__name__)

# ── Columnas para la tabla del explorador ─────────────────────
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
    "doc_score_documentation_pct" : "Documentación",
    "open_score_openness_pct"     : "Apertura",
    "score_global"                : "Score",
}

_PROGRESS_COLS = {
    "Completitud", "Exactitud", "Consistencia", "Unicidad", "Puntualidad",
    "Documentación", "Apertura",
}


# ── Helpers de alertas (portados de alertas.py) ───────────────

def _load_toml_thresholds() -> dict:
    """Carga umbrales de calidad desde config/thresholds.toml."""
    toml_path = os.path.join(os.path.dirname(__file__), "..", "config", "thresholds.toml")
    try:
        with open(toml_path, "rb") as f:
            data = tomllib.load(f)
        return data.get("quality_thresholds", {})
    except (FileNotFoundError, tomllib.TOMLDecodeError):
        return {}


def _as_pct(value: object, default: float) -> float:
    """Convierte un valor a porcentaje float; usa default solo si es None o NaN."""
    if value is None or pd.isna(value):
        return default
    return float(value)


_LOWERCASE_ES = frozenset({
    "de", "del", "la", "las", "el", "los", "y", "o", "en",
    "para", "por", "con", "a", "al", "un", "una",
})


def _humanize_slug(slug: str) -> str:
    """Convierte 'prepa-abierta' → 'Prepa Abierta' (Title Case con preposiciones ES)."""
    cleaned = slug.replace("-", " ").replace("_", " ").strip()
    if not cleaned:
        return "Sin nombre"
    words = cleaned.split()
    out: list[str] = []
    for i, w in enumerate(words):
        lw = w.lower()
        if i > 0 and lw in _LOWERCASE_ES:
            out.append(lw)
        else:
            out.append(w[:1].upper() + w[1:].lower() if w else w)
    return " ".join(out)


def _severity(score: float, umbral: float) -> tuple[str, str]:
    """Etiqueta + clase CSS según el score."""
    if score >= 90:
        return ("Excelente", "nl-alerta-sev--ok")
    if score >= umbral:
        return ("Aceptable", "nl-alerta-sev--warn")
    return ("Crítico", "nl-alerta-sev--critical")


def _recomendaciones(row: dict, umbral: float = UMBRAL_GOBERNANZA) -> list[str]:
    """Genera hasta 4 recomendaciones ordenadas por impacto según las dimensiones críticas."""
    recs = []
    # Si falta el campo: default permisivo (no recomendar sobre datos ausentes).
    # Un valor real de 0.0 SE PRESERVA (no se colapsa con `or`).
    _d    = DIM_REC_DEFAULTS
    comp  = _as_pct(row.get("comp_completitud_global_pct"), _d["comp_completitud_global_pct"])
    acc   = _as_pct(row.get("acc_score_accuracy_pct"),      _d["acc_score_accuracy_pct"])
    cons  = _as_pct(row.get("cons_score_consistency_pct"),  _d["cons_score_consistency_pct"])
    uniq  = _as_pct(row.get("uniq_score_uniqueness_pct"),   _d["uniq_score_uniqueness_pct"])
    time_ = _as_pct(row.get("time_score_timeliness_pct"),   _d["time_score_timeliness_pct"])
    doc   = _as_pct(row.get("doc_score_documentation_pct"), _d["doc_score_documentation_pct"])
    open_ = _as_pct(row.get("open_score_openness_pct"),     _d["open_score_openness_pct"])

    if comp < umbral:
        recs.append(
            "Completar los campos obligatorios: revisar nulos en columnas clave "
            "y validar que el esquema de metadatos cumpla el estándar CKAN."
        )
    if acc < umbral:
        recs.append(
            "Estandarizar tipos de datos: eliminar espacios al inicio/fin de celdas "
            "y separar columnas con datos mixtos (texto + numérico)."
        )
    if cons < umbral:
        recs.append(
            "Resolver inconsistencias: normalizar valores de texto (mayúsculas, tildes) "
            "y revisar outliers estadísticos en columnas numéricas."
        )
    if uniq < umbral:
        recs.append(
            "Eliminar registros duplicados e implementar una clave primaria única "
            "para garantizar la trazabilidad de cada fila."
        )
    if time_ < umbral:
        recs.append(
            "Actualizar el dataset acorde a la frecuencia de publicación declarada "
            "en el portal — se detecta retraso significativo desde la última modificación."
        )
    if doc < umbral:
        recs.append(
            "Mejorar la documentación del dataset: completar la descripción (≥200 caracteres), "
            "agregar descripción a cada recurso e incluir metodología o fuente de datos."
        )
    if open_ < umbral:
        recs.append(
            "Mejorar la apertura: publicar en formatos abiertos (CSV, JSON, GeoJSON) "
            "y asignar una licencia Creative Commons en el portal CKAN."
        )
    if not recs:
        recs.append(
            "Revisar manualmente las anomalías detectadas y contactar al enlace técnico "
            "de la dependencia para coordinación de correcciones."
        )
    return recs[:4]


def _render_failure_panel(coverage: dict | None) -> None:
    """Panel de trazabilidad de fallos de extraccion del pipeline."""
    if coverage is None:
        return
    fallidos = coverage.get("fallidos", 0)
    if fallidos == 0:
        return

    failed_details = coverage.get("failed_details", [])

    # Agrupar por causa
    causes: dict[str, list[dict]] = {}
    for item in failed_details:
        reason = item.get("reason", "")
        if reason.startswith("Download failed"):
            key = "download_failed"
        elif reason == "No URL":
            key = "no_url"
        else:
            key = "other"
        causes.setdefault(key, []).append(item)

    # Resumen por causa
    cause_rows = []
    labels = {
        "download_failed": (
            "Descarga fallida (mismatch de formato)",
            "failure-cause-badge",
        ),
        "no_url": (
            "Sin URL disponible en fuente CKAN",
            "failure-cause-badge failure-cause-badge-gold",
        ),
        "other": (
            "Otro error",
            "failure-cause-badge",
        ),
    }
    for key, items in causes.items():
        lbl, badge_cls = labels.get(key, labels["other"])
        cause_rows.append(
            f'<div class="failure-cause-row">'
            f'<span class="{badge_cls}">{len(items)}</span>'
            f'<span class="failure-reason">{_html.escape(lbl)}</span>'
            f'</div>'
        )

    # Detalle por dataset
    detail_rows = []
    for item in failed_details:
        slug = _html.escape(item.get("slug", "desconocido"))
        reason = _html.escape(item.get("reason", ""))
        detail_rows.append(
            f'<div class="failure-cause-row">'
            f'<span class="failure-slug">{slug}</span>'
            f'<span class="failure-reason">{reason}</span>'
            f'</div>'
        )

    st.markdown(
        f'<div class="failure-panel fade-up" aria-live="polite">'
        f'<div class="failure-panel-header">'
        f'<span class="failure-panel-title">'
        f'<span class="material-symbols-outlined nl-failure-icon" aria-hidden="true">error_outline</span>'
        f'Fallos de Extraccion'
        f'</span>'
        f'<span class="failure-panel-count" aria-label="{fallidos} fallos de extraccion">{fallidos}</span>'
        f'</div>'
        f'{"".join(cause_rows)}'
        f'<details class="nl-failure-details">'
        f'<summary class="nl-failure-summary">Ver detalle por dataset</summary>'
        f'<div class="nl-failure-detail-list">{"".join(detail_rows)}</div>'
        f'</details>'
        f'{_failure_summary_html(causes)}'
        f'</div>',
        unsafe_allow_html=True,
    )


def _failure_summary_html(causes: dict[str, list[dict]]) -> str:
    """Mensaje dinámico de remediación derivado de las causas reales."""
    parts: list[str] = []
    n_mismatch = len(causes.get("download_failed", []))
    n_no_url   = len(causes.get("no_url", []))
    n_other    = len(causes.get("other", []))
    if n_mismatch:
        parts.append(
            f"{n_mismatch} por mismatch de formato declarado (usar "
            f"<code>--force</code> en el próximo run)"
        )
    if n_no_url:
        parts.append(f"{n_no_url} sin URL en la fuente CKAN")
    if n_other:
        parts.append(f"{n_other} otros")
    if not parts:
        return ""
    return (
        '<p class="failure-panel-note">'
        f'Remediación sugerida: {"; ".join(parts)}.'
        "</p>"
    )


def _render_alerta_card(row: dict, umbral: float = UMBRAL_GOBERNANZA) -> str:
    """Genera el HTML de una tarjeta de alerta crítica con barras por dimensión."""
    dims = [
        (label.upper(), _as_pct(row.get(col), DIM_ALERT_DEFAULTS.get(col, 0.0)))
        for col, label in _DIM_COLS
    ]

    bars_html = ""
    for dim_name, val in dims:
        bar_cls = "bar-fill-rose" if val < umbral else "bar-fill-gold" if val < 90 else ""
        dim_label = _html.escape(str(dim_name))
        val_int = f"{val:.0f}"
        bars_html += (
            f'<div class="nl-alerta-dim-row">'
            f'<span class="nl-alerta-dim-label">{dim_label}</span>'
            f'<div class="bar-track nl-alerta-dim-bar" role="progressbar"'
            f' aria-label="{dim_label}"'
            f' aria-valuenow="{val_int}" aria-valuemin="0" aria-valuemax="100">'
            f'<div class="bar-fill {bar_cls}" style="width:{min(val, 100):.0f}%"></div>'
            f'</div>'
            f'<span class="nl-alerta-dim-val">{val_int}%</span>'
            f'</div>'
        )

    ds_raw  = str(row.get("dataset", "")).strip()
    if not ds_raw or ds_raw.lower() == "nan":
        ds_raw = "Sin nombre"
    slug    = str(row.get("slug", "")).strip() or ds_raw.replace(" ", "-").lower()
    ds_name = _humanize_slug(ds_raw)
    url     = f"https://catalogodatos.nl.gob.mx/dataset/{slug}"
    score   = _as_pct(row.get("score_global"), 0)
    org     = str(row.get("organizacion", "")).strip()
    cat     = str(row.get("categoria", "")).strip()
    cat_is_empty = cat.lower() in ("", "sin categoría", "sin categoria", "nan")
    cat_eyebrow = (
        "" if cat_is_empty
        else f'<span class="nl-alerta-eyebrow">{_html.escape(cat)}</span>'
    )

    sev_label, sev_cls = _severity(score, umbral)

    recs      = _recomendaciones(row, umbral=umbral)[:3]
    recs_html = "".join(
        f'<li class="nl-alerta-rec-item">'
        f'<span class="nl-alerta-rec-num" aria-hidden="true">{i + 1}</span>'
        f'<span class="nl-alerta-rec-text">{_html.escape(str(rec))}</span>'
        f'</li>'
        for i, rec in enumerate(recs)
    )

    return (
        f'<details class="nl-alerta-accordion nl-reveal">'
        f'<summary class="nl-alerta-summary">'
        f'<div class="nl-alerta-summary-inner">'
        f'<div class="nl-alerta-summary-meta">'
        f'{cat_eyebrow}'
        f'<h3 class="nl-alerta-title" title="{_html.escape(ds_raw)}">{_html.escape(ds_name)}</h3>'
        f'<p class="nl-alerta-org">{_html.escape(org)}</p>'
        f'</div>'
        f'<div class="nl-alerta-summary-score">'
        f'<div class="alert-score" aria-label="Score {score:.1f} de 100">'
        f'{score:.1f}<span class="nl-alerta-score-unit">%</span></div>'
        f'<div class="kpi-label">Score de Calidad</div>'
        f'<span class="nl-alerta-sev {sev_cls}">{sev_label}</span>'
        f'</div>'
        f'<span class="material-symbols-outlined nl-alerta-chevron" aria-hidden="true">expand_more</span>'
        f'</div>'
        f'</summary>'
        f'<div class="nl-alerta-detail">'
        f'<div class="nl-alerta-dim-list">{bars_html}</div>'
        f'<section class="nl-alerta-card-actions" aria-label="Acciones recomendadas">'
        f'<h4 class="kpi-label">Acciones recomendadas</h4>'
        f'<ol class="nl-alerta-rec-list">{recs_html}</ol>'
        f'</section>'
        f'<footer class="nl-alerta-card-footer">'
        f'<a href="{_html.escape(url)}" target="_blank" rel="noopener" class="nl-alerta-card-link">'
        f'Ver en catalogodatos.nl.gob.mx <span aria-hidden="true">→</span></a>'
        f'</footer>'
        f'</div>'
        f'</details>'
    )


# ── Panel de alertas (reutilizable tab/sección) ───────────────

def _render_alerts_body(df: pd.DataFrame) -> None:
    """Renderiza el monitor de alertas críticas (ex-sección independiente)."""
    toml_thresholds = _load_toml_thresholds()
    umbral = toml_thresholds.get("gobernanza", UMBRAL_GOBERNANZA)

    if "score_global" not in df.columns:
        st.markdown(
            '<div class="nl-insight-card nl-insight-warn">'
            '<p>No se encontró la columna <code class="nl-code-inline">score_global</code> en los datos.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    _missing = frozenset(DIM_ALERT_DEFAULTS) - set(df.columns)
    if _missing:
        _log.warning("Alert card: columnas de dimensión ausentes %s — se usarán defaults de DIM_ALERT_DEFAULTS", sorted(_missing))
        st.markdown(
            f'<div class="nl-insight-card nl-insight-warn">'
            f'<p>Datos incompletos: {len(_missing)} columna(s) de dimensión no disponibles '
            f'({", ".join(sorted(_missing))}). Las barras mostrarán valores por defecto.</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

    df_alertas = df[df["score_global"] < umbral].sort_values("score_global")
    n = len(df_alertas)

    if n == 0:
        st.markdown(f"""
        <div class="alert-banner-success mb-5">
            <span class="material-symbols-outlined nl-alert-banner-icon--lg" aria-hidden="true">check_circle</span>
            <div>
                <div>
                    ¡Ningún dataset está por debajo del umbral de calidad ({umbral:.0f}%)!
                </div>
                <div class="section-subtitle mt-2">
                    El catálogo cumple el estándar mínimo de gobernanza ISO 25012.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="alert-banner mb-6">
            <span class="material-symbols-outlined nl-alert-banner-icon" aria-hidden="true">warning</span>
            <div>
                <div>
                    {_html.escape(str(n))} dataset{"s" if n > 1 else ""}&nbsp;
                    {"requieren" if n > 1 else "requiere"} intervención inmediata
                </div>
                <div class="section-subtitle mt-2">
                    Score de calidad inferior al {umbral:.0f}% — Umbral mínimo de gobernanza ISO 25012
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        cards_html = "".join(
            _render_alerta_card(row.to_dict(), umbral)
            for _, row in df_alertas.iterrows()
        )
        st.markdown(
            f'<div class="nl-alerta-accordion-list">{cards_html}</div>',
            unsafe_allow_html=True,
        )

    # ── Alerta de metadatos ────────────────────────────────────
    sin_cat = df[df["categoria"].isin(["Sin categoría", "", "Sin Categoría"])].shape[0]
    pct_sin_cat = (sin_cat / len(df) * 100) if len(df) > 0 else 0

    if sin_cat > 0:
        st.markdown(
            "<h3 class='section-title nl-alerta-heading'>"
            "<span class='material-symbols-outlined nl-alert-banner-icon' aria-hidden='true'>warning</span>"
            "Alerta de Gobernanza de Metadatos</h3>",
            unsafe_allow_html=True,
        )
        st.markdown(f"""
<div class="stitch-card stitch-card-accent-gold p-5 mb-4">
  <div class="d-flex justify-between align-center mb-3">
    <div>
      <div class="nl-stat-label">
        {sin_cat} datasets sin categoría asignada en el portal CKAN
      </div>
      <div class="section-subtitle mt-2">
        {pct_sin_cat:.1f}% del catálogo carece de clasificación temática.
        Esto limita la navegabilidad y el análisis por sector.
      </div>
    </div>
    <div class="nl-stat-pct">{pct_sin_cat:.0f}%</div>
  </div>
  <div class="kpi-label mb-2">Acción recomendada</div>
  <div class="p-3 nl-stat-note">
    Contactar al enlace técnico de cada dependencia para asignar grupos temáticos
    en el portal <strong>catalogodatos.nl.gob.mx</strong> (campo <code>groups</code> de la API CKAN).
    Este es un indicador de calidad de metadatos ISO 25012 &mdash; Dimensión: Completitud de Metadatos.
  </div>
</div>
""", unsafe_allow_html=True)


def _render_app_card(row: dict, _tokens: dict) -> str:
    """Genera el HTML de una tarjeta estilo App Store para un dataset."""
    score = _as_pct(row.get("score_global"), 0)

    # Determinar color y clase de salud
    health_cls = "app-card-score-excellent" if score >= 90 else "app-card-score-good" if score >= 70 else "app-card-score-poor"
    health_label = "Excelente" if score >= 90 else "Aceptable" if score >= 70 else "Crítico"

    # Determinar ícono según categoría
    cat = str(row.get("categoria", "Otros")).lower()
    icon = "database"
    if "finanzas" in cat or "economía" in cat:
        icon = "payments"
    elif "salud" in cat:
        icon = "medical_services"
    elif "educación" in cat:
        icon = "school"
    elif "transporte" in cat or "movilidad" in cat:
        icon = "directions_bus"
    elif "seguridad" in cat:
        icon = "shield"
    elif "gobierno" in cat:
        icon = "account_balance"
    elif "ambiente" in cat or "ecología" in cat:
        icon = "eco"

    ds_name = str(row.get("dataset", "N/A"))
    org = str(row.get("organizacion", "Dependencia desconocida"))

    # Resumen en lenguaje natural
    recs = _recomendaciones(row)
    summary = recs[0] if recs else "Dataset con estructura estable y metadatos completos."
    if score >= 90:
        summary = "Este conjunto de datos cumple con los más altos estándares de gobernanza y transparencia."

    slug = str(row.get("slug", "")).strip() or ds_name.replace(" ", "-").lower()
    url = f"https://catalogodatos.nl.gob.mx/dataset/{slug}"

    rows_count = int(row.get("filas", 0))
    fmt = str(row.get("formato", "CSV")).upper()

    return (
        f'<div class="app-card fade-up">'
        f'  <div class="app-card-header">'
        f'    <div class="app-card-icon">'
        f'      <span class="material-symbols-outlined">{icon}</span>'
        f'    </div>'
        f'    <div class="app-card-score-badge {health_cls}">'
        f'      {health_label} · {score:.1f}%'
        f'    </div>'
        f'  </div>'
        f'  <div class="app-card-content">'
        f'    <h3 class="app-card-title" title="{_html.escape(ds_name)}">{_html.escape(ds_name)}</h3>'
        f'    <p class="app-card-org">{_html.escape(org)}</p>'
        f'    <p class="app-card-summary">{_html.escape(summary)}</p>'
        f'  </div>'
        f'  <div class="app-card-footer">'
        f'    <div class="app-card-meta">'
        f'      <span class="app-card-meta-label">Registros</span>'
        f'      <span class="app-card-meta-value">{rows_count:,}</span>'
        f'    </div>'
        f'    <div class="app-card-meta">'
        f'      <span class="app-card-meta-label">Formato</span>'
        f'      <span class="app-card-meta-value">{fmt}</span>'
        f'    </div>'
        f'    <a href="{url}" target="_blank" class="app-card-btn">Explorar →</a>'
        f'  </div>'
        f'</div>'
    )


# ── Render principal ──────────────────────────────────────────

def render_datasets(data: SectionData, df: pd.DataFrame, tokens: dict) -> None:
    """Sección Datasets — Explorador App Store + Monitor de Alertas (tabs)."""

    # ── Encabezado ────────────────────────────────────────────
    n_alertas = data.n_critical
    alert_badge = f' <span class="nl-count-badge">{n_alertas}</span>' if n_alertas > 0 else ""

    st.markdown("""
    <h2 class="hero-title" style="margin-bottom:8px;">
        Catálogo de Datos Abiertos
    </h2>
    <p class="hero-subtitle">
        Descubre y accede a los activos de información del Estado de Nuevo León con una mirada ciudadana.
    </p>
    """, unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────
    tab_explorador, tab_orgs, tab_alertas = st.tabs([
        "Explorar Catálogo",
        "Por Organización",
        f"Alertas de Calidad{alert_badge}",
    ])

    # ══════════════════════════════════════════════════════════
    # TAB 1 — Explorador App Store
    # ══════════════════════════════════════════════════════════
    with tab_explorador:
        # ── Barra de filtros ──────────────────────────────────
        st.markdown('<div class="section-panel" style="margin-bottom:24px">', unsafe_allow_html=True)
        fc1, fc2, fc3, fc4 = st.columns([1.5, 1.5, 1, 2])
        with fc1:
            cats       = ["Todas las categorías"] + sorted(df["categoria"].dropna().unique().tolist())
            cat_filter = st.selectbox("Categoría", cats, label_visibility="collapsed")
        with fc2:
            orgs       = ["Todas las organizaciones"] + sorted(df["organizacion"].dropna().unique().tolist())
            org_filter = st.selectbox("Organización", orgs, label_visibility="collapsed")
        with fc3:
            score_min  = st.select_slider("Calidad mínima", options=[0, 70, 80, 90], value=0)
        with fc4:
            search     = st.text_input("Buscar dataset", placeholder="Ej: Catastro, Nómina, Calidad del aire...",
                                       label_visibility="collapsed")
        st.markdown("</div>", unsafe_allow_html=True)

        # ── Aplicar filtros ───────────────────────────────────
        df_f = apply_filters(
            df,
            categorias     = [cat_filter] if cat_filter != "Todas las categorías" else None,
            organizaciones = [org_filter] if org_filter != "Todas las organizaciones" else None,
            score_min      = score_min,
        )
        if search:
            mask = df_f["dataset"].str.contains(search, case=False, na=False)
            df_f = df_f[mask]

        # ── Conteo de resultados ──────────────────────────────
        st.markdown(f"""
        <div class="nl-results-bar">
            <div class="nl-results-left">
                <span class="nl-results-count">{len(df_f)}</span>
                <span class="nl-results-label">resultados encontrados</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if df_f.empty:
            st.markdown(
                '<div class="nl-insight-card nl-insight-neutral">'
                '<span class="material-symbols-outlined nl-insight-icon">search_off</span>'
                '<p>No se encontraron datasets con los filtros seleccionados. '
                'Prueba ampliar la búsqueda o cambiar los criterios.</p>'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            # ── Grid de tarjetas ──────────────────────────────
            # Limitamos a 24 resultados por página para no saturar el DOM de Streamlit
            MAX_CARDS = 24
            df_display = df_f.head(MAX_CARDS)

            cards_html = "".join([_render_app_card(row.to_dict(), tokens) for _, row in df_display.iterrows()])

            st.markdown(f'<div class="dataset-grid">{cards_html}</div>', unsafe_allow_html=True)

            if len(df_f) > MAX_CARDS:
                st.markdown(f"""
                <div class="nl-load-more">
                    <p>Mostrando los primeros {MAX_CARDS} de {len(df_f)} datasets.</p>
                    <p>Usa los filtros superiores para refinar tu búsqueda.</p>
                </div>
                """, unsafe_allow_html=True)

        # ── Barra de exportación (simplificada) ───────────────
        with st.expander("Opciones avanzadas de exportación"):
            st.markdown(
                "<div class='p-4'>",
                unsafe_allow_html=True
            )
            bc1, bc2, _ = st.columns([1, 1, 2])
            with bc1:
                st.download_button(
                    "EXPORTAR CSV",
                    df_f.to_csv(index=False).encode("utf-8"),
                    "results_nl_2026.csv",
                    "text/csv",
                    use_container_width=True,
                )
            with bc2:
                st.download_button(
                    "EXPORTAR JSON",
                    df_f.to_json(orient="records", force_ascii=False, indent=2).encode("utf-8"),
                    "results_nl_2026.json",
                    "application/json",
                    use_container_width=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)



    # ══════════════════════════════════════════════════════════
    # TAB 2 — Organizaciones
    # ══════════════════════════════════════════════════════════
    with tab_orgs:
        from sections.organizaciones import render_organizaciones
        render_organizaciones(df, tokens)

    # ══════════════════════════════════════════════════════════
    # TAB 3 — Alertas Críticas
    # ══════════════════════════════════════════════════════════
    with tab_alertas:
        render_alertas(df, tokens)


def render_alertas(_data: SectionData, df: pd.DataFrame, _tokens: dict) -> None:
    """Monitor de Alertas Críticas (función pública).

    Reúne el panel de fallos de extracción del pipeline + banner de datasets
    bajo umbral + tarjetas con recomendaciones. Reutilizable desde cualquier
    sección sin depender del contenedor de tabs.
    """
    coverage = load_coverage_report()
    _render_failure_panel(coverage)

    toml_cfg = _load_toml_thresholds()
    umbral   = toml_cfg.get("gobernanza", UMBRAL_GOBERNANZA)
    st.markdown(f"""
    <p class="nl-section-intro">
        Datasets con score de calidad por debajo del umbral de gobernanza ({umbral:.0f}%).
        Basado en ISO/IEC 25012:2008.
    </p>
    """, unsafe_allow_html=True)
    _render_alerts_body(df)
