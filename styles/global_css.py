# styles/global_css.py
"""NL 2026 Design System — Midnight/Teal/Gold/Rose palette.

Canonical reference: .agent/skills/design-system-pro/SKILL.md

Architecture:
    inject_design_system(theme) → returns full <style> block for st.markdown()
    get_plotly_layout(theme)    → returns Plotly layout dict with resolved hex
    PLOTLY_THEMES              → raw theme dicts for Plotly (CSS vars not supported)

Fonts: Playfair Display (titles), DM Sans (body), DM Mono (data/labels).
Palette: midnight/navy base, teal (positive), gold (structure), rose (alert).
"""

from __future__ import annotations

# ══════════════════════════════════════════════════════════════
# PLOTLY THEMES (resolved hex — CSS vars don't work in Plotly)
# ══════════════════════════════════════════════════════════════

PLOTLY_THEMES: dict[str, dict[str, str]] = {
    "dark": {
        "paper_bgcolor": "#1a2d45",
        "plot_bgcolor":  "#1a2d45",
        "font_color":    "#8a9bb0",
        "font_family":   "DM Sans, sans-serif",
        "grid_color":    "#1a2d45",
        "primary_line":  "#2a7a6f",
        "excellent":     "#3aa895",
        "good":          "#c8973a",
        "poor":          "#b85c6e",
        "text_on_bar":   "#faf6ee",
        "annotation_bg": "#1a2d45",
        "annotation_border": "#3b466c",
        "annotation_font":   "#8a9bb0",
    },
    "light": {
        "paper_bgcolor": "#faf6ee",
        "plot_bgcolor":  "#faf6ee",
        "font_color":    "#1a2d45",
        "font_family":   "DM Sans, sans-serif",
        "grid_color":    "#e8e2d8",
        "primary_line":  "#2a7a6f",
        "excellent":     "#2a7a6f",
        "good":          "#c8973a",
        "poor":          "#b85c6e",
        "text_on_bar":   "#faf6ee",
        "annotation_bg": "#faf6ee",
        "annotation_border": "#d4cfc5",
        "annotation_font":   "#1a2d45",
    },
}


def get_plotly_layout(theme: str = "dark") -> dict:
    """Return a Plotly layout dict with resolved colors for the given theme."""
    t = PLOTLY_THEMES.get(theme, PLOTLY_THEMES["dark"])
    return dict(
        paper_bgcolor=t["paper_bgcolor"],
        plot_bgcolor=t["plot_bgcolor"],
        font=dict(family=t["font_family"], color=t["font_color"]),
        margin=dict(l=50, r=30, t=40, b=50),
    )


# ══════════════════════════════════════════════════════════════
# TOKEN DEFINITIONS
# ══════════════════════════════════════════════════════════════

_TOKENS_DARK = """
    --midnight:    #0f1c2e;
    --navy:        #1a2d45;
    --card-bg:     rgba(255,255,255,0.04);
    --cream:       #faf6ee;
    --paper:       #f5f0e8;
    --muted:       #8a9bb0;
    --ink:         #0d1117;
    --teal:        #2a7a6f;
    --teal-light:  #3aa895;
    --gold:        #c8973a;
    --gold-light:  #e4b96a;
    --rose:        #b85c6e;
    --rose-light:  #d4738a;
    --border:      rgba(200,151,58,0.25);
    --card-border: rgba(255,255,255,0.07);
    --ghost-border: rgba(79,69,55,0.15);
    --shadow-sm:   0 1px 3px 0 rgba(2,14,32,0.3);
    --shadow-md:   0 4px 8px -1px rgba(2,14,32,0.4), 0 2px 4px -1px rgba(2,14,32,0.25);
    --shadow-lg:   0 12px 32px rgba(2,14,32,0.5);
    --shadow-xl:   0 24px 48px -8px rgba(2,14,32,0.6);
    --nav-bg:      rgba(15,28,46,0.85);
    --sidebar-bg:  #1a2d45;
    --surface:     #1a2d45;
    --surface-alt: #152538;
    --surface-high: #1e2a3d;
    --surface-lowest: #020e20;
    --gold-gradient: linear-gradient(135deg, #c8973a, #f3be5d);
    --teal-gradient: linear-gradient(135deg, #2a7a6f, #3aa895);
    --teal-dim:    rgba(42,122,111,0.15);
    --gold-dim:    rgba(200,151,58,0.15);
    --rose-dim:    rgba(184,92,110,0.15);
    --focus-ring:  rgba(58,168,149,0.55);
    --overlay:     rgba(255,255,255,0.04);
    /* Motion tokens */
    --ease-out:    cubic-bezier(0.0, 0.0, 0.2, 1);
    --ease-in-out: cubic-bezier(0.4, 0.0, 0.2, 1);
    --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
    --dur-fast:    150ms;
    --dur-base:    220ms;
    --dur-slow:    380ms;
    /* Radii */
    --radius-xs:   6px;
    --radius-sm:   10px;
    --radius-md:   14px;
    --radius-lg:   20px;
    --radius-xl:   28px;
    --radius-full: 9999px;"""

_TOKENS_LIGHT = """
    --midnight:    #faf6ee;
    --navy:        #f0ebe3;
    --card-bg:     rgba(15,28,46,0.04);
    --cream:       #0f1c2e;
    --paper:       #1a2d45;
    --muted:       #5a6a7e;
    --ink:         #faf6ee;
    --teal:        #2a7a6f;
    --teal-light:  #1e6359;
    --gold:        #c8973a;
    --gold-light:  #a67a2e;
    --rose:        #b85c6e;
    --rose-light:  #9a4558;
    --border:      rgba(200,151,58,0.25);
    --card-border: rgba(15,28,46,0.08);
    --shadow-sm:   0 1px 2px 0 rgba(0,0,0,0.05);
    --shadow-md:   0 4px 6px -1px rgba(0,0,0,0.08), 0 2px 4px -1px rgba(0,0,0,0.04);
    --shadow-lg:   0 10px 15px -3px rgba(0,0,0,0.08);
    --shadow-xl:   0 20px 25px -5px rgba(0,0,0,0.1);
    --nav-bg:      rgba(250,246,238,0.85);
    --sidebar-bg:  #f0ebe3;
    --surface:     #f5f0e8;
    --surface-alt: #ede8df;
    --surface-high: #ffffff;
    --surface-lowest: #e8e2d8;
    --ghost-border: rgba(15,28,46,0.06);
    --gold-gradient: linear-gradient(135deg, #c8973a, #e4b96a);
    --teal-gradient: linear-gradient(135deg, #2a7a6f, #3aa895);
    --teal-dim:    rgba(42,122,111,0.10);
    --gold-dim:    rgba(200,151,58,0.12);
    --rose-dim:    rgba(184,92,110,0.10);
    --focus-ring:  rgba(42,122,111,0.45);
    --overlay:     rgba(15,28,46,0.06);
    /* Motion tokens */
    --ease-out:    cubic-bezier(0.0, 0.0, 0.2, 1);
    --ease-in-out: cubic-bezier(0.4, 0.0, 0.2, 1);
    --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
    --dur-fast:    150ms;
    --dur-base:    220ms;
    --dur-slow:    380ms;
    /* Radii */
    --radius-xs:   6px;
    --radius-sm:   10px;
    --radius-md:   14px;
    --radius-lg:   20px;
    --radius-xl:   28px;
    --radius-full: 9999px;"""


# ══════════════════════════════════════════════════════════════
# CSS BLOCKS (modular)
# ══════════════════════════════════════════════════════════════

