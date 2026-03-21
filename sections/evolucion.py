# sections/evolucion.py
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def render_evolucion_line_chart(tokens: dict):
    """
    Réplica del line chart SVG de Stitch adaptado a Plotly.
    El diseño Stitch usa SVG inline — en Streamlit usamos Plotly
    con los mismos colores y estilos.
    """
    # Datos históricos simulados (replicar los puntos del SVG de Stitch)
    dates  = ["2023 Q1","2023 Q2","2023 Q3","2023 Q4",
               "2024 Q1","2024 Q2","2024 Q3","2024 Q4",
               "2025 Q1","2025 Q2","2025 Q3","2025 Q4",
               "2026 Q1","2026 Q2"]
    scores = [50, 52, 55, 54, 57, 63, 68, 75, 78, 81, 85, 89, 92, 94]

    fig = go.Figure()

    # Área de gradiente (replicar el fill del SVG de Stitch)
    fig.add_trace(go.Scatter(
        x=dates, y=scores,
        fill="tozeroy",
        fillcolor="rgba(26,115,232,0.08)",
        line=dict(color="#1a73e8", width=2.5),
        mode="lines+markers",
        marker=dict(size=7, color="#1a73e8", symbol="circle", line=dict(color='white', width=1)),
        name="NL Promedio",
        hovertemplate="<b>%{x}</b><br>Score: <b>%{y:.1f}%</b><extra></extra>",
    ))

    # Annotation: Lanzamiento del portal Ago 2024 (replicar Stitch)
    fig.add_vline(
        x="2024 Q3",
        line_dash="dash", line_color="#9aa0a6", line_width=1.5,
        annotation_text="Lanzamiento del portal<br>Ago 2024",
        annotation_font_size=10,
        annotation_font_color="#414754",
        annotation_bgcolor="white",
        annotation_bordercolor="#dadce0",
        annotation_borderwidth=1,
    )

    fig.update_layout(
        autosize=True,
        height=400,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="'Inter', sans-serif", color="#3c4043"),
        xaxis=dict(
            gridcolor="#f1f3f4", tickfont=dict(size=11, color="#5f6368"),
            tickangle=0,
        ),
        yaxis=dict(
            gridcolor="#f1f3f4", range=[45, 100],
            ticksuffix="%", tickfont=dict(size=11, color="#5f6368"),
            title="Score Promedio", title_font=dict(size=11, color="#414754"),
        ),
        margin=dict(l=50, r=30, t=60, b=50),
        legend=dict(
            bgcolor="white", bordercolor="#dadce0", borderwidth=1,
            font=dict(size=12), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
        ),
        showlegend=True,
    )
    return fig


def render_related_viz_cards():
    """
    Replica la sección 'Related visualizations' de Stitch (3 cards).
    Estructura idéntica al patrón de Google Cloud Blog.
    """
    cards = [
        {
            "badge": "ATRIBUTOS",
            "title": "Nivel de completitud por secretaría",
            "desc":  "Análisis de campos vacíos vs. obligatorios en cada dependencia.",
        },
        {
            "badge": "ESTANDARIZACIÓN",
            "title": "Cumplimiento de catálogos ISO",
            "desc":  "Adopción de estándares internacionales de datos geográficos.",
        },
        {
            "badge": "LATENCIA",
            "title": "Frecuencia de actualización real",
            "desc":  "Tiempos de carga declarados vs. observados en producción.",
        },
    ]
    cards_html = ""
    for card in cards:
        cards_html += f"""
        <div style="background:white;border:1px solid #dadce0;border-radius:12px;
                    overflow:hidden;transition:border-color 0.2s"
             onmouseover="this.style.borderColor='#005bbf'"
             onmouseout="this.style.borderColor='#dadce0'">
            <div style="height:120px;background:#f8f9fa;position:relative;overflow:hidden">
                <div style="position:absolute;inset:0;
                            background:linear-gradient(to top, white, transparent)"></div>
            </div>
            <div style="padding:20px">
                <span style="font-size:10px;font-weight:700;color:#1a73e8;
                             text-transform:uppercase;letter-spacing:0.08em">{card['badge']}</span>
                <h5 style="font-size:15px;font-weight:600;color:#202124;
                           margin:4px 0 8px;font-family:'Plus Jakarta Sans',sans-serif">
                    {card['title']}
                </h5>
                <p style="font-size:12px;color:#5f6368;margin:0;line-height:1.5">
                    {card['desc']}
                </p>
            </div>
        </div>"""

    return f"""
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:24px;margin-top:24px">
        {cards_html}
    </div>
    """

def render_evolucion(df: pd.DataFrame, tokens: dict):
    st.markdown("""
    <h2 style="font-size:40px;font-weight:800;letter-spacing:-0.02em;
               font-family:'Plus Jakarta Sans',sans-serif;color:#1a1b1e;margin-bottom:8px">
        Evolución Histórica
    </h2>
    <p style="color:#414754;max-width:640px;margin-bottom:32px">
        Monitoreo longitudinal de la calidad de gobernanza a través de los diversos trimestres.
    </p>
    """, unsafe_allow_html=True)
    
    t1, t2, t3, t4 = st.tabs([
        "Evolución histórica", "Perfil de calidad", 
        "Distribución", "Rankings"
    ])
    
    with t1:
        st.plotly_chart(render_evolucion_line_chart(tokens), use_container_width=True)
        st.markdown(render_related_viz_cards(), unsafe_allow_html=True)
        
    with t2:
        st.info("Gráfico de radar del perfil estandarizado.")
    with t3:
        st.info("Distribución de métricas y correlación.")
    with t4:
        st.info("Rankings y comparativas relativas.")
