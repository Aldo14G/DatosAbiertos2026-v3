# sections/alertas.py
import streamlit as st
import pandas as pd


def _recomendaciones(row: dict) -> list[str]:
    """
    Genera recomendaciones específicas según qué dimensiones están por debajo
    del umbral. Máximo 4 acciones ordenadas por impacto.
    """
    recs = []
    comp  = row.get("comp_completitud_global_pct", 100) or 100
    acc   = row.get("acc_score_accuracy_pct",      100) or 100
    cons  = row.get("cons_score_consistency_pct",  100) or 100
    uniq  = row.get("uniq_score_uniqueness_pct",   100) or 100
    time_ = row.get("time_score_timeliness_pct",    50) or 50

    if comp < 70:
        recs.append(
            "Completar los campos obligatorios: revisar nulos en columnas clave "
            "y validar que el esquema de metadatos cumpla el estándar CKAN."
        )
    if acc < 70:
        recs.append(
            "Estandarizar tipos de datos: eliminar espacios al inicio/fin de celdas "
            "y separar columnas con datos mixtos (texto + numérico)."
        )
    if cons < 70:
        recs.append(
            "Resolver inconsistencias: normalizar valores de texto (mayúsculas, tildes) "
            "y revisar outliers estadísticos en columnas numéricas."
        )
    if uniq < 70:
        recs.append(
            "Eliminar registros duplicados e implementar una clave primaria única "
            "para garantizar la trazabilidad de cada fila."
        )
    if time_ < 70:
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


def render_alerta_card(row: dict) -> str:
    """
    Replica la alert card de Stitch con datos reales y dimensiones correctas.
    Las 4 barras muestran: COMPLETITUD, EXACTITUD, CONSISTENCIA, PUNTUALIDAD.
    """
    dims = [
        ("COMPLETITUD",  row.get("comp_completitud_global_pct", 0) or 0),
        ("EXACTITUD",    row.get("acc_score_accuracy_pct",      0) or 0),
        ("CONSISTENCIA", row.get("cons_score_consistency_pct",  0) or 0),
        ("PUNTUALIDAD",  row.get("time_score_timeliness_pct",  50) or 50),
    ]

    bars_html = ""
    for dim_name, val in dims:
        bar_color = "#d93025" if val < 70 else "#e37400" if val < 90 else "#1e8e3e"
        bars_html += f"""
        <div style="margin-bottom:14px">
            <div style="display:flex;justify-content:space-between;
                        font-size:11px;font-weight:700;color:#5f6368;margin-bottom:5px">
                <span>{dim_name}</span>
                <span>{val:.0f}%</span>
            </div>
            <div style="height:6px;background:#f1f3f4;border-radius:9999px;overflow:hidden">
                <div style="width:{min(val, 100):.0f}%;height:100%;
                            background:{bar_color};border-radius:9999px"></div>
            </div>
        </div>"""

    ds_name = str(row.get("dataset", "N/A"))
    if not ds_name or ds_name == "nan":
        ds_name = "N/A"
    slug    = str(row.get("slug", "")).strip() or ds_name.replace(" ", "-").lower()
    url     = f"https://catalogodatos.nl.gob.mx/dataset/{slug}"
    score   = float(row.get("score_global", 0) or 0)
    org     = str(row.get("organizacion", ""))[:65]
    cat     = str(row.get("categoria", ""))

    recs     = _recomendaciones(row)
    recs_html = "".join([
        f"""<li style="display:flex;align-items:flex-start;gap:12px;
                       font-size:13px;color:#3c4043;line-height:1.6">
            <span style="flex-shrink:0;width:20px;height:20px;border-radius:50%;
                         background:#f1f3f4;display:flex;align-items:center;
                         justify-content:center;font-size:10px;font-weight:700;
                         color:#5f6368">{i+1}</span>
            {rec}
        </li>"""
        for i, rec in enumerate(recs)
    ])

    return f"""
    <div style="background:#ffffff;border:1px solid #dadce0;
                border-left:6px solid #d93025;border-radius:0 12px 12px 0;
                overflow:hidden;margin-bottom:24px">
        <div style="padding:28px 32px">
            <!-- Header -->
            <div style="display:flex;justify-content:space-between;
                        align-items:flex-start;margin-bottom:20px">
                <div style="flex:1;min-width:0;margin-right:16px">
                    <h3 style="font-size:17px;font-weight:700;
                               font-family:'Plus Jakarta Sans',sans-serif;
                               color:#202124;margin:0 0 4px;
                               overflow:hidden;text-overflow:ellipsis;
                               white-space:nowrap"
                        title="{ds_name}">{ds_name[:55]}</h3>
                    <p style="font-size:12px;color:#5f6368;margin:0">{org}</p>
                    <span style="display:inline-block;margin-top:6px;padding:2px 8px;
                                 background:#f4f3f7;border-radius:4px;
                                 font-size:10px;font-weight:700;color:#414754;
                                 text-transform:uppercase;letter-spacing:0.05em">
                        {cat}
                    </span>
                </div>
                <div style="text-align:right;flex-shrink:0">
                    <div style="font-size:36px;font-weight:800;
                                font-family:'Plus Jakarta Sans',sans-serif;
                                color:#d93025;line-height:1">{score:.1f}%</div>
                    <div style="font-size:10px;font-weight:700;
                                text-transform:uppercase;letter-spacing:0.08em;
                                color:#5f6368;margin-top:4px">Score de Calidad</div>
                </div>
            </div>
            <!-- Barras de dimensiones -->
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px 24px;
                        margin-bottom:20px">
                {bars_html}
            </div>
            <!-- Recomendaciones -->
            <div style="padding-top:20px;border-top:1px solid #f1f0f4">
                <h4 style="font-size:11px;font-weight:700;text-transform:uppercase;
                           letter-spacing:0.08em;color:#5f6368;margin-bottom:12px">
                    Acciones recomendadas
                </h4>
                <ol style="padding:0;list-style:none;
                           display:flex;flex-direction:column;gap:10px">
                    {recs_html}
                </ol>
            </div>
        </div>
        <!-- Footer -->
        <div style="background:rgba(248,249,250,0.5);padding:14px 32px;
                    border-top:1px solid #f1f0f4">
            <a href="{url}" target="_blank"
               style="color:#1a73e8;font-weight:600;font-size:14px;
                      text-decoration:none">
                Ver en catalogodatos.nl.gob.mx →
            </a>
        </div>
    </div>
    """


