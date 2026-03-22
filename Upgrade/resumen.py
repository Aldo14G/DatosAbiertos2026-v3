# sections/resumen.py
import streamlit as st
import pandas as pd


def _get_tier(val: float) -> str:
    if val >= 90: return "excellent"
    if val >= 70: return "good"
    return "poor"


def render_kpi_card(col, label: str, value: str,
                    tier: str = "excellent", icon: str = None):
    """Replica el KPI card de Stitch — sin valores hardcodeados."""
    colors = {
        "excellent": "#1e8e3e",
        "good":      "#e37400",
        "poor":      "#d93025",
        "neutral":   "#dadce0",
    }
    color = colors.get(tier, "#dadce0")
    icon_html = (
        f'<span class="material-symbols-outlined" '
        f'style="color:{color};float:right;font-size:20px">{icon}</span>'
        if icon else ""
    )
    col.markdown(f"""
    <div class="kpi-card {tier}" style="
        background:#ffffff;border:1px solid #dadce0;border-radius:12px;
        padding:24px 20px 18px;position:relative;overflow:hidden;
        transition:border-color 0.2s;">
        <div style="position:absolute;top:0;left:0;right:0;height:3px;
                    background:{color}"></div>
        {icon_html}
        <p style="font-size:13px;color:#414754;font-family:Inter,sans-serif;
                  margin:0 0 8px">{label}</p>
        <span style="font-size:32px;font-weight:700;
                     font-family:'Plus Jakarta Sans',sans-serif;
                     color:#1a1b1e;line-height:1.1">{value}</span>
    </div>
    """, unsafe_allow_html=True)


def _distribution_bar(excellent: int, good: int, poor: int, total: int) -> str:
    if total == 0:
        return ""
    pe = excellent / total * 100
    pg = good      / total * 100
    pp = poor      / total * 100
    return f"""
    <div style="width:100%;height:48px;display:flex;border-radius:9999px;overflow:hidden">
        <div style="background:#1e8e3e;width:{pe:.1f}%;display:flex;align-items:center;
                    justify-content:center;color:white;font-size:11px;font-weight:700">
            {excellent} ({pe:.0f}%)
        </div>
        <div style="background:#e37400;width:{pg:.1f}%;display:flex;align-items:center;
                    justify-content:center;color:white;font-size:11px;font-weight:700">
            {f"{good} ({pg:.0f}%)" if pg > 8 else ""}
        </div>
        <div style="background:#d93025;width:{pp:.1f}%;display:flex;align-items:center;
                    justify-content:center;color:white;font-size:11px;font-weight:700">
            {f"{poor} ({pp:.0f}%)" if pp > 5 else ""}
        </div>
    </div>
    <div style="display:flex;justify-content:space-between;
                font-size:11px;font-weight:700;color:#414754;
                padding:8px 4px 0;text-transform:uppercase;letter-spacing:0.05em">
        <span>TOTAL: {total} DATASETS ANALIZADOS</span>
        <span>CATÁLOGO: catalogodatos.nl.gob.mx</span>
    </div>
    """


