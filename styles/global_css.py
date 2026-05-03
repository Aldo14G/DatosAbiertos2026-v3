# styles/global_css.py
"""NL 2026 Design System — Midnight/Teal/Gold/Rose palette.

Canonical reference: .agent/skills/design-system-pro/SKILL.md

Architecture:
    inject_design_system(theme) → returns full <style> block for st.markdown()
    get_plotly_layout(theme)    → returns Plotly layout dict with resolved hex
    PLOTLY_THEMES              → raw theme dicts for Plotly (CSS vars not supported)

Fonts: Chronicle Display (titles), IBM Plex Sans (body), IBM Plex Mono (data/labels).
Palette: midnight/navy base, teal (positive), gold (structure), rose (alert).
"""

from __future__ import annotations

# ══════════════════════════════════════════════════════════════
# RAW TOKEN DICTS  (single source of truth for Python consumers)
# Keys mirror CSS custom-property names; PLOTLY_THEMES derives from these.
# ══════════════════════════════════════════════════════════════

_RAW_DARK: dict[str, str] = {
    "midnight"         : "#0f1c2e",
    "navy"             : "#1a2d45",
    "cream"            : "#faf6ee",
    "teal"             : "#3aa895",
    "teal_dim"         : "rgba(58,168,149,0.12)",
    "gold"             : "#d4a24c",
    "rose"             : "#c66b7d",
    "font_family"      : "'IBM Plex Sans', sans-serif",
    "annotation_border": "#3b466c",
    "annotation_font"  : "#8a9bb0",
}

_RAW_LIGHT: dict[str, str] = {
    "midnight"         : "#f9f8f5",
    "navy"             : "#f3f4f6",
    "cream"            : "#0d1117",
    "teal"             : "#2a7a6f",
    "teal_dim"         : "rgba(42,122,111,0.10)",
    "gold"             : "#c8973a",
    "rose"             : "#b85c6e",
    "font_family"      : "'IBM Plex Sans', sans-serif",
    "grid_color"       : "#e8e2d8",
    "text_on_bar"      : "#faf6ee",
    "annotation_bg"    : "#faf6ee",
    "annotation_border": "#d4cfc5",
    "annotation_font"  : "#1a2d45",
}


# ══════════════════════════════════════════════════════════════
# PLOTLY THEMES (derived from _RAW_DARK / _RAW_LIGHT)
# CSS vars don't work in Plotly — resolved hex required.
# ══════════════════════════════════════════════════════════════

