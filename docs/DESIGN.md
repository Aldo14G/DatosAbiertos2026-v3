---
name: Gobernanza de Datos — Nuevo León 2026
description: Auditoría continua de calidad de datos abiertos del gobierno de Nuevo León, impulsada por ISO/IEC 25012.
colors:
  midnight: "#0f1c2e"
  navy: "#1a2d45"
  cream: "#faf6ee"
  teal: "#3aa895"
  teal-light: "#4bcbb4"
  teal-dim: "#0d2e29"
  gold: "#d4a24c"
  gold-light: "#eec87d"
  gold-dim: "#2e2410"
  rose: "#c66b7d"
  rose-light: "#e08fa3"
  rose-dim: "#2e1218"
  muted: "#9ba9b4"
  surface: "#1a2d45"
  surface-alt: "#152538"
  card-bg: "#0f1c2efa"
typography:
  display:
    fontFamily: "Chronicle Display, Georgia, serif"
    fontSize: "clamp(2.25rem, 5vw, 3.5rem)"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.03em"
  headline:
    fontFamily: "Chronicle Display, Georgia, serif"
    fontSize: "clamp(1.75rem, 3vw, 2.25rem)"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Chronicle Display, Georgia, serif"
    fontSize: "1.75rem"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "-0.01em"
  body:
    fontFamily: "IBM Plex Sans, system-ui, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "DM Mono, monospace"
    fontSize: "0.6875rem"
    fontWeight: 500
    letterSpacing: "0.1em"
rounded:
  xs: "8px"
  sm: "12px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  full: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  xxl: "48px"
  section: "3.5rem"
components:
  btn-primary:
    backgroundColor: "{colors.teal}"
    textColor: "#ffffff"
    rounded: "{rounded.full}"
    padding: "14px 28px"
  btn-primary-hover:
    backgroundColor: "{colors.teal-light}"
    textColor: "#ffffff"
    rounded: "{rounded.full}"
    padding: "14px 28px"
  btn-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.cream}"
    rounded: "{rounded.full}"
    padding: "14px 28px"
  btn-ghost-hover:
    backgroundColor: "{colors.gold-dim}"
    textColor: "{colors.gold-light}"
    rounded: "{rounded.full}"
    padding: "14px 28px"
  stat-card:
    backgroundColor: "{colors.card-bg}"
    textColor: "{colors.cream}"
    rounded: "{rounded.sm}"
    padding: "2rem"
  stat-card-focus:
    backgroundColor: "{colors.card-bg}"
    textColor: "{colors.cream}"
    rounded: "{rounded.sm}"
    padding: "calc(2rem - 2px) 2rem 2rem"
  badge:
    backgroundColor: "{colors.teal-dim}"
    textColor: "{colors.teal-light}"
    rounded: "{rounded.full}"
    padding: "4px 12px"
  alert-card:
    backgroundColor: "{colors.rose-dim}"
    textColor: "{colors.rose-light}"
    rounded: "{rounded.sm}"
    padding: "1.5rem"
  nav:
    backgroundColor: "#0f1c2eeb"
    textColor: "{colors.muted}"
    height: "64px"
    padding: "0 20px"
---

# Design System: Gobernanza de Datos — Nuevo León 2026

## 1. Overview

**Creative North Star: "La Sala de Control"**

Este sistema visual existe para hacer inteligibles los datos públicos de Nuevo León: transformar métricas ISO en juicio ciudadano. No es un dashboard corporativo ni un portal de gobierno genérico. Es el lugar donde un periodista de datos, un CIO municipal o un investigador de políticas llega a entender la salud del ecosistema de datos abiertos del estado, sin que el diseño se interponga entre ellos y los hallazgos.

La densidad está al servicio de la claridad. La oscuridad del tema no es estética, es funcional: reduce el ruido visual para que los datos en teal, gold y rose dominen la lectura. Chronicle Display ancla los números con autoridad editorial; IBM Plex Sans entrega el cuerpo con precisión técnica sin frialdad; DM Mono marca los labels y contadores con la cadencia de un instrumento de medición. Juntos forman un sistema tipográfico que habla con la voz de un expediente oficial, no de un producto SaaS.

El sistema es bilingüe por diseño. Ninguna jerarquía visual favorece el español sobre el inglés ni viceversa: mismos pesos, mismos tamaños, mismo espacio.

