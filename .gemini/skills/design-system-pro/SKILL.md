---
name: design-system-pro
description: Professional Design System agent for NL 2026 Data Governance Dashboard (Filosofía Claude/Anthropic). Enforces Midnight/Teal/Gold/Rose palette, typographic hierarchy (Playfair Display + DM Sans + DM Mono), semantic opacities, and component patterns replacing inline CSS.
---

# 📐 Documentación de Agentes para Estandarización de Diseño Web
## Guía Completa del Sistema de Diseño — Filosofía Claude/Anthropic

## 1. FILOSOFÍA DE DISEÑO
- "El diseño más sofisticado es el que no se nota". 
- Todo el código debe ser HTML5 abstracto con clases semánticas mapeadas al `global_css.py`.
- **PROHIBIDO**: el uso de variables "inline" largas (`style="font-family: 'DM Sans', sans-serif; color: var(--muted);"`). Utiliza las clases correctas, por ejemplo: `class="section-subtitle"`.

## 2. ARQUITECTURA DEL SISTEMA
- **CSS**: Vanilla CSS3 vía inyección en Streamlit (`styles/global_css.py`)
- **Fuentes**: Google Fonts CDN
- **Íconos**: Material Symbols Outlined (CDN)
- **Frameworks**: NO Bootstrap, NO Tailwind.

## 3. DESIGN TOKENS (Paleta Semántica)
### Midnight, Teal, Gold, Rose
Asegurar el cumplimiento estricto del mapeo semántico:
- `--teal` / `--teal-light`: Positivo (Excelente), Datos afirmativos, >90%
- `--gold` / `--gold-light`: Advertencia baja, Identificadores estructurales, Bueno (70-89%)
- `--rose` / `--rose-light`: Alertas, Crítico, Negativo, <70%

### Chromatic Rule
> **NUNCA mezclar los 3 acentos semánticos (teal, gold, rose) en el mismo componente visual a menos que sea una barra de distribución compartida.** Utiliza máximo 1 acento.

## 4. SISTEMA TIPOGRÁFICO
Siempre usa clases en vez de inline styles.
- **`.eyebrow`**: `DM Mono`, uppercase, gold, para identificadores de nivel alto.
- **`.section-title`**: `Playfair Display`, títulos jerarquía H1 y H2. Textos elegantes.
- **`.section-subtitle`**: `DM Sans`, subtítulos e introducción.
- **`.kpi-value`**: `Playfair Display`, números robustos.
- **`.kpi-label`**: `DM Mono` o `DM Sans` bold/uppercase.
- Resto de textos genéricos: `DM Sans` regular.

## 5. REGLAS PARA HTML INJECTADO
Cuando se utilicen bloques `st.markdown(unsafe_allow_html=True)`:
1. **Evitar inline padding y margin cuando sea posible**. Crea abstracciones genéricas en `.card`, `.bento`, etc.
2. Inyectar `html.escape()` donde haya input interactivo.
3. El hover `transition: transform 0.2s ease, border-color 0.2s ease;` siempre debe ir a través de las clases `.stitch-card` o `.kpi-card`.

## 6. CALIDAD GARANTIZADA CERO INLINE CSS
Es tarea obligatoria migrar todos los strings del proyecto bajo `sections/` que tengan grandes `style="..."` hacia sus equivalentes semánticos.l design specification |
