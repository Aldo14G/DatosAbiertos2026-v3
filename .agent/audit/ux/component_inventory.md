# Component Inventory — CSS Design System

**Fuente:** [styles/global_css.py](../../../styles/global_css.py) (1555 líneas, 30+ bloques modulares).
**Método:** Extracción de todas las clases `.xxx { }` + grep de uso en `sections/*.py` y `dashboard_v3.py`.

## Bloques CSS definidos (orden de inyección)

| # | Bloque | Líneas | Clases clave |
|---|---|---|---|
| 1 | `_TOKENS_DARK` | 68-116 | CSS vars: palette, spacing, shadows, motion, radii |
| 2 | `_TOKENS_LIGHT` | 117-170 | Paridad de tokens para light mode |
| 3 | `_CSS_RESET` | 171-184 | Reset base `.material-symbols-outlined` |
| 4 | `_CSS_HIDE_CHROME` | 185-193 | Oculta chrome de Streamlit |
| 5 | `_CSS_TOPBAR` | 194-383 | `.stitch-topbar*`, `.stitch-mobile-*` |
| 6 | `_CSS_SIDEBAR` | 385-396 | Sidebar overrides |
| 7 | `_CSS_LAYOUT` | 397-405 | `.block-container` |
| 8 | `_CSS_TYPOGRAPHY` | 406-458 | `.eyebrow`, `.section-title`, `.section-subtitle`, `.hero-title`, `.hero-subtitle`, `.divider` |
| 9 | `_CSS_CARDS` | 460-534 | `.stitch-card`, `.stitch-card-accent(-gold/-rose)`, `.bento-card`, `.section-panel`, `.stitch-btn-*` |
| 10 | `_CSS_KPI` | 536-593 | `.kpi-card`, `.kpi-label`, `.kpi-value`, `.kpi-delta(.up/.down)` |
| 11 | `_CSS_BADGE` | 595-657 | `.badge`, `.badge-gold`, `.badge-rose`, `.category-badge`, `.filter-chip` |
| 12 | `_CSS_BARS` | 659-680 | `.bar-track`, `.bar-fill`, `.bar-fill-gold`, `.bar-fill-rose` |
| 13 | `_CSS_STAT` | 682-703 | `.stat-card`, `.stat-number`, `.stat-label` |
| 14 | `_CSS_QUOTE` | 705-729 | `.quote-block`, `.quote-text`, `.quote-source` |
| 15 | `_CSS_HEATMAP` | 731-743 | `.heatmap-cell` |
| 16 | `_CSS_ALERTS` | 745-796 | `.alert-banner`, `.alert-banner-success`, `.alert-banner-warning`, `.alert-card`, `.alert-score` |
| 17 | `_CSS_ICON_LIST` | 797-835 | `.icon-list`, `.icon-list-item`, `.icon-box`, `.icon-box-gold`, `.icon-box-rose` |
| 18 | `_CSS_TABLE` | 836-862 | `.comparison-table` |
| 19 | `_CSS_GRIDS` | 863-881 | `.card-grid`, `.card-grid-2/3/4` |
| 20 | `_CSS_GAUGE` | 883-894 | `.gauge-container` |
| 21 | `_CSS_TABS` | 895-915 | `.stTabs [aria-selected]` overrides |
| 22 | `_CSS_DATA_TABLE` | 916-938 | `.data-table` |
| 23 | `_CSS_STREAMLIT_OVERRIDES` | 939-971 | Button/input theming |
| 24 | `_CSS_SIDEBAR_TOGGLE` | 972-988 | Sidebar collapse button |
| 25 | `_CSS_SCROLLBAR` | 989-996 | Custom scrollbar |
| 26 | `_CSS_ANIMATIONS` | 997-1083 | `.fade-up`, `.fade-up-1…5`, `@keyframes` (shimmer, scaleIn, slideInLeft, slideInRight, numberPop, barGrow, pulseSoft, spin, topbarAppear), `prefers-reduced-motion` |
| 27 | `_CSS_SKELETON` | 1084-1110 | `.skeleton`, `.skeleton-card`, `.skeleton-line(-sm/-lg)`, `.skeleton-circle`, `.skeleton-kpi` |
| 28 | `_CSS_BENTO_GRID` | 1111-1135 | `.bento-grid`, `.bento-col-4/6/8/12`, `.bento-row-2/3` |
| 29 | `_CSS_INICIO` | 1137-1305 | `.inicio-hero`, `.inicio-divider*`, `.inicio-activity-*`, `.inicio-health-*`, `.inicio-empty-state`, `.inicio-footer` |
| 30 | `_CSS_A11Y` | 1307-1405 | Focus rings, pagination `.stitch-pagination*`, `.stitch-page-link` |
| 31 | `_CSS_BACKGROUNDS` | 1407-1426 | `.bg-hero`, `.bg-teal`, `.bg-gold` |
| 32 | `_CSS_UTILITIES` | 1427-1547 | `.d-flex`, `.align-center`, `.gap-*`, `.mt-*`, `.mb-*`, `.p-*`, `.text-*`, `.w-100`, `.btn-gold-gradient`, `.data-breadcrumb`, `.surface-high-card`, `.score-ring(-value/-label)` |