**Key Characteristics:**
- Tema oscuro por defecto; tema claro como alternativa real, no como modo accesorio
- Tipografía de tres familias con roles estrictamente definidos: display serif, body sans, datos mono
- Paleta comprometida: teal como confianza institucional, gold como excelencia, rose como diagnóstico
- Elevación híbrida: capas tonales en reposo, sombras suaves solo en estado interactivo
- Máximo 1200px de ancho de contenido; respira, no llena la pantalla
- Bilingual parity: no hay contenido oculto en ningún idioma

## 2. Colors: La Paleta del Expediente

Una paleta de cuatro roles semánticos sobre una base de profundidad tonal. Cada color tiene una función, no una decoración.

### Primary
- **Tinta de Archivo** (`#0f1c2e`): El fondo de toda la aplicación en tema oscuro. Azul noche regiomontana; suficientemente oscuro para ocultar el chrome de Streamlit, lo suficientemente tintado para no ser negro. Nunca texto.
- **Capa Elevada** (`#1a2d45`): Superficies elevadas, nav bar en reposo, cards de segundo nivel. Separa contenido del fondo sin sombras.

### Secondary
- **Verde Datos** (`#3aa895`, light: `#4bcbb4`): El color de confianza institucional y resultados positivos. Botones primarios, indicadores ISO Excellent (≥90%), líneas de gráficos principales, badges activos. Presencia media: 20–35% de la superficie.
- **Oro de Calidad** (`#d4a24c`, light: `#eec87d`): Distinción, estructura, excelencia. Indicadores ISO Good (70–89%), eyebrows de sección, bordes activos en hover de elementos ghost, el top-accent de `.nl-stat-card--focus`. Presencia contenida: 10–20%.

### Tertiary
- **Señal Crítica** (`#c66b7d`, light: `#e08fa3`): Diagnóstico sin alarma. Indicadores ISO Poor (<70%), alertas de datasets con problemas, score bajo en tarjetas de alerta. No es rojo; no es urgencia, es diagnóstico. Presencia mínima: ≤10%.

### Neutral
- **Crema Editorial** (`#faf6ee`): Texto primario de títulos y valores numéricos en tema oscuro. No es blanco puro; el tinte cálido reduce la fatiga visual en sesiones largas.
- **Niebla de Datos** (`#9ba9b4`): Texto secundario, labels, metadatos, contadores de soporte. El color que dice "contexto, no protagonismo".
- **Card Glass** (`rgba(255,255,255,0.03)`): Fondo de cards en tema oscuro. Transparencia ínfima que separa la card del fondo sin levantar una capa opaca.

### Quality Tiers (ISO/IEC 25012)

| Tier | Umbral | Token | Hex |
|------|--------|-------|-----|
| Excellent | Score ≥ 90% | `--teal` | `#3aa895` |
| Good | Score 70–89% | `--gold` | `#d4a24c` |
| Poor | Score < 70% | `--rose` | `#c66b7d` |

**La Regla de la Rareza.** Rose (`--rose`) aparece solo cuando hay algo que diagnosticar. Su rarity es la señal. Si el 40% de la pantalla es rose, se normaliza y pierde el significado. Mantenlo por debajo del 10% de superficie visible en cualquier pantalla.

**La Regla del Tintado.** Ningún neutro es puro. Midnight tiene tinte azul, cream tiene tinte cálido, muted tiene tinte frío. Nunca `#000000` ni `#ffffff` solos en ningún elemento.

## 3. Typography: El Instrumento de Lectura

**Display Font:** Chronicle Display (con Georgia, serif como fallback)
**Body Font:** IBM Plex Sans (con system-ui, sans-serif como fallback)
**Label/Data Font:** DM Mono (con monospace como fallback)
**Navigation Font:** DM Sans (con sans-serif como fallback)

**Character:** Chronicle Display trae autoridad editorial sin rigidez académica; sus curvas inclinadas dan a los titulares y números grandes un peso que no consigue ninguna sans. IBM Plex Sans es el par perfecto: técnico sin ser frío, claro sin ser genérico. DM Mono impone la cadencia de un instrumento de medición a cada label, eyebrow y contador.

### Hierarchy

