"""Seccion Calidad Pro -- Analizador Avanzado de Calidad de Datos.

Diagnostico transversal ISO/IEC 25012, ISO 8000 y DAMA-DMBOK 2.0.
Fuente canonica: Pipeline A (df via load_results). Pipeline B (avanzado)
se integra como overlay suplementario via merge_advanced_overlay.
Usa tokens semanticos del design system NL 2026 (Midnight/Teal/Gold/Rose).
"""

import html as _html

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_layer import (
    agg_dim_means_by,
    load_advanced_catalog_stats,
    load_coverage_report,
    merge_advanced_overlay,
)
from styles.global_css import PLOTLY_THEMES, get_plotly_layout

# ── Helpers internos ─────────────────────────────────────────────


def _render_pipeline_coverage(
    coverage: dict, plotly_layout: dict, theme: str,
) -> None:
    """Barra de cobertura del pipeline + donut de fallos."""
    total = coverage.get("total_catalogo", 0)
    exitosos = coverage.get("procesados_exitosos", 0)
    fallidos = coverage.get("fallidos", 0)
    elapsed = coverage.get("elapsed_total_s", 0)
    pct = coverage.get("cobertura_pct", 0)
    t = PLOTLY_THEMES.get(theme, PLOTLY_THEMES["dark"])

    col_bar, col_donut = st.columns([1.1, 1])

    with col_bar:
        st.markdown("""
        <div class="editorial-container mb-2">
        <div class="nl-panel-head">
            <span class="material-symbols-outlined icon-teal-sm" aria-hidden="true">monitoring</span>
            <span class="eyebrow">Cobertura del Pipeline</span>
        </div>
        """, unsafe_allow_html=True)

        fig_cov = go.Figure()
        fig_cov.add_trace(go.Bar(
            x=[exitosos], y=["Pipeline"], orientation="h",
            name=f"Exitosos ({exitosos})",
            marker_color=t["excellent"],
            text=[f"{exitosos}"], textposition="inside",
            textfont=dict(color=t["text_on_bar"], size=13),
        ))
        if fallidos > 0:
            fig_cov.add_trace(go.Bar(
                x=[fallidos], y=["Pipeline"], orientation="h",
                name=f"Fallidos ({fallidos})",
                marker_color=t["poor"],
                text=[f"{fallidos}"], textposition="inside",
                textfont=dict(color=t["text_on_bar"], size=13),
            ))

        cov_layout = {
            **plotly_layout,
            "barmode": "stack",
            "height": 120,
            "margin": dict(t=10, l=0, r=20, b=10),
            "showlegend": True,
            "legend": dict(
                orientation="h", yanchor="bottom", y=1.02,
                xanchor="left", x=0,
                font=dict(size=11, color=t["font_color"]),
            ),
            "xaxis": dict(
                showgrid=False, showticklabels=False, range=[0, total],
            ),
            "yaxis": dict(showgrid=False, showticklabels=False),
            "transition": dict(duration=600, easing="cubic-in-out"),
        }
        fig_cov.update_layout(**cov_layout)
        st.plotly_chart(fig_cov, use_container_width=True)

        st.markdown(f"""
        <div class="d-flex justify-between" style="margin-top:4px">
            <span class="text-muted-xs">{pct:.1f}% cobertura</span>
            <span class="text-muted-xs">{elapsed:.0f}s total</span>
        </div>
        </div>
        """, unsafe_allow_html=True)

    with col_donut:
        st.markdown("""
        <div class="editorial-container mb-2">
        <div class="nl-panel-head">
            <span class="material-symbols-outlined icon-rose-sm" aria-hidden="true">error_outline</span>
            <span class="eyebrow">Distribución de Fallos</span>
        </div>
        """, unsafe_allow_html=True)

        if fallidos > 0:
            failed_details = coverage.get("failed_details", [])
            cause_counts: dict[str, int] = {}
            for item in failed_details:
                reason = item.get("reason", "")
                if reason.startswith("Download failed"):
                    key = "Mismatch formato"
                elif reason == "No URL":
                    key = "Sin URL"
                else:
                    key = "Otro"
                cause_counts[key] = cause_counts.get(key, 0) + 1

            fig_donut = go.Figure(go.Bar(
                x=list(cause_counts.values()),
                y=list(cause_counts.keys()),
                orientation="h",
                marker_color=t["poor"],
                text=list(cause_counts.values()),
                textposition="auto",
                textfont=dict(size=12, color=t["font_color"]),
            ))
            donut_layout = {
                **plotly_layout,
                "height": 160,
                "margin": dict(t=10, l=10, r=20, b=10),
                "showlegend": False,
                "xaxis": dict(showgrid=False, visible=False),
                "yaxis": dict(autorange="reversed", tickfont=dict(size=11, color=t["font_color"])),
                "transition": dict(duration=600, easing="cubic-in-out"),
            }
            fig_donut.update_layout(**donut_layout)
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.markdown("""
            <div class="nl-empty-state nl-empty-state--success">
                <span class="material-symbols-outlined nl-empty-state-icon" aria-hidden="true">check_circle</span>
                <p class="nl-empty-state-text">Sin fallos de extracción</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def _render_dimension_heatmap(
    df: pd.DataFrame, plotly_layout: dict, theme: str,
) -> None:
    """Heatmap de dimensiones ISO por categoria del catalogo."""
    if df.empty:
        return

    grouped = agg_dim_means_by(df, "categoria", rename=True).sort_index()
    if grouped.empty:
        return

    t = PLOTLY_THEMES.get(theme, PLOTLY_THEMES["dark"])

    st.markdown("""
    <div class="editorial-container mt-5">
    <h2 class="section-title">Dimensiones por Categoría</h2>
    <p>El mapa de calor muestra el nivel de cumplimiento por dimensión ISO en cada categoría del catálogo. Colores más brillantes indican mayor madurez.</p>
    </div>
    <div class="editorial-figure">
    """, unsafe_allow_html=True)

    n_cats = len(grouped)
    fig_heat = go.Figure(go.Heatmap(
        z=grouped.values,
        x=list(grouped.columns),
        y=list(grouped.index),
        colorscale=[
            [0, t["poor"]],
            [0.5, t["good"]],
            [1, t["excellent"]],
        ],
        text=[[f"{v:.0f}%" for v in row] for row in grouped.values],
        texttemplate="%{text}",
        textfont=dict(size=11, color=t["text_on_bar"]),
        colorbar=dict(
            title=dict(text="Score %", font=dict(color=t["font_color"])),
            ticksuffix="%", len=0.8,
            tickfont=dict(color=t["font_color"]),
        ),
        hovertemplate=(
            "<b>%{y}</b><br>%{x}: %{z:.1f}%<extra></extra>"
        ),
    ))

    heat_layout = {
        **plotly_layout,
        "height": max(400, n_cats * 30 + 100),
        "margin": dict(t=20, l=200, r=60, b=30),
        "xaxis": dict(
            side="top", tickfont=dict(size=11, color=t["font_color"]),
        ),
        "yaxis": dict(
            tickfont=dict(size=11, color=t["font_color"]),
            autorange="reversed",
        ),
        "transition": dict(duration=600, easing="cubic-in-out"),
    }
    fig_heat.update_layout(**heat_layout)
    st.plotly_chart(fig_heat, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ── Render principal ─────────────────────────────────────────────


def render_calidad_pro(df: pd.DataFrame, tokens: dict) -> None:
    """Renderiza la seccion Calidad Pro usando Pipeline A como fuente canonica."""
    theme = tokens.get("theme", "dark")
    plotly_layout = get_plotly_layout(theme)

    # ── Datos unificados ──────────────────────────────────────
    df_enriched = merge_advanced_overlay(df)
    adv_stats = load_advanced_catalog_stats()
    has_advanced = adv_stats is not None

    # Header eliminado — se delega al wrapper render_dashboards (evita doble título).

    # --- 1. KPIs RESUMEN ---
    stats = {
        "total": len(df),
        "score": float(df["score_global"].mean()) if not df.empty else 0.0
    }

    _total = stats["total"] or 1
    _n_excellent = int((df["score_global"] >= 85).sum()) if "score_global" in df.columns else 0
    _n_good = int(((df["score_global"] >= 60) & (df["score_global"] < 85)).sum()) if "score_global" in df.columns else 0
    _n_critical = int((df["score_global"] < 60).sum()) if "score_global" in df.columns else 0
    _pct_excellent = _n_excellent / _total * 100
    _pct_good = _n_good / _total * 100
    _pct_critical = _n_critical / _total * 100
    _score_color = "teal" if stats["score"] >= 75 else "rose"

    st.markdown(f"""
<div class="nl-distband nl-reveal">
  <div class="nl-distband-header">
    <span class="nl-distband-score nl-distband-score--{_score_color}">{stats['score']:.1f}</span>
    <div class="nl-distband-meta">
      <span class="nl-distband-label">Salud promedio del catálogo</span>
      <span class="nl-distband-sub">{stats['total']} datasets auditados</span>
    </div>
  </div>
  <div class="nl-distband-track" role="group" aria-label="Distribución por niveles de calidad">
    <div class="nl-distband-seg nl-distband-seg--excellent"
         style="width:{_pct_excellent:.1f}%"
         role="progressbar" aria-valuenow="{_n_excellent}" aria-valuemin="0" aria-valuemax="{_total}"
         title="Excelentes: {_n_excellent}"></div>
    <div class="nl-distband-seg nl-distband-seg--good"
         style="width:{_pct_good:.1f}%"
         role="progressbar" aria-valuenow="{_n_good}" aria-valuemin="0" aria-valuemax="{_total}"
         title="En desarrollo: {_n_good}"></div>
    <div class="nl-distband-seg nl-distband-seg--critical"
         style="width:{_pct_critical:.1f}%"
         role="progressbar" aria-valuenow="{_n_critical}" aria-valuemin="0" aria-valuemax="{_total}"
         title="Críticos: {_n_critical}"></div>
  </div>
  <div class="nl-distband-legend">
    <span class="nl-distband-legend-item">
      <span class="nl-distband-dot nl-distband-dot--excellent" aria-hidden="true"></span>
      {_n_excellent} excelentes ({_pct_excellent:.0f}%)
    </span>
    <span class="nl-distband-legend-item">
      <span class="nl-distband-dot nl-distband-dot--good" aria-hidden="true"></span>
      {_n_good} en desarrollo ({_pct_good:.0f}%)
    </span>
    <span class="nl-distband-legend-item">
      <span class="nl-distband-dot nl-distband-dot--critical" aria-hidden="true"></span>
      {_n_critical} críticos ({_pct_critical:.0f}%)
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

    st.write("")

    # Expander para metodologia
    with st.expander("Metodologia Tecnica y Calculo", icon=":material/menu_book:"):
        st.markdown("""
<div class="nl-insight-card nl-insight-neutral">
<p>Los puntajes se calculan mediante un sistema de penalización ponderada sobre cada recurso del catálogo CKAN. Se normalizan en escala 0-100 con 7 dimensiones ISO 25012: Completitud (30%), Exactitud (25%), Consistencia (15%), Documentación (10%), Unicidad (8%), Apertura (7%) y Puntualidad (5%).</p>
<p class="nl-weight-desc">Actualizar datos: <code class="nl-code-inline">python pipeline/refresh_engine.py --force</code></p>
</div>
""", unsafe_allow_html=True)

    st.write("")

    # --- 1. COBERTURA DEL PIPELINE ---
    coverage = load_coverage_report()
    if coverage is not None:
        _render_pipeline_coverage(coverage, plotly_layout, theme)
        st.markdown(
            "<div class='divider'></div>",
            unsafe_allow_html=True,
        )

    # --- 1c. HEATMAP DIMENSIONES POR CATEGORIA ---
    _render_dimension_heatmap(df, plotly_layout, theme)
    st.markdown(
        "<div class='divider'></div>",
        unsafe_allow_html=True,
    )

    # --- 2. TREEMAP DE DATASETS ---
    st.markdown("""
<div class="editorial-container mt-5">
<h2 class="section-title">Treemap de Datasets</h2>
<p>Cada bloque es un dataset. El <strong class="accent-teal">color verde</strong> indica calidad excelente; <strong class="accent-gold">dorado</strong>, aceptable; <strong class="accent-rose">rojo</strong>, crítico. El tamaño refleja cuántos datasets hay por categoría.</p>
</div>
<div class="editorial-figure">
""", unsafe_allow_html=True)

    if "clasificacion" not in df_enriched.columns and "score_global" in df_enriched.columns:
        from config import UMBRAL_EXCELENTE
        from config import UMBRAL_GOBERNANZA as _UMBRAL_GOB

        def _classify(s: float) -> str:
            if s >= UMBRAL_EXCELENTE:
                return "Excelente"
            if s >= _UMBRAL_GOB:
                return "Aceptable"
            return "Crítico"

        df_enriched = df_enriched.copy()
        df_enriched["clasificacion"] = df_enriched["score_global"].apply(_classify)

    if not df_enriched.empty and "clasificacion" in df_enriched.columns:
        t = PLOTLY_THEMES.get(theme, PLOTLY_THEMES["dark"])

        # Null-safe frame — expose gaps visually, never drop rows silently
        df_tree = df_enriched.copy()
        df_tree["categoria"] = (
            df_tree["categoria"].fillna("Sin Categoría").replace("", "Sin Categoría")
            if "categoria" in df_tree.columns
            else pd.Series("Sin Categoría", index=df_tree.index)
        )
        df_tree["clasificacion"] = (
            df_tree["clasificacion"].fillna("Sin Clasificar").replace("", "Sin Clasificar")
        )

        fig_tree = px.treemap(
            df_tree,
            path=[px.Constant("Nuevo León"), "categoria", "dataset"],
            values="score_global",
            color="clasificacion",
            color_discrete_map={
                "Excelente":    t["excellent"],
                "Aceptable":    t["good"],
                "Crítico":      t["poor"],
                "Sin Clasificar": t["annotation_font"],
            },
            custom_data=["score_global", "organizacion"],
        )
        fig_tree.update_traces(
            textinfo="label",
            textfont=dict(size=12, family="DM Sans, sans-serif"),
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Organización: %{customdata[1]}<br>"
                "Score: %{customdata[0]:.1f}%"
                "<extra></extra>"
            ),
            marker=dict(line=dict(width=0.5, color=t["paper_bgcolor"])),
        )
        fig_tree.update_layout(
            **{
                **plotly_layout,
                "margin": dict(t=20, l=10, r=10, b=10),
                "height": 600,
                "showlegend": False,
                "transition": dict(duration=600, easing="cubic-in-out"),
            }
        )
        st.plotly_chart(fig_tree, use_container_width=True)

        st.markdown("""
<div class="nl-treemap-legend">
<span class="nl-treemap-chip nl-treemap-chip--excellent">Excelente</span>
<span class="nl-treemap-chip nl-treemap-chip--good">Aceptable</span>
<span class="nl-treemap-chip nl-treemap-chip--poor">Crítico</span>
</div>
""", unsafe_allow_html=True)

        n_criticos = int((df_tree["clasificacion"] == "Crítico").sum())
        n_excelentes = int((df_tree["clasificacion"] == "Excelente").sum())
        top_cat = _html.escape(str(df_tree["categoria"].value_counts().index[0]))
        st.markdown(f"""
<div class="nl-chart-insight nl-reveal">
<span class="material-symbols-outlined nl-chart-insight-icon" aria-hidden="true">insights</span>
<p class="nl-chart-insight-text">
Categoría más representada: <strong>{top_cat}</strong>.
Hay <strong>{n_excelentes}</strong> datasets de calidad excelente y <strong class="accent-rose">{n_criticos}</strong> críticos que requieren atención inmediata.
</p>
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown("""
<div class="nl-empty-state">
<p class="nl-empty-state-text">Sin datos para renderizar el treemap.</p>
</div>
""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # --- 3. REPORTE COMPLETO ---
    if not df_enriched.empty:
        with st.expander(
            "Ver Auditoria Maestra (Dataset por Dataset)",
            icon=":material/table_chart:",
        ):
            display_cols = [
                "dataset", "organizacion", "categoria", "score_global",
                "clasificacion",
            ]
            col_names = {
                "dataset": "Dataset",
                "organizacion": "Organizacion",
                "categoria": "Categoria",
                "score_global": "Global",
                "clasificacion": "Clasificacion",
            }
            col_config = {
                "Global": st.column_config.ProgressColumn(
                    "Calificacion Final",
                    format="%.1f%%",
                    min_value=0,
                    max_value=100,
                ),
            }

            # Agregar columnas multi-framework si hay overlay
            if has_advanced:
                for col in ("score_iso_25012", "score_iso_8000", "score_dama"):
                    if col in df_enriched.columns:
                        display_cols.append(col)
                col_names["score_iso_25012"] = "ISO 25012"
                col_names["score_iso_8000"] = "ISO 8000"
                col_names["score_dama"] = "DAMA"
                col_config["ISO 25012"] = st.column_config.NumberColumn(
                    format="%.1f",
                )
                col_config["ISO 8000"] = st.column_config.NumberColumn(
                    format="%.1f",
                )
                col_config["DAMA"] = st.column_config.NumberColumn(
                    format="%.1f",
                )

            existing_cols = [c for c in display_cols if c in df_enriched.columns]
            df_display = (
                df_enriched[existing_cols]
                .rename(columns=col_names)
                .sort_values(by="Global", ascending=False)
            )

            st.dataframe(
                df_display,
                use_container_width=True,
                height=400,
                hide_index=True,
                column_config=col_config,
            )
