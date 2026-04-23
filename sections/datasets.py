# sections/datasets.py
"""Explorador de Datasets + Monitor de Alertas Críticas (fusionado).

Fase 2 de la refactorización de navegación:
  - Tab 1: Explorador full-text con filtros y descarga.
  - Tab 2: Alertas críticas (datasets bajo umbral de gobernanza).
    Absorbido desde sections/alertas.py — ya no existe como sección independiente.
"""

import html as _html
import os
import tomllib

import pandas as pd
import streamlit as st

from config import UMBRAL_GOBERNANZA
from data_layer import apply_filters, load_coverage_report

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


def _recomendaciones(row: dict, umbral: float = UMBRAL_GOBERNANZA) -> list[str]:
    """Genera hasta 4 recomendaciones ordenadas por impacto según las dimensiones críticas."""
    recs = []
    # Si falta el campo: default permisivo (no recomendar sobre datos ausentes).
    # Un valor real de 0.0 SE PRESERVA (no se colapsa con `or`).
    comp  = _as_pct(row.get("comp_completitud_global_pct"), 100)
    acc   = _as_pct(row.get("acc_score_accuracy_pct"),      100)
    cons  = _as_pct(row.get("cons_score_consistency_pct"),  100)
    uniq  = _as_pct(row.get("uniq_score_uniqueness_pct"),   100)
    time_ = _as_pct(row.get("time_score_timeliness_pct"),    50)

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
        ("COMPLETITUD",  _as_pct(row.get("comp_completitud_global_pct"),  0)),
        ("EXACTITUD",    _as_pct(row.get("acc_score_accuracy_pct"),       0)),
        ("CONSISTENCIA", _as_pct(row.get("cons_score_consistency_pct"),   0)),
        ("PUNTUALIDAD",  _as_pct(row.get("time_score_timeliness_pct"),   50)),
    ]

    bars_html = ""
    for dim_name, val in dims:
        bar_cls = "nl-bar-critical" if val < umbral else "nl-bar-warn" if val < 90 else "nl-bar-ok"
        bars_html += (
            f'<div class="nl-alerta-dim-row">'
            f'<div class="nl-alerta-dim-head">'
            f'<span>{_html.escape(str(dim_name))}</span>'
            f'<span>{_html.escape(f"{val:.0f}")}%</span>'
            f'</div>'
            f'<div class="bar-track" role="progressbar" aria-label="{_html.escape(str(dim_name))}"'
            f' aria-valuenow="{val:.0f}" aria-valuemin="0" aria-valuemax="100">'
            f'<div class="bar-fill {bar_cls}" style="width:{min(val, 100):.0f}%"></div>'
            f'</div>'
            f'</div>'
        )

    ds_name = str(row.get("dataset", "N/A"))
    if not ds_name or ds_name == "nan":
        ds_name = "N/A"
    slug    = str(row.get("slug", "")).strip() or ds_name.replace(" ", "-").lower()
    url     = f"https://catalogodatos.nl.gob.mx/dataset/{slug}"
    score   = _as_pct(row.get("score_global"), 0)
    org     = str(row.get("organizacion", ""))[:65]
    cat     = str(row.get("categoria", ""))

    recs      = _recomendaciones(row, umbral=umbral)
    recs_html = "".join(
        f'<li class="nl-alerta-rec-item">'
        f'<span class="nl-alerta-rec-num">{i + 1}</span>'
        f'{_html.escape(str(rec))}'
        f'</li>'
        for i, rec in enumerate(recs)
    )

    return (
        f'<div class="stitch-card stitch-card-accent-rose p-0 mb-5" style="overflow:hidden;">'
        f'<div class="p-5">'
        f'<div class="d-flex justify-between mb-4" style="align-items:flex-start">'
        f'<div class="nl-alerta-card-inner">'
        f'<h3 class="section-title text-truncate" style="margin:0 0 4px"'
        f' title="{_html.escape(ds_name)}">{_html.escape(ds_name[:55])}</h3>'
        f'<p class="section-subtitle" style="margin:0">{_html.escape(str(org))}</p>'
        f'<span class="badge mt-2">{_html.escape(str(cat))}</span>'
        f'</div>'
        f'<div class="text-right nl-alerta-card-score-col">'
        f'<div class="alert-score">{_html.escape(f"{score:.1f}")}%</div>'
        f'<div class="kpi-label mt-2">Score de Calidad</div>'
        f'</div>'
        f'</div>'
        f'<div class="card-grid card-grid-2 mb-4">{bars_html}</div>'
        f'<div class="nl-alerta-card-actions">'
        f'<h4 class="kpi-label">Acciones recomendadas</h4>'
        f'<ul class="icon-list p-0">{recs_html}</ul>'
        f'</div>'
        f'</div>'
        f'<div class="nl-alerta-card-footer p-4">'
        f'<a href="{_html.escape(url)}" target="_blank" class="nl-alerta-card-link">'
        f'Ver en catalogodatos.nl.gob.mx →</a>'
        f'</div>'
        f'</div>'
    )


# ── Panel de alertas (reutilizable tab/sección) ───────────────