_CSS_RESET = """
/* ══ RESET & BASE ═════════════════════════════════════════ */
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
.stApp {{ background: var(--midnight) !important; }}
.stApp, .stApp * {{ font-family: 'DM Sans', system-ui, sans-serif !important; }}
h1, h2, h3 {{ font-family: 'Playfair Display', serif !important; letter-spacing: -0.01em !important; }}

.material-symbols-outlined {{
    font-family: 'Material Symbols Outlined' !important;
    font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24;
    font-size: 20px; vertical-align: middle;
}}
"""

_CSS_HIDE_CHROME = """
/* ══ HIDE STREAMLIT CHROME ════════════════════════════════ */
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
header[data-testid="stHeader"],
#MainMenu, footer {{ display: none !important; }}
"""

_CSS_TOPBAR = """
/* ══ NAVBAR ═══════════════════════════════════════════════ */
.stitch-topbar {
    position: fixed; top: 0; left: 0; right: 0; z-index: 999;
    height: 64px;
    background: var(--nav-bg);
    backdrop-filter: blur(20px) saturate(200%);
    -webkit-backdrop-filter: blur(20px) saturate(200%);
    border-bottom: 1px solid var(--card-border);
    padding: 0 20px;
}
.stitch-topbar-inner {
    width: 100%;
    max-width: 1440px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: center;
    gap: 16px;
}
.stitch-topbar-brand {
    font-size: 20px; font-weight: 700; letter-spacing: -0.03em;
    font-family: 'Playfair Display', serif;
    color: var(--gold-light); white-space: nowrap;
    line-height: 1.2; padding-top: 2px;
    display: flex; align-items: center; gap: 10px;
}
.stitch-topbar-nav {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    min-width: 0;
    overflow-x: auto;
    scrollbar-width: thin;
}
.stitch-topbar-nav a {
    font-family: 'DM Sans', sans-serif;
    font-size: 13px; font-weight: 500;
    color: var(--muted);
    text-decoration: none; padding: 8px 16px;
    border-radius: 9999px;
    transition: all 240ms cubic-bezier(0.4, 0, 0.2, 1);
    white-space: nowrap;
    display: flex; align-items: center; gap: 6px;
}
.stitch-topbar-nav a:hover {
    color: var(--cream);
    background: rgba(255,255,255,0.05);
}
.stitch-topbar-nav a.active {
    color: var(--teal-light); font-weight: 600;
    background: rgba(42,122,111,0.12);
}
.stitch-topbar-nav a .material-symbols-outlined {
    font-size: 16px; transition: transform 0.2s;
}
.stitch-topbar-nav a:hover .material-symbols-outlined {
    transform: translateY(-1px);
}

.stitch-topbar-actions {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 8px;
}
.stitch-topbar-btn {
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    height: 36px;
    padding: 0 12px;
    border-radius: 10px;
    font-family: 'DM Sans', sans-serif;
    font-size: 12px;
    font-weight: 700;
    white-space: nowrap;
    border: 1px solid transparent;
    transition: all 200ms ease;
}
.stitch-topbar-btn .material-symbols-outlined {
    font-size: 16px;
}
.stitch-topbar-btn-primary {
    color: #fff;
    background: var(--teal);
}
.stitch-topbar-btn-primary:hover {
    filter: brightness(1.06);
}
.stitch-topbar-btn-secondary {
    color: var(--cream);
    background: var(--surface);
    border-color: var(--card-border);
}
.stitch-topbar-btn-secondary:hover {
    border-color: var(--gold);
    color: var(--gold-light);
}

.stitch-mobile-shell {
    display: none;
    margin-top: 8px;
}
.stitch-mobile-menu {
    border: 1px solid var(--card-border);
    border-radius: 12px;
    background: var(--surface);
}
.stitch-mobile-menu > summary {
    list-style: none;
    cursor: pointer;
    padding: 10px 14px;
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--cream);
    font-size: 13px;
    font-weight: 600;
}
.stitch-mobile-menu > summary::-webkit-details-marker {
    display: none;
}
.stitch-mobile-panel {
    padding: 0 10px 10px;
    border-top: 1px solid var(--card-border);
}
.stitch-mobile-nav {
    display: grid;
    gap: 6px;
    padding: 10px 0;
}
.stitch-mobile-nav a {
    color: var(--muted);
    text-decoration: none;
    font-size: 13px;
    font-weight: 500;
    border-radius: 10px;
    padding: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.stitch-mobile-nav a.active {
    color: var(--teal-light);
    background: rgba(42,122,111,0.12);
    font-weight: 600;
}
.stitch-mobile-actions {
    display: grid;
    gap: 8px;
    padding-top: 6px;
}

@media (max-width: 1200px) {
    .stitch-topbar-inner { gap: 10px; }
    .stitch-topbar-nav { justify-content: flex-start; }
}
@media (max-width: 992px) {
    .stitch-topbar-nav a { padding: 8px 10px; font-size: 12px; }
    .stitch-topbar-btn {
        height: 34px;
        padding: 0 10px;
        font-size: 11px;
    }
}
@media (max-width: 768px) {
    .stitch-topbar {
        height: 56px;
        padding: 0 12px;
    }
    .stitch-topbar-inner {
        grid-template-columns: 1fr;
    }
    .stitch-topbar-nav,
    .stitch-topbar-actions {
        display: none !important;
    }
    .stitch-topbar-brand {
        font-size: 18px;
    }
    .stitch-mobile-shell {
        display: block;
    }
}

"""

_CSS_SIDEBAR = """
/* ══ SIDEBAR ══════════════════════════════════════════════ */
[data-testid="stSidebar"] {{
    background: var(--sidebar-bg) !important;
    border-right: 1px solid var(--card-border) !important;
    width: 220px !important;
    min-width: 220px !important;
}}
[data-testid="stSidebar"] > div {{ padding-top: 0.25rem !important; }}
[data-testid="collapsedControl"] {{ display: none !important; }}
"""

_CSS_LAYOUT = """
/* ══ MAIN CONTAINER ═══════════════════════════════════════ */
.block-container {{
    padding: 5rem 2.5rem 3rem !important;
    max-width: 1440px !important;
    margin: 0 auto !important;
}}
"""

_CSS_TYPOGRAPHY = """
/* ══ TYPOGRAPHY ═══════════════════════════════════════════ */
.eyebrow {{
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--gold);
    font-weight: 400;
}}
.section-title {{
    font-family: 'Playfair Display', serif;
    font-size: clamp(1.8rem, 3.5vw, 2.6rem);
    font-weight: 700;
    color: var(--cream);
    line-height: 1.2;
    letter-spacing: -0.01em;
}}
.section-subtitle {{
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    font-weight: 300;
    line-height: 1.6;
    color: var(--muted);
}}

/* ══ DIVIDER ══════════════════════════════════════════════ */
.divider {{
    width: 60px;
    height: 2px;
    background: linear-gradient(90deg, var(--gold), transparent);
    margin: 2rem 0 1.5rem 0;
}}

/* ══ HERO TYPOGRAPHY ══════════════════════════════════════ */
.hero-title {{
    font-family: 'Playfair Display', serif;
    font-size: clamp(32px, 4.5vw, 52px);
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1.08;
    color: var(--cream);
    margin: 0 0 20px;
}}
.hero-subtitle {{
    font-family: 'DM Sans', sans-serif;
    font-size: 16px;
    line-height: 1.75;
    color: var(--muted);
    margin: 0 0 28px;
    max-width: 540px;
}}
"""

