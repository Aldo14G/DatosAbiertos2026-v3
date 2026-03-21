# sections/alertas.py
import streamlit as st
import pandas as pd

def render_alerta_card(row: pd.Series) -> str:
    """
    Replica EXACTAMENTE la alert card del HTML Stitch.
    Dimensiones que muestra Stitch: INTEGRIDAD, FRECUENCIA, FORMATO, CONSISTENCIA
    """
    # Mapeo a las variables de calidad en el dataframe (usamos las disponibles)
    dims = [
        ("INTEGRIDAD",   row.get("comp_completitud_global_pct", 0) or 0),
        ("FRECUENCIA",   row.get("acc_score_accuracy_pct", 0) or 0),
        ("FORMATO",      row.get("form_score_format_pct", 0) or 0),
        ("CONSISTENCIA", row.get("cons_score_consistency_pct", 0) or 0),
    ]
    bars_html = ""
    for dim_name, val in dims:
        bar_color = "#d93025" if val < 70 else "#e37400" if val < 90 else "#1e8e3e"
        bars_html += f"""
        <div style="margin-bottom:16px">
            <div style="display:flex;justify-content:space-between;
                        font-size:11px;font-weight:700;color:#5f6368;margin-bottom:6px">
                <span>{dim_name}</span><span>{val:.0f}%</span>
            </div>
            <div style="height:6px;background:#f1f3f4;border-radius:9999px;overflow:hidden">
                <div style="width:{min(val,100):.0f}%;height:100%;
                            background:{bar_color};border-radius:9999px"></div>
            </div>
        </div>"""

    # Fix: df.to_dict() returns rows. Using `.get` on dict handles missing values securely.
    ds_name = row.get("dataset", "N/A")
    if isinstance(ds_name, float): 
        ds_name = "N/A"
        
    slug = row.get("id", ds_name.replace(" ", "-").lower()) if "id" in row else ds_name.replace(" ", "-").lower()
    url  = f"https://catalogodatos.nl.gob.mx/dataset/{slug}"
    score= row.get("score_global", 0) or 0
    org  = str(row.get("organizacion", ""))[:50]

    return f"""
    <div style="background:#ffffff;border:1px solid #dadce0;
                border-left:6px solid #d93025;border-radius:0 12px 12px 0;
                overflow:hidden;display:flex;flex-direction:column;margin-bottom:24px">
        <div style="padding:32px;flex:1">
            <div style="display:flex;justify-content:space-between;
                        align-items:flex-start;margin-bottom:24px">
                <div>
                    <h3 style="font-size:22px;font-weight:700;
                               font-family:'Plus Jakarta Sans',sans-serif;
                               color:#202124;margin:0 0 4px">{ds_name[:50]}</h3>
                    <p style="font-size:14px;color:#5f6368;margin:0">{org}</p>
                </div>
                <div style="text-align:right">
                    <div style="font-size:40px;font-weight:800;
                                font-family:'Plus Jakarta Sans',sans-serif;
                                color:#d93025;line-height:1">{score:.2f}%</div>
                    <div style="font-size:10px;font-weight:700;
                                text-transform:uppercase;letter-spacing:0.08em;
                                color:#5f6368;margin-top:4px">Score de Calidad</div>
                </div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;
                        margin-bottom:32px">
                {bars_html}
            </div>
            <div style="padding-top:24px;border-top:1px solid #f1f0f4">
                <h4 style="font-size:11px;font-weight:700;text-transform:uppercase;
                           letter-spacing:0.08em;color:#5f6368;margin-bottom:16px">
                    Acciones recomendadas
                </h4>
                <ol style="padding:0;list-style:none;display:flex;flex-direction:column;gap:12px">
                    <li style="display:flex;align-items:flex-start;gap:12px;
                               font-size:14px;color:#3c4043;line-height:1.6">
                        <span style="flex-shrink:0;width:20px;height:20px;border-radius:50%;
                                     background:#f1f3f4;display:flex;align-items:center;
                                     justify-content:center;font-size:10px;font-weight:700;
                                     color:#5f6368">1</span>
                        Validar esquemas de metadatos y campos obligatorios faltantes en {ds_name[:20]}.
                    </li>
                    <li style="display:flex;align-items:flex-start;gap:12px;
                               font-size:14px;color:#3c4043;line-height:1.6">
                        <span style="flex-shrink:0;width:20px;height:20px;border-radius:50%;
                                     background:#f1f3f4;display:flex;align-items:center;
                                     justify-content:center;font-size:10px;font-weight:700;
                                     color:#5f6368">2</span>
                        Estandarizar formatos de columna según ISO.
                    </li>
                    <li style="display:flex;align-items:flex-start;gap:12px;
                               font-size:14px;color:#3c4043;line-height:1.6">
                        <span style="flex-shrink:0;width:20px;height:20px;border-radius:50%;
                                     background:#f1f3f4;display:flex;align-items:center;
                                     justify-content:center;font-size:10px;font-weight:700;
                                     color:#5f6368">3</span>
                        Notificar al enlace técnico de la dependencia {org[:15]} vía ticket M3.
                    </li>
                </ol>
            </div>
        </div>
        <div style="background:rgba(248,249,250,0.5);padding:16px 32px;
                    border-top:1px solid #f1f0f4">
            <a href="{url}" target="_blank"
               style="color:#1a73e8;font-weight:600;font-size:14px;
                      text-decoration:none;display:flex;align-items:center;gap:8px">
                Ver en catalogodatos.nl.gob.mx →
            </a>
        </div>
    </div>
    """


def render_alertas(df: pd.DataFrame, tokens: dict):
    st.markdown("""
    <h2 style="font-size:40px;font-weight:800;letter-spacing:-0.02em;
               font-family:'Plus Jakarta Sans',sans-serif;color:#1a1b1e;margin-bottom:8px">
        Monitoreo de Alertas Críticas
    </h2>
    <p style="color:#414754;max-width:640px;margin-bottom:32px">
        Datasets con score de calidad por debajo del umbral de gobernanza (70%).
    </p>
    """, unsafe_allow_html=True)
    
    umbral_alerta = 70.0
    if 'score_global' in df.columns:
        df_alertas = df[df['score_global'] < umbral_alerta].sort_values('score_global')
    else:
        df_alertas = pd.DataFrame()

    st.markdown(f"""
    <div style="background:#fce8e6; border:1px solid #f28b82; border-radius:12px; padding:16px 24px; display:flex; align-items:center; gap:16px; margin-bottom:32px;">
        <span class="material-symbols-outlined" style="color:#d93025; font-size:24px;">warning</span>
        <div style="font-family:'Inter',sans-serif; font-size:18px; font-weight:600; color:#d93025;">{len(df_alertas)} Datasets requieren intervención inmediata</div>
    </div>
    """, unsafe_allow_html=True)

    if len(df_alertas) == 0:
        st.success("🎉 ¡Excelente! Ningún dataset está por debajo del umbral.")
        return

    # Usamos grid visual mediante st.columns para mostrar las tarjetas tal cual mockups
    cols = st.columns(2)
    for i, (_, row) in enumerate(df_alertas.iterrows()):
        col = cols[i % 2]
        col.markdown(render_alerta_card(row.to_dict()), unsafe_allow_html=True)