PLOTLY_THEMES: dict[str, dict[str, str]] = {
    "dark": {
        "paper_bgcolor"    : _RAW_DARK["midnight"],
        "plot_bgcolor"     : _RAW_DARK["midnight"],
        "font_color"       : _RAW_DARK["cream"],
        "font_family"      : _RAW_DARK["font_family"],
        "grid_color"       : _RAW_DARK["navy"],
        "primary_line"     : _RAW_DARK["teal"],
        "excellent"        : _RAW_DARK["teal"],
        "excellent_dim"    : _RAW_DARK["teal_dim"],
        "good"             : _RAW_DARK["gold"],
        "poor"             : _RAW_DARK["rose"],
        "text_on_bar"      : _RAW_DARK["cream"],
        "annotation_bg"    : _RAW_DARK["navy"],
        "annotation_border": _RAW_DARK["annotation_border"],
        "annotation_font"  : _RAW_DARK["annotation_font"],
    },
    "light": {
        "paper_bgcolor"    : _RAW_LIGHT["midnight"],
        "plot_bgcolor"     : _RAW_LIGHT["midnight"],
        "font_color"       : _RAW_LIGHT["cream"],
        "font_family"      : _RAW_LIGHT["font_family"],
        "grid_color"       : _RAW_LIGHT["grid_color"],
        "primary_line"     : _RAW_LIGHT["teal"],
        "excellent"        : _RAW_LIGHT["teal"],
        "excellent_dim"    : _RAW_LIGHT["teal_dim"],
        "good"             : _RAW_LIGHT["gold"],
        "poor"             : _RAW_LIGHT["rose"],
        "text_on_bar"      : _RAW_LIGHT["text_on_bar"],
        "annotation_bg"    : _RAW_LIGHT["annotation_bg"],
        "annotation_border": _RAW_LIGHT["annotation_border"],
        "annotation_font"  : _RAW_LIGHT["annotation_font"],
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
    --card-bg:     rgba(255,255,255,0.03);
    --cream:       #faf6ee;
    --paper:       #ffffff;
    --muted:       #9ba9b4;
    --ink:         #0d1117;
    --teal:        #3aa895;
    --teal-light:  #4bcbb4;
    --gold:        #d4a24c;
    --gold-light:  #eec87d;
    --rose:        #c66b7d;
    --rose-light:  #e08fa3;
    --border:      rgba(155,169,180,0.15);
    --card-border: rgba(255,255,255,0.05);
    --ghost-border: rgba(155,169,180,0.1);
    --shadow-sm:   0 2px 4px rgba(0,0,0,0.2);
    --shadow-md:   0 4px 12px rgba(0,0,0,0.3);
    --shadow-lg:   0 12px 24px rgba(0,0,0,0.4);
    --shadow-xl:   0 24px 48px rgba(0,0,0,0.5);
    --nav-bg:      rgba(15,28,46,0.92);
    --sidebar-bg:  #0f1c2e;
    --surface:          #1a2d45;
    --surface-alt:      #0f1c2e;
    --surface-high:     #1e293b;
    --surface-elevated: #243347;
    --surface-lowest:   #0d1117;
    --gold-gradient: linear-gradient(135deg, #d4a24c, #f4d08b);
    --teal-gradient: linear-gradient(135deg, #3aa895, #4bcbb4);
    --teal-dim:    rgba(58,168,149,0.12);
    --gold-dim:    rgba(212,162,76,0.12);
    --rose-dim:    rgba(198,107,125,0.12);
    --focus-ring:  rgba(75,203,180,0.4);
    --overlay:     rgba(255,255,255,0.02);
    /* Motion tokens */
    --ease-out:    cubic-bezier(0.2, 0.0, 0, 1);
    --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
    --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
    --dur-fast:    100ms;
    --dur-base:    200ms;
    --dur-slow:    400ms;
    /* Radii */
    --radius-xs:   8px;
    --radius-sm:   12px;
    --radius-md:   16px;
    --radius-lg:   24px;
    --radius-xl:   32px;
    --radius-full: 9999px;"""

_TOKENS_LIGHT = """
    --midnight:    #f9f8f5;
    --navy:        #f3f4f6;
    --card-bg:     rgba(15,28,46,0.04);
    --cream:       #0d1117;
    --paper:       #1e293b;
    --muted:       #5a6a7e;
    --ink:         #f9f8f5;
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
    --nav-bg:      rgba(249,248,245,0.85);
    --sidebar-bg:  #f9f8f5;
    --surface:          #ffffff;
    --surface-alt:      #f3f4f6;
    --surface-high:     #ffffff;
    --surface-elevated: #f8f9fa;
    --surface-lowest:   #e5e7eb;
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
    --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
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
.stApp {{
    background: var(--midnight) !important;
    color: var(--cream) !important;
    transition: background-color 0.4s ease, color 0.4s ease;
}}
.stApp {{
    font-size: var(--fs-body) !important;
}}
.stApp, .stApp * {{
    font-family: 'IBM Plex Sans', system-ui, sans-serif !important;
    line-height: var(--lh-body) !important;
}}
h1, h2, h3 {{
    font-family: 'Chronicle Display', serif !important;
    letter-spacing: -0.02em !important;
    line-height: var(--lh-heading) !important;
    font-weight: var(--fw-bold) !important;
    margin-bottom: var(--margin-after-header) !important;
    text-wrap: balance !important;
}}
h1 {{ font-size: var(--fs-h1) !important; }}
h2 {{ font-size: var(--fs-h2) !important; }}
h3 {{ font-size: var(--fs-h3) !important; }}

/* ── Icon font protection: MUST come after the * override ─ */
/* Protects custom HTML icon spans */
.material-symbols-outlined,
.stApp .material-symbols-outlined,
.stApp * .material-symbols-outlined {{
    font-family: 'Material Symbols Outlined' !important;
    font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24 !important;
    font-size: 20px;
    vertical-align: middle;
    line-height: 1;
    letter-spacing: normal;
    word-wrap: normal;
    white-space: nowrap;
    direction: ltr;
    -webkit-font-feature-settings: 'liga';
    font-feature-settings: 'liga';
    -webkit-font-smoothing: antialiased;
}}

/* Protects Streamlit's native expander icon span (generated by icon=":material/...") */
[data-testid="stExpander"] [data-testid="stExpanderToggleIcon"] span,
[data-testid="stExpander"] summary span[class*="material"],
[data-testid="stExpander"] summary [aria-hidden="true"],
button[data-testid="stBaseButton-headerNoPadding"] span,
.stExpander summary span {{
    font-family: 'Material Symbols Outlined' !important;
    font-variation-settings: 'FILL' 1, 'wght' 400, 'GRAD' 0, 'opsz' 24 !important;
    font-feature-settings: 'liga' !important;
}}
"""

_CSS_TYPO_SCALE = """
/* ══ TYPOGRAPHY & SPACING SCALE (responsive tokens) ═══════ */
/* Desktop baseline: open & breathing                       */
/* Tablet ≤1024px : moderate compression                    */
/* Mobile ≤640px  : compact                                  */
:root {
    /* Type sizes */
    --fs-body: 16px;
    --fs-small: 13px;
    --fs-h3: 1.375rem;       /* 22px */
    --fs-h2: 1.75rem;        /* 28px */
    --fs-h1: 2.25rem;        /* 36px */
    --fs-hero: 3.5rem;       /* 56px */
    /* Line heights */
    --lh-body: 1.6;
    --lh-heading: 1.3;
    --lh-card: 1.5;
    /* Weights */
    --fw-normal: 400;
    --fw-medium: 500;
    --fw-semibold: 600;
    --fw-bold: 700;
    /* Vertical rhythm */
    --gap-section: 3.5rem;
    --gap-subsection: 2rem;
    --gap-section-break: 3rem;
    --pad-card: 2rem;
    --pad-card-tight: 1.5rem;
    --margin-after-header: 1.5rem;
}

@media (max-width: 1024px) {
    :root {
        --fs-body: 15px;
        --fs-small: 12px;
        --fs-h3: 1.25rem;
        --fs-h2: 1.5625rem;
        --fs-h1: 2rem;
        --fs-hero: 2.75rem;
        --lh-body: 1.55;
        --gap-section: 2.5rem;
        --gap-subsection: 1.5rem;
        --gap-section-break: 2rem;
        --pad-card: 1.5rem;
        --pad-card-tight: 1.25rem;
        --margin-after-header: 1.25rem;
    }
}

@media (max-width: 640px) {
    :root {
        --fs-body: 14px;
        --fs-small: 11px;
        --fs-h3: 1.125rem;
        --fs-h2: 1.375rem;
        --fs-h1: 1.75rem;
        --fs-hero: 2.25rem;
        --lh-body: 1.5;
        --gap-section: 1.5rem;
        --gap-subsection: 1.25rem;
        --gap-section-break: 1.5rem;
        --pad-card: 1.25rem;
        --pad-card-tight: 1rem;
        --margin-after-header: 1rem;
    }
}
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
    max-width: 1200px;     /* alineado con .block-container */
    margin: 0 auto;
    display: grid;
    grid-template-columns: auto 1fr auto;
    align-items: center;
    gap: 16px;
    height: 100%;
}
.stitch-topbar-brand {
    font-size: 18px; font-weight: 700; letter-spacing: -0.03em;
    font-family: 'Chronicle Display', serif;
    color: var(--cream); white-space: nowrap;
    line-height: 1.15;
    display: flex; align-items: center; gap: 10px;
}
.stitch-topbar-brand .stitch-topbar-brand-text {
    display: flex;
    flex-direction: column;
    line-height: 1.1;
}
.stitch-topbar-brand .eyebrow-nav {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    color: var(--gold);
    margin-bottom: 2px;
}
.stitch-topbar-nav {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;
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
    background: var(--overlay);
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
button.stitch-topbar-btn {
    cursor: pointer;
    background: var(--surface);
}
.stitch-topbar-btn-icon {
    padding: 0;
    width: 36px;
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
    background: var(--surface-alt);
    transform: translateY(-1px);
}
.stitch-topbar-btn-theme {
    border-radius: 50%;
    width: 38px;
    height: 38px;
    padding: 0;
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
.stitch-topbar-btn-mobile {
    width: 100%;
    justify-content: flex-start;
    gap: 12px;
    margin-top: 6px;
    border-radius: 12px;
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
"""

_CSS_LAYOUT = """
/* ══ MAIN CONTAINER ═══════════════════════════════════════ */
.block-container {
    padding: 6rem 1.5rem 4rem !important;
    max-width: 1200px !important;
    margin: 0 auto !important;
}


.editorial-container {
    max-width: 720px;
    margin: 0 auto 3rem;
    text-align: center;
}

.nl-center-measure {
    max-width: 640px;
    margin: 0 auto;
}


.editorial-container p {
    font-size: var(--fs-body);
    line-height: var(--lh-body);
    color: var(--muted);
    margin: 0 auto var(--margin-after-header);
    max-width: 65ch;
    text-align: center;
}

/* ══ MAP COMPONENT (Responsive) ═══════════════════════════ */
.stitch-map-container {
    position: relative;
    width: 100%;
    aspect-ratio: 16/9;
    border-radius: var(--radius-lg);
    overflow: hidden;
    background: var(--surface-alt);
    border: 1px solid var(--card-border);
    margin: 2rem auto;
}

.map-bg {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0.45;
    mix-blend-mode: luminosity;
}

.map-scrim {
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 50% 50%, transparent 20%, var(--midnight) 100%);
}

.map-overlay {
    position: absolute;
    z-index: 10;
    display: flex;
    align-items: center;
    gap: 8px;
    pointer-events: auto;
}

.map-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    border: 2px solid #fff;
    box-shadow: 0 0 10px rgba(255,255,255,0.3);
}

.map-tooltip {
    background: var(--nav-bg);
    backdrop-filter: blur(8px);
    padding: 6px 12px;
    border-radius: 8px;
    border: 1px solid var(--card-border);
    font-size: 11px;
    color: var(--cream);
    box-shadow: var(--shadow-md);
    opacity: 0;
    transition: opacity 0.2s ease;
}

.map-overlay:hover .map-tooltip {
    opacity: 1;
}

.map-central-card {
    position: absolute;
    bottom: 10%;
    left: 50%;
    transform: translateX(-50%);
    background: var(--nav-bg);
    backdrop-filter: blur(16px);
    padding: 1.5rem 2rem;
    border-radius: var(--radius-md);
    border: 1px solid var(--card-border);
    text-align: center;
    box-shadow: var(--shadow-xl);
    width: 90%;
    max-width: 400px;
    z-index: 20;
}

@media (max-width: 768px) {
    .stitch-map-container { aspect-ratio: 1/1; }
    .map-overlay { display: none; } /* Hide dots on mobile for clarity */
    .map-central-card { bottom: 5%; padding: 1rem; }
}
"""

_CSS_TYPOGRAPHY = """
/* ══ TYPOGRAPHY ═══════════════════════════════════════════ */
.eyebrow {{
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--gold) !important;
    display: block;
    text-align: center;
    margin-bottom: 1rem;
}}
.section-title {{
    font-family: 'Chronicle Display', serif;
    font-size: var(--fs-h2);
    font-weight: var(--fw-bold);
    color: var(--cream) !important;
    line-height: var(--lh-heading);
    letter-spacing: -0.01em;
    text-wrap: balance;
    text-align: center;
}}
.section-subtitle {{
    font-family: 'DM Sans', sans-serif;
    font-size: var(--fs-body);
    font-weight: var(--fw-normal);
    line-height: var(--lh-body);
    color: var(--muted) !important;
    text-align: center;
    max-width: 680px;
    margin-left: auto;
    margin-right: auto;
}}

/* ══ HERO TYPOGRAPHY ══════════════════════════════════════ */
.hero-title {{
    font-family: 'Chronicle Display', serif;
    font-size: var(--fs-hero) !important;
    font-weight: var(--fw-bold);
    letter-spacing: -0.03em;
    line-height: 1.1;
    color: var(--cream);
    margin: 0 auto 20px !important;
    max-width: 900px;
    text-align: center;
}}
.hero-subtitle {{
    font-family: 'DM Sans', sans-serif;
    font-size: var(--fs-body);
    line-height: var(--lh-body);
    color: var(--muted);
    margin: 0 auto 28px;
    max-width: 700px;
    text-align: center;
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
.stitch-card-accent      {{ background: var(--teal-dim); border-color: rgba(58,168,149,0.25); }}
.stitch-card-accent-gold {{ background: var(--gold-dim); border-color: rgba(200,151,58,0.25); }}
.stitch-card-accent-rose {{ background: var(--rose-dim); border-color: rgba(184,92,110,0.25); }}

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
    gap: 10px;
    padding: 14px 28px;
    border-radius: 9999px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 700;
    font-size: 15px;
    text-decoration: none;
    cursor: pointer;
    transition: transform 200ms cubic-bezier(0.4, 0, 0.2, 1),
                filter 200ms,
                box-shadow 200ms;
    letter-spacing: 0.01em;
}}

.stitch-btn-primary {{
    background: var(--teal);
    color: #fff;
    box-shadow: 0 8px 28px rgba(42,122,111,0.28), 0 2px 8px rgba(0,0,0,0.12);
}}

.stitch-btn-primary:hover {{
    transform: translateY(-2px);
    filter: brightness(1.08);
    box-shadow: 0 14px 36px rgba(42,122,111,0.38), 0 4px 12px rgba(0,0,0,0.16);
}}

.stitch-btn-ghost {{
    background: transparent;
    border: 1.5px solid var(--card-border);
    color: var(--cream);
}}

.stitch-btn-ghost:hover {{
    border-color: var(--gold);
    color: var(--gold-light);
    background: var(--overlay);
    transform: translateY(-1px);
}}
"""

_CSS_KPI = """
/* ══ STAT CARD (nl-* primitive) ═══════════════════════════ */
.nl-stat-card {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-sm);
    padding: var(--pad-card);
    box-shadow: var(--shadow-sm);
    transition: box-shadow var(--dur-base) var(--ease-out),
                border-color var(--dur-base) var(--ease-out),
                transform var(--dur-base) var(--ease-out);
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}}
.nl-stat-card:hover {{
    box-shadow: var(--shadow-md);
    border-color: var(--border);
    transform: translateY(-2px);
}}
.nl-stat-card--focus {{
    border-top: 3px solid var(--gold);
    padding-top: calc(var(--pad-card) - 2px);
}}
.nl-stat-card-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
}}
.nl-stat-card-label {{
    font-family: 'DM Mono', monospace;
    font-size: 0.6875rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    margin: 0;
}}
.nl-stat-card-icon {{
    font-size: 1.125rem;
    color: var(--muted);
}}
.nl-stat-card-value {{
    font-family: 'Chronicle Display', serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--cream);
    line-height: 1;
    margin: 0;
}}
.nl-stat-card-meta {{
    font-family: 'DM Sans', sans-serif;
    font-size: 0.8125rem;
    color: var(--muted);
    margin: 0;
}}
.nl-stat-card-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.25rem;
    margin: 1rem 0 1.5rem;
}}
@media (max-width: 600px) {{
    .nl-stat-card-grid {{ grid-template-columns: 1fr; }}
}}