_CSS_CARDS = """
/* ══ CARDS ════════════════════════════════════════════════ */
.stitch-card {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 10px;
    padding: 1.5rem;
    transition: transform 0.2s ease, border-color 0.2s ease;
}}
.stitch-card:hover {{
    transform: translateY(-2px);
    border-color: var(--border);
}}

/* Accent variants */
.stitch-card-accent {{ border-left: 3px solid var(--teal); }}
.stitch-card-accent-gold {{ border-left: 3px solid var(--gold); }}
.stitch-card-accent-rose {{ border-left: 3px solid var(--rose); }}

/* ══ BENTO & HERO CARDS ═══════════════════════════════════ */
.bento-card {{
    background: var(--surface);
    border-radius: 20px;
    border: 1px solid var(--card-border);
    transition: transform 0.2s ease, border-color 0.2s ease;
}}
.bento-card:hover {{
    transform: translateY(-2px);
    border-color: var(--border);
}}

/* ══ SECTION PANELS & CTA LINKS ═══════════════════════════ */
.section-panel {{
    background: var(--surface);
    border: 1px solid var(--card-border);
    border-radius: 14px;
    padding: 20px 24px;
}}

.stitch-btn-primary,
.stitch-btn-ghost {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 12px 22px;
    border-radius: 9999px;
    font-weight: 700;
    font-size: 13px;
    text-decoration: none;
    transition: all 180ms ease;
}}

.stitch-btn-primary {{
    background: var(--teal);
    color: #fff;
    box-shadow: 0 8px 20px rgba(42,122,111,0.2);
}}

.stitch-btn-primary:hover {{
    transform: translateY(-1px);
    filter: brightness(1.05);
}}

.stitch-btn-ghost {{
    background: transparent;
    border: 1px solid var(--card-border);
    color: var(--cream);
}}

.stitch-btn-ghost:hover {{
    border-color: var(--gold);
    color: var(--gold-light);
    background: var(--overlay);
}}
"""

_CSS_KPI = """
/* ══ KPI CARD ═════════════════════════════════════════════ */
.kpi-card {{
    background: var(--surface-high, var(--card-bg));
    border: 1px solid var(--ghost-border, var(--card-border));
    border-radius: 12px;
    padding: 1.5rem 1.25rem 1.125rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.25s cubic-bezier(0.4,0,0.2,1),
                border-color 0.25s ease,
                box-shadow 0.25s ease;
    box-shadow: var(--shadow-sm);
    cursor: pointer;
}}
.kpi-card:hover {{
    transform: translateY(-3px);
    border-color: var(--border);
    box-shadow: var(--shadow-lg);
}}
.kpi-card::before {{
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
}}
.kpi-card.excellent::before {{ background: var(--teal); }}
.kpi-card.good::before      {{ background: var(--gold); }}
.kpi-card.poor::before       {{ background: var(--rose); }}
.kpi-card.neutral::before    {{ background: var(--muted); }}

/* Left accent variant — Stitch "Editorial Authority" signature */
.kpi-card--left::before {{
    top: 0; left: 0; bottom: 0;
    width: 3px; height: 100%; right: auto;
}}
.kpi-label {{
    font-size: 0.8rem;
    font-family: 'DM Mono', monospace;
    color: var(--muted);
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}
.kpi-value {{
    font-size: 2.2rem;
    font-weight: 700;
    font-family: 'Playfair Display', serif;
    color: var(--cream);
    line-height: 1.1;
}}
.kpi-delta {{
    font-size: 0.7rem;
    font-weight: 700;
    margin-left: 8px;
    font-family: 'DM Mono', monospace;
}}
.kpi-delta.up   {{ color: var(--teal-light); }}
.kpi-delta.down {{ color: var(--rose); }}
"""

_CSS_BADGE = """
/* ══ BADGE ════════════════════════════════════════════════ */
.badge {{
    display: inline-block;
    padding: 0.2rem 0.6rem;
    background: rgba(42,122,111,0.15);
    border: 1px solid rgba(42,122,111,0.3);
    border-radius: 2rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    color: var(--teal-light);
    letter-spacing: 0.05em;
}}
.badge-gold {{
    background: rgba(200,151,58,0.15);
    border-color: rgba(200,151,58,0.3);
    color: var(--gold-light);
}}
.badge-rose {{
    background: rgba(184,92,110,0.15);
    border-color: rgba(184,92,110,0.3);
    color: var(--rose-light);
}}

/* ══ CATEGORY BADGE ═══════════════════════════════════════ */
.category-badge {{
    display: inline-block;
    padding: 4px 12px;
    background: var(--overlay);
    border: 1px solid var(--card-border);
    border-radius: 8px;
    font-size: 12px; font-weight: 600;
    color: var(--paper);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    transition: all 200ms ease;
    cursor: pointer;
}}
.category-badge:hover {{
    background: var(--surface);
    border-color: var(--gold);
    color: var(--gold-light);
    transform: translateY(-1px);
}}

/* ══ FILTER CHIPS ═════════════════════════════════════════ */
.filter-chip {{
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 12px;
    background: rgba(42,122,111,0.10);
    border: 1px solid rgba(42,122,111,0.20);
    border-radius: 9999px;
    font-size: 12px; font-weight: 600;
    color: var(--teal-light);
    cursor: pointer;
    transition: all 200ms ease;
}}
.filter-chip:hover {{
    background: rgba(42,122,111,0.18);
    border-color: rgba(42,122,111,0.35);
}}
"""

_CSS_BARS = """
/* ══ DATA BARS ════════════════════════════════════════════ */
.bar-track {{
    height: 8px;
    background: var(--overlay);
    border-radius: 4px;
    overflow: hidden;
    position: relative;
}}
.bar-fill {{
    height: 100%;
    background: linear-gradient(90deg, var(--teal), var(--teal-light));
    border-radius: 4px;
    transition: width 1s ease;
}}
.bar-fill-gold {{
    background: linear-gradient(90deg, var(--gold), var(--gold-light));
}}
.bar-fill-rose {{
    background: linear-gradient(90deg, var(--rose), var(--rose-light));
}}
"""

_CSS_STAT = """
/* ══ STAT CARD ════════════════════════════════════════════ */
.stat-card {{
    text-align: center;
    padding: 2rem 1.5rem;
}}
.stat-number {{
    font-family: 'Playfair Display', serif;
    font-size: clamp(2rem, 4vw, 3rem);
    font-weight: 700;
    color: var(--gold-light);
    line-height: 1;
    margin-bottom: 0.5rem;
}}
.stat-label {{
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
}}
"""

_CSS_QUOTE = """
/* ══ QUOTE BLOCK ══════════════════════════════════════════ */
.quote-block {{
    border-left: 3px solid var(--gold);
    padding: 1rem 1.5rem;
    background: rgba(200,151,58,0.05);
    border-radius: 0 8px 8px 0;
    margin: 1.5rem 0;
}}
.quote-text {{
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 1.1rem;
    color: var(--paper);
    line-height: 1.6;
}}
.quote-source {{
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: var(--gold);
    margin-top: 0.5rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}}
"""

_CSS_HEATMAP = """
/* ══ HEATMAP TABLE ════════════════════════════════════════ */
.heatmap-cell {{
    height: 40px; display: flex; align-items: center;
    justify-content: center; border-radius: 4px;
    font-weight: 700; color: white;
    transition: all 200ms ease; cursor: pointer;
}}
.heatmap-cell:hover {{
    opacity: 0.9; transform: scale(1.05);
    z-index: 10; box-shadow: var(--shadow-md);
}}
"""

