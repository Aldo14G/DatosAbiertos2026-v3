# sections/avanzado.py
import streamlit as st
import pandas as pd
import plotly.express as px

def render_gauge_svg(value: float, label: str, badge: str,
                     color_class: str) -> str:
    """
    Replica EXACTAMENTE el gauge SVG del Análisis Data Science de Stitch.
    """
    colors = {
        "tertiary" : ("#006d2a", "rgba(0,109,42,0.10)", "#006d2a"),
        "secondary": ("#2a5bb3", "rgba(42,91,179,0.10)", "#2a5bb3"),
        "primary"  : ("#005bbf", "rgba(0,91,191,0.10)",  "#005bbf"),
        "error"    : ("#ba1a1a", "rgba(186,26,26,0.10)",  "#ba1a1a"),
    }
    stroke_color, badge_bg, badge_text = colors.get(color_class, colors["primary"])
    # Para stroke-dasharray en radio 15.9155 el perímetro es exactamente 100
    dasharray = f"{value}, 100"

    return f"""
    <div style="background:#f4f3f7;border-radius:12px;padding:24px;
                display:flex;flex-direction:column;align-items:center;
                border:1px solid transparent;transition:border-color 0.2s"
         onmouseover="this.style.borderColor='#dadce0'"
         onmouseout="this.style.borderColor='transparent'">
        <span style="font-size:11px;font-weight:700;text-transform:uppercase;
                     letter-spacing:0.1em;color:#414754;margin-bottom:16px">{label}</span>
        <div style="position:relative;width:128px;height:128px;margin-bottom:16px">
            <svg style="width:100%;height:100%;transform:rotate(-90deg)"
                 viewBox="0 0 36 36">
                <!-- Track -->
                <circle cx="18" cy="18" r="15.9155"
                    fill="none" stroke="#e3e2e6" stroke-width="3"/>
                <!-- Progress -->
                <circle cx="18" cy="18" r="15.9155"
                    fill="none"
                    stroke="{stroke_color}"
                    stroke-width="3"
                    stroke-dasharray="{dasharray}"
                    stroke-linecap="round"/>
            </svg>
            <div style="position:absolute;inset:0;display:flex;align-items:center;
                        justify-content:center">
                <span style="font-size:24px;font-weight:700;color:#1a1b1e">{value:.0f}%</span>
            </div>
        </div>
        <span style="padding:4px 12px;border-radius:9999px;font-size:11px;font-weight:700;
                     background:{badge_bg};color:{badge_text}">{badge}</span>
    </div>
    """


def render_avanzado(df: pd.DataFrame, tokens: dict):
    st.markdown("""
    <h2 style="font-size:40px;font-weight:800;letter-spacing:-0.02em;
               font-family:'Plus Jakarta Sans',sans-serif;color:#1a1b1e;margin-bottom:8px">
        Análisis de Data Science
    </h2>
    <p style="color:#414754;max-width:640px;margin-bottom:32px">
        Diagnóstico estadístico de la gobernanza, outliers y dispersión mediante métricas avanzadas.
    </p>
    """, unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(render_gauge_svg(92, "COMPLETITUD ISO", "OPTIMAL", "tertiary"), unsafe_allow_html=True)
    c2.markdown(render_gauge_svg(78, "EXACTITUD NORMAL", "STABLE", "secondary"), unsafe_allow_html=True)
    c3.markdown(render_gauge_svg(65, "CONSISTENCIA DATA", "REGULAR", "primary"), unsafe_allow_html=True)
    c4.markdown(render_gauge_svg(42, "UNICIDAD ALERTA", "CRITICAL", "error"), unsafe_allow_html=True)

    st.markdown("<hr style='border:none;border-top:1px solid rgba(193,198,214,0.3);margin:40px 0;'>", unsafe_allow_html=True)

    # Gráfico de Correlación
    st.markdown("<h3>Correlación de Dimensiones</h3>", unsafe_allow_html=True)
    if not df.empty and 'score_global' in df.columns:
        cols_numericas = df.select_dtypes(include=['float64', 'int64']).columns
        if len(cols_numericas) > 1:
            matriz_corr = df[cols_numericas].corr()
            fig = px.imshow(matriz_corr,
                            text_auto=".2f",
                            aspect="auto",
                            color_continuous_scale="RdBu",
                            zmin=-1, zmax=1)
            fig.update_layout(
                paper_bgcolor="white", plot_bgcolor="white",
                margin=dict(l=0, r=0, t=30, b=0),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