- **Display** (700, `clamp(2.25rem, 5vw, 3.5rem)`, lh 1.1, ls -0.03em): Hero titulares, stat-numbers grandes. Solo Chronicle Display. Solo cuando el número o título es el protagonista absoluto de la pantalla.
- **Headline** (700, `clamp(1.75rem, 3vw, 2.25rem)`, lh 1.3, ls -0.02em): Títulos de sección (`<h1>`). Chronicle Display.
- **Title** (700, `1.75rem → 1.375rem tablet → 1.125rem mobile`, lh 1.3): Sub-secciones (`<h2>`, `<h3>`). Chronicle Display.
- **Body** (400, `16px → 14px mobile`, lh 1.6): Todo el texto de párrafo. IBM Plex Sans. Línea máxima: 65ch. Nunca más de 75ch.
- **Label** (500, `0.6875rem`, ls 0.1em, uppercase): Eyebrows, badges, encabezados de tabla, contadores auxiliares. DM Mono siempre. Nunca serif en este rol.
- **Nav** (500, `13px`): Links de navegación. DM Sans. Peso medio, nunca bold en reposo.

**La Regla del Instrumento.** DM Mono es para datos, no para decoración. Si un texto mide, clasifica, fecha o etiqueta, va en mono. Si narra, explica o titula, no va en mono. Mezclar roles rompe la cadencia del instrumento.

**La Regla del Peso.** Chronicle Display solo en 700. No existe Chronicle Regular en este sistema: si no amerita bold, usa IBM Plex Sans en su lugar.

## 4. Elevation: Tonal Primero, Sombras Solo en Estado

Este sistema usa elevación tonal como base y sombras como respuesta de estado, nunca como decoración estática.

En reposo, la profundidad viene de capas de superficie: `midnight (#0f1c2e)` → `navy (#1a2d45)` → `surface-elevated (#243347)`. No hay sombras visibles en elementos estáticos; la separación entre layers es tonal.

Las sombras aparecen cuando un elemento responde a interacción, comunicando que algo se ha levantado o activado.

### Shadow Vocabulary

- **shadow-sm** (`0 2px 4px rgba(0,0,0,0.2)`): Cards en reposo con sutil separación del fondo. Raramente usado; el tonal suele bastar.
- **shadow-md** (`0 4px 12px rgba(0,0,0,0.3)`): Hover en cards estándar (`.stitch-card:hover`, `.nl-stat-card:hover`). Comunica elevación en respuesta a cursor.
- **shadow-lg** (`0 12px 24px rgba(0,0,0,0.4)`): Hover en alert cards. Señal de criticidad levantada.
- **shadow-xl** (`0 24px 48px rgba(0,0,0,0.5)`): Overlays, map central card, elementos flotantes de máxima jerarquía.
- **teal-glow** (`0 8px 28px rgba(42,122,111,0.28)`): Exclusivo del botón primario (`.stitch-btn-primary`). Halo de acción principal.

**La Regla del Reposo Plano.** Ningún elemento tiene sombra visible en su estado de reposo a menos que sea un overlay flotante. La sombra es la recompensa de la interacción.

## 5. Components

### Navigation (Top Bar)
Técnico y transparente: 64px altura, `backdrop-filter: blur(20px) saturate(200%)`. En mobile colapsa a hamburger con `<details>` nativo.
- **Reposo:** links en `--muted`, sin indicador activo
- **Hover:** `background: var(--overlay)`, color a `--cream`
- **Activo:** color `--teal-light` (400 weight → 600), background `rgba(42,122,111,0.12)`, pill completo (`border-radius: 9999px`)
- **Brand:** Chronicle Display 18px/700, con eyebrow DM Mono 0.6rem en gold

### Botones Principales
Pill completo (`border-radius: 9999px`), DM Sans 15px/700, transición `200ms ease-in-out`.
- **Primary:** `background: --teal`, texto blanco, `box-shadow: 0 8px 28px rgba(42,122,111,0.28)`. Hover: `translateY(-2px)` + `brightness(1.08)` + sombra amplificada.
- **Ghost:** `background: transparent`, `border: 1.5px solid --card-border`, texto cream. Hover: borde gold, texto gold-light, `translateY(-1px)`.

### Stat Card (`nl-stat-card`)
El componente central del sistema. Cards de datos cuantitativos con anatomía fija.
- **Shape:** `border-radius: 12px` (dark) / `10px` (light)
- **Background:** `var(--card-bg)` — transparencia que se funde con la superficie
- **Label:** DM Mono 0.6875rem uppercase, color `--muted`
- **Value:** Chronicle Display 2rem/700, color `--cream`
- **Meta:** IBM Plex Sans 0.8125rem, color `--muted`
- **Variante Focus:** `border-top: 3px solid var(--gold)` — la única instancia de top-stripe en el sistema, semánticamente reservada para el indicador principal de una sección
- **Hover:** `translateY(-2px)` + shadow-md + border-color a `--border`