_CSS_ALERTS = """
/* ══ ALERT BANNER ═════════════════════════════════════════ */
.alert-banner {
    background: rgba(184,92,110,0.10);
    border: 1px solid rgba(184,92,110,0.3);
    border-radius: 10px;
    padding: 16px 24px;
    display: flex; align-items: center; gap: 16px;
    color: var(--rose-light);
    font-weight: 600; font-size: 16px;
}
.alert-banner-success {
    background: rgba(42,122,111,0.10);
    border: 1px solid rgba(42,122,111,0.3);
    border-radius: 10px;
    padding: 16px 24px;
    display: flex; align-items: center; gap: 16px;
    color: var(--teal-light);
    font-weight: 600; font-size: 16px;
}
.alert-banner-warning {
    background: rgba(200,151,58,0.10);
    border: 1px solid rgba(200,151,58,0.3);
    border-radius: 10px;
    padding: 16px 24px;
    display: flex; align-items: center; gap: 16px;
    color: var(--gold-light);
    font-weight: 600; font-size: 16px;
}

/* ══ ALERT CARD ═══════════════════════════════════════════ */
.alert-card {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-left: 3px solid var(--rose);
    border-radius: 0 10px 10px 0;
    padding: 1.5rem;
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.alert-card:hover {
    transform: translateY(-2px);
    border-color: var(--border);
}
.alert-score {
    font-size: 2.5rem;
    font-weight: 700;
    font-family: 'Playfair Display', serif;
    color: var(--rose-light);
    line-height: 1;
}
"""

_CSS_ICON_LIST = """
/* ══ ICON LIST ════════════════════════════════════════════ */
.icon-list {{
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}}
.icon-list-item {{
    display: flex;
    align-items: flex-start;
    gap: 1rem;
}}
.icon-box {{
    width: 40px;
    height: 40px;
    min-width: 40px;
    background: rgba(42,122,111,0.15);
    border: 1px solid rgba(42,122,111,0.3);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'DM Mono', monospace;
    font-size: 1.2rem;
    color: var(--teal-light);
}}
.icon-box-gold {{
    background: rgba(200,151,58,0.15);
    border-color: rgba(200,151,58,0.3);
    color: var(--gold-light);
}}
.icon-box-rose {{
    background: rgba(184,92,110,0.15);
    border-color: rgba(184,92,110,0.3);
    color: var(--rose-light);
}}
"""

_CSS_TABLE = """
/* ══ COMPARISON TABLE ═════════════════════════════════════ */
.comparison-table {{
    width: 100%;
    border-collapse: collapse;
}}
.comparison-table th {{
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--gold);
    text-align: left;
    padding: 1rem;
    border-bottom: 1px solid var(--border);
}}
.comparison-table td {{
    font-size: 0.85rem;
    color: var(--muted);
    padding: 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}}
.comparison-table tr:hover {{
    background: rgba(255,255,255,0.02);
}}
"""

_CSS_GRIDS = """
/* ══ CARD GRIDS ═══════════════════════════════════════════ */
.card-grid {{
    display: grid;
    gap: 1.25rem;
}}
.card-grid-2 {{ grid-template-columns: repeat(2, 1fr); }}
.card-grid-3 {{ grid-template-columns: repeat(3, 1fr); }}
.card-grid-4 {{ grid-template-columns: repeat(4, 1fr); }}

@media (max-width: 900px) {{
    .card-grid-3, .card-grid-4 {{ grid-template-columns: 1fr 1fr; }}
}}
@media (max-width: 600px) {{
    .card-grid-2, .card-grid-3, .card-grid-4 {{
        grid-template-columns: 1fr;
    }}
}}
"""

_CSS_GAUGE = """
/* ══ GAUGE SVG ════════════════════════════════════════════ */
.gauge-container {{
    background: var(--surface);
    border-radius: 10px;
    padding: 24px;
    display: flex; flex-direction: column; align-items: center;
    border: 1px solid transparent; transition: border-color 0.2s;
}}
.gauge-container:hover {{ border-color: var(--card-border); }}
"""

_CSS_TABS = """
/* ══ TABS ═════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {{
    border-bottom: 1px solid var(--card-border) !important;
    background: transparent !important; gap: 32px !important;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important; border: none !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important; font-weight: 500 !important;
    color: var(--muted) !important;
    padding: 0 0 16px !important; transition: all 200ms ease; cursor: pointer;
}}
.stTabs [data-baseweb="tab"]:hover {{ color: var(--teal-light) !important; }}
.stTabs [aria-selected="true"] {{
    color: var(--gold-light) !important;
    border-bottom: 2px solid var(--gold) !important;
    font-weight: 600 !important;
}}
"""

_CSS_DATA_TABLE = """
/* ══ DATA TABLE ═══════════════════════════════════════════ */
[data-testid="stDataFrame"] thead tr th {{
    background: var(--surface) !important;
    font-size: 11px !important; font-weight: 600 !important;
    text-transform: uppercase !important; letter-spacing: 0.05em !important;
    color: var(--muted) !important;
    padding: 16px 24px !important;
    border-bottom: 2px solid var(--card-border) !important;
    font-family: 'DM Mono', monospace !important;
}}
[data-testid="stDataFrame"] tbody tr {{
    border-bottom: 1px solid var(--card-border) !important;
}}
[data-testid="stDataFrame"] tbody tr:hover {{
    background: var(--overlay) !important;
}}
[data-testid="stDataFrame"] tbody tr td {{
    padding: 12px 24px !important; font-size: 14px !important;
    color: var(--paper) !important;
}}
"""

_CSS_STREAMLIT_OVERRIDES = """
/* ══ NATIVE STREAMLIT OVERRIDES ═══════════════════════════ */
.stButton > button {{
    color: var(--paper) !important;
    border-color: var(--card-border) !important;
    background: var(--surface) !important;
    transition: all 200ms ease;
}}
.stButton > button:hover {{
    border-color: var(--gold) !important;
    color: var(--gold-light) !important;
}}
.stTextInput input,
.stSelectbox > div > div,
.stMultiSelect > div > div {{
    background-color: var(--card-bg) !important;
    color: var(--paper) !important;
    border-color: var(--card-border) !important;
}}
.stSlider [data-baseweb="slider"] {{
    background: transparent !important;
}}
.stDownloadButton > button {{
    background: var(--teal) !important;
    color: var(--cream) !important;
    border: none !important; border-radius: 8px;
    font-weight: 600 !important;
}}
.stDownloadButton > button:hover {{
    opacity: 0.9;
}}
"""

_CSS_SIDEBAR_TOGGLE = """
/* ══ THEME TOGGLE BUTTON ══════════════════════════════════ */
[data-testid="stSidebar"] .stButton[data-testid*="theme_toggle"] > button {{
    background: var(--surface) !important;
    color: var(--paper) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 9999px !important;
    font-weight: 600 !important; font-size: 13px !important;
    padding: 8px 16px !important;
    transition: all 200ms ease;
}}
[data-testid="stSidebar"] .stButton[data-testid*="theme_toggle"] > button:hover {{
    background: var(--surface-alt) !important;
    border-color: var(--gold) !important;
}}
"""

_CSS_SCROLLBAR = """
/* ══ SCROLLBAR ════════════════════════════════════════════ */
::-webkit-scrollbar {{ width: 8px; height: 8px; }}
::-webkit-scrollbar-track {{ background: var(--surface); }}
::-webkit-scrollbar-thumb {{ background: var(--muted); border-radius: 4px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--gold); }}
"""