/* ══ CHART CARD (chrome wrapper for plotly) ═══════════════ */
.nl-chart-card {{
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-sm);
    padding: var(--pad-card);
    box-shadow: var(--shadow-sm);
    margin: 1rem 0 var(--margin-after-header);
    transition: box-shadow var(--dur-base) var(--ease-out),
                border-color var(--dur-base) var(--ease-out);
}}
.nl-chart-card:hover {{
    box-shadow: var(--shadow-md);
    border-color: var(--border);
}}
.nl-chart-card-header {{
    margin-bottom: 1rem;
}}

/* Legacy: .kpi-label retained — used by datasets.py as a
   generic label primitive. Migrate to .nl-stat-card-label
   in a follow-up if datasets.py is touched. */
.kpi-label {{
    font-size: 0.75rem;
    font-family: 'DM Mono', monospace;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
}}
"""

_CSS_BADGE = """
/* ══ BADGE ════════════════════════════════════════════════ */
.badge {{
    display: inline-block;
    padding: 4px 12px;
    background: var(--teal-dim);
    border: 1px solid var(--teal);
    border-radius: var(--radius-full);
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    color: var(--teal-light);
    letter-spacing: 0.05em;
}}
.nl-code-inline {{
    font-family: 'DM Mono', monospace;
    font-size: 0.875em;
    background: var(--card-bg);
    padding: 2px 6px;
    border-radius: 4px;
    color: var(--teal-light);
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
    transition: width 0.6s ease-out;
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
    font-family: 'Chronicle Display', serif;
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
    border: 1px solid rgba(200,151,58,0.25);
    padding: 1rem 1.5rem;
    background: var(--gold-dim);
    border-radius: 8px;
    margin: 1.5rem 0;
}}
.quote-text {{
    font-family: 'Chronicle Display', serif;
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
    background: var(--rose-dim);
    border: 1px solid rgba(184,92,110,0.2);
    border-radius: 10px;
    padding: 1.5rem;
    transition: transform 220ms cubic-bezier(0.4, 0, 0.2, 1),
                box-shadow 220ms,
                border-color 220ms;
}
.alert-card:hover {
    transform: translateY(-3px);
    border-color: rgba(184,92,110,0.4);
    box-shadow: 0 22px 48px -22px rgba(0,0,0,0.55),
                0 0 0 1px rgba(199,109,109,0.18);
}
.alert-score {
    font-size: 2.5rem;
    font-weight: 700;
    font-family: 'Chronicle Display', serif;
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


_CSS_EDITORIAL = """
/* ══ EDITORIAL LAYOUT ═════════════════════════════════════ */
.editorial-header {{
    text-align: center;
    max-width: 850px;
    margin: 0 auto 3rem;
    padding: 0;
}}
.editorial-title {{
    font-family: 'Chronicle Display', serif;
    font-size: clamp(2.6rem, 5.5vw, 4rem);
    font-weight: 700;
    color: var(--cream);
    letter-spacing: -0.025em;
    line-height: 1.12;
    text-align: center;
    text-wrap: balance;
    margin-bottom: 1.25rem !important;
    text-shadow: 0 0 60px rgba(58, 168, 149, 0.12);
}}
.editorial-subtitle {{
    font-family: 'DM Sans', sans-serif;
    font-size: 1.125rem;
    font-weight: 400;
    line-height: 1.75;
    color: var(--muted);
    max-width: 680px;
    margin: 0 auto 1.75rem;
    text-align: center;
    text-wrap: pretty;
    hyphens: auto;
}}
.editorial-meta {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--muted);
    margin-bottom: 1rem;
}}
.editorial-meta span + span::before {{
    content: '·';
    margin-right: 16px;
    color: var(--gold);
}}
.editorial-figure {{
    max-width: 1100px;
    margin: 0 auto 3rem;
    border-radius: var(--radius-lg);
    overflow: hidden;
    border: 1px solid var(--card-border);
    background: var(--surface);
}}

/* ── Contextual section image ───────────────────────────── */
.nl-ctx-img-wrap {{
    max-width: 720px;
    margin: 0 auto 2.5rem;
    border-radius: var(--radius-lg);
    overflow: hidden;
    border: 1px solid var(--card-border);
}}
.nl-ctx-img {{
    width: 100%;
    height: 260px;
    object-fit: cover;
    display: block;
    opacity: 0.85;
    transition: opacity 300ms;
}}
.nl-ctx-img:hover {{ opacity: 1; }}

/* ── Hero stat block (Score global prominente en Inicio) ─── */
.nl-hero-stat-block {{
    max-width: 640px;
    margin: 0 auto 2.5rem;
    padding: 0;
    text-align: center;
}}
.nl-hero-stat-prose {{
    font-family: 'Chronicle Display', serif;
    font-size: clamp(1.5rem, 3vw, 2rem);
    font-weight: 400;
    line-height: 1.35;
    letter-spacing: -0.01em;
    margin: 0 0 0.75rem;
}}
.nl-hero-stat-score {{
    font-weight: 700;
    letter-spacing: -0.03em;
    font-size: 1.25em;
    line-height: 1;
    display: inline-block;
    vertical-align: text-bottom;
}}
.nl-hero-stat-score--excellent {{ color: var(--teal-light); }}
.nl-hero-stat-score--poor      {{ color: var(--rose-light); }}
.nl-hero-stat-label {{
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--muted);
    display: block;
}}

/* ── Organization summary bar ──────────────────────────────── */
.nl-score-center {{
    display: flex;
    justify-content: center;
    margin-bottom: 24px;
}}
.nl-org-summary {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 32px;
    padding: 24px 32px;
    background: var(--surface-alt);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-md);
    margin: 0 auto 24px;
    flex-wrap: wrap;
    max-width: 520px;
}}
.nl-org-summary-primary {{
    display: flex;
    flex-direction: column;
    gap: 4px;
    flex-shrink: 0;
    min-width: 100px;
}}
.nl-org-summary-score {{
    font-family: 'Chronicle Display', serif;
    font-size: 2.75rem;
    font-weight: 700;
    line-height: 1;
    letter-spacing: -0.03em;
}}
.nl-org-summary-score.excellent {{ color: var(--teal-light); }}
.nl-org-summary-score.good      {{ color: var(--gold-light); }}
.nl-org-summary-score.poor      {{ color: var(--rose-light); }}
.nl-org-summary-caption {{
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    font-family: 'DM Mono', monospace;
}}
.nl-org-summary-sep {{
    width: 1px;
    height: 44px;
    background: var(--card-border);
    flex-shrink: 0;
}}
.nl-org-summary-stats {{
    display: flex;
    gap: 28px;
    flex-wrap: wrap;
    align-items: center;
}}
.nl-org-summary-stat {{
    display: flex;
    flex-direction: column;
    gap: 3px;
}}
.nl-org-summary-stat-value {{
    font-family: 'DM Mono', monospace;
    font-size: 1.375rem;
    font-weight: 600;
    line-height: 1;
}}
.nl-org-summary-stat-value.teal {{ color: var(--teal-light); }}
.nl-org-summary-stat-value.rose {{ color: var(--rose-light); }}
.nl-org-summary-stat-label {{
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
}}
.nl-org-summary .score-ring {{ margin: 0; }}

/* ── KPI card left-aligned variant ─────────────────────── */
.kpi-card--left {{
    text-align: left;
    position: relative;
}}
.kpi-card--left .kpi-value {{
    font-size: 2rem;
}}
.kpi-card--ring {{
    text-align: center;
    padding: 1.5rem 1rem;
}}

/* ── KPI inline value (inside running text) ─────────────── */
.kpi-value--hero {{
    font-family: 'Chronicle Display', serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--teal-light);
    vertical-align: middle;
    line-height: 1;
    letter-spacing: -0.02em;
    text-shadow: 0 0 24px rgba(58, 168, 149, 0.35);
}}

/* ── KPI delta indicator ─────────────────────────────────── */
.kpi-delta {{
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 0.75rem;
    font-family: 'DM Mono', monospace;
    color: var(--muted);
    margin-top: 8px;
}}
.kpi-delta.up   {{ color: var(--teal-light); }}
.kpi-delta.down {{ color: var(--rose-light); }}

/* ── Animation delay aliases (fade-up-dN) ────────────────── */
.fade-up-d1 {{ animation: fadeUp 0.8s 0.10s var(--ease-out-expo) both; }}
.fade-up-d2 {{ animation: fadeUp 0.8s 0.18s var(--ease-out-expo) both; }}
.fade-up-d3 {{ animation: fadeUp 0.8s 0.26s var(--ease-out-expo) both; }}
.fade-up-d4 {{ animation: fadeUp 0.8s 0.34s var(--ease-out-expo) both; }}

/* ── Section divider ─────────────────────────────────────── */
.divider {{
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--card-border) 40%, var(--card-border) 60%, transparent);
    margin: 3rem auto;
    max-width: 840px;
}}

/* ── Editorial footer strip ──────────────────────────────── */
.editorial-footer {{
    border-top: 1px solid var(--card-border);
    padding-top: 2.5rem;
    margin-top: 3.5rem;
    color: var(--muted);
    font-size: 0.8rem;
    font-family: 'DM Mono', monospace;
    text-align: center;
    opacity: 0.75;
    letter-spacing: 0.02em;
}}

/* ── Topbar landing CTA (gold outline variant) ───────────── */
.stitch-topbar-btn-landing {{
    border-color: var(--gold) !important;
    color: var(--gold-light) !important;
}}
.stitch-topbar-btn-landing:hover {{
    background: var(--gold-dim) !important;
}}

/* ── Spacing utilities (missing mt-5/mt-6) ───────────────── */
.mt-5 {{ margin-top: 3rem; }}
.mt-6 {{ margin-top: 4rem; }}

/* ── Calidad Pro: distribution band ────────────────────────── */
.nl-distband {{
    max-width: 640px;
    margin: 0 auto 24px;
    padding: 28px 32px;
    background: var(--surface-alt);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-md);
}}
.nl-distband-header {{
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 20px;
}}
.nl-distband-score {{
    font-family: 'Chronicle Display', serif;
    font-size: 3.25rem;
    font-weight: 700;
    line-height: 1;
    letter-spacing: -0.03em;
}}
.nl-distband-score::after {{
    content: '%';
    font-size: 1.5rem;
    font-weight: 400;
    opacity: 0.55;
    margin-left: 2px;
}}
.nl-distband-score--teal {{ color: var(--teal-light); }}
.nl-distband-score--rose {{ color: var(--rose-light); }}
.nl-distband-meta {{
    display: flex;
    flex-direction: column;
    gap: 4px;
}}
.nl-distband-label {{
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--cream);
}}
.nl-distband-sub {{
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
}}
.nl-distband-track {{
    display: flex;
    height: 10px;
    border-radius: 5px;
    overflow: hidden;
    gap: 2px;
    margin-bottom: 14px;
    background: var(--surface-elevated);
}}
.nl-distband-seg {{
    border-radius: 3px;
    min-width: 3px;
    transition: width 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}}
.nl-distband-seg--excellent {{ background: var(--teal); }}
.nl-distband-seg--good      {{ background: var(--gold); }}
.nl-distband-seg--critical  {{ background: var(--rose); }}
.nl-distband-legend {{
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
}}
.nl-distband-legend-item {{
    display: flex;
    align-items: center;
    gap: 6px;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: var(--muted);
}}
.nl-distband-dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
    flex-shrink: 0;
}}
.nl-distband-dot--excellent {{ background: var(--teal-light); }}
.nl-distband-dot--good      {{ background: var(--gold-light); }}
.nl-distband-dot--critical  {{ background: var(--rose-light); }}
@media (max-width: 600px) {{
    .nl-distband {{ padding: 20px 18px; }}
    .nl-distband-score {{ font-size: 2.5rem; }}
    .nl-distband-legend {{ gap: 12px; }}
}}
"""

_CSS_SECTIONS = """
/* ══ SECTION-LEVEL COMPONENTS ════════════════════════════ */

/* Section separator icon (app.py section breaks) */
.nl-section-icon-wrap {{ text-align: center; margin-bottom: 2rem; }}
.nl-section-icon-xl {{ font-size: 48px; color: var(--gold); opacity: 0.4; }}

/* Panel sub-heading row (calidad_pro coverage/failure panels) */
.nl-panel-head {{ display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }}
.icon-teal-sm {{ color: var(--teal); font-size: 20px; vertical-align: middle; }}
.icon-rose-sm {{ color: var(--rose); font-size: 20px; vertical-align: middle; }}

/* Empty states */
.nl-empty-state {{ text-align: center; padding: 24px; }}
.nl-empty-state-icon {{ font-size: 36px; display: block; margin: 0 auto 4px; }}
.nl-empty-state-text {{ margin: 8px 0 0; font-size: 13px; color: var(--muted); }}

/* Micro typography */
.text-muted-xs {{ font-size: 12px; color: var(--muted); }}

/* Governance metadata alert block */
.nl-stat-label {{ font-size: 17px; font-weight: 700; color: var(--cream); }}
.nl-stat-pct {{
    font-size: 36px; font-weight: 700;
    font-family: 'Chronicle Display', serif;
    color: var(--gold); margin-left: 24px; flex-shrink: 0;
}}
.nl-stat-note {{
    font-size: 13px; color: var(--cream);
    background: var(--surface-alt); border-radius: 8px;
}}

/* Alert count badge (used in tab label) */
.nl-count-badge {{
    background: var(--rose); color: #fff;
    font-size: 10px; font-weight: 700;
    padding: 2px 8px; border-radius: 9999px;
    vertical-align: middle;
}}

/* Results count bar */
.nl-results-bar {{
    display: flex; align-items: center;
    justify-content: space-between; margin-bottom: 24px;
}}
.nl-results-left {{ display: flex; align-items: center; gap: 8px; }}
.nl-results-count {{
    font-size: 20px; font-weight: 700;
    font-family: 'Chronicle Display', serif; color: var(--cream);
}}
.nl-results-label {{ color: var(--muted); font-weight: 500; font-family: 'DM Sans', sans-serif; }}

/* Load-more pagination hint */
.nl-load-more {{
    text-align: center; margin-top: 32px; padding: 24px;
    background: var(--surface-alt); border-radius: 16px;
    border: 1px dashed var(--card-border);
}}
.nl-load-more p {{ color: var(--muted); margin-bottom: 16px; }}
.nl-load-more p + p {{ font-size: 13px; margin-bottom: 0; }}

/* Alerts section intro paragraph */
.nl-section-intro {{ color: var(--muted); max-width: 640px; margin: 8px 0 24px; }}

/* Inline accent text spans — replaces style="color:var(--...)" */
.accent-teal {{ color: var(--teal-light); font-weight: 600; }}
.accent-gold {{ color: var(--gold-light); font-weight: 600; }}
.accent-rose {{ color: var(--rose-light); font-weight: 600; }}

/* Success variant for empty-state container */
.nl-empty-state--success {{ color: var(--teal-light); }}

/* Criteria card (Metodología — 4 criterios pedagógicos) */
.nl-criteria-card {{
    text-align: left;
    max-width: 640px;
    margin: 1.5rem auto 0;
    padding: 1.75rem 2rem;
    background: var(--card-bg);
    border-radius: 16px;
    border: 1px solid var(--card-border);
    box-shadow: 0 1px 0 rgba(255,255,255,0.02) inset, 0 14px 40px -20px rgba(0,0,0,0.45);
    transition: transform 240ms cubic-bezier(0.4,0,0.2,1), box-shadow 240ms;
}}
.nl-criteria-card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 1px 0 rgba(255,255,255,0.04) inset, 0 22px 50px -22px rgba(0,0,0,0.55);
    border-color: var(--teal);
}}
.nl-criteria-list {{
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
}}
.nl-criteria-list li {{
    font-family: 'DM Sans', sans-serif;
    font-size: 15px;
    line-height: 1.55;
    color: var(--cream);
    padding-left: 0.25rem;
}}

/* Hover-lift utility for cards (KPI, alerts, insights) */
.nl-hover-lift {{
    transition: transform 220ms cubic-bezier(0.4,0,0.2,1),
                box-shadow 220ms,
                border-color 220ms;
}}
.nl-hover-lift:hover {{
    transform: translateY(-3px);
    box-shadow: 0 18px 36px -18px rgba(0,0,0,0.55);
    border-color: var(--teal);
}}
"""

_CSS_GAUGE = """
/* ══ GAUGE SVG ════════════════════════════════════════════ */
.gauge-container {{
    padding: 1.5rem;
    display: flex; flex-direction: column; align-items: center;
}}
"""

_CSS_TABS = """
/* ══ TABS ═════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {{
    border-bottom: 1px solid var(--card-border) !important;
    gap: 32px !important;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    font-size: 14px !important;
    color: var(--muted) !important;
    padding: 0 0 12px !important;
}}
.stTabs [aria-selected="true"] {{
    color: var(--teal-light) !important;
    border-bottom: 2px solid var(--teal) !important;
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
/* ── Theme-aware text: override Streamlit's hardcoded dark textColor ── */
.stMarkdownContainer,
[data-testid="stMarkdownContainer"],
.stMarkdownContainer p,
[data-testid="stMarkdownContainer"] p,
.stMarkdownContainer li,
[data-testid="stMarkdownContainer"] li {{
    color: var(--cream) !important;
}}
.stMarkdownContainer a,
[data-testid="stMarkdownContainer"] a {{
    color: var(--teal) !important;
    text-decoration: none !important;
}}
.stMarkdownContainer a:hover,
[data-testid="stMarkdownContainer"] a:hover {{
    color: var(--gold-light) !important;
}}
"""

_CSS_SIDEBAR_TOGGLE = """
/* ── THEME TOGGLE BUTTON ────────────────────────────────── */
[data-testid="stSidebar"] .stButton[data-testid*="theme_toggle"] > button {{
    background: var(--surface) !important;
    color: var(--cream) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: var(--radius-full) !important;
    font-weight: 700 !important; font-size: 13px !important;
    padding: 10px 20px !important;
    transition: all 0.3s var(--ease-out-expo) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
}}
[data-testid="stSidebar"] .stButton[data-testid*="theme_toggle"] > button:hover {{
    background: var(--surface-alt) !important;
    border-color: var(--gold) !important;
    color: var(--gold-light) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 16px rgba(0,0,0,0.2) !important;
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
        transform: translateY(16px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}
.fade-up {{
    animation: fadeUp 0.8s var(--ease-out-expo, cubic-bezier(0.16, 1, 0.3, 1)) forwards;
}}
.fade-up-1 {{ animation-delay: 0.05s; }}
.fade-up-2 {{ animation-delay: 0.12s; }}
.fade-up-3 {{ animation-delay: 0.19s; }}
.fade-up-4 {{ animation-delay: 0.26s; }}
.fade-up-5 {{ animation-delay: 0.33s; }}

@keyframes fadeInUp {{
    from {{ opacity: 0; transform: translateY(12px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.fade-in-up {{
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.6s ease, transform 0.6s ease;
}}
.fade-in-up.show {{
    opacity: 1;
    transform: translateY(0);
}}

/* Update any remaining Playfair Display references to Chronicle Display */

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

/* Health mini-cards (dimension bars) */
.health-mini-card {{
    background: var(--surface-high);
    border: 1px solid var(--card-border);
    border-radius: var(--radius-sm);
    padding: 0.875rem 1.125rem;
    margin-bottom: 0.625rem;
    transition: border-color 200ms;
}}
.health-mini-card:hover {{ border-color: rgba(255,255,255,0.1); }}
.health-mini-card-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.2rem;
}}
.health-mini-card-label {{
    font-family: 'DM Sans', sans-serif;
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--cream);
}}
.health-mini-card-pct {{
    font-family: 'DM Mono', monospace;
    font-size: 0.8125rem;
    color: var(--muted);
}}
.health-mini-card-desc {{
    font-size: 0.725rem;
    color: var(--muted);
    margin: 0 0 0.5rem;
    line-height: 1.5;
    opacity: 0.85;
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
    background: var(--rose-dim);
    border: 1px solid rgba(184,92,110,0.2);
    border-radius: var(--radius-sm, 10px);
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
    font-family: 'Chronicle Display', serif;
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
    font-family: 'Chronicle Display', serif;
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
    padding: var(--gap-section) 0 var(--gap-subsection);
}}

.nl-section-title {{
    margin-bottom: 12px !important;
    text-align: center;
}}

.nl-section-subtitle {{
    max-width: 720px;
    margin-left: auto;
    margin-right: auto;
    margin-bottom: 8px;
    text-align: center;
}}

.nl-section-break {{
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--card-border) 40%, var(--card-border) 60%, transparent);
    margin: var(--gap-section-break) 0 var(--gap-subsection);
}}

.nl-section-error {{
    border: 1px solid var(--rose-dim);
    background: var(--rose-dim);
    border-radius: 14px;
    padding: 20px 24px;
    margin: 24px 0;
}}
.nl-section-error-title {{
    font-family: 'Chronicle Display', serif;
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
    margin: var(--gap-subsection) 0 var(--margin-after-header);
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
    font-family: 'Chronicle Display', serif;
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
    text-align: left;
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
    font-family: 'Chronicle Display', serif;
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
    background: var(--surface-alt);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    padding: 22px;
    display: flex;
    gap: 14px;
    align-items: flex-start;
}}
.nl-insight-positive {{ background: var(--teal-dim); border-color: rgba(58,168,149,0.25); }}
.nl-insight-warn     {{ background: var(--gold-dim); border-color: rgba(200,151,58,0.25); }}
.nl-insight-critical {{ background: var(--rose-dim); border-color: rgba(184,92,110,0.25); }}
.nl-insight-neutral  {{ background: var(--surface-alt); }}
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
    font-family: 'Chronicle Display', serif;
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
    background: var(--gold-dim);
    border: 1px solid rgba(200,151,58,0.2);
    border-radius: 10px;
}}
.nl-rec-item::before {{
    content: counter(rec);
font-family: 'Chronicle Display', serif;
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

/* ── Conclusiones: editorial lead (governance stat) ─────── */
.nl-conc-lead {{
    display: flex;
    align-items: center;
    gap: 36px;
    padding: 32px 36px;
    background: var(--teal-dim);
    border: 1px solid rgba(58,168,149,0.2);
    border-radius: 14px;
    margin-bottom: 20px;
}}
.nl-conc-lead-stat {{
    font-family: 'DM Mono', monospace;
    font-size: 60px;
    font-weight: 500;
    color: var(--teal-light);
    line-height: 1;
    flex-shrink: 0;
    letter-spacing: -0.03em;
}}
.nl-conc-lead-body {{ flex: 1; min-width: 0; }}
.nl-conc-lead-title {{
    font-family: 'Chronicle Display', serif;
    font-size: 18px;
    font-weight: 700;
    color: var(--cream);
    margin: 0 0 8px;
}}
.nl-conc-lead-text {{
    font-size: 14px;
    color: var(--muted);
    line-height: 1.65;
    margin: 0;
}}
.nl-conc-lead-text strong {{ color: var(--cream); }}

/* ── Conclusiones: dimension comparison strip ────────────── */
.nl-dim-pair {{
    display: grid;
    grid-template-columns: 1fr 1px 1fr;
    border: 1px solid var(--card-border);
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 20px;
}}
.nl-dim-half {{
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 24px 28px;
}}
.nl-dim-strong {{ background: var(--teal-dim); }}
.nl-dim-weak   {{ background: var(--gold-dim); }}
.nl-dim-sep    {{ background: var(--card-border); }}
.nl-dim-tag {{
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}}
.nl-dim-strong .nl-dim-tag {{ color: var(--teal-light); }}
.nl-dim-weak   .nl-dim-tag {{ color: var(--gold-light); }}
.nl-dim-name {{
    font-size: 16px;
    font-weight: 600;
    color: var(--cream);
}}
.nl-dim-score {{
    font-family: 'DM Mono', monospace;
    font-size: 32px;
    font-weight: 500;
    line-height: 1;
    letter-spacing: -0.03em;
}}
.nl-dim-strong .nl-dim-score {{ color: var(--teal-light); }}
.nl-dim-weak   .nl-dim-score {{ color: var(--gold-light); }}

@media (max-width: 640px) {{
    .nl-conc-lead {{
        flex-direction: column;
        align-items: flex-start;
        gap: 12px;
        padding: 24px;
    }}
    .nl-conc-lead-stat {{ font-size: 44px; }}
    .nl-dim-pair {{ grid-template-columns: 1fr; }}
    .nl-dim-sep  {{ height: 1px; width: 100%; }}
}}

/* ── Conclusiones: disclosure cards ────────────────────────── */
.nl-flip-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 20px;
    margin-bottom: 32px;
}}
.nl-flip-card--primary {{
    grid-column: span 2;
}}
.nl-flip-card {{
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid var(--card-border);
}}
.nl-flip-front {{
    list-style: none;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 32px 24px;
    text-align: center;
    user-select: none;
    min-height: 210px;
    transition: opacity 150ms ease;
}}
.nl-flip-front::-webkit-details-marker {{ display: none; }}
.nl-flip-card[open] > .nl-flip-front {{
    border-bottom: 1px solid var(--card-border);
    min-height: 0;
}}
.nl-flip-back {{
    padding: 24px 22px;
    background: var(--surface-elevated);
    display: flex;
    flex-direction: column;
    gap: 10px;
}}
.nl-flip--teal {{ border-color: rgba(58,168,149,0.3); }}
.nl-flip--gold {{ border-color: rgba(200,151,58,0.3); }}
.nl-flip--rose {{ border-color: rgba(184,92,110,0.3); }}
.nl-flip--teal > .nl-flip-front {{ background: var(--teal-dim); }}
.nl-flip--gold > .nl-flip-front {{ background: var(--gold-dim); }}
.nl-flip--rose > .nl-flip-front {{ background: var(--rose-dim); }}
.nl-flip--neutral > .nl-flip-front {{ background: var(--surface-elevated); }}
.nl-flip-icon {{ font-size: 42px; }}
.nl-flip--teal .nl-flip-icon {{ color: var(--teal-light); }}
.nl-flip--gold .nl-flip-icon {{ color: var(--gold-light); }}
.nl-flip--rose .nl-flip-icon {{ color: var(--rose-light); }}
.nl-flip--neutral .nl-flip-icon {{ color: var(--muted); }}
.nl-flip-tag {{
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}}
.nl-flip--teal .nl-flip-tag {{ color: var(--teal-light) !important; }}
.nl-flip--gold .nl-flip-tag {{ color: var(--gold-light) !important; }}
.nl-flip--rose .nl-flip-tag {{ color: var(--rose-light) !important; }}
.nl-flip--neutral .nl-flip-tag {{ color: var(--muted) !important; }}
.nl-flip-kpi {{
    font-family: 'DM Mono', monospace;
    font-size: 38px;
    font-weight: 500;
    line-height: 1;
    letter-spacing: -0.03em;
}}
.nl-flip--teal .nl-flip-kpi {{ color: var(--teal-light) !important; }}
.nl-flip--gold .nl-flip-kpi {{ color: var(--gold-light) !important; }}
.nl-flip--rose .nl-flip-kpi {{ color: var(--rose-light) !important; }}
.nl-flip--neutral .nl-flip-kpi {{ color: var(--cream) !important; }}
.nl-flip-hint {{ font-size: 10px; color: var(--muted) !important; opacity: 0.65; margin-top: 4px; }}
.nl-flip-card[open] .nl-flip-hint {{ display: none; }}
.nl-flip-back-title {{
    font-size: 14px;
    font-weight: 700;
    color: var(--cream) !important;
    margin: 0;
    line-height: 1.35;
}}
.nl-flip-back-text {{
    font-size: 13px;
    color: var(--muted) !important;
    line-height: 1.65;
    margin: 0;
}}
.nl-flip-back-text strong {{ color: var(--cream) !important; }}

/* dimension comparison card front */
.nl-flip-dim-row {{
    display: flex;
    flex-direction: column;
    gap: 6px;
    width: 100%;
    text-align: left;
}}
.nl-flip-dim-label {{
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: var(--muted) !important;
}}
.nl-flip-dim-val {{
    font-family: 'DM Mono', monospace;
    font-size: 26px;
    font-weight: 500;
    line-height: 1;
    letter-spacing: -0.03em;
}}
.nl-dim-up-val {{ color: var(--teal-light) !important; }}
.nl-dim-down-val {{ color: var(--gold-light) !important; }}
.nl-flip-dim-sep {{ height: 1px; background: var(--card-border); margin: 4px 0; }}

@media (max-width: 600px) {{
    .nl-flip-card--primary {{ grid-column: span 1; }}
}}

/* ── Conclusiones: roadmap recommendations ─────────────────── */
.nl-roadmap {{
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
}}
.nl-roadmap-step {{
    display: grid;
    grid-template-columns: 52px 1fr;
    gap: 20px;
    position: relative;
    padding-bottom: 32px;
}}
.nl-roadmap-step:last-child {{ padding-bottom: 0; }}
.nl-roadmap-step::after {{
    content: '';
    position: absolute;
    top: 52px;
    left: 25px;
    bottom: 0;
    width: 2px;
    background: var(--card-border);
}}
.nl-roadmap-step:last-child::after {{ display: none; }}
.nl-roadmap-marker {{
    width: 52px;
    height: 52px;
    border-radius: 50%;
    background: var(--surface-elevated);
    border: 2px solid rgba(200,151,58,0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'DM Mono', monospace;
    font-size: 18px;
    font-weight: 500;
    color: var(--gold-light) !important;
    flex-shrink: 0;
    position: relative;
    z-index: 1;
}}
.nl-roadmap-body {{ padding: 10px 0 0; }}
.nl-roadmap-title {{
    font-size: 1.125rem;
    font-weight: 700;
    color: var(--cream) !important;
    margin: 0 0 6px;
}}
.nl-roadmap-text {{
    font-size: 13px;
    color: var(--muted) !important;
    line-height: 1.65;
    margin: 0;
}}

/* ── Footer ──────────────────────────────────────────────── */
.nl-footer {{
    margin-top: 80px;
    padding-top: 48px;
    border-top: 1px solid var(--card-border);
}}
.nl-footer-top {{
    display: grid;
    grid-template-columns: minmax(200px, 2fr) repeat(3, minmax(160px, 1fr));
    gap: 48px;
    padding-bottom: 40px;
    align-items: start;
}}
.nl-footer-brand {{
    display: flex;
    flex-direction: column;
    gap: 14px;
}}
.nl-footer-logo {{
    font-family: 'Chronicle Display', serif;
    font-size: 24px;
    font-weight: 700;
    color: var(--gold-light) !important;
    letter-spacing: -0.01em;
}}
.nl-footer-tagline {{
    font-size: 13px;
    color: var(--muted) !important;
    line-height: 1.65;
    margin: 0;
    max-width: 260px;
}}
.nl-footer-col {{
    display: flex;
    flex-direction: column;
    gap: 8px;
}}
.nl-footer-col-title {{
    font-size: 10px;
    font-weight: 700;
    color: var(--cream) !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin: 0 0 8px !important;
    white-space: nowrap !important;
    text-wrap: nowrap !important;
    overflow-wrap: normal !important;
    word-break: normal !important;
    font-family: 'DM Mono', monospace;
}}
.nl-footer-link {{
    color: var(--muted) !important;
    font-size: 13px;
    font-weight: 500;
    text-decoration: none !important;
    font-family: 'DM Sans', sans-serif;
    transition: all 0.25s var(--ease-out-expo);
    display: block;
    padding: 2px 0;
}}
.nl-footer-link:hover {{
    color: var(--gold-light) !important;
    transform: translateX(4px);
}}
.nl-footer-bottom {{
    border-top: 1px solid var(--card-border);
    padding: 20px 0 30px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
    font-family: 'DM Sans', sans-serif;
    font-size: 12px;
    color: var(--muted) !important;
}}
.nl-footer-bottom strong {{ color: var(--cream) !important; }}
.nl-footer-copy {{
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.03em;
}}
.nl-footer-meta {{
    opacity: 0.7;
}}

@media (max-width: 860px) {{
    .nl-footer-top {{
        grid-template-columns: 1fr 1fr;
        gap: 28px;
    }}
    .nl-footer-brand {{
        grid-column: span 2;
    }}
    .nl-pipeline-grid,
    .nl-insights-grid,
    .nl-weights-grid,
    .nl-stats-grid {{
        grid-template-columns: 1fr;
    }}
}}
@media (max-width: 580px) {{
    .nl-footer-top {{
        grid-template-columns: 1fr;
        gap: 20px;
    }}
    .nl-footer-brand {{
        grid-column: span 1;
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

_CSS_UX_ENHANCEMENTS = """
/* ══ UX ENHANCEMENTS ══════════════════════════════════════ */

/* Hover lift for stat cards */
.nl-stat-card {{
    transition: transform 0.25s var(--ease-out, cubic-bezier(0,0,0.2,1)),
                border-color 0.25s ease,
                box-shadow 0.25s ease;
}}
.nl-stat-card:hover {{
    transform: translateY(-4px);
    border-color: var(--border);
    box-shadow: var(--shadow-md);
}}

/* Hover lift for pipeline steps */
.nl-pipeline-step {{
    transition: transform 0.22s var(--ease-out), border-color 0.22s ease, box-shadow 0.22s ease;
}}
.nl-pipeline-step:hover {{
    transform: translateY(-3px);
    border-color: var(--border);
    box-shadow: var(--shadow-md);
}}

/* Hover lift for insight cards */
.nl-insight-card {{
    transition: transform 0.22s var(--ease-out), box-shadow 0.22s ease;
}}
.nl-insight-card:hover {{
    transform: translateY(-3px);
    box-shadow: var(--shadow-md);
}}

/* Hover lift for recommendation items */
.nl-rec-item {{
    transition: background 0.18s ease, box-shadow 0.18s ease;
}}
.nl-rec-item:hover {{
    background: var(--surface);
    box-shadow: var(--shadow-sm);
}}

/* ── Entrance Animations ── */
@keyframes stFadeInUp {
    from {{ opacity: 0; transform: translateY(20px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}
/* Stagger delays via CSS custom property — works with both fallback and observer paths */
.nl-reveal-d1 {{ --reveal-delay: 0.10s; }}
.nl-reveal-d2 {{ --reveal-delay: 0.20s; }}
.nl-reveal-d3 {{ --reveal-delay: 0.30s; }}
.nl-reveal-d4 {{ --reveal-delay: 0.40s; }}
.nl-reveal-d5 {{ --reveal-delay: 0.50s; }}

/* No-JS fallback: animate immediately on load */
.nl-reveal {{
    opacity: 0;
    will-change: transform, opacity;
    animation: stFadeInUp 0.75s var(--ease-out-expo, cubic-bezier(0.16,1,0.3,1)) var(--reveal-delay, 0s) forwards;
}}
/* JS path: hide until observer fires */
.js-reveals .nl-reveal {{ animation: none; }}
.js-reveals .nl-reveal.nl-revealed {{
    animation: stFadeInUp 0.85s var(--ease-out-expo, cubic-bezier(0.16,1,0.3,1)) var(--reveal-delay, 0s) forwards;
}}

@media (prefers-reduced-motion: reduce) {{
    .nl-reveal, .js-reveals .nl-reveal, .js-reveals .nl-reveal.nl-revealed {{
        opacity: 1 !important; animation: none !important;
    }}
}}

/* ── Chart insight panel ───────────────────────────────── */
.nl-chart-insight {{
    background: var(--teal-dim);
    border: 1px solid rgba(58,168,149,0.2);
    border-radius: 10px;
    padding: 14px 20px;
    margin: 10px 0 28px;
    display: flex;
    align-items: flex-start;
    gap: 12px;
}}
.nl-chart-insight-icon {{
    color: var(--teal-light);
    font-size: 20px;
    flex-shrink: 0;
    margin-top: 1px;
}}
.nl-chart-insight-text {{
    font-size: 13px;
    color: var(--muted);
    line-height: 1.65;
    margin: 0;
}}
.nl-chart-insight-text strong {{ color: var(--cream); }}

/* ── Treemap legend chips ──────────────────────────────── */
.nl-treemap-legend {{
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    padding: 0.5rem 0 1rem;
    justify-content: center;
}}
.nl-treemap-chip {{
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.25rem 0.875rem;
    border-radius: 999px;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.06em;
    font-weight: 500;
    background: var(--surface-high);
    border: 1px solid var(--card-border);
    color: var(--muted);
}}
.nl-treemap-chip::before {{
    content: '';
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}}
.nl-treemap-chip--excellent::before {{ background: var(--teal-light); }}
.nl-treemap-chip--good::before {{ background: var(--gold-light); }}
.nl-treemap-chip--poor::before {{ background: var(--rose-light); }}

/* ── CSS Tooltips via data-tooltip ─────────────────────── */
[data-tooltip] {{ position: relative; cursor: help; }}
[data-tooltip]::after {{
    content: attr(data-tooltip);
    position: absolute;
    bottom: calc(100% + 10px);
    left: 50%;
    transform: translateX(-50%);
    background: var(--surface-high);
    border: 1px solid var(--card-border);
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 12px;
    font-family: 'DM Sans', sans-serif;
    color: var(--muted);
    white-space: normal;
    max-width: 240px;
    z-index: 200;
    pointer-events: none;
    opacity: 0;
    transition: opacity 180ms ease;
    box-shadow: var(--shadow-md);
    text-align: left;
    line-height: 1.5;
}}
[data-tooltip]:hover::after {{ opacity: 1; }}

@media (max-width: 600px) {{
    .nl-chart-insight {{ flex-direction: column; gap: 6px; }}
    [data-tooltip]::after {{ left: 0; transform: none; max-width: 200px; }}
}}

/* ── Bienvenida / Onboarding ──────────────────────────── */
.nl-bienvenida {{
    text-align: center;
    padding: 48px 0 12px;
    max-width: 820px;
    margin: 0 auto;
}}
.nl-bienvenida-qes {{
    max-width: 740px;
    margin: 0 auto 8px;
    display: flex;
    flex-direction: column;
    gap: 14px;
    text-align: left;
}}
.nl-bienvenida-nav {{
    max-width: 740px;
    margin: 0 auto 8px;
    text-align: left;
}}
.nl-cta-btn {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--teal-gradient);
    color: var(--cream);
    border-radius: var(--radius-full);
    padding: 12px 28px;
    font-family: 'DM Sans', sans-serif;
    font-size: 15px;
    font-weight: 600;
    text-decoration: none;
    transition: opacity 0.2s ease, transform 0.2s var(--ease-out);
    margin-top: 20px;
}}
.nl-cta-btn:hover {{
    opacity: 0.88;
    transform: translateY(-2px);
    color: var(--cream);
    text-decoration: none;
}}

/* ── Failure panel ────────────────────────────────────── */
.nl-failure-icon {{ font-size: 18px; color: var(--rose-light); }}
.nl-failure-details {{ margin-top: 12px; }}
.nl-failure-summary {{ color: var(--muted); font-size: 13px; cursor: pointer; }}
.nl-failure-detail-list {{ margin-top: 8px; }}

/* ══ Alerta cards — sistema unificado v2 (Material 3 / Linear) ── */
.nl-alerta-heading {{
    color: var(--rose);
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    text-align: left;
}}

/* Grid de tarjetas: filas auto-equalizan altura */
.nl-alerta-grid {{
    display: grid;
    grid-template-columns: 1fr;
    gap: 20px;
    margin-bottom: 8px;
}}

/* Tarjeta raíz: altura uniforme + columna + alineación forzada */
.nl-alerta-card {{
    display: flex;
    flex-direction: column;
    overflow: hidden;
    padding: 0;
    margin-bottom: 0;
    height: 100%;
    min-height: 460px;
    text-align: left;
}}
.nl-alerta-card *,
.nl-alerta-card *::before,
.nl-alerta-card *::after {{ text-align: inherit; }}
.nl-alerta-card .nl-alerta-card-score-col,
.nl-alerta-card .nl-alerta-card-score-col * {{ text-align: right; }}
.nl-alerta-card .nl-alerta-dim-val {{ text-align: right; }}

.nl-alerta-card-body {{
    padding: 20px 22px;
    display: flex;
    flex-direction: column;
    flex: 1;
    gap: 18px;
}}

/* Cabecera: título + score (alineación a baseline para evitar huecos) */
.nl-alerta-card-head {{
    display: grid;
    grid-template-columns: 1fr auto;
    align-items: start;
    gap: 16px;
    min-height: 88px;
}}
.nl-alerta-card-inner {{
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 4px;
}}

/* Eyebrow categoría */
.nl-alerta-eyebrow {{
    font-family: 'DM Mono', monospace;
    font-size: 0.625rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--gold-light);
    line-height: 1;
    margin-bottom: 2px;
}}

.nl-alerta-title {{
    font-family: 'Chronicle Display', serif;
    font-size: 1.0625rem;
    font-weight: 700;
    line-height: 1.3;
    letter-spacing: -0.005em;
    color: var(--cream);
    margin: 0;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    word-break: break-word;
}}
.nl-alerta-org {{
    font-family: 'DM Sans', sans-serif;
    font-size: 0.75rem;
    color: var(--muted);
    margin: 2px 0 0;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}}
.nl-alerta-card-score-col {{
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 4px;
    min-width: 96px;
}}
.nl-alerta-score-unit {{
    font-size: 0.5em;
    font-weight: 500;
    color: var(--muted);
    margin-left: 2px;
    letter-spacing: 0;
}}

/* Severidad */
.nl-alerta-sev {{
    display: inline-flex;
    align-items: center;
    font-family: 'DM Mono', monospace;
    font-size: 0.5625rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 9999px;
    border: 1px solid transparent;
    line-height: 1.4;
}}
.nl-alerta-sev--ok       {{ color: var(--teal-light); background: rgba(42,122,111,0.12); border-color: rgba(42,122,111,0.35); }}
.nl-alerta-sev--warn     {{ color: var(--gold-light); background: rgba(200,151,58,0.12); border-color: rgba(200,151,58,0.35); }}
.nl-alerta-sev--critical {{ color: var(--rose-light); background: rgba(184,92,110,0.12); border-color: rgba(184,92,110,0.35); }}

/* Lista de dimensiones — filas inline uniformes (no grid) */
.nl-alerta-dim-list {{
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 14px 0;
    border-top: 1px solid var(--card-border);
    border-bottom: 1px solid var(--card-border);
}}

/* Acciones (recomendaciones) — flex 1 empuja footer abajo */
.nl-alerta-card-actions {{
    padding-top: 0;
    display: flex;
    flex-direction: column;
    gap: 8px;
    flex: 1;
}}
.nl-alerta-card-actions .kpi-label {{
    margin: 0 0 4px;
    font-size: 0.625rem;
    letter-spacing: 0.1em;
}}

/* Pie con CTA */
.nl-alerta-card-footer {{
    background: var(--surface-alt);
    border-top: 1px solid var(--card-border);
    padding: 12px 22px;
}}
.nl-alerta-card-link {{
    color: var(--gold-light);
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    font-size: 0.8125rem;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}}
.nl-alerta-card-link:hover {{ color: var(--gold); text-decoration: none; }}

/* Filas inline de dimensión: label · barra · valor */
.nl-alerta-dim-row {{
    display: grid;
    grid-template-columns: 96px 1fr 40px;
    align-items: center;
    gap: 10px;
}}
.nl-alerta-dim-label {{
    font-family: 'DM Mono', monospace;
    font-size: 0.625rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    color: var(--muted);
    text-transform: uppercase;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.nl-alerta-dim-bar {{
    height: 5px;
    border-radius: 3px;
}}
.nl-alerta-dim-val {{
    font-family: 'DM Mono', monospace;
    font-variant-numeric: tabular-nums;
    font-size: 0.6875rem;
    font-weight: 700;
    color: var(--cream);
}}
/* Items de recomendación */
.nl-alerta-rec-list {{
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 8px;
}}
.nl-alerta-rec-item {{
    display: flex;
    align-items: flex-start;
    gap: 10px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.75rem;
    color: var(--cream);
    line-height: 1.5;
    margin: 0;
}}
.nl-alerta-rec-text {{ flex: 1; min-width: 0; }}
.nl-alerta-rec-num {{
    width: 18px;
    height: 18px;
    min-width: 18px;
    font-family: 'DM Mono', monospace;
    font-size: 0.625rem;
    font-weight: 700;
    border-radius: 50%;
    background: var(--surface-alt);
    color: var(--gold-light);
    border: 1px solid var(--card-border);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 1px;
}}

/* Banner icon (reemplaza style="font-size:..." inline) */
.nl-alert-banner-icon {{ font-size: 28px; line-height: 1; }}
.nl-alert-banner-icon--lg {{ font-size: 32px; line-height: 1; }}

/* Score: tamaño moderado dentro del card (era 2.5rem por defecto) */
.nl-alerta-card .alert-score {{
    font-size: 1.75rem;
    line-height: 1;
    color: var(--rose-light);
    letter-spacing: -0.02em;
}}
.nl-alerta-card .nl-alerta-card-score-col .kpi-label {{
    font-size: 0.5625rem;
    letter-spacing: 0.1em;
    color: var(--muted);
    line-height: 1.2;
}}

@media (max-width: 600px) {{
    .nl-alerta-card {{ min-height: 0; }}
    .nl-alerta-card-body {{ padding: 18px; gap: 16px; }}
    .nl-alerta-card-footer {{ padding: 12px 18px; }}
    .nl-alerta-card .alert-score {{ font-size: 1.5rem; }}
    .nl-alerta-card-score-col {{ min-width: 80px; }}
    .nl-alerta-card-head {{ min-height: 0; }}
    .nl-alerta-dim-row {{ grid-template-columns: 84px 1fr 36px; }}
}}

/* ── Accordion list wrapper ────────────────────────────────── */
.nl-alerta-accordion-list {{
    display: flex;
    flex-direction: column;
    gap: 0;
    margin-bottom: 24px;
}}

/* ── Accordion alerta cards (collapsible details/summary) ── */
.nl-alerta-accordion {{
    border: 1px solid rgba(184,92,110,0.25);
    border-radius: 12px;
    overflow: hidden;
    background: var(--surface-elevated);
    transition: border-color 0.2s ease;
    margin-bottom: 8px;
}}
.nl-alerta-accordion[open] {{
    border-color: rgba(184,92,110,0.45);
    box-shadow: 0 0 0 1px rgba(184,92,110,0.12);
}}
.nl-alerta-summary {{
    list-style: none;
    cursor: pointer;
    padding: 18px 20px;
    user-select: none;
    -webkit-user-select: none;
    transition: background 0.15s ease;
}}
.nl-alerta-summary::-webkit-details-marker {{ display: none; }}
.nl-alerta-summary::marker {{ display: none; }}
.nl-alerta-summary:hover {{ background: rgba(184,92,110,0.04); }}
.nl-alerta-summary-inner {{
    display: grid;
    grid-template-columns: 1fr auto 28px;
    align-items: center;
    gap: 16px;
}}
.nl-alerta-summary-meta {{ min-width: 0; }}
.nl-alerta-summary-score {{
    text-align: right;
    flex-shrink: 0;
}}
.nl-alerta-accordion .alert-score {{
    font-size: 1.625rem;
    line-height: 1;
    color: var(--rose-light);
    letter-spacing: -0.02em;
}}
.nl-alerta-accordion .kpi-label {{
    font-size: 0.5625rem;
    letter-spacing: 0.1em;
    color: var(--muted);
    line-height: 1.3;
    margin: 3px 0 4px;
}}
.nl-alerta-chevron {{
    font-size: 20px;
    color: var(--muted);
    transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    display: flex;
    align-items: center;
    justify-content: center;
}}
.nl-alerta-accordion[open] .nl-alerta-chevron {{ transform: rotate(180deg); }}
.nl-alerta-detail {{
    border-top: 1px solid var(--card-border);
    padding: 20px 20px 0;
    display: flex;
    flex-direction: column;
    gap: 0;
}}
.nl-alerta-detail .nl-alerta-dim-list {{ margin-bottom: 16px; }}
.nl-alerta-detail .nl-alerta-card-actions {{ flex: 1; padding-top: 0; margin-bottom: 16px; }}
.nl-alerta-detail .nl-alerta-card-footer {{
    margin: 0 -20px;
    border-radius: 0;
}}

@media (max-width: 600px) {{
    .nl-alerta-summary-inner {{ grid-template-columns: 1fr auto 24px; gap: 10px; }}
    .nl-alerta-accordion .alert-score {{ font-size: 1.375rem; }}
    .nl-alerta-summary {{ padding: 16px; }}
    .nl-alerta-detail {{ padding: 16px 16px 0; }}
    .nl-alerta-detail .nl-alerta-card-footer {{ margin: 0 -16px; }}
}}
"""

_CSS_BACKGROUNDS = """
/* ══ ATMOSPHERIC BACKGROUNDS ══════════════════════════════ */
.bg-hero {
    background: var(--midnight);
    border-bottom: 1px solid var(--card-border);
}
"""

_CSS_APP_STORE = """
/* ══ APP STORE STYLE GRID & CARDS ═════════════════════════ */
.dataset-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 24px;
    margin-top: 24px;
}

.app-card {
    background: var(--surface-high);
    border: 1px solid var(--card-border);
    border-radius: 20px;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    transition: all 0.3s var(--ease-out-expo);
    position: relative;
    overflow: hidden;
    height: 100%;
    text-decoration: none !important;
}

.app-card:hover {
    transform: translateY(-6px) scale(1.01);
    border-color: var(--gold-light);
    box-shadow: var(--shadow-xl);
}

.app-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}

.app-card-icon {
    width: 64px;
    height: 64px;
    background: var(--surface-alt);
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--gold-light);
}

.app-card-icon .material-symbols-outlined {
    font-size: 32px;
}

.app-card-score-badge {
    padding: 6px 14px;
    border-radius: 9999px;
    font-family: 'DM Mono', monospace;
    font-size: 14px;
    font-weight: 700;
}

.app-card-score-excellent { background: var(--teal-dim); color: var(--teal-light); }
.app-card-score-good      { background: var(--gold-dim); color: var(--gold-light); }
.app-card-score-poor      { background: var(--rose-dim); color: var(--rose-light); }

.app-card-content {
    flex: 1;
}

.app-card-title {
    font-family: 'Chronicle Display', serif;
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--cream);
    margin-bottom: 8px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    line-height: 1.3;
}

