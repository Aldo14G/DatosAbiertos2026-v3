# DESIGN.md — Calidad de Datos Abiertos NL 2026
# Formato: Stitch Design System (vibe design specification)
# Referencia: stitch.withgoogle.com/docs/design-systems

## Identity
name: "Gobernanza de Datos NL"
platform: web
theme: dark
primary_language: es-MX

## Color System (Material Design 3 × NL Government Palette)
colors:
  primary:           "#2E75B6"   # Azul Gobierno NL — acción principal
  primary_container: "#1A4A7A"   # Contenedor primario (hover, pressed)
  on_primary:        "#FFFFFF"   # Texto sobre primario
  secondary:         "#0288D1"   # Acento informativo
  tertiary:          "#00ACC1"   # Acento de apoyo (tabs, badges)

  surface_0:  "#0F0F1A"          # Fondo base (más oscuro)
  surface_1:  "#1A1A2E"          # Cards de nivel 1
  surface_2:  "#22223A"          # Cards de nivel 2 (elevados)
  surface_3:  "#2A2A46"          # Modales, tooltips

  on_surface:         "#E8E8F0"  # Texto principal
  on_surface_variant: "#9898B8"  # Texto secundario / labels

  outline:         "#3A3A5C"     # Bordes de cards
  outline_variant: "#2A2A42"     # Bordes sutiles

  # Semántica de calidad (NO decorativa)
  quality_excellent: "#4CAF50"   # Score >= 90%
  quality_good:      "#FF9800"   # Score 70–89%
  quality_poor:      "#F44336"   # Score < 70%
  quality_na:        "#607D8B"   # Sin datos

## Typography (Roboto — Google Fonts)
fonts:
  display:  { family: "Roboto", size: 36, weight: 700, tracking: -0.5 }
  headline: { family: "Roboto", size: 24, weight: 600, tracking: 0    }
  title:    { family: "Roboto", size: 18, weight: 500, tracking: 0.15 }
  body:     { family: "Roboto", size: 14, weight: 400, tracking: 0.25 }
  label:    { family: "Roboto", size: 11, weight: 400, tracking: 0.5  }
  mono:     { family: "Roboto Mono", size: 12, weight: 400            }

## Spacing Scale (8px base grid — Google Material)
spacing:
  xs:   4px
  sm:   8px
  md:  16px
  lg:  24px
  xl:  32px
  xxl: 48px
  xxxl: 64px

## Shape (Border Radius)
shape:
  xs:   4px    # Badges, chips
  sm:   8px    # Botones, inputs
  md:  12px    # Cards normales
  lg:  16px    # Cards destacadas, KPIs
  xl:  24px    # Modales, drawers
  pill: 50px   # Tags de categoría

## Elevation (Tonal Surface — sin box-shadow)
elevation:
  0: surface_0   # Fondo de página
  1: surface_1   # Cards base
  2: surface_2   # Cards interactivas
  3: surface_3   # Tooltips, overlays

## Components
kpi_card:
  background: surface_2
  border_top_accent: 3px solid <quality_color_by_score>
  border_radius: lg
  padding: "24px 20px 18px"
  value_font: display
  label_font: label
  progress_bar_height: 4px
  progress_bar_radius: xs

data_table:
  header_bg: surface_2
  row_bg_odd: surface_1
  row_bg_even: surface_0
  border: "0.5px solid outline"
  cell_padding: "10px 14px"
  score_column_width: 100px
  sortable: true
  sticky_header: true

heatmap:
  colorscale: "RdYlGn"
  text_in_cell: true
  cell_font: label
  category_axis_width: 180px
  dimension_axis_height: 48px

sidebar:
  width: 240px
  background: surface_1
  border_right: "1px solid outline"
  nav_item_height: 44px
  nav_item_radius: sm
  nav_active_bg: primary_container

alert_banner:
  background: "rgba(244, 67, 54, 0.10)"
  border_left: "4px solid quality_poor"
  border_radius: "0 md md 0"
  padding: "16px 20px"

## Screens
screens:
  - id: "screen_resumen"
    route: "/"
    title: "Resumen del Portal"
  - id: "screen_categorias"
    route: "/categorias"
    title: "Por Categoría"
  - id: "screen_datasets"
    route: "/datasets"
    title: "Explorador de Datasets"
  - id: "screen_alertas"
    route: "/alertas"
    title: "Alertas Críticas"
  - id: "screen_evolucion"
    route: "/evolucion"
    title: "Evolución Histórica"