_CSS_ANIMATIONS = """
/* ══ ENTRY ANIMATIONS ═════════════════════════════════════ */
@keyframes fadeUp {{
    from {{
        opacity: 0;
        transform: translateY(20px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}
.fade-up {{
    animation: fadeUp 0.5s ease forwards;
}}
.fade-up-1 {{ animation-delay: 0s; }}
.fade-up-2 {{ animation-delay: 0.08s; }}
.fade-up-3 {{ animation-delay: 0.16s; }}
.fade-up-4 {{ animation-delay: 0.24s; }}
.fade-up-5 {{ animation-delay: 0.32s; }}

@keyframes fadeInUp {{
    from {{ opacity: 0; transform: translateY(12px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

@keyframes bounceY {{
    0%, 100% {{ transform: translateY(0); }}
    50%      {{ transform: translateY(6px); }}
}}

@keyframes shimmer {{
    0%   {{ background-position: -600px 0; }}
    100% {{ background-position: 600px 0; }}
}}

@keyframes scaleIn {{
    from {{ opacity: 0; transform: scale(0.94); }}
    to   {{ opacity: 1; transform: scale(1); }}
}}

@keyframes slideInLeft {{
    from {{ opacity: 0; transform: translateX(-20px); }}
    to   {{ opacity: 1; transform: translateX(0); }}
}}

@keyframes slideInRight {{
    from {{ opacity: 0; transform: translateX(20px); }}
    to   {{ opacity: 1; transform: translateX(0); }}
}}

@keyframes numberPop {{
    0%   {{ opacity: 0; transform: scale(0.85); }}
    60%  {{ transform: scale(1.05); }}
    100% {{ opacity: 1; transform: scale(1); }}
}}

@keyframes barGrow {{
    from {{ transform: scaleX(0); }}
    to   {{ transform: scaleX(1); }}
}}

@keyframes pulseSoft {{
    0%, 100% {{ opacity: 1; }}
    50%      {{ opacity: 0.6; }}
}}

@keyframes spin {{
    to {{ transform: rotate(360deg); }}
}}

@keyframes topbarAppear {{
    from {{ opacity: 0; transform: translateY(-8px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

/* ══ REDUCED MOTION ═══════════════════════════════════════ */
@media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }}
}}
"""

_CSS_SKELETON = """
/* ══ SKELETON / SHIMMER LOADING ═══════════════════════════ */
.skeleton {{
    background: linear-gradient(
        90deg,
        var(--ghost-border) 25%,
        var(--overlay) 37%,
        var(--ghost-border) 63%
    );
    background-size: 800px 100%;
    animation: shimmer 1.6s infinite linear;
    border-radius: var(--radius-xs, 6px);
}}
.skeleton-card {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-md, 14px);
    padding: 1.5rem;
    display: flex; flex-direction: column; gap: 12px;
}}
.skeleton-line     {{ height: 12px; border-radius: 9999px; }}
.skeleton-line-sm  {{ height: 10px; width: 60%; }}
.skeleton-line-lg  {{ height: 20px; }}
.skeleton-circle   {{ width: 40px; height: 40px; border-radius: 9999px; }}
.skeleton-kpi      {{ height: 120px; border-radius: var(--radius-md, 14px); }}
"""

_CSS_BENTO_GRID = """
/* ══ BENTO GRID LAYOUT ═══════════════════════════════════ */
.bento-grid {{
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    grid-auto-rows: minmax(80px, auto);
    gap: 16px;
}}
.bento-col-4  {{ grid-column: span 4; }}
.bento-col-6  {{ grid-column: span 6; }}
.bento-col-8  {{ grid-column: span 8; }}
.bento-col-12 {{ grid-column: span 12; }}
.bento-row-2  {{ grid-row: span 2; }}
.bento-row-3  {{ grid-row: span 3; }}

@media (max-width: 1024px) {{
    .bento-col-4, .bento-col-6 {{ grid-column: span 6; }}
    .bento-col-8 {{ grid-column: span 12; }}
}}
@media (max-width: 640px) {{
    .bento-grid {{ gap: 10px; }}
    .bento-col-4, .bento-col-6,
    .bento-col-8, .bento-col-12 {{ grid-column: span 12; }}
}}
"""

_CSS_INICIO = """
/* ══ INICIO SECTION ═══════════════════════════════════════ */

/* Hero */
.inicio-hero {{
    text-align: center;
    padding: 72px 24px 48px;
    max-width: 680px;
    margin: 0 auto;
}}

.inicio-hero-tag {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(200,151,58,0.12);
    border: 1px solid rgba(200,151,58,0.28);
    border-radius: 9999px;
    padding: 5px 16px;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: var(--gold-light);
    letter-spacing: 0.10em;
    text-transform: uppercase;
    margin-bottom: 24px;
    animation: fadeInUp 0.5s 0.1s both;
}}

.inicio-hero .hero-title {{
    animation: fadeInUp 0.5s 0.2s both;
}}

.inicio-hero .hero-title em {{
    font-style: normal;
    color: var(--gold-light);
}}

.inicio-hero .hero-subtitle {{
    animation: fadeInUp 0.5s 0.3s both;
}}

/* Scroll hint */
.inicio-scroll-hint {{
    text-align: center;
    color: var(--muted);
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    padding: 12px 0 40px;
    animation: fadeInUp 1s 0.6s both;
    letter-spacing: 0.06em;
}}

.inicio-scroll-arrow {{
    display: block;
    font-size: 20px;
    animation: bounceY 2s 1.5s infinite;
    margin-top: 4px;
}}

/* Divider */
.inicio-divider {{
    display: flex;
    align-items: center;
    gap: 16px;
    margin: 48px 0 32px;
    animation: fadeInUp 0.5s both;
}}

.inicio-divider-label {{
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.10em;
    white-space: nowrap;
    flex-shrink: 0;
}}

.inicio-divider-line {{
    flex: 1;
    height: 1px;
    background: var(--card-border);
}}

/* Activity feed */
.inicio-activity-item {{
    padding: 14px 0;
    border-bottom: 1px solid var(--card-border);
    animation: fadeInUp 0.4s both;
}}

.inicio-activity-name {{
    font-size: 0.88rem;
    font-weight: 500;
    color: var(--cream);
    line-height: 1.3;
    margin-bottom: 6px;
}}

.inicio-activity-meta {{
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.inicio-activity-org {{
    font-size: 0.75rem;
    color: var(--muted);
}}

.inicio-activity-date {{
    font-size: 0.75rem;
    color: var(--muted);
    opacity: 0.6;
}}

/* Health bars */
.inicio-health-label {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}}

.inicio-health-name {{
    font-size: 0.82rem;
    color: var(--cream);
    font-weight: 500;
}}

.inicio-health-pct {{
    font-size: 0.80rem;
    color: var(--muted);
    font-weight: 500;
    font-family: 'DM Mono', monospace;
}}

/* Empty state */
.inicio-empty-state {{
    padding: 32px;
    text-align: center;
    color: var(--muted);
    font-size: 0.85rem;
    border: 1px dashed var(--card-border);
    border-radius: 8px;
    margin-top: 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
}}

/* Footer */
.inicio-footer {{
    text-align: center;
    padding: 48px 24px 24px;
    color: var(--muted);
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.04em;
    opacity: 0.7;
}}

@media (max-width: 768px) {{
    .inicio-hero {{
        padding: 48px 16px 32px;
    }}
}}
"""

