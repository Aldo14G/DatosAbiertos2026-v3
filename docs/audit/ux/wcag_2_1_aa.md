# WCAG 2.1 AA · Checklist de Accesibilidad

**Alcance:** HTML inyectado en `sections/*.py` + `dashboard_v3.py` + `styles/global_css.py`.
**Método:** Grep de atributos ARIA + inspección visual de contraste vía tokens.

## Resumen

| Criterio | Nivel | Estado | Bloquea Fase 2 |
|---|---|---|---|
| 1.1.1 Non-text Content | A | **Fail** | Sí |
| 1.3.1 Info and Relationships | A | Partial | No |
| 1.4.3 Contrast (Minimum) | AA | Partial | No |
| 1.4.4 Resize Text | AA | Pass | — |
| 1.4.11 Non-text Contrast | AA | Partial | No |
| 2.1.1 Keyboard | A | Partial | Sí |
| 2.3.3 Animation from Interactions | AAA (implementado) | Pass | — |
| 2.4.4 Link Purpose | A | Partial | No |
| 2.4.7 Focus Visible | AA | Pass | — |
| 3.3.2 Labels or Instructions | A | Pass | — |
| 4.1.2 Name, Role, Value | A | **Fail** | Sí |

---

## 1.1.1 · Non-text Content (A) — **FAIL**

**Requisito:** Toda imagen, icono informativo y gráfico debe tener texto alternativo.