### Alert Card
Para datasets con score ISO Poor. Diagnóstico, no alarma.
- **Background:** `var(--rose-dim)` — tint suave, no alarma roja
- **Border:** `1px solid rgba(184,92,110,0.2)`
- **Hover:** `translateY(-3px)` + shadow-lg compuesta, border a `rgba(184,92,110,0.4)`
- No usa border-left como stripe: la card entera es el contenedor semántico

### Badge / Eyebrow Label
DM Mono 0.65rem uppercase, `letter-spacing: 0.15em`. Pill completo.
- **Badge:** `background: --teal-dim`, `border: 1px solid --teal`, texto `--teal-light`. Para estado activo / categoría confirmada.
- **Eyebrow:** texto `--gold`, sin fondo ni borde. Para introducir secciones desde arriba.

### Heatmap
Células 40px altura, `border-radius: 4px`, texto blanco bold. Color de fondo según tier ISO.
- Hover: `scale(1.05)` + shadow-md. Interacción táctil sin animación de layout.

### Data Bar (`bar-track` / `bar-fill`)
Track 8px, `border-radius: 4px`. Fill animado con `transition: width 0.6s ease-out`.
- Teal: score positivo. Gold: score medio. Rose: score bajo.
- Nunca animar la propiedad `width` con spring o bounce.

### Quote Block
Chronicle Display italic 1.1rem para el texto, DM Mono 0.7rem uppercase para la fuente.
- Background `--gold-dim`, border `rgba(200,151,58,0.25)`, `border-radius: 8px`.

## 6. Do's and Don'ts

### Do:
- **Do** usar CSS custom properties (`var(--teal)`, `var(--gold)`) para todos los colores en HTML/CSS de Streamlit. Nunca hex hardcodeado fuera de `global_css.py`.
- **Do** reservar Chronicle Display exclusivamente en weight 700. Titulares, valores numéricos grandes, citas.
- **Do** usar DM Mono para todo lo que mida, clasifique, fecha o etiquete (labels, eyebrows, badges, contadores).
- **Do** usar IBM Plex Sans para texto narrativo, descripciones, subtítulos de sección.
- **Do** mantener body text dentro de 65ch máximo. El contenido de análisis no necesita líneas de 120 caracteres.
- **Do** seguir la jerarquía de elevación tonal antes de agregar sombras: midnight → navy → surface-elevated.
- **Do** agregar `aria-hidden="true"` a todos los iconos decorativos Material Symbols.
- **Do** agregar `role="progressbar"` + `aria-valuenow/min/max` a todas las data bars.
- **Do** aplicar `html.escape()` a cualquier string de usuario antes de `unsafe_allow_html=True`.
- **Do** dar a cada superficie de tema claro su valor exacto del mapa `_TOKENS_LIGHT` — no es el inverso del dark; tiene sus propios hex calibrados.

### Don't:
- **Don't** usar `st.metric()`, `st.success()`, `st.error()` ni ningun primitivo nativo de Streamlit para UI nueva. Todo el UI pasa por `st.markdown(unsafe_allow_html=True)` con clases del design system.
- **Don't** usar clichés de dashboards SaaS: bloques hero con métricas gigantes sobre gradientes, accent stripes de color en tarjetas, cards idénticas en grilla infinita. Si parece un dashboard de 2019, rediseña.
- **Don't** usar `border-left` mayor a 1px como stripe de color decorativo en cards o alertas. Las alert cards usan tinting de fondo completo, no stripe lateral.
- **Don't** usar `background-clip: text` con gradiente para texto decorativo. Énfasis via peso o tamaño.
- **Don't** hardcodear hex fuera de `global_css.py`. Todo pasa por tokens.
- **Don't** crear urgencia falsa ni lenguaje de alarma. El sistema diagnostica; no amenaza. Rose es señal, no sirena.
- **Don't** usar emojis en ningún elemento de UI ni en el código fuente.
- **Don't** ignorar el tema claro. No es modo accesorio: tiene su propio mapa de tokens y debe verse calibrado, no como una inversión automática.
- **Don't** usar Playfair Display ni DM Sans como fuentes display. Las fuentes del sistema son Chronicle Display + IBM Plex Sans + DM Mono + DM Sans (nav). Cualquier referencia a Playfair en código o docs es un artefacto de una versión anterior.
- **Don't** agregar sombras a elementos en reposo estático salvo overlays flotantes. La sombra es respuesta de estado, no decoración.
- **Don't** omitir `html.escape()` en strings que provienen de la API CKAN o de input del usuario antes de renderizarlos con `unsafe_allow_html=True`.