def _render_alerts_body(df: pd.DataFrame) -> None:
    """Renderiza el monitor de alertas críticas (ex-sección independiente)."""
    toml_thresholds = _load_toml_thresholds()
    umbral = toml_thresholds.get("gobernanza", UMBRAL_GOBERNANZA)

    if "score_global" not in df.columns:
        st.warning("No se encontró la columna `score_global` en los datos.")
        return

    df_alertas = df[df["score_global"] < umbral].sort_values("score_global")
    n = len(df_alertas)

    if n == 0:
        st.markdown(f"""
        <div class="alert-banner-success mb-5">
            <span class="material-symbols-outlined" aria-hidden="true" style="font-size:32px">check_circle</span>
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
            <span class="material-symbols-outlined" aria-hidden="true" style="font-size:28px">warning</span>
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

        cols = st.columns(2)
        for i, (_, row) in enumerate(df_alertas.iterrows()):
            cols[i % 2].markdown(_render_alerta_card(row.to_dict(), umbral), unsafe_allow_html=True)

    # ── Alerta de metadatos ────────────────────────────────────
    sin_cat = df[df["categoria"].isin(["Sin categoría", "", "Sin Categoría"])].shape[0]
    pct_sin_cat = (sin_cat / len(df) * 100) if len(df) > 0 else 0

    if sin_cat > 0:
        st.markdown("---")
        st.markdown(
            "<h3 class='section-title nl-alerta-heading'>"
            "<span class='material-symbols-outlined' aria-hidden='true' style='font-size:22px'>warning</span>"
            "Alerta de Gobernanza de Metadatos</h3>",
            unsafe_allow_html=True,
        )
        st.markdown(f"""
<div class="stitch-card stitch-card-accent-gold p-5 mb-4">
  <div class="d-flex justify-between align-center mb-3">
    <div>
      <div style="font-size:17px;font-weight:700;color:var(--cream)">
        {sin_cat} datasets sin categoría asignada en el portal CKAN
      </div>
      <div class="section-subtitle mt-2">
        {pct_sin_cat:.1f}% del catálogo carece de clasificación temática.
        Esto limita la navegabilidad y el análisis por sector.
      </div>
    </div>
    <div style="font-size:36px;font-weight:700;font-family:'Playfair Display',serif;color:var(--gold);margin-left:24px;flex-shrink:0">{pct_sin_cat:.0f}%</div>
  </div>
  <div class="kpi-label mb-2">Acción recomendada</div>
  <div class="p-3" style="font-size:13px;color:var(--cream);background:var(--surface-alt);border-radius:8px;">
    Contactar al enlace técnico de cada dependencia para asignar grupos temáticos
    en el portal <strong>catalogodatos.nl.gob.mx</strong> (campo <code>groups</code> de la API CKAN).
    Este es un indicador de calidad de metadatos ISO 25012 &mdash; Dimensión: Completitud de Metadatos.
  </div>
</div>
""", unsafe_allow_html=True)


def _render_app_card(row: dict, tokens: dict) -> str:
    """Genera el HTML de una tarjeta estilo App Store para un dataset."""
    score = _as_pct(row.get("score_global"), 0)
    
    # Determinar color y clase de salud
    health_cls = "app-card-score-excellent" if score >= 90 else "app-card-score-good" if score >= 70 else "app-card-score-poor"
    health_label = "Excelente" if score >= 90 else "Aceptable" if score >= 70 else "Crítico"
    
    # Determinar ícono según categoría
    cat = str(row.get("categoria", "Otros")).lower()
    icon = "database"
    if "finanzas" in cat or "economía" in cat: icon = "payments"
    elif "salud" in cat: icon = "medical_services"
    elif "educación" in cat: icon = "school"
    elif "transporte" in cat or "movilidad" in cat: icon = "directions_bus"
    elif "seguridad" in cat: icon = "shield"
    elif "gobierno" in cat: icon = "account_balance"
    elif "ambiente" in cat or "ecología" in cat: icon = "eco"
    
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

def render_datasets(df: pd.DataFrame, tokens: dict) -> None:
    """Sección Datasets — Explorador App Store + Monitor de Alertas (tabs)."""

    # ── Encabezado ────────────────────────────────────────────
    n_alertas = int((df["score_global"] < UMBRAL_GOBERNANZA).sum()) if "score_global" in df.columns else 0
    alert_badge = f' <span style="background:var(--rose);color:#fff;font-size:10px;font-weight:700;padding:2px 8px;border-radius:9999px;vertical-align:middle">{n_alertas}</span>' if n_alertas > 0 else ""

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
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:24px">
            <div style="display:flex;align-items:center;gap:8px">
                <span style="font-size:20px;font-weight:700;font-family:'Playfair Display',serif;color:var(--cream)">{len(df_f)}</span>
                <span style="color:var(--muted);font-weight:500;font-family:'DM Sans',sans-serif">resultados encontrados</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if df_f.empty:
            st.info("No se encontraron datasets con los filtros seleccionados.")
        else:
            # ── Grid de tarjetas ──────────────────────────────
            # Limitamos a 24 resultados por página para no saturar el DOM de Streamlit
            MAX_CARDS = 24
            df_display = df_f.head(MAX_CARDS)
            
            cards_html = "".join([_render_app_card(row.to_dict(), tokens) for _, row in df_display.iterrows()])
            
            st.markdown(f'<div class="dataset-grid">{cards_html}</div>', unsafe_allow_html=True)
            
            if len(df_f) > MAX_CARDS:
                st.markdown(f"""
                <div style="text-align:center;margin-top:32px;padding:24px;background:var(--surface-alt);border-radius:16px;border:1px dashed var(--card-border)">
                    <p style="color:var(--muted);margin-bottom:16px">Mostrando los primeros {MAX_CARDS} de {len(df_f)} datasets.</p>
                    <p style="font-size:13px">Usa los filtros superiores para refinar tu búsqueda.</p>
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


def render_alertas(df: pd.DataFrame, tokens: dict) -> None:
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
    <p style="color:var(--muted);max-width:640px;margin:8px 0 24px">
        Datasets con score de calidad por debajo del umbral de gobernanza ({umbral:.0f}%).
        Basado en ISO/IEC 25012:2008.
    </p>
    """, unsafe_allow_html=True)
    _render_alerts_body(df)