**Hallazgos:**
- ✅ [sections/organizaciones.py:496](../../../sections/organizaciones.py#L496) — único `alt=` en todo el proyecto: `<img alt="Mapa de Nuevo León">`.
- ❌ **~80+ instancias** de `<span class="material-symbols-outlined">` sin `aria-hidden="true"` ni `aria-label`. Los lectores de pantalla leerán el ligature ("analytics", "shield", "warning", etc.).
- ❌ Plotly charts (`st.plotly_chart` en [calidad_pro.py:192,226](../../../sections/calidad_pro.py#L192), [organizaciones.py:232,295](../../../sections/organizaciones.py#L232)) sin `aria-label` ni descripción textual paralela.
- ❌ SVG ring gauge en [inicio.py:119-134](../../../sections/inicio.py#L119-L134) sin `<title>` ni `role="img"`.

**Fix Fase 2:**
```html
<!-- Iconos decorativos -->
<span class="material-symbols-outlined" aria-hidden="true">analytics</span>

<!-- SVG informativo -->
<svg role="img" aria-labelledby="score-title">
  <title id="score-title">Score global: 85 de 100</title>
  …
</svg>
```

---

## 1.3.1 · Info and Relationships (A) — PARTIAL

- ✅ [dashboard_v3.py:172,175,195](../../../dashboard_v3.py#L172) — `aria-label` en `<nav>` y topbar actions.
- ❌ Tabla HTML custom en [organizaciones.py:340-347](../../../sections/organizaciones.py#L340-L347) usa `<table><thead><tr><th>` pero sin `scope="col"` en headers ni `<caption>`.
- ❌ Bento grid en [global_css.py:1111](../../../styles/global_css.py#L1111) no expone `role="grid"` ni `aria-rowcount`.

---

## 1.4.3 · Contrast Minimum (AA) — PARTIAL

**Requisito:** 4.5:1 para texto normal, 3:1 para texto grande (≥18pt o ≥14pt bold).

**Hallazgos (estimados desde tokens):**
- ✅ Dark mode: `--cream #f0ebe0` sobre `--surface #1a2d45` ≈ 11.2:1 — OK.
- ✅ Dark mode: `--muted #8a9bb0` sobre `--surface` ≈ 4.9:1 — OK.
- ⚠ Light mode: `--muted #7a6d58` sobre `--surface-high #ffffff` ≈ 5.1:1 — OK para body, **borderline** para texto pequeño.
- ❌ **Glass overlays** sobre imagen de Unsplash en [organizaciones.py:475-479](../../../sections/organizaciones.py#L475-L479) usan `rgba(255,255,255,0.12)` con texto blanco — contraste variable según pixel de fondo, probablemente **< 4.5:1** en zonas claras del mapa.

**Fix Fase 2:** Reemplazar glass overlays sobre imagen por tarjetas opacas con blur del fondo solamente, o garantizar gradiente de legibilidad más intenso (actualmente `85% surface` ya existe pero no cubre toda la zona de texto).

---

## 1.4.11 · Non-text Contrast (AA) — PARTIAL

- Botones primarios `bg-primary` (teal `#2a7a6f`) sobre surface — OK.
- Focus rings `--focus-ring` definidos en tokens — aplicación inconsistente (no auditado exhaustivamente en todos los CSS blocks).
- Bordes `--card-border` sobre `--surface-alt` en dark mode: baja visibilidad (cumple 3:1 marginalmente).

---

## 2.1.1 · Keyboard (A) — PARTIAL

- ✅ `<a>` y `<nav>` navegables con Tab.
- ✅ `<details><summary>` mobile menu [dashboard_v3.py:189-209](../../../dashboard_v3.py#L189-L209) es keyboard-accesible por default.
- ❌ **Custom hover handlers:** `onmouseover`/`onmouseout` en [organizaciones.py:136](../../../sections/organizaciones.py#L136), [organizaciones.py:332](../../../sections/organizaciones.py#L332), [organizaciones.py:368](../../../sections/organizaciones.py#L368), [organizaciones.py:388](../../../sections/organizaciones.py#L388), [dashboard_v3.py:238](../../../dashboard_v3.py#L238) — no tienen equivalente `:focus`, romper keyboard-only experience.
- ❌ Overlays de mapa [organizaciones.py:456-481](../../../sections/organizaciones.py#L456-L481) con `cursor:pointer` pero sin `tabindex` ni handler de teclado.

**Fix Fase 2:** Reemplazar `onmouseover` por clase CSS `:hover, :focus` y añadir `tabindex="0"` + handler Enter/Space a overlays clicables.

---

## 2.3.3 · Animation from Interactions — PASS

- ✅ `@media (prefers-reduced-motion: reduce)` en [global_css.py:997+](../../../styles/global_css.py#L997) desactiva animaciones globales.

---

## 2.4.4 · Link Purpose (A) — PARTIAL

- ❌ Footer links `href="#"` en [dashboard_v3.py:253-256](../../../dashboard_v3.py#L253-L256) — destinos placebo ("Privacidad", "Términos", "Contacto", "Accesibilidad") confunden al usuario de screen reader.
- ✅ Exportar CSV/JSON tienen texto descriptivo.
- ⚠ "Ver en catalogodatos.nl.gob.mx →" [datasets.py:160](../../../sections/datasets.py#L160) — OK pero repetido N veces; agregar `aria-label` específico con nombre del dataset.

---

## 3.3.2 · Labels or Instructions (A) — PASS

- ✅ `st.selectbox("Categoría", …)`, `st.slider("Score mínimo", …)` en [datasets.py:283-288](../../../sections/datasets.py#L283-L288).
- ⚠ `st.text_input("Buscar", …, label_visibility="collapsed")` — label existe pero oculta visualmente; placeholder visible compensa.

---

## 4.1.2 · Name, Role, Value (A) — **FAIL**

**Requisito:** Cada widget custom debe exponer name + role + state accesible.

**Hallazgos:**
- ❌ "Cards" KPI en [inicio.py:35-41](../../../sections/inicio.py#L35-L41), [calidad_pro.py:130-154](../../../sections/calidad_pro.py#L130-L154) son `<div>` sin `role`.
- ❌ `.bar-track` / `.bar-fill` en [inicio.py:74-84](../../../sections/inicio.py#L74-L84) son visualmente progressbar pero sin `role="progressbar" aria-valuenow aria-valuemax`.
- ❌ Tabs custom en [organizaciones.py:340-347](../../../sections/organizaciones.py#L340-L347) — aquí Streamlit maneja la accesibilidad nativamente en `st.tabs()` ✅, pero la tabla HTML hecha a mano carece de ARIA.
- ❌ `<details>` mobile menu ([dashboard_v3.py:189](../../../dashboard_v3.py#L189)) carece de `aria-controls` para identificar el panel.

**Fix Fase 2:**
```html
<div role="progressbar" aria-valuenow="85" aria-valuemin="0" aria-valuemax="100"
     aria-label="Completitud: 85 por ciento">
  <div class="bar-fill" style="width:85%"></div>
</div>
```

---

## Recomendaciones priorizadas

1. **Crítico (bloquea Fase 2):** Añadir `aria-hidden="true"` a los ~80 iconos decorativos y `aria-label` a los interactivos.
2. **Alto:** Sustituir `onmouseover`/`onmouseout` por clases `:hover, :focus`.
3. **Alto:** `role="progressbar"` + `aria-valuenow` en todos los `.bar-fill` de dimensiones ISO.
4. **Medio:** Eliminar links placebo del footer o apuntarlos a `/ayuda#privacidad` etc.
5. **Medio:** `<title>` + `role="img"` en SVG ring gauges.
6. **Medio:** Glass overlays sobre imagen → tarjetas con fondo opaco.

## Herramientas recomendadas (Fase 2)

- `axe-devtools` en Chrome — auditoría automática.
- `pa11y-ci` en CI — gate de accesibilidad.
- Lighthouse — score de accesibilidad en cada PR.
