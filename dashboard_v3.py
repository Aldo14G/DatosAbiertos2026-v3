# dashboard_v3.py
# Orquestador principal del dashboard NL 2026 — Single-Page Scrollable.
# Ejecutar con: streamlit run dashboard_v3.py
#
# Arquitectura v3.3 — Narrativa vertical con 5 secciones:
# Inicio → Desarrollo → Dashboards → Conclusiones → Footer.

import base64
import datetime

import pandas as pd
import streamlit as st

from config import CACHE_TTL_SECONDS, UMBRAL_GOBERNANZA, VERSION

st.set_page_config(
    page_title="NL 2026 — Gobernanza de Datos",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Tema ──────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# ── Inyectar sistema de diseño NL 2026 ───────────────────────
from styles.global_css import inject_design_system  # noqa: E402

st.markdown(inject_design_system(st.session_state.theme), unsafe_allow_html=True)


# ── Carga de datos ────────────────────────────────────────────
@st.cache_data(ttl=CACHE_TTL_SECONDS)
def load_data() -> pd.DataFrame:
    """Carga y cachea los resultados de calidad desde CSV o JSON."""
    from data_layer import load_results
    return load_results()


try:
    with st.spinner("Cargando datos de calidad…"):
        df = load_data()
except (FileNotFoundError, ValueError, KeyError) as e:
    st.error(
        f"**Error al cargar los datos:** {e}\n\n"
        "Verifica que exista `resultados_calidad_datos_nl.csv` o "
        "`.antigravity/team/shared/quality_results.json`."
    )
    st.stop()

if df.empty:
    st.warning("El archivo de resultados existe pero no contiene datos.")
    st.stop()


# ── Métricas para la Status Bar ──────────────────────────────
if "score_global" in df.columns:
    _n_alertas  = int((df["score_global"] < UMBRAL_GOBERNANZA).sum())
    _mean       = df["score_global"].mean()
    _score_prom = float(_mean) if pd.notna(_mean) else 0.0
else:
    _n_alertas  = 0
    _score_prom = 0.0

_csv_bytes = df.to_csv(index=False).encode("utf-8")
_csv_b64 = base64.b64encode(_csv_bytes).decode("ascii")
_download_href = f"data:text/csv;base64,{_csv_b64}"


# ── Secciones de la topbar (single-page, anchor-based) ───────
_SECTIONS: list[tuple[str, str, str]] = [
    ("Inicio",        "inicio",        "home"),
    ("Desarrollo",    "desarrollo",    "account_tree"),
    ("Dashboards",    "dashboards",    "insights"),
    ("Conclusiones",  "conclusiones",  "lightbulb"),
    ("Footer",        "footer",        "bookmark"),
]


# ── STATUS BAR (sidebar colapsado) ────────────────────────────
_alert_cls   = "is-critical" if _n_alertas > 0 else "is-ok"
_alert_icon  = "warning" if _n_alertas > 0 else "check_circle"
_today_iso   = datetime.date.today().isoformat()

with st.sidebar:
    st.markdown(f"""
    <div class="nl-sb-brand">
        <div class="nl-sb-title">
            <span class="material-symbols-outlined" aria-hidden="true">shield</span>
            Gobernanza Pro
        </div>
        <div class="nl-sb-version">Sistema de Calidad v{VERSION}</div>
    </div>
    <hr class="nl-sb-divider" />
    <div class="nl-sb-status">
        <div class="nl-sb-row">
            <span class="material-symbols-outlined" aria-hidden="true">calendar_today</span>
            <span>Actualizado: <strong>{_today_iso}</strong></span>
        </div>
        <div class="nl-sb-row">
            <span class="material-symbols-outlined" aria-hidden="true">database</span>
            <span>Universo: <strong>{len(df)} datasets</strong></span>
        </div>
        <div class="nl-sb-row">
            <span class="material-symbols-outlined" aria-hidden="true">bar_chart</span>
            <span>Promedio: <strong>{_score_prom:.1f}%</strong></span>
        </div>
        <div class="nl-sb-alerts {_alert_cls}">
            <span class="material-symbols-outlined" aria-hidden="true">{_alert_icon}</span>
            {_n_alertas} alertas críticas
        </div>
    </div>
    <div class="nl-sb-gap"></div>
    """, unsafe_allow_html=True)

    _t_label = "Modo Claro" if st.session_state.theme == "dark" else "Modo Oscuro"
    if st.button(f"{_t_label}", key="theme_toggle", use_container_width=True):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()


# ── TOPBAR (navegación por anchors + IntersectionObserver) ───
_nav_links = "".join(
    f'<a href="#{slug}" data-section="{slug}">'
    f'<span class="material-symbols-outlined" aria-hidden="true">{icon}</span>{name}</a>'
    for name, slug, icon in _SECTIONS
)

st.markdown(f"""
<div class="stitch-topbar">
    <div class="stitch-topbar-inner">
        <div class="stitch-topbar-brand">
            <span class="material-symbols-outlined" aria-hidden="true">analytics</span>
            <div>
                <span>Gobernanza Pro</span>
                <span>Nuevo León 2026</span>
            </div>
        </div>
        <nav class="stitch-topbar-nav" aria-label="Navegación principal">
            {_nav_links}
        </nav>
        <div class="stitch-topbar-actions" aria-label="Acciones globales">
            <a class="stitch-topbar-btn stitch-topbar-btn-primary"
               href="{_download_href}" download="resultados_nl_2026.csv">
                <span class="material-symbols-outlined" aria-hidden="true">download</span>
                Exportar CSV
            </a>
            <a class="stitch-topbar-btn stitch-topbar-btn-secondary"
               href="https://catalogodatos.nl.gob.mx" target="_blank" rel="noopener noreferrer">
                <span class="material-symbols-outlined" aria-hidden="true">open_in_new</span>
                Portal NL
            </a>
        </div>
    </div>
</div>

<div class="stitch-mobile-shell">
    <details class="stitch-mobile-menu">
        <summary>
            <span class="material-symbols-outlined" aria-hidden="true">menu</span>
            Menú de Navegación
        </summary>
        <div class="stitch-mobile-panel">
            <nav class="stitch-mobile-nav" aria-label="Navegación móvil">
                {_nav_links}
            </nav>
        </div>
    </details>
</div>

<script>
(function() {{
    const observer = new IntersectionObserver((entries) => {{
        entries.forEach((entry) => {{
            if (entry.isIntersecting) {{
                const id = entry.target.id;
                document.querySelectorAll('.stitch-topbar-nav a, .stitch-mobile-nav a').forEach((a) => {{
                    a.classList.toggle('active', a.dataset.section === id);
                }});
            }}
        }});
    }}, {{ rootMargin: '-40% 0px -55% 0px', threshold: 0 }});

    ['inicio', 'desarrollo', 'dashboards', 'conclusiones', 'footer'].forEach((id) => {{
        const el = document.getElementById(id);
        if (el) observer.observe(el);
    }});
}})();
</script>
""", unsafe_allow_html=True)


# ── Render de la página ───────────────────────────────────────
_tokens = {"theme": st.session_state.theme}

from sections.app import render as render_app  # noqa: E402

render_app(df, _tokens)

# ── Scroll-reveal IntersectionObserver ───────────────────
st.markdown("""
<script>
(function() {
    function setupReveal() {
        var io = new IntersectionObserver(function(entries) {
            entries.forEach(function(e) {
                if (e.isIntersecting) {
                    e.target.classList.add('nl-revealed');
                    io.unobserve(e.target);
                }
            });
        }, { threshold: 0.06, rootMargin: '0px 0px -60px 0px' });
        document.querySelectorAll('.nl-reveal').forEach(function(el) { io.observe(el); });
    }
    if (document.readyState === 'complete') {
        setupReveal();
    } else {
        window.addEventListener('load', setupReveal);
    }
})();
</script>
""", unsafe_allow_html=True)
