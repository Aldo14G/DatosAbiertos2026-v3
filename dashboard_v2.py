import streamlit as st
import pandas as pd
import json
import plotly.express as px

st.set_page_config(page_title="Tablero M3 - Nuevo Leon", layout="wide", page_icon="📊")

# --- CARGAR TOKENS ---
with open('.antigravity/team/shared/design_tokens.json', 'r', encoding='utf-8') as f:
    tokens = json.load(f)

# --- CSS GLOBAL M3 ---
CSS_M3 = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;600;700&display=swap');

:root {
  --md-sys-color-primary:         #2E75B6;
  --md-sys-color-on-primary:      #FFFFFF;
  --md-sys-color-secondary:       #1565C0;
  --md-sys-color-tertiary:        #0288D1;
  --md-sys-color-surface:         #1E1E2E;
  --md-sys-color-surface-1:       #252538;
  --md-sys-color-surface-2:       #2C2C42;
  --md-sys-color-on-surface:      #E0E0E0;
  --md-sys-color-on-surface-var:  #9E9EC2;
  --md-sys-color-outline:         #3A3A5C;
  --md-sys-color-error:           #EF5350;
  --md-sys-color-warning:         #FFA726;
  --md-sys-color-success:         #66BB6A;
  
  --md-sys-typescale-display:     700 36px/1.2 'Roboto', system-ui, sans-serif;
  --md-sys-typescale-headline:    600 24px/1.3 'Roboto', system-ui, sans-serif;
  --md-sys-typescale-title:       500 18px/1.4 'Roboto', system-ui, sans-serif;
  --md-sys-typescale-body:        400 14px/1.5 'Roboto', system-ui, sans-serif;
  --md-sys-typescale-label:       400 11px/1.4 'Roboto', system-ui, sans-serif;
  
  --md-sys-shape-sm:  8px;
  --md-sys-shape-md:  12px;
  --md-sys-shape-lg:  16px;
  --md-sys-shape-xl:  24px;
}

.stApp {
  background-color: #121212;
  font-family: 'Roboto', system-ui, sans-serif;
}

.metric-container {
    background: var(--md-sys-color-surface-2);
    border: 1px solid var(--md-sys-color-outline);
    border-radius: var(--md-sys-shape-md);
    padding: 1rem;
}
.metric-value { font: var(--md-sys-typescale-display); }
.metric-good { color: var(--md-sys-color-success); }
.metric-neutral { color: var(--md-sys-color-warning); }
.metric-bad { color: var(--md-sys-color-error); }
.metric-primary { color: var(--md-sys-color-primary); }

h1 { font: var(--md-sys-typescale-display) !important; color: var(--md-sys-color-primary) !important; }
h2, .section-title {
  font: var(--md-sys-typescale-headline) !important;
  color: var(--md-sys-color-on-surface)  !important;
  border-bottom: 1px solid var(--md-sys-color-outline);
  padding-bottom: 8px;
  margin-bottom: 24px;
}

[data-testid="stSidebar"] {
  background: var(--md-sys-color-surface-1) !important;
  border-right: 1px solid var(--md-sys-color-outline);
}
</style>
"""
st.markdown(CSS_M3, unsafe_allow_html=True)

# --- PLOTLY THEME ---
def get_plotly_theme():
    return dict(
        paper_bgcolor=tokens["elevation"]["1"],
        plot_bgcolor=tokens["elevation"]["0"],
        font=dict(family=tokens["typography"]["family"], size=14, color=tokens["color"]["on_surface"]),
        colorway=[tokens["color"]["primary"], tokens["color"]["tertiary"], tokens["color"]["success"]],
        xaxis=dict(gridcolor=tokens["color"]["outline"], zerolinecolor=tokens["color"]["outline"]),
        yaxis=dict(gridcolor=tokens["color"]["outline"], zerolinecolor=tokens["color"]["outline"]),
    )

# --- CARGAR Y ESTRUCTURAR DATOS ---
@st.cache_data
def load_data():
    with open('.antigravity/team/shared/quality_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    rows = []
    for d in data['datasets']:
        if d['scores'] is not None:
            rows.append({
                'Dataset': d['slug'],
                'Categoria': d['categoria'],
                'Organizacion': d['organizacion'],
                'Filas': d['filas'],
                'Completitud': d['scores']['completeness'],
                'Exactitud': d['scores']['accuracy'],
                'Consistencia': d['scores']['consistency'],
                'Unicidad': d['scores']['uniqueness'],
                'Score Global': d['scores']['global']
            })
    return data['metadata'], pd.DataFrame(rows)

metadata, df = load_data()

# --- SIDEBAR NAV ---
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 16px 0 24px'>
      <div style='font-size:32px'>🗂️</div>
      <div style='font: 600 16px Roboto; color: #E0E0E0; margin-top:8px'>Calidad de Datos NL</div>
      <div style='font: 400 11px Roboto; color: #9E9EC2; margin-top:4px'>catalogodatos.nl.gob.mx</div>
    </div>
    """, unsafe_allow_html=True)
    
    seccion = st.radio("Ir a sección", ["📊 Resumen", "🗺️ Por Categoría", "📋 Por Dataset", "🚨 Alertas", "📈 Evolución"], label_visibility="collapsed")
    st.divider()
    st.markdown(f"""
    <div style='font: 400 12px Roboto; color: #9E9EC2; line-height:1.8'>
      <div>🗓️ Análisis: {metadata.get('generado')}</div>
      <div>📦 Script V{metadata.get('version_script')}</div>
      <div>📁 {len(df)} datasets validos</div>
    </div>
    """, unsafe_allow_html=True)

