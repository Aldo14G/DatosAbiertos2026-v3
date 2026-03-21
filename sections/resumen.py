# sections/resumen.py

import streamlit as st
import pandas as pd

def render_kpi_card(col, label: str, value: str, delta: str = None,
                    tier: str = "excellent", icon: str = None):
    """
    Replica exactamente el KPI card del Resumen General de Stitch.
    """
    colors = {
        "excellent": "#1e8e3e",
        "good":      "#e37400",
        "poor":      "#d93025",
        "neutral":   "#dadce0",
    }
    color = colors.get(tier, "#dadce0")
    delta_html = ""
    if delta:
        arrow = "↑" if not delta.startswith("-") else "↓"
        delta_color = "#1e8e3e" if arrow == "↑" else "#d93025"
        delta_html = f'<span style="font-size:11px;font-weight:700;color:{delta_color};margin-left:6px">{arrow} {delta}</span>'

    icon_html = ""
    if icon:
        icon_html = f'<span class="material-symbols-outlined" style="color:{color};float:right;font-size:20px">{icon}</span>'

    html = f"""
    <div class="kpi-card {tier}" style="
        background:#ffffff;
        border:1px solid #dadce0;
        border-radius:12px;
        padding:24px 20px 18px;
        position:relative;
        overflow:hidden;
        transition:border-color 0.2s;
    ">
        <div style="position:absolute;top:0;left:0;right:0;height:3px;background:{color}"></div>
        {icon_html}
        <p style="font-size:13px;color:#414754;font-family:Inter,sans-serif;margin:0 0 8px">{label}</p>
        <div style="display:flex;align-items:baseline">
            <span style="font-size:32px;font-weight:700;font-family:'Plus Jakarta Sans',sans-serif;
                         color:#1a1b1e;line-height:1.1">{value}</span>
            {delta_html}
        </div>
    </div>
    """
    col.markdown(html, unsafe_allow_html=True)


def render_distribution_bar(excellent: int, good: int, poor: int, total: int):
    """
    Replica la barra de distribución horizontal del Resumen General.
    """
    pct_e = excellent / total * 100 if total > 0 else 0
    pct_g = good      / total * 100 if total > 0 else 0
    pct_p = poor      / total * 100 if total > 0 else 0

    return f"""
    <div style="width:100%;height:48px;display:flex;border-radius:9999px;overflow:hidden">
        <div style="background:#1e8e3e;width:{pct_e:.1f}%;display:flex;align-items:center;
                    justify-content:center;color:white;font-size:11px;font-weight:700">
            {excellent} ({pct_e:.1f}%)
        </div>
        <div style="background:#e37400;width:{pct_g:.1f}%;display:flex;align-items:center;
                    justify-content:center;color:white;font-size:11px;font-weight:700">
            {good if pct_g > 5 else ''}
        </div>
        <div style="background:#d93025;width:{pct_p:.1f}%;display:flex;align-items:center;
                    justify-content:center;color:white;font-size:11px;font-weight:700">
            {poor if pct_p > 3 else ''}
        </div>
    </div>
    <div style="display:flex;justify-content:space-between;
                font-size:11px;font-weight:700;color:#414754;
                padding:8px 4px 0;text-transform:uppercase;letter-spacing:0.05em">
        <span>TOTAL: {total} DATASETS ANALIZADOS</span>
        <span>ÚLTIMA ACTUALIZACIÓN: HOY</span>
    </div>
    """