.app-card-org {
    font-size: 13px;
    color: var(--muted);
    font-weight: 500;
    margin-bottom: 12px;
}

.app-card-summary {
    font-size: 14px;
    color: var(--paper);
    line-height: 1.5;
    margin-bottom: 16px;
    opacity: 0.9;
}

.app-card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 16px;
    border-top: 1px solid var(--card-border);
}

.app-card-meta {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.app-card-meta-label {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--muted);
}

.app-card-meta-value {
    font-size: 12px;
    font-weight: 600;
    color: var(--cream);
}

.app-card-btn {
    padding: 8px 16px;
    background: var(--surface-alt);
    color: var(--gold-light);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    font-size: 12px;
    font-weight: 700;
    text-decoration: none;
    transition: all 0.2s ease;
}

.app-card-btn:hover {
    background: var(--gold-dim);
    border-color: var(--gold);
}

/* ══ TEXT TRUNCATION UTILITIES ════════════════════════════ */
.text-clamp-1 { display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; overflow: hidden; }
.text-clamp-2 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.text-clamp-3 { display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
"""

_CSS_UTILITIES = """
/* ══ UTILITIES ════════════════════════════════════════════ */
.d-flex { display: flex; }
.align-center { align-items: center; }
.align-start  { align-items: flex-start; }
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
    font-family: 'Chronicle Display', serif;
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
@keyframes ring-draw {{
    from {{ stroke-dashoffset: 339.3; }}
    to   {{ stroke-dashoffset: 0; }}
}}
.score-ring-arc {{
    stroke-dashoffset: 339.3;
    animation: ring-draw 1.2s var(--ease-out-expo) 0.3s both;
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

    Call with: st.html(inject_design_system(theme))
    """
    tokens = _TOKENS_DARK if theme == "dark" else _TOKENS_LIGHT

    blocks = [
        _CSS_RESET,
        _CSS_TYPO_SCALE,
        _CSS_HIDE_CHROME,
        _CSS_TOPBAR,
        _CSS_SIDEBAR,
        _CSS_LAYOUT,
        _CSS_EDITORIAL,
        _CSS_SECTIONS,
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
        _CSS_UX_ENHANCEMENTS,
        _CSS_APP_STORE,
        _CSS_BACKGROUNDS,
        _CSS_UTILITIES,
    ]

    # All blocks are raw CSS strings. Some use {{ }} for Python escaping,
    # others use raw { }. We normalize by unescaping {{ → { and }} → }.
    resolved: list[str] = []
    for b in blocks:
        resolved.append(b.replace("{{", "{").replace("}}", "}"))
    css_body = "\n".join(resolved)

    return (
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        f"""<style>
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=block');
        @import url('https://fonts.googleapis.com/css2?family=Chronicle+Display:ital,wght@0,400;0,600;0,700;1,400&family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
        :root {{ {tokens} }}
        {css_body}
        </style>"""
    )
