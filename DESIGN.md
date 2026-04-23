# DESIGN.md — Sistema de Diseño NL 2026
# Gobernanza de Datos — Nuevo León
# Canon visual para todo el proyecto. Referencia: .agent/skills/design-system-pro/SKILL.md

## Identity

- **Name**: Gobernanza de Datos — Nuevo León 2026
- **Platform**: Web (Streamlit)
- **Theme**: Dark (default), Light (toggle)
- **Language**: es-MX
- **Design System**: Midnight/Teal/Gold/Rose

## Fonts (Google Fonts CDN)

| Font | Role | Weight | Usage |
|---|---|---|---|
| **Playfair Display** | Display/Serif | 400, 600, 700 (+ italic) | H1–H3 titles, hero stats, quote text |
| **DM Sans** | Body/Sans | 300, 400, 500, 600, 700 | Body text, UI, nav, descriptions |
| **DM Mono** | Data/Mono | 400, 500 | Eyebrows, badges, dates, counters, labels |

## Color System

### Dark Theme (default)

| Token | Hex | Usage |
|---|---|---|
| `--midnight` | `#0f1c2e` | Page background |
| `--navy` | `#1a2d45` | Elevated surfaces |
| `--card-bg` | `rgba(255,255,255,0.04)` | Card backgrounds |
| `--cream` | `#faf6ee` | Primary titles |
| `--paper` | `#f5f0e8` | Body text |
| `--muted` | `#8a9bb0` | Secondary text, labels |
| `--teal` | `#2a7a6f` | Positive/data/success |
| `--teal-light` | `#3aa895` | Positive highlight |
| `--gold` | `#c8973a` | Structural/highlight |
| `--gold-light` | `#e4b96a` | Gold highlight |
| `--rose` | `#b85c6e` | Alert/negative |
| `--rose-light` | `#d4738a` | Alert highlight |
| `--border` | `rgba(200,151,58,0.25)` | Hover borders |
| `--card-border` | `rgba(255,255,255,0.07)` | Card borders |
| `--surface` | `#1a2d45` | Surface level 1 |
| `--surface-alt` | `#152538` | Surface level 2 |

### Quality Tiers (ISO 25012)

| Tier | Condition | Color |
|---|---|---|
| Excellent | Score ≥ 90% | `var(--teal)` |
| Good | Score 70–89% | `var(--gold)` |
| Poor | Score < 70% | `var(--rose)` |

## Spacing Scale (8px base)

| Token | Size |
|---|---|
| xs | 4px |
| sm | 8px |
| md | 16px |
| lg | 24px |
| xl | 32px |
| xxl | 48px |

## Shape (Border Radius)

| Token | Size | Usage |
|---|---|---|
| xs | 4px | Heatmap cells, small tags |
| sm | 8px | Buttons, inputs |
| md | 10px | Cards |
| lg | 12px | KPI cards, filter bars |
| xl | 20px | Bento panels, hero cards |
| pill | 9999px | Badges, nav pills, CTAs |

## Component Architecture

### KPI Card
- 3px top accent stripe (tier color)
- `border-radius: 12px`
- Padding: `24px 20px 18px`
- Value: Playfair Display 32px 700
- Label: DM Mono 13px uppercase

### Data Table
- Header: `var(--surface)` bg, DM Mono 11px uppercase
- Rows: `var(--card-border)` separator
- Hover: `var(--overlay)` highlight

### Heatmap
- Cells: 40px height, rounded 4px
- Colors: teal/gold/rose based on score
- Hover: `scale(1.05)` transform

### Alert Card
- Left border: 6px solid `var(--rose)`
- `border-radius: 0 12px 12px 0`
- Score: Playfair Display 36px 700 rose
- Recommendations: numbered list

### Navigation (Top Bar)
- Fixed, 64px height
- Blur backdrop: `blur(16px) saturate(180%)`
- Active link: gold-light text, gold bg at 12%
- Mobile: hamburger menu

## Screens

| ID | Route | Title |
|---|---|---|
| inicio | `/?section=inicio` | Landing Page |
| categorias | `/?section=categorias` | Rendimiento por Categoría |
| datasets | `/?section=datasets` | Explorador de Datasets |
| organizaciones | `/?section=organizaciones` | Organizaciones |
| evolucion | `/?section=evolucion` | Evolución Histórica |
| avanzado | `/?section=avanzado` | Análisis Avanzado |
| calidad_pro | `/?section=calidad_pro` | Calidad Pro (ISO 8000/DAMA) |

## Files

| File | Role |
|---|---|
| `styles/global_css.py` | Token injection, CSS classes, Plotly themes |
| `sections/*.py` | Section renderers using design tokens |
| `.streamlit/config.toml` | Streamlit native theme config |
| `.agent/skills/design-system-pro/SKILL.md` | Agent skill reference |