_CSS_PIPELINE = """
/* ══ PIPELINE STATUS PANEL ════════════════════════════════ */
.pipeline-status-panel {{
    background: var(--surface);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-md, 14px);
    padding: 24px;
    margin-bottom: 24px;
}}
.pipeline-status-header {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;
}}
.pipeline-status-title {{
    font-family: 'DM Sans', sans-serif;
    font-size: 15px;
    font-weight: 600;
    color: var(--cream);
}}

/* ── Antes vs Ahora comparison grid ─────────────────────── */
.comparison-row {{
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 60px;
    gap: 12px;
    align-items: center;
    padding: 14px 16px;
    border-bottom: 1px solid var(--card-border);
    transition: background var(--dur-base, 220ms) ease;
}}
.comparison-row:hover {{
    background: var(--overlay);
}}
.comparison-row-header {{
    border-bottom: 2px solid var(--border);
    font-weight: 700;
}}
.comparison-metric-label {{
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    font-weight: 500;
    color: var(--cream);
    display: flex;
    align-items: center;
    gap: 8px;
}}
.comparison-value-antes {{
    font-family: 'DM Mono', monospace;
    font-size: 14px;
    color: var(--muted);
    text-align: right;
}}
.comparison-value-ahora {{
    font-family: 'DM Mono', monospace;
    font-size: 14px;
    font-weight: 700;
    color: var(--teal-light);
    text-align: right;
}}
.comparison-delta {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 2px;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    color: var(--teal-light);
    background: var(--teal-dim);
    border-radius: var(--radius-full, 9999px);
    padding: 2px 8px;
    white-space: nowrap;
}}

/* ── Failure panel ──────────────────────────────────────── */
.failure-panel {{
    background: var(--surface);
    border: 1px solid var(--card-border);
    border-left: 3px solid var(--rose);
    border-radius: 0 var(--radius-sm, 10px) var(--radius-sm, 10px) 0;
    padding: 20px 24px;
    margin-bottom: 16px;
}}
.failure-panel-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
}}
.failure-panel-title {{
    font-family: 'Playfair Display', serif;
    font-size: 18px;
    font-weight: 700;
    color: var(--cream);
    display: flex;
    align-items: center;
    gap: 8px;
}}
.failure-panel-count {{
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    font-weight: 700;
    background: var(--rose-dim);
    color: var(--rose-light);
    border-radius: var(--radius-full, 9999px);
    padding: 2px 10px;
}}
.failure-panel-note {{
    color: var(--muted);
    font-size: 12px;
    margin: 12px 0 0;
}}
.failure-cause-row {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid var(--card-border);
}}
.failure-cause-row:last-child {{
    border-bottom: none;
}}
.failure-cause-badge {{
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 3px 10px;
    border-radius: var(--radius-full, 9999px);
    background: var(--rose-dim);
    color: var(--rose-light);
    border: 1px solid rgba(184,92,110,0.3);
    white-space: nowrap;
}}
.failure-cause-badge-gold {{
    background: var(--gold-dim);
    color: var(--gold-light);
    border-color: rgba(200,151,58,0.3);
}}
.failure-slug {{
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    color: var(--muted);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}}
.failure-reason {{
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    color: var(--cream);
    line-height: 1.4;
}}

/* ── Resource vs unique clarity ─────────────────────────── */
.resource-clarity-row {{
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 12px 16px;
    background: var(--surface);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-sm, 10px);
    margin-bottom: 12px;
}}
.resource-clarity-number {{
    font-family: 'Playfair Display', serif;
    font-size: 28px;
    font-weight: 700;
    color: var(--cream);
    line-height: 1;
}}
.resource-clarity-label {{
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    color: var(--muted);
}}
.resource-clarity-arrow {{
    color: var(--gold);
    font-size: 20px;
    flex-shrink: 0;
}}

/* ── Pipeline responsive ────────────────────────────────── */
@media (max-width: 1024px) {{
    .comparison-row {{
        grid-template-columns: 2fr 1fr 1fr 50px;
        gap: 8px;
        padding: 12px;
    }}
}}
@media (max-width: 768px) {{
    .comparison-row {{
        grid-template-columns: 1fr;
        gap: 4px;
        padding: 12px;
    }}
    .comparison-value-antes,
    .comparison-value-ahora {{
        text-align: left;
    }}
    .comparison-delta {{
        justify-content: flex-start;
        width: fit-content;
    }}
    .failure-cause-row {{
        flex-wrap: wrap;
    }}
    .resource-clarity-row {{
        flex-wrap: wrap;
    }}
}}
@media (max-width: 375px) {{
    .pipeline-status-panel {{
        padding: 16px;
    }}
    .failure-panel {{
        padding: 14px 16px;
    }}
    .comparison-metric-label {{
        font-size: 13px;
    }}
}}

/* ── Focus visible for pipeline interactive elements ───── */
.comparison-row a:focus-visible,
.failure-cause-row a:focus-visible {{
    outline: 2px solid var(--gold);
    outline-offset: 2px;
}}
"""