def render_resumen(df: pd.DataFrame, tokens: dict):
    """
    Pantalla 1: Resumen General
    Replica el HTML del archivo 01_resumen-general_desktop.html de Stitch
    """
    # ── Hero Section ──────────────────────────────────────────
    st.markdown("""
    <span style="display:inline-flex;align-items:center;padding:4px 12px;
                 border-radius:9999px;background:rgba(0,91,191,0.10);
                 color:#005bbf;font-size:11px;font-weight:700;
                 letter-spacing:0.08em;text-transform:uppercase;margin-bottom:8px">
        Datos Abiertos · NL 2026
    </span>
    """, unsafe_allow_html=True)

    st.markdown("""
    <h1 style="font-size:40px;font-weight:800;letter-spacing:-0.02em;
               color:#1a1b1e;font-family:'Plus Jakarta Sans',sans-serif;
               line-height:1.15;margin:0 0 8px">
        Gobernanza de Datos — Nuevo León 2026
    </h1>
    <div style="display:flex;align-items:center;gap:16px;
                font-size:13px;color:#414754;margin-bottom:24px">
        <span>🗓️ 2026-03-19</span>
        <span>🗄️ {n} datasets procesados</span>
    </div>
    """.format(n=len(df)), unsafe_allow_html=True)

    # Hero Image Section (Añadiendo el gráfico hero)
    st.markdown("""
    <div style="position:relative; width:100%; padding-bottom:40%; border-radius:16px; overflow:hidden; background:#0f172a; margin-bottom:32px; box-shadow:0 10px 15px -3px rgba(0,0,0,0.1); border:1px solid #e2e8f0;">
        <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuCc5p75CylBWL7W72_OKvhLdjPSPlAzh5Fh1Io1mlGuqzmzwstOPIip4IUNv7Ft-8J1unrruAIozWN7Auk4qZiKBAcXkHsiC3tdZEpmeFlrJ0_gzsvE97wNh2wxzfgZalfElN-bvbROZiF1vcJwSx7zCPVACyBmPJnZ_vgbFN8bQE4z_dGxK8n67ykQVZ-NS_SzHkz9sbthf4AOR8xhgWkCT7rKav1vCCYk7IdPPdBFuhNp_dL8rpuuZaQb_a_gSHKtltjDsW2nAOU" 
             style="position:absolute; top:0; left:0; width:100%; height:100%; object-fit:cover; opacity:0.6;" 
             alt="Data Dashboard Preview" />
             
        <div style="position:absolute; top:0; left:0; width:100%; height:100%; background:linear-gradient(to top, rgba(15,23,42,0.8), transparent);"></div>
        
        <div style="position:absolute; bottom:32px; left:32px;">
            <div style="display:flex; align-items:center; gap:8px; padding:10px 20px; background:rgba(255,255,255,0.15); backdrop-filter:blur(16px); -webkit-backdrop-filter:blur(16px); border-radius:12px; border:1px solid rgba(255,255,255,0.2);">
                <div style="width:10px; height:10px; background:#4ade80; border-radius:50%; box-shadow:0 0 10px #4ade80;"></div>
                <div style="color:white; font-family:'Inter',sans-serif; font-size:13px; font-weight:600;">Sistema en línea y actualizado</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Grid 4 columnas (replicar grid de Stitch) ─────────
    st.markdown('<h3 style="font-family:\'Plus Jakarta Sans\',sans-serif;font-size:18px;font-weight:600;color:#1a1b1e;margin-bottom:16px">Resumen General de Calidad</h3>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    render_kpi_card(c1, "Datasets Válidos", str(len(df)),
                    tier="neutral")
    score_global_mean = df['score_global'].mean() if 'score_global' in df.columns else 0
    render_kpi_card(c2, "Score Global",
                    f"{score_global_mean:.1f}%",
                    delta="2.1%", tier="excellent")
                    
    comp_mean = df['comp_completitud_global_pct'].mean() if 'comp_completitud_global_pct' in df.columns else 0
    render_kpi_card(c3, "Completitud Prom.",
                    f"{comp_mean:.1f}%",
                    tier="excellent")
                    
    cons_mean = df['cons_score_consistency_pct'].mean() if 'cons_score_consistency_pct' in df.columns else 0
    render_kpi_card(c4, "Consistencia Prom.",
                    f"{cons_mean:.1f}%",
                    tier="good")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Segunda fila KPIs (replicar 2-col row de Stitch) ──────
    c5, c6 = st.columns(2)
    acc_mean = df['acc_score_accuracy_pct'].mean() if 'acc_score_accuracy_pct' in df.columns else 0
    render_kpi_card(c5, "Exactitud Prom.",
                    f"{acc_mean:.1f}%",
                    icon="verified", tier="excellent")
                    
    uniq_mean = df['uniq_score_uniqueness_pct'].mean() if 'uniq_score_uniqueness_pct' in df.columns else 0
    render_kpi_card(c6, "Unicidad Prom.",
                    f"{uniq_mean:.1f}%",
                    icon="filter_none", tier="excellent")

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # ── Distribution Chart (replicar barra horizontal de Stitch) ──
    if 'score_global' in df.columns:
        excellent_n = (df['score_global'] >= 90).sum()
        good_n      = ((df['score_global'] >= 70) & (df['score_global'] < 90)).sum()
        poor_n      = (df['score_global'] < 70).sum()
    else:
        excellent_n, good_n, poor_n = 0, 0, 0

    st.markdown(f"""
    <div style="background:#f4f3f7;border-radius:12px;padding:32px;border:0">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:24px">
            <h3 style="font-family:'Plus Jakarta Sans',sans-serif;font-size:18px;
                       font-weight:700;color:#1a1b1e;margin:0">Distribución de Calidad</h3>
            <div style="display:flex;gap:24px">
                <span style="display:flex;align-items:center;gap:6px;font-size:12px;color:#414754">
                    <span style="width:12px;height:12px;background:#1e8e3e;border-radius:2px;display:inline-block"></span>Excelentes
                </span>
                <span style="display:flex;align-items:center;gap:6px;font-size:12px;color:#414754">
                    <span style="width:12px;height:12px;background:#e37400;border-radius:2px;display:inline-block"></span>Buenos
                </span>
                <span style="display:flex;align-items:center;gap:6px;font-size:12px;color:#414754">
                    <span style="width:12px;height:12px;background:#d93025;border-radius:2px;display:inline-block"></span>Deficientes
                </span>
            </div>
        </div>
        {render_distribution_bar(excellent_n, good_n, poor_n, len(df))}
    </div>
    """, unsafe_allow_html=True)
