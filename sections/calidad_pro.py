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
    DIM_LABEL_MAP,
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
        <div class="editorial-container mb-2" style="font-size: 0.95rem;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px">
            <span class="material-symbols-outlined" aria-hidden="true"
                  style="color:var(--teal);font-size:20px">monitoring</span>
            <span class="eyebrow" style="margin:0;">Cobertura del Pipeline</span>
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
        }
        fig_cov.update_layout(**cov_layout)
        st.plotly_chart(fig_cov, use_container_width=True)

        st.markdown(f"""
        <div class="d-flex justify-between" style="margin-top:4px">
            <span style="font-size:12px;color:var(--muted)">
                {pct:.1f}% cobertura
            </span>
            <span style="font-size:12px;color:var(--muted)">
                {elapsed:.0f}s total
            </span>
        </div>
        </div>
        """, unsafe_allow_html=True)

    with col_donut:
        st.markdown("""
        <div class="editorial-container mb-2" style="font-size: 0.95rem;">
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px">
            <span class="material-symbols-outlined" aria-hidden="true"
                  style="color:var(--rose);font-size:20px">error_outline</span>
            <span class="eyebrow" style="margin:0;">Distribucion de Fallos</span>
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
            }
            fig_donut.update_layout(**donut_layout)
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.markdown("""
            <div style="text-align:center;padding:24px;color:var(--teal-light)">
                <span class="material-symbols-outlined"
                      aria-hidden="true" style="font-size:36px">
                    check_circle
                </span>
                <p style="margin:8px 0 0;font-size:13px;color:var(--muted)">
                    Sin fallos de extraccion
                </p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def _render_dimension_heatmap(
    df: pd.DataFrame, plotly_layout: dict, theme: str,
) -> None:
    """Heatmap de dimensiones ISO por categoria del catalogo."""
    if df.empty:
        return

    _dim_map = {k: v for k, v in DIM_LABEL_MAP.items() if k != "score_global"}
    available = {k: v for k, v in _dim_map.items() if k in df.columns}
    if not available:
        return

    grouped = (
        df.groupby("categoria")[list(available.keys())]
        .mean()
        .rename(columns=available)
        .sort_index()
    )
    if grouped.empty:
        return

    t = PLOTLY_THEMES.get(theme, PLOTLY_THEMES["dark"])

    st.markdown("""
    <div class="editorial-container mt-5">
    <h2>Dimensiones por Categoria</h2>
    <p>The following heatmap illustrates the density of compliance across standard ISO dimensions, grouped by semantic categories in the data catalog.</p>
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

    # --- HEADER ---
    st.markdown(f"""
    <div class="editorial-header fade-up">
        <div class="editorial-meta mb-4">
            <span>Análisis Avanzado</span>
            <span>Gobernanza Pro</span>
        </div>
        <h1 class="editorial-title">Diagnóstico Transversal de Calidad</h1>
        <p class="editorial-subtitle">
            Un análisis profundo sobre la madurez de los datos abiertos. Adoptamos el estándar <strong>ISO/IEC 25012:2008</strong> como motor de auditoría automatizada.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # --- 1. KPIs RESUMEN ---
    stats = {
        "total": len(df),
        "score": float(df["score_global"].mean()) if not df.empty else 0.0
    }
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="kpi-card kpi-card--left excellent">
            <div class="kpi-value">{stats['score']:.1f}%</div>
            <div class="kpi-label">Salud Global</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="kpi-card kpi-card--left neutral">
            <div class="kpi-value">{stats['total']}</div>
            <div class="kpi-label">Datasets Auditados</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        status_label = "Óptima" if stats['score'] >= 85 else "En Riesgo"
        status_cls = "excellent" if stats['score'] >= 85 else "poor"
        st.markdown(f"""
        <div class="kpi-card kpi-card--left {status_cls}">
            <div class="kpi-value">{status_label}</div>
            <div class="kpi-label">Condición General</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # Expander para metodologia
    with st.expander("Metodologia Tecnica y Calculo", icon=":material/menu_book:"):
        st.info(
            "Los puntajes se calculan mediante un sistema de penalizacion "
            "ponderada sobre cada recurso del catalogo CKAN. Se normalizan "
            "en escala 0-100 con 7 dimensiones ISO 25012: Completitud (30%), "
            "Exactitud (25%), Consistencia (15%), Documentacion (10%), "
            "Unicidad (8%), Apertura (7%) y Puntualidad (5%).\n\n"
            "Para actualizar los datos ejecuta el pipeline desde terminal: "
            "`python pipeline/refresh_engine.py --force`"
        )

    st.write("")

    # --- 1. COBERTURA DEL PIPELINE ---
    coverage = load_coverage_report()
    if coverage is not None:
        _render_pipeline_coverage(coverage, plotly_layout, theme)
        st.markdown(
            "<div class='divider' style='margin:2rem auto;width:100%'></div>",
            unsafe_allow_html=True,
        )

    # --- 1c. HEATMAP DIMENSIONES POR CATEGORIA ---
    _render_dimension_heatmap(df, plotly_layout, theme)
    st.markdown(
        "<div class='divider' style='margin:2rem auto;width:100%'></div>",
        unsafe_allow_html=True,
    )

    # --- 2. MAPA RADIAL DE DATASETS ---
    st.markdown("""
    <div class="editorial-container mt-5">
        <h2>Treemap de Datasets</h2>
        <p>A hierarchical representation of dataset classifications by category.</p>
    </div>
    <div class="editorial-figure">
    """, unsafe_allow_html=True)

    if not df_enriched.empty and "clasificacion" in df_enriched.columns:
        data_sunburst = (
            df_enriched.groupby(["categoria", "clasificacion"])
            .size()
            .reset_index(name="Valor")
        )
        data_sunburst["Centro"] = "Nuevo Leon"

        fig_sun = px.treemap(
            data_sunburst,
            path=["Centro", "categoria", "clasificacion"],
            values="Valor",
            color="Valor",
            color_continuous_scale=[
                [0, "rgba(56, 168, 149, 0.2)"],
                [1, "rgba(56, 168, 149, 1)"],
            ],
        )

        _sun_layout = {
            **plotly_layout,
            "margin": dict(t=20, l=10, r=10, b=10),
            "height": 480,
        }
        fig_sun.update_layout(**_sun_layout)
        fig_sun.update_traces(
            textinfo="label+value",
        )
        st.plotly_chart(fig_sun, use_container_width=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:24px;color:var(--muted)">
            <p style="font-size:13px">Sin datos para renderizar el treemap.</p>
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