_CSS_SINGLEPAGE = """
/* ══════════════════════════════════════════════════════════
   SINGLE-PAGE LAYOUT — scroll anchors, section breaks,
   status-bar, footer, pipeline/weights/insights grids
   ══════════════════════════════════════════════════════════ */

/* ── Scroll + anchors ─────────────────────────────────────── */
html {{ scroll-behavior: smooth; }}

.nl-anchor,
section[id="desarrollo"],
section[id="dashboards"],
section[id="conclusiones"],
section[id="footer"] {{
    scroll-margin-top: 96px;
    display: block;
}}

.nl-section {{
    padding: 72px 0 40px;
}}

.nl-section-title {{
    margin-bottom: 12px;
}}

.nl-section-subtitle {{
    max-width: 720px;
    margin-bottom: 8px;
}}

.nl-section-break {{
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--card-border) 40%, var(--card-border) 60%, transparent);
    margin: 56px 0 24px;
}}

.nl-section-error {{
    border: 1px solid var(--rose-dim);
    background: var(--rose-dim);
    border-radius: 14px;
    padding: 20px 24px;
    margin: 24px 0;
}}
.nl-section-error-title {{
    font-family: 'Playfair Display', serif;
    font-size: 18px;
    color: var(--rose-light);
    margin: 0 0 8px;
}}
.nl-section-error-body {{
    color: var(--muted);
    font-size: 13px;
    font-family: 'DM Mono', monospace;
    margin: 0;
    overflow-wrap: anywhere;
}}

.nl-subsection-header {{
    display: flex;
    align-items: baseline;
    gap: 16px;
    margin: 32px 0 20px;
}}

.nl-section-closure {{
    border-top: 1px solid var(--card-border);
    padding-top: 20px;
    margin-top: 32px;
}}

/* ── Sidebar Status Bar (extraído de dashboard_v3.py) ───── */
.nl-sb-brand {{
    padding: 0 0 18px;
}}
.nl-sb-title {{
    font-family: 'Playfair Display', serif;
    font-size: 20px;
    font-weight: 700;
    color: var(--gold-light);
    display: flex;
    align-items: center;
    gap: 8px;
}}
.nl-sb-version {{
    font-size: 10px;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
    font-family: 'DM Mono', monospace;
    margin-top: 4px;
}}
.nl-sb-divider {{
    border: none;
    border-top: 1px solid var(--card-border);
    margin: 0 0 16px;
}}
.nl-sb-status {{
    background: var(--surface-alt);
    border-radius: 12px;
    padding: 12px;
    border: 1px solid var(--card-border);
    color: var(--muted);
    font-size: 11px;
    line-height: 1.8;
    font-family: 'DM Sans', sans-serif;
}}
.nl-sb-row {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 6px;
}}
.nl-sb-row .material-symbols-outlined {{
    font-size: 14px;
    color: var(--gold);
}}
.nl-sb-row strong {{ color: var(--cream); }}
.nl-sb-alerts {{
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid var(--card-border);
}}
.nl-sb-alerts.is-critical {{ color: var(--rose-light); }}
.nl-sb-alerts.is-ok       {{ color: var(--teal-light); }}
.nl-sb-gap {{ height: 20px; }}

/* ── Pipeline grid (Desarrollo) ──────────────────────────── */
.nl-pipeline-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 20px;
    margin-top: 20px;
}}
.nl-pipeline-step {{
    padding: 24px;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
}}
.nl-pipeline-icon {{
    color: var(--gold);
    font-size: 32px;
}}
.nl-pipeline-title {{
    margin: 0;
    font-size: 18px;
}}
.nl-pipeline-body {{
    margin: 0;
    font-size: 13px;
    color: var(--muted);
    line-height: 1.6;
}}

/* ── Weights grid (Desarrollo / ISO 25012) ──────────────── */
.nl-weights-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
    margin-top: 20px;
}}
.nl-weight-row {{
    display: flex;
    flex-direction: column;
    gap: 6px;
}}
.nl-weight-head {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
}}
.nl-weight-label {{
    font-weight: 700;
    color: var(--cream);
    font-size: 14px;
}}
.nl-weight-value {{
    font-family: 'DM Mono', monospace;
    color: var(--gold-light);
    font-weight: 600;
    font-size: 13px;
}}
.nl-weight-fill {{
    background: var(--gold);
    height: 100%;
}}
.nl-weight-fill[data-width]   {{ width: 30%; }}
.nl-weight-fill[data-width="8"]  {{ width: 8%; }}
.nl-weight-fill[data-width="15"] {{ width: 15%; }}
.nl-weight-fill[data-width="21"] {{ width: 21%; }}
.nl-weight-fill[data-width="24"] {{ width: 24%; }}
.nl-weight-fill[data-width="30"] {{ width: 30%; }}
.nl-weight-fill[data-width="45"] {{ width: 45%; }}
.nl-weight-fill[data-width="75"] {{ width: 75%; }}
.nl-weight-fill[data-width="90"] {{ width: 90%; }}
.nl-weight-fill[data-width="100"] {{ width: 100%; }}
.nl-weight-desc {{
    font-size: 12px;
    color: var(--muted);
    margin: 4px 0 0;
    line-height: 1.5;
}}

/* ── Stats grid (Desarrollo / universo) ─────────────────── */
.nl-stats-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
    margin-top: 20px;
}}
.nl-stat-card {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 6px;
}}
.nl-stat-icon {{
    color: var(--gold-light);
    font-size: 22px;
}}
.nl-stat-value {{
    font-family: 'Playfair Display', serif;
    font-size: 28px;
    font-weight: 700;
    color: var(--cream);
    line-height: 1;
}}
.nl-stat-label {{
    font-size: 12px;
    color: var(--muted);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}}

/* ── Insight cards (Conclusiones) ────────────────────────── */
.nl-insights-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 20px;
}}
.nl-insight-card {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-left: 3px solid var(--muted);
    border-radius: 12px;
    padding: 22px;
    display: flex;
    gap: 14px;
    align-items: flex-start;
}}
.nl-insight-positive  {{ border-left-color: var(--teal); }}
.nl-insight-warn      {{ border-left-color: var(--gold); }}
.nl-insight-critical  {{ border-left-color: var(--rose); }}
.nl-insight-neutral   {{ border-left-color: var(--muted); }}
.nl-insight-icon {{
    font-size: 26px;
    flex-shrink: 0;
}}
.nl-insight-positive .nl-insight-icon {{ color: var(--teal-light); }}
.nl-insight-warn     .nl-insight-icon {{ color: var(--gold-light); }}
.nl-insight-critical .nl-insight-icon {{ color: var(--rose-light); }}
.nl-insight-neutral  .nl-insight-icon {{ color: var(--muted); }}
.nl-insight-body {{
    flex: 1;
}}
.nl-insight-title {{
    font-family: 'Playfair Display', serif;
    color: var(--cream);
    font-size: 17px;
    margin: 0 0 6px;
    font-weight: 700;
}}
.nl-insight-text {{
    color: var(--muted);
    font-size: 13px;
    line-height: 1.6;
    margin: 0;
}}
.nl-insight-text strong {{ color: var(--cream); }}

/* ── Recommendations list (Conclusiones) ─────────────────── */
.nl-rec-list {{
    list-style: none;
    counter-reset: rec;
    padding: 0;
    margin: 20px 0 0;
    display: flex;
    flex-direction: column;
    gap: 14px;
}}
.nl-rec-item {{
    counter-increment: rec;
    display: flex;
    gap: 16px;
    align-items: flex-start;
    padding: 18px 20px;
    background: var(--surface-alt);
    border-left: 3px solid var(--gold);
    border-radius: 10px;
}}
.nl-rec-item::before {{
    content: counter(rec);
    font-family: 'Playfair Display', serif;
    font-weight: 700;
    font-size: 22px;
    color: var(--gold-light);
    min-width: 32px;
}}
.nl-rec-icon {{
    color: var(--gold-light);
    font-size: 22px;
    margin-top: 2px;
}}
.nl-rec-body {{ flex: 1; }}
.nl-rec-title {{
    font-size: 15px;
    font-weight: 700;
    color: var(--cream);
    margin: 0 0 4px;
}}
.nl-rec-text {{
    font-size: 13px;
    color: var(--muted);
    line-height: 1.6;
    margin: 0;
}}

/* ── Footer (extraído de dashboard_v3.py) ────────────────── */
.nl-footer {{
    margin-top: 80px;
    padding-top: 48px;
    border-top: 1px solid var(--card-border);
}}
.nl-footer-top {{
    display: grid;
    grid-template-columns: minmax(240px, 1.4fr) repeat(3, 1fr);
    gap: 40px;
    padding-bottom: 40px;
}}
.nl-footer-brand {{
    display: flex;
    flex-direction: column;
    gap: 12px;
}}
.nl-footer-logo {{
    font-family: 'Playfair Display', serif;
    font-size: 26px;
    font-weight: 700;
    color: var(--gold-light);
    letter-spacing: -0.01em;
}}
.nl-footer-tagline {{
    font-size: 13px;
    color: var(--muted);
    line-height: 1.6;
    margin: 0;
    max-width: 260px;
}}
.nl-footer-col {{
    display: flex;
    flex-direction: column;
    gap: 10px;
}}
.nl-footer-col-title {{
    font-size: 12px;
    font-weight: 700;
    color: var(--cream);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0 0 6px;
    font-family: 'DM Mono', monospace;
}}
.nl-footer-link {{
    color: var(--muted);
    font-size: 13px;
    font-weight: 500;
    text-decoration: none;
    font-family: 'DM Sans', sans-serif;
    transition: color 180ms ease;
}}
.nl-footer-link:hover {{
    color: var(--gold-light);
}}
.nl-footer-bottom {{
    border-top: 1px solid var(--card-border);
    padding: 20px 0 30px;
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 16px;
    font-family: 'DM Sans', sans-serif;
    font-size: 12px;
    color: var(--muted);
}}
.nl-footer-bottom strong {{ color: var(--cream); }}

@media (max-width: 860px) {{
    .nl-footer-top {{
        grid-template-columns: 1fr;
        gap: 24px;
    }}
    .nl-pipeline-grid,
    .nl-insights-grid,
    .nl-weights-grid,
    .nl-stats-grid {{
        grid-template-columns: 1fr;
    }}
}}
"""


