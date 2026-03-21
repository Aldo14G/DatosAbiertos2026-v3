# styles/global_css.py

def inject_stitch_design_system() -> str:
    """
    Inyecta el sistema de diseño extraído de Google Stitch.
    Replica exactamente el Tailwind config y estilos de las 6 pantallas.

    Llamar con: st.markdown(inject_stitch_design_system(), unsafe_allow_html=True)
    """
    return """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">

<style>
/* ══ BASE ═══════════════════════════════════════════════════════════════════ */
:root {
    --primary:            #005bbf;
    --primary-container:  #1a73e8;
    --background:         #faf9fd;
    --surface-lowest:     #ffffff;
    --surface-low:        #f4f3f7;
    --surface-container:  #efedf1;
    --surface-highest:    #e3e2e6;
    --on-surface:         #1a1b1e;
    --on-surface-variant: #414754;
    --outline:            #727785;
    --outline-variant:    #dadce0;
    --excellent:          #1e8e3e;
    --good:               #e37400;
    --poor:               #d93025;
    --tertiary:           #006d2a;
    --error:              #ba1a1a;
    --error-container:    #ffdad6;
    --secondary:          #2a5bb3;
}

/* ══ TIPOGRAFÍA ═════════════════════════════════════════════════════════════ */
.stApp { background: var(--background) !important; }
.stApp, .stApp * { font-family: 'Inter', system-ui, sans-serif !important; }
h1, h2, h3 { font-family: 'Plus Jakarta Sans', sans-serif !important;
              letter-spacing: -0.02em !important; }

.material-symbols-outlined {
    font-family: 'Material Symbols Outlined';
    font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
    font-size: 20px;
    vertical-align: middle;
}

/* ══ NAVBAR (replicar fixed nav de Stitch) ══════════════════════════════════ */
header[data-testid="stHeader"] {
    background: rgba(255,255,255,0.7) !important;
    backdrop-filter: blur(12px) !important;
    border-bottom: 1px solid var(--outline-variant) !important;
    height: 64px !important;
}

/* ══ SIDEBAR (replicar aside de Stitch) ════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: #f8f9fa !important;
    border-right: 1px solid var(--outline-variant) !important;
    width: 220px !important;
}
[data-testid="stSidebar"] .stRadio label {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 13px !important;
    color: var(--on-surface-variant) !important;
    padding: 8px 16px !important;
    border-radius: 9999px;
    transition: all 0.2s;
}
[data-testid="stSidebar"] .stRadio label:hover {
    transform: translateX(4px);
    color: var(--primary) !important;
}

/* ══ CONTENEDOR PRINCIPAL ═══════════════════════════════════════════════════ */
.block-container {
    padding: 2rem 2rem 3rem !important;
    max-width: 1440px !important;
}

/* ══ CARDS (replicar cards de Stitch) ══════════════════════════════════════ */
.stitch-card {
    background: var(--surface-lowest);
    border: 1px solid var(--outline-variant);
    border-radius: 12px;
    padding: 24px;
    transition: border-color 0.2s ease;
}
.stitch-card:hover { border-color: var(--primary); }

/* ══ KPI CARD (replicar Resumen General de Stitch) ═════════════════════════ */
.kpi-card {
    background: var(--surface-lowest);
    border: 1px solid var(--outline-variant);
    border-radius: 12px;
    padding: 24px 20px 18px;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.kpi-card.excellent::before { background: var(--excellent); }
.kpi-card.good::before      { background: var(--good); }
.kpi-card.poor::before      { background: var(--poor); }
.kpi-card.neutral::before   { background: var(--outline-variant); }
.kpi-label {
    font-size: 13px; font-family: 'Inter', sans-serif;
    color: var(--on-surface-variant); margin-bottom: 8px;
}
.kpi-value {
    font-size: 36px; font-weight: 700;
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: var(--on-surface); line-height: 1.1;
}
.kpi-delta {
    font-size: 11px; font-weight: 700;
    margin-left: 8px;
}
.kpi-delta.up   { color: var(--excellent); }
.kpi-delta.down { color: var(--poor); }

/* ══ BADGE DE CATEGORÍA (replicar pill de Stitch) ══════════════════════════ */
.category-badge {
    display: inline-block;
    padding: 2px 10px;
    background: var(--surface-highest);
    border: 1px solid rgba(193,198,214,0.5);
    border-radius: 4px;
    font-size: 10px;
    font-weight: 700;
    color: var(--on-surface-variant);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.category-badge:hover {
    background: #e8f0fe;
    border-color: var(--primary);
    color: var(--primary);
}

/* ══ FILTER CHIPS (replicar chips dismissibles de Stitch) ═══════════════════ */
.filter-chip {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 12px;
    background: rgba(0,91,191,0.10);
    border: 1px solid rgba(0,91,191,0.20);
    border-radius: 9999px;
    font-size: 12px; font-weight: 600; color: var(--primary);
    cursor: pointer;
}

/* ══ HEATMAP TABLE (replicar heatmap de Stitch) ════════════════════════════ */
.heatmap-cell {
    height: 40px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 4px;
    font-weight: 700; color: white;
    transition: transform 0.2s ease;
    cursor: default;
}
.heatmap-cell:hover { transform: scale(1.05); z-index: 10; }

/* ══ ALERTA BANNER (replicar banner de Stitch) ══════════════════════════════ */
.alert-banner {
    background: #fce8e6;
    border: 1px solid #f28b82;
    border-radius: 12px;
    padding: 16px 24px;
    display: flex; align-items: center; gap: 16px;
    color: var(--poor);
    font-weight: 600; font-size: 18px;
}

/* ══ ALERT CARD (replicar alert cards de Stitch) ═══════════════════════════ */
.alert-card {
    background: var(--surface-lowest);
    border: 1px solid var(--outline-variant);
    border-left: 6px solid var(--poor);
    border-radius: 0 12px 12px 0;
    padding: 32px;
}
.alert-score {
    font-size: 40px; font-weight: 800;
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: var(--poor); line-height: 1;
}

/* ══ TABS (replicar tab bar de Stitch — Evolución) ══════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    border-bottom: 1px solid var(--outline-variant) !important;
    background: transparent !important;
    gap: 32px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 14px !important; font-weight: 500 !important;
    color: var(--on-surface-variant) !important;
    padding: 0 0 16px !important;
}
.stTabs [aria-selected="true"] {
    color: var(--primary) !important;
    border-bottom: 2px solid var(--primary) !important;
    font-weight: 600 !important;
}

/* ══ GAUGE SVG (replicar gauge de Stitch — Análisis Data Science) ═══════════ */
.gauge-container {
    background: var(--surface-low);
    border-radius: 12px;
    padding: 24px;
    display: flex; flex-direction: column; align-items: center;
    border: 1px solid transparent;
    transition: border-color 0.2s;
}
.gauge-container:hover { border-color: var(--outline-variant); }
.gauge-label {
    font-size: 11px; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.1em; color: var(--on-surface-variant); margin-bottom: 16px;
}
.gauge-badge {
    padding: 4px 12px; border-radius: 9999px;
    font-size: 11px; font-weight: 700;
    margin-top: 16px;
}
.gauge-badge.optimal   { background: rgba(0,109,42,0.10); color: var(--tertiary); }
.gauge-badge.stable    { background: rgba(42,91,179,0.10); color: var(--secondary); }
.gauge-badge.regular   { background: rgba(0,91,191,0.10); color: var(--primary); }
.gauge-badge.critical  { background: rgba(186,26,26,0.10); color: var(--error); }

/* ══ DATA TABLE (replicar tabla de Explorador de Datasets) ═════════════════ */
[data-testid="stDataFrame"] thead tr th {
    background: var(--surface-low) !important;
    font-size: 11px !important; font-weight: 700 !important;
    text-transform: uppercase !important; letter-spacing: 0.05em !important;
    color: var(--on-surface-variant) !important;
    padding: 16px 24px !important;
    border-bottom: 2px solid var(--outline-variant) !important;
}
[data-testid="stDataFrame"] tbody tr {
    border-bottom: 1px solid rgba(193,198,214,0.2) !important;
}
[data-testid="stDataFrame"] tbody tr:hover {
    background: var(--surface-low) !important;
}
[data-testid="stDataFrame"] tbody tr td {
    padding: 12px 24px !important; font-size: 14px !important;
    color: var(--on-surface) !important;
}

/* ══ SCROLLBAR (replicar estilo Stitch) ════════════════════════════════════ */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--surface-low); }
::-webkit-scrollbar-thumb { background: var(--outline-variant); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--outline); }

/* ══ FOOTER (replicar footer de Stitch) ════════════════════════════════════ */
.stitch-footer {
    border-top: 1px solid #f1f0f4;
    background: white;
    padding: 48px 32px;
    margin-top: 48px;
    display: flex; justify-content: space-between; align-items: center;
}
</style>
"""
