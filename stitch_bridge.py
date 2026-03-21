"""
stitch_bridge.py
Extrae el Design DNA de cada pantalla Stitch y lo convierte
en tokens CSS inyectables en Streamlit.
"""
import subprocess
import json
import re
import os

def get_screen_design_dna(project_id: str, screen_id: str) -> dict:
    try:
        # Intenta usar Stitch MCP
        result = subprocess.run(
            ["npx", "@_davideast/stitch-mcp", "tool", "get_screen_code",
             "-d", json.dumps({"projectId": project_id, "screenId": screen_id})],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            html_content = json.loads(result.stdout).get("html", "")
            style_match = re.search(r"<style>(.*?)</style>", html_content, re.DOTALL)
            css_block   = style_match.group(1) if style_match else ""
            hex_colors  = list(set(re.findall(r"#[0-9A-Fa-f]{3,8}", css_block)))
            fonts       = list(set(re.findall(r"font-family:\s*([^;]+)", css_block)))
            return {
                "screen_id": screen_id,
                "css"      : css_block,
                "colors"   : hex_colors,
                "fonts"    : fonts,
                "html"     : html_content,
            }
    except Exception as e:
        pass
        
    print(f"[StitchBridge] Fallback: Stitch MCP inactivo ({screen_id}). Usando tokens locales...")
    return {
        "screen_id": screen_id,
        "css"      : "",
        "colors"   : [],
        "fonts"    : ["Roboto"],
        "html"     : f"<div>Fallback genérico para {screen_id}</div>",
    }


def build_streamlit_css(dna: dict, tokens: dict) -> str:
    stitch_css = dna.get("css", "")

    streamlit_overrides = f"""
    /* ── Importar Inter y Plus Jakarta Sans ─────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

    /* ── Stitch Design DNA extraído ──────────────────────── */
    {stitch_css}

    /* ── Overrides Streamlit M3 / Stitch Frame ─────────────── */
    header[data-testid="stHeader"] {{ display: none !important; }}
    footer[data-testid="stFooter"] {{ display: none !important; }}
    .stApp               {{ background: {tokens['elevation']['0']} !important; }}
    .stApp *             {{ font-family: 'Inter', system-ui, sans-serif !important; }}
    [data-testid="stSidebar"] {{
        background   : {tokens['elevation']['1']} !important;
        border-right : 1px solid #e2e8f0 !important;
        width        : 260px !important;
        padding-top  : 80px !important;
    }}
    
    /* ── Magia UX: Convertir Radio a Links Stitch ───────── */
    [data-testid="stRadio"] div[role="radiogroup"] label {{
        background: transparent;
        padding: 10px 16px;
        border-radius: 9999px;
        margin-bottom: 4px;
        transition: 0.2s all;
        cursor: pointer;
    }}
    [data-testid="stRadio"] div[role="radiogroup"] label:hover {{
        background: #f1f5f9 !important;
        color: {tokens['color']['primary']} !important;
    }}
    /* Esconder el circulito del input */
    [data-testid="stRadio"] div[role="radiogroup"] label span[data-baseweb="radio"] {{
        display: none !important;
    }}
    /* Link activo / seleccionado */
    [data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"] {{
        background: rgba(0,91,191,0.08) !important;
    }}
    /* Ajuste texto del Navbar Lateral */
    [data-testid="stRadio"] div[role="radiogroup"] label p {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 13px !important;
        font-weight: 700 !important;
        color: {tokens['color']['on_surface_variant']};
        margin: 0 !important;
    }}
    [data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"] p {{
        color: {tokens['color']['primary']} !important;
    }}
    
    [data-testid="stMetric"]       {{ display: none; }}
    
    /* Layout expansivo idéntico al diseño Web de Stitch */
    .block-container {{
        padding: 96px 2rem 2rem !important; 
        max-width: 1440px !important;
    }}
    
    /* Tab Styling Minimalista */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: transparent !important;
        border-bottom: 1px solid #e2e8f0 !important;
        margin-bottom: 24px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background    : transparent;
        border-bottom : 2px solid transparent;
        font-weight   : 600;
        color         : {tokens['color']['on_surface_variant']} !important;
        padding-top   : 12px;
        padding-bottom: 12px;
    }}
    .stTabs [aria-selected="true"] {{
        border-bottom-color: {tokens['color']['primary']} !important;
        color              : {tokens['color']['primary']} !important;
    }}
    h1 {{ font-weight: {tokens['typography']['display_large']['weight']} !important; color: {tokens['color']['primary']} !important; font-family:'Plus Jakarta Sans',sans-serif !important; }}
    h2, .section-title {{
      font-weight: {tokens['typography']['headline_medium']['weight']} !important;
      color: {tokens['color']['on_surface']} !important;
      padding-bottom: 8px;
      margin-bottom: 24px;
      font-family:'Plus Jakarta Sans',sans-serif !important;
    }}
    """
    return f"<style>{streamlit_overrides}</style>"


def extract_all_screens(project_id: str, screen_ids: list[str], output_dir: str = "stitch_output") -> dict:
    os.makedirs(output_dir, exist_ok=True)
    dnas = {}
    for sid in screen_ids:
        dna = get_screen_design_dna(project_id, sid)
        dnas[sid] = dna
        with open(f"{output_dir}/{sid}.html", "w", encoding="utf-8") as f:
            f.write(dna["html"])
    return dnas