_CSS_A11Y = """
/* ══ ACCESSIBILITY: REDUCED MOTION ════════════════════════ */
@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }}
}}

/* ══ FOCUS STATES ═════════════════════════════════════════ */
a:focus-visible,
button:focus-visible {
    outline: 2px solid var(--gold);
    outline-offset: 2px;
}

/* ══ PAGINATION ═══════════════════════════════════════════ */
.stitch-pagination {
    margin-top: 20px;
    border: 1px solid var(--card-border);
    border-radius: 12px;
    background: var(--surface);
    padding: 10px 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
}

.stitch-pagination-meta {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    color: var(--muted);
}

.stitch-pagination-meta strong {
    color: var(--cream);
}

.stitch-pagination-controls {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}

.stitch-page-link {
    min-width: 36px;
    height: 36px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0 10px;
    background: var(--surface);
    border: 1px solid var(--card-border);
    border-radius: 10px;
    color: var(--muted);
    text-decoration: none;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 200ms ease;
}

.stitch-page-link:hover {
    background: var(--overlay);
    border-color: var(--gold);
    color: var(--gold-light);
}

.stitch-page-link.active {
    background: rgba(42,122,111,0.12);
    border-color: rgba(42,122,111,0.35);
    color: var(--teal-light);
}

.stitch-page-link.disabled {
    pointer-events: none;
    opacity: 0.35;
}

@media (max-width: 768px) {
    .stitch-pagination {
        padding: 10px;
    }
    .stitch-pagination-controls {
        width: 100%;
        justify-content: center;
    }
}

"""

_CSS_BACKGROUNDS = """
/* ══ ATMOSPHERIC BACKGROUNDS ══════════════════════════════ */
.bg-hero {
    background:
        radial-gradient(ellipse at 20% 50%, rgba(42,122,111,0.15), transparent 60%),
        radial-gradient(ellipse at 80% 20%, rgba(200,151,58,0.10), transparent 50%),
        var(--midnight);
}
.bg-teal {
    background:
        radial-gradient(ellipse at 70% 40%, rgba(42,122,111,0.12), transparent 55%),
        var(--midnight);
}
.bg-gold {
    background:
        radial-gradient(ellipse at 30% 60%, rgba(200,151,58,0.12), transparent 55%),
        var(--midnight);
}
"""

_CSS_UTILITIES = """
/* ══ UTILITIES ════════════════════════════════════════════ */
.d-flex { display: flex; }
.align-center { align-items: center; }
.justify-between { justify-content: space-between; }
.gap-2 { gap: 8px; }
.gap-3 { gap: 12px; }
.gap-4 { gap: 16px; }
.mt-2 { margin-top: 8px; }
.mt-3 { margin-top: 12px; }
.mt-4 { margin-top: 16px; }
.mb-2 { margin-bottom: 8px; }
.mb-3 { margin-bottom: 12px; }
.mb-4 { margin-bottom: 16px; }
.mb-5 { margin-bottom: 24px; }
.mb-6 { margin-bottom: 32px; }
.p-0 { padding: 0; }
.p-4 { padding: 16px; }
.p-5 { padding: 24px; }
.text-center { text-align: center; }
.text-right { text-align: right; }
.text-truncate { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.w-100 { width: 100%; }
.h-100 { height: 100%; }

/* ══ GOLD GRADIENT CTA — Stitch Signature ════════════════ */
.btn-gold-gradient {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 12px 24px;
    background: var(--gold-gradient);
    color: #1a1400;
    font-family: 'DM Sans', sans-serif;
    font-weight: 700;
    font-size: 13px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    text-decoration: none;
    transition: all 200ms ease;
    box-shadow: 0 4px 12px rgba(200,151,58,0.25);
}}
.btn-gold-gradient:hover {{
    filter: brightness(1.08);
    transform: translateY(-1px);
    box-shadow: 0 8px 20px rgba(200,151,58,0.35);
}}
.btn-gold-gradient .material-symbols-outlined {{
    font-size: 18px;
}}

/* ══ DATA BREADCRUMB — Stitch "Digital Archives" ═════════ */
.data-breadcrumb {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    background: rgba(1,98,88,0.15);
    border: 1px solid rgba(1,98,88,0.3);
    border-radius: 9999px;
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    color: var(--teal-light);
    letter-spacing: 0.04em;
}}
.data-breadcrumb .material-symbols-outlined {{
    font-size: 14px;
}}

/* ══ SURFACE CARDS — Stitch Tonal Hierarchy ══════════════ */
.surface-high-card {{
    background: var(--surface-high, #1e2a3d);
    border-radius: 12px;
    padding: 1.25rem;
    border: 1px solid var(--ghost-border, rgba(79,69,55,0.15));
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}}
.surface-high-card:hover {{
    border-color: var(--card-border);
    box-shadow: var(--shadow-md);
}}

/* ══ CIRCULAR SCORE GAUGE — Calidad Pro ══════════════════ */
.score-ring {{
    position: relative;
    width: 160px;
    height: 160px;
    margin: 0 auto 16px;
}}
.score-ring svg {{
    transform: rotate(-90deg);
}}
.score-ring-value {{
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-family: 'Playfair Display', serif;
    font-size: 2.8rem;
    font-weight: 700;
    color: var(--cream);
    line-height: 1;
}}
.score-ring-label {{
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 4px;
}}
"""



# ══════════════════════════════════════════════════════════════
# MAIN INJECTION FUNCTION
# ══════════════════════════════════════════════════════════════

def inject_design_system(theme: str = "dark") -> str:
    """Inject the full NL 2026 design system CSS.

    Composes all modular CSS blocks with resolved theme tokens.

    Args:
        theme: 'dark' (default) or 'light'.

    Call with: st.markdown(inject_design_system(theme), unsafe_allow_html=True)
    """
    tokens = _TOKENS_DARK if theme == "dark" else _TOKENS_LIGHT

    blocks = [
        _CSS_RESET,
        _CSS_HIDE_CHROME,
        _CSS_TOPBAR,
        _CSS_SIDEBAR,
        _CSS_LAYOUT,
        _CSS_TYPOGRAPHY,
        _CSS_CARDS,
        _CSS_KPI,
        _CSS_BADGE,
        _CSS_BARS,
        _CSS_STAT,
        _CSS_QUOTE,
        _CSS_HEATMAP,
        _CSS_ALERTS,
        _CSS_ICON_LIST,
        _CSS_TABLE,
        _CSS_GRIDS,
        _CSS_GAUGE,
        _CSS_TABS,
        _CSS_DATA_TABLE,
        _CSS_STREAMLIT_OVERRIDES,
        _CSS_SIDEBAR_TOGGLE,
        _CSS_SCROLLBAR,
        _CSS_ANIMATIONS,
        _CSS_SKELETON,
        _CSS_BENTO_GRID,
        _CSS_INICIO,
        _CSS_PIPELINE,
        _CSS_SINGLEPAGE,
        _CSS_A11Y,
        _CSS_BACKGROUNDS,
        _CSS_UTILITIES,
    ]

    # All blocks are raw CSS strings. Some use {{ }} for Python escaping,
    # others use raw { }. We normalize by unescaping {{ → { and }} → }.
    resolved: list[str] = []
    for b in blocks:
        resolved.append(b.replace("{{", "{").replace("}}", "}"))
    css_body = "\n".join(resolved)

    return f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');
:root {{ {tokens} }}
{css_body}
</style>"""