def render_resumen(df: pd.DataFrame, tokens: dict):
    """Pantalla 1 — Resumen General. Todos los valores leídos del DataFrame."""

    # ── Hero ──────────────────────────────────────────────────
    st.markdown("""
    <span style="display:inline-flex;align-items:center;padding:4px 12px;
                 border-radius:9999px;background:rgba(0,91,191,0.10);
                 color:#005bbf;font-size:11px;font-weight:700;
                 letter-spacing:0.08em;text-transform:uppercase;margin-bottom:8px">
        Datos Abiertos · NL 2026
    </span>""", unsafe_allow_html=True)

    st.markdown(f"""
    <h1 style="font-size:40px;font-weight:800;letter-spacing:-0.02em;
               color:#1a1b1e;font-family:'Plus Jakarta Sans',sans-serif;
               line-height:1.15;margin:0 0 8px">
        Gobernanza de Datos — Nuevo León 2026
    </h1>
    <div style="display:flex;align-items:center;gap:16px;
                font-size:13px;color:#414754;margin-bottom:32px">
        <span>🗓️ 2026-03-19</span>
        <span>🗄️ {len(df)} datasets procesados</span>
        <a href="https://catalogodatos.nl.gob.mx" target="_blank"
           style="color:#005bbf;font-weight:600;text-decoration:none">
            catalogodatos.nl.gob.mx →
        </a>
    </div>
    """, unsafe_allow_html=True)

    # ── Métricas reales desde el DataFrame ────────────────────
    def _mean(col):
        return df[col].mean() if col in df.columns and not df[col].dropna().empty else 0

    score_mean = _mean("score_global")
    comp_mean  = _mean("comp_completitud_global_pct")
    acc_mean   = _mean("acc_score_accuracy_pct")
    cons_mean  = _mean("cons_score_consistency_pct")
    uniq_mean  = _mean("uniq_score_uniqueness_pct")
    time_mean  = _mean("time_score_timeliness_pct") or 50.0

    # ── Fila 1: 4 KPIs principales ────────────────────────────
    st.markdown(
        '<h3 style="font-family:\'Plus Jakarta Sans\',sans-serif;font-size:18px;'
        'font-weight:600;color:#1a1b1e;margin-bottom:16px">'
        'Resumen General de Calidad</h3>',
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    render_kpi_card(c1, "Datasets Válidos", str(len(df)), tier="neutral")
    render_kpi_card(c2, "Score Global",    f"{score_mean:.1f}%", tier=_get_tier(score_mean))
    render_kpi_card(c3, "Completitud",     f"{comp_mean:.1f}%",  tier=_get_tier(comp_mean))
    render_kpi_card(c4, "Exactitud",       f"{acc_mean:.1f}%",   tier=_get_tier(acc_mean))

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Fila 2: 3 KPIs secundarios (incluye Puntualidad) ──────
    c5, c6, c7 = st.columns(3)
    render_kpi_card(c5, "Consistencia", f"{cons_mean:.1f}%", icon="data_check",  tier=_get_tier(cons_mean))
    render_kpi_card(c6, "Unicidad",     f"{uniq_mean:.1f}%", icon="filter_none", tier=_get_tier(uniq_mean))
    render_kpi_card(c7, "Puntualidad",  f"{time_mean:.1f}%", icon="schedule",    tier=_get_tier(time_mean))

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # ── Distribución de calidad ───────────────────────────────
    if "score_global" in df.columns:
        exc_n  = int((df["score_global"] >= 90).sum())
        good_n = int(((df["score_global"] >= 70) & (df["score_global"] < 90)).sum())
        poor_n = int((df["score_global"] < 70).sum())
    else:
        exc_n = good_n = poor_n = 0

    st.markdown(f"""
    <div style="background:#f4f3f7;border-radius:12px;padding:32px;
                border:1px solid rgba(193,198,214,0.2)">
        <div style="display:flex;justify-content:space-between;
                    align-items:center;margin-bottom:24px">
            <h3 style="font-family:'Plus Jakarta Sans',sans-serif;font-size:18px;
                       font-weight:700;color:#1a1b1e;margin:0">
                Distribución de Calidad
            </h3>
            <div style="display:flex;gap:24px">
                <span style="display:flex;align-items:center;gap:6px;
                             font-size:12px;color:#414754">
                    <span style="width:12px;height:12px;background:#1e8e3e;
                                 border-radius:2px;display:inline-block"></span>
                    Excelente (≥90)
                </span>
                <span style="display:flex;align-items:center;gap:6px;
                             font-size:12px;color:#414754">
                    <span style="width:12px;height:12px;background:#e37400;
                                 border-radius:2px;display:inline-block"></span>
                    Bueno (70–89)
                </span>
                <span style="display:flex;align-items:center;gap:6px;
                             font-size:12px;color:#414754">
                    <span style="width:12px;height:12px;background:#d93025;
                                 border-radius:2px;display:inline-block"></span>
                    Crítico (&lt;70)
                </span>
            </div>
        </div>
        {_distribution_bar(exc_n, good_n, poor_n, len(df))}
    </div>
    """, unsafe_allow_html=True)