# --- MAIN CONTENT ---
st.title("Gobernanza de Datos NL - M3")

if df.empty:
    st.warning("No hay datos cargados.")
    st.stop()
    
score_mean = df['Score Global'].mean()
def get_color_class(val):
    if val >= 90: return "metric-good"
    elif val >= 70: return "metric-neutral"
    else: return "metric-bad"

if seccion == "📊 Resumen":
    st.markdown("<h2>Resumen General de Calidad</h2>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    # KPIs customizados (Bug #1 Fix)
    c1.markdown(f"<div class='metric-container'><div style='color:#9E9EC2'>Datasets Válidos</div><div class='metric-value metric-primary'>{len(df)}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-container'><div style='color:#9E9EC2'>Score Global</div><div class='metric-value {get_color_class(score_mean)}'>{score_mean:.1f}%</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-container'><div style='color:#9E9EC2'>Completitud Prom.</div><div class='metric-value {get_color_class(df['Completitud'].mean())}'>{df['Completitud'].mean():.1f}%</div></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='metric-container'><div style='color:#9E9EC2'>Consistencia Prom.</div><div class='metric-value {get_color_class(df['Consistencia'].mean())}'>{df['Consistencia'].mean():.1f}%</div></div>", unsafe_allow_html=True)
    
elif seccion == "🗺️ Por Categoría":
    st.markdown("<h2>Rendimiento por Categoría Temática</h2>", unsafe_allow_html=True)
    cat_df = df.groupby('Categoria')[['Completitud', 'Exactitud', 'Consistencia', 'Unicidad', 'Score Global']].mean().reset_index()
    # FIX Bug #2: Heatmap responsivo con color scheme de la DB y Update Layout
    fig_cat = px.imshow(cat_df.set_index('Categoria'), color_continuous_scale="Blues_r", aspect="auto")
    
    # Aplicando theme de Design Tokens
    fig_cat.update_layout(
        autosize=True,
        height=600,
        margin=dict(l=200, r=40, t=60, b=40),
        **get_plotly_theme()
    )
    st.plotly_chart(fig_cat, use_container_width=True)
    
elif seccion == "📋 Por Dataset":
    st.markdown("<h2>Explorador de Datasets</h2>", unsafe_allow_html=True)
    # Dataframe mejorado
    st.dataframe(df.style.background_gradient(cmap='RdYlGn', vmin=0, vmax=100, subset=['Score Global']).format(precision=1), use_container_width=True, height=500)
    
elif seccion == "🚨 Alertas":
    st.markdown("<h2>Tablero de Monitoreo - Alertas Críticas</h2>", unsafe_allow_html=True)
    alertas = df[df['Score Global'] < 70].sort_values('Score Global')
    if not alertas.empty:
        st.markdown(f"""
        <div style='background: rgba(239, 83, 80, 0.15); border: 1px solid #EF5350; padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;'>
          <h4 style='color: #EF5350; margin-top:0'>⚠️ {len(alertas)} Datasets requieren intervención inmediata</h4>
          <p style='color: #FFCDD2; margin-bottom:0'>Los siguientes conjuntos presentan calidad deficiente e impactan la experiencia del usuario y portabilidad técnica.</p>
        </div>
        """, unsafe_allow_html=True)
        st.dataframe(alertas[['Dataset', 'Categoria', 'Organizacion', 'Score Global']], use_container_width=True)
    else:
        st.success("Toda la plataforma promedia scores aceptables (Ningún dataset bajó de 70%).")
        
elif seccion == "📈 Evolución":
    st.markdown("<h2>Evolución de la Calidad (Histórico Simulada)</h2>", unsafe_allow_html=True)
    # FIX Bug #3: Eje X en fechas
    evolucion = pd.DataFrame({
        'año_base': [2023.0, 2023.75, 2024.50, 2025.25, 2026.0], 
        'Score Promedio': [50.1, 55.4, 62.4, 75.8, score_mean]
    })
    # Transformar a YYYY QN datetime
    evolucion["fecha"] = pd.to_datetime(
        evolucion["año_base"].astype(int).astype(str) + "-" + 
        (((evolucion["año_base"] % 1) * 4 + 1).astype(int) * 3).astype(str).str.zfill(2) + "-01"
    )
    
    fig_evo = px.line(evolucion, x='fecha', y='Score Promedio', markers=True)
    
    fig_evo.update_xaxes(
        tickformat="%Y Q%q",
        dtick="M3"
    )
    
    fig_evo.update_layout(
        height=500,
        **get_plotly_theme()
    )
    fig_evo.update_traces(line_color=tokens["color"]["primary"], marker=dict(size=10))
    st.plotly_chart(fig_evo, use_container_width=True)
    
st.markdown("<br><hr><center><span style='color:#9E9EC2; font-size:12px;'>Proyecto Datos Abiertos NL 2026 - M3 Aesthetic Edition</span></center>", unsafe_allow_html=True)