## Uso confirmado en `sections/*.py`

| Clase | inicio.py | datasets.py | calidad_pro.py | organizaciones.py |
|---|---|---|---|---|
| `.kpi-card` / `.kpi-value` / `.kpi-label` | ✅ | — | ✅ | — (usa inline) |
| `.hero-title` / `.hero-subtitle` | ✅ | ✅ | — | ✅ |
| `.section-title` / `.section-subtitle` | ✅ | ✅ | ✅ | ✅ |
| `.eyebrow` | ✅ | — | ✅ | — |
| `.stitch-card` / `-accent-rose` / `-accent-gold` | — | ✅ | — | — |
| `.bento-card` | — | — | — | ✅ |
| `.section-panel` | ✅ | ✅ | — | ✅ |
| `.bar-track` / `.bar-fill` | ✅ | ✅ | — | — |
| `.surface-high-card` | ✅ | — | ✅ | — |
| `.badge` / `-gold` / `-rose` | ✅ | ✅ | — | — |
| `.data-breadcrumb` | ✅ | — | ✅ | — |
| `.alert-banner(-success)` | — | ✅ | — | — |
| `.icon-list` / `.icon-box` | — | ✅ | — | — |
| `.score-ring(-value/-label)` | ✅ | — | — | — |
| `.fade-up` | ✅ | — | — | — |
| `.bg-teal` | — | — | ✅ | — |
| `.card-grid-2` | — | ✅ | — | — |
| Utilities `.d-flex/.mb-*/.mt-*` | ✅ | ✅ | — | — |

## Huérfanos — **definidas pero NO consumidas**

Clases presentes en `global_css.py` sin llamada encontrada en `sections/` o `dashboard_v3.py`:

| Clase | Bloque | Recomendación |
|---|---|---|
| `.skeleton`, `.skeleton-card`, `.skeleton-line*`, `.skeleton-circle`, `.skeleton-kpi` | `_CSS_SKELETON` | **Aplicar en Fase 2** durante `load_data()` y filter re-renders |
| `.bento-grid`, `.bento-col-*`, `.bento-row-*` | `_CSS_BENTO_GRID` | **Aplicar en Fase 2** para reestructurar landing y sección Organizaciones |
| `.heatmap-cell` | `_CSS_HEATMAP` | Huérfano real (se usa Plotly Heatmap) — **evaluar borrado** |
| `.stat-card`, `.stat-number`, `.stat-label` | `_CSS_STAT` | Huérfano — `kpi-card` cumple la función |
| `.quote-block`, `.quote-text`, `.quote-source` | `_CSS_QUOTE` | Huérfano — planeado para testimonios; **borrar o marcar experimental** |
| `.comparison-table` | `_CSS_TABLE` | Huérfano — sin vista comparativa actual |
| `.gauge-container` | `_CSS_GAUGE` | Huérfano — se usa SVG custom en `inicio.py` |
| `.stitch-pagination*`, `.stitch-page-link*` | `_CSS_A11Y` | Huérfano — Streamlit maneja paginación de dataframes nativamente |
| `.filter-chip`, `.category-badge` | `_CSS_BADGE` | Huérfano — `.badge` cumple función |
| `.data-table` | `_CSS_DATA_TABLE` | Huérfano — `st.dataframe` reemplaza |
| `.btn-gold-gradient` | `_CSS_UTILITIES` | Huérfano |
| `.bg-hero`, `.bg-gold` | `_CSS_BACKGROUNDS` | Huérfano (solo `.bg-teal` se usa) |

## Inline CSS residual — violación design-system-pro

**Regla:** "PROHIBIDO el uso de variables inline largas" ([.agent/skills/design-system-pro/SKILL.md](../../skills/design-system-pro/SKILL.md)).

**Conteo de `style="..."` con ≥30 caracteres:**

| Archivo | Ocurrencias | Severidad |
|---|---|---|
| [sections/organizaciones.py](../../../sections/organizaciones.py) | **76** | **Crítica** |
| [sections/datasets.py](../../../sections/datasets.py) | 16 | Alta |
| [sections/calidad_pro.py](../../../sections/calidad_pro.py) | 11 | Media |
| [sections/inicio.py](../../../sections/inicio.py) | 4 | Baja |
| [dashboard_v3.py](../../../dashboard_v3.py) | ~15 (sidebar, topbar, footer) | Media |

**Total:** ~120 violations.

### Peores ofensores

1. **`_render_mapa_visual()`** en [organizaciones.py:484-562](../../../sections/organizaciones.py#L484-L562) — el mapa entero es HTML inline sin una sola clase consumida (excepto `material-symbols-outlined`).
2. **`_render_org_kpis()`** en [organizaciones.py:136-144](../../../sections/organizaciones.py#L136-L144) — KPI cards 100% inline en lugar de `.kpi-card`.
3. **`_render_org_table()`** en [organizaciones.py:304-347](../../../sections/organizaciones.py#L304-L347) — tabla custom con inline cell-by-cell.
4. **`_render_top_bottom()`** en [organizaciones.py:367-395](../../../sections/organizaciones.py#L367-L395) — cards de ranking inline.

## Propuesta de migración (Fase 2)

Añadir al design system las siguientes clases nuevas:

- `.org-kpi-card` — reemplazar inline de `_render_org_kpis`.
- `.org-row` + `.org-cell` — reemplazar `_render_org_table`.
- `.org-rank-item` — reemplazar `_render_top_bottom`.
- `.org-map-shell` + `.org-map-overlay` + `.org-map-glass-card` + `.org-map-legend-chip` — reemplazar `_render_mapa_visual`.

Estimación: ~200 líneas CSS nuevas vs ~600 líneas de inline removidas.

## Consumo confirmado de tokens en `_TOKENS_DARK`

Tokens `--*` usados directamente en `sections/*.py`:

- `--teal`, `--teal-light` — OK (inicio, datasets)
- `--gold`, `--gold-light` — OK
- `--rose`, `--rose-light` — OK
- `--cream` — OK
- `--muted` — OK
- `--card-bg`, `--card-border` — OK
- `--surface`, `--surface-alt`, `--surface-high` — OK
- `--ghost-border` — usado solo en `inicio.py:122, 262`
- `--overlay` — usado en `organizaciones.py` (map shadows)
- `--focus-ring` — **sin uso directo en sections/**; solo referenciado dentro de `global_css.py` → aplicar explícitamente en botones y links.