def render_alertas(df: pd.DataFrame, tokens: dict):
    """Pantalla 4: Monitoreo de Alertas Críticas."""

    st.markdown("""
    <h2 style="font-size:40px;font-weight:800;letter-spacing:-0.02em;
               font-family:'Plus Jakarta Sans',sans-serif;color:#1a1b1e;margin-bottom:8px">
        Monitoreo de Alertas Críticas
    </h2>
    <p style="color:#414754;max-width:640px;margin-bottom:32px">
        Datasets con score de calidad por debajo del umbral de gobernanza (70%).
        Basado en ISO/IEC 25012:2008.
    </p>
    """, unsafe_allow_html=True)

    umbral = 70.0
    if "score_global" not in df.columns:
        st.warning("No se encontró la columna `score_global` en los datos.")
        return

    df_alertas = df[df["score_global"] < umbral].sort_values("score_global")
    n = len(df_alertas)

    if n == 0:
        st.markdown("""
        <div style="background:#e6f4ea;border:1px solid #34a853;border-radius:12px;
                    padding:24px 32px;display:flex;align-items:center;gap:16px">
            <span style="font-size:28px">✓</span>
            <div>
                <div style="font-size:16px;font-weight:600;color:#1e8e3e">
                    ¡Ningún dataset está por debajo del umbral de calidad (70%)!
                </div>
                <div style="font-size:13px;color:#2e7d32;margin-top:4px">
                    El catálogo cumple el estándar mínimo de gobernanza ISO 25012.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f"""
    <div style="background:#fce8e6;border:1px solid #f28b82;border-radius:12px;
                padding:16px 24px;display:flex;align-items:center;gap:16px;
                margin-bottom:32px">
        <span style="font-size:24px">⚠️</span>
        <div>
            <div style="font-size:18px;font-weight:700;color:#d93025">
                {n} dataset{"s" if n > 1 else ""}&nbsp;
                {"requieren" if n > 1 else "requiere"} intervención inmediata
            </div>
            <div style="font-size:13px;color:#c62828;margin-top:4px">
                Score de calidad inferior al 70% — Umbral mínimo de gobernanza ISO 25012
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Grid de 2 columnas de tarjetas
    cols = st.columns(2)
    for i, (_, row) in enumerate(df_alertas.iterrows()):
        cols[i % 2].markdown(render_alerta_card(row.to_dict()), unsafe_allow_html=True)
