# UX · Heurísticas de Nielsen (10 × Dashboard NL 2026)

**Escala de severidad:** 0 (sin problema) · 1 (cosmético) · 2 (menor) · 3 (mayor) · 4 (catastrófico)

## Resumen ejecutivo

| # | Heurística | Max severidad | Bloquea Fase 2 |
|---|---|---|---|
| H1 | Visibilidad del estado del sistema | **3** | Sí |
| H2 | Match con mundo real | 2 | No |
| H3 | Control y libertad del usuario | 2 | No |
| H4 | Consistencia y estándares | 2 | No |
| H5 | Prevención de errores | 2 | No |
| H6 | Reconocer vs recordar | 1 | No |
| H7 | Flexibilidad y eficiencia | 1 | No |
| H8 | Estético y minimalista | 2 | No |
| H9 | Diagnóstico y recuperación de errores | **3** | Sí |
| H10 | Ayuda y documentación | **3** | Sí |

---

## H1 · Visibilidad del estado del sistema — Severidad 3

**Hallazgos:**
- `st.spinner("Cargando datos de calidad…")` en [dashboard_v3.py:44](../../../dashboard_v3.py#L44) es el único indicador de carga global. No hay feedback durante filtrado de tabla ni durante re-render al cambiar tema.
- Skeleton loaders `.skeleton-card`, `.skeleton-kpi` existen en [styles/global_css.py:1084](../../../styles/global_css.py#L1084) pero **no se consumen** en ninguna sección.
- `st.spinner("")` vacío en [sections/inicio.py:406](../../../sections/inicio.py#L406) — sin mensaje visible.
- Ejecución del pipeline agentic usa `st.status` correctamente en [sections/calidad_pro.py:44](../../../sections/calidad_pro.py#L44).
- Sin indicador de staleness del CSV cacheado (TTL 300s silencioso).

**Recomendación Fase 2:** Reemplazar `st.spinner` por componente skeleton durante primera carga + agregar timestamp "Actualizado hace X min" en status bar.

---

## H2 · Match con el mundo real — Severidad 2

**Hallazgos:**
- Terminología técnica ISO 25012 ("Completitud", "Exactitud", "Consistencia", "Unicidad", "Puntualidad", "Documentación", "Apertura") bien mapeada en [data_layer.py:43-52](../../../data_layer.py#L43-L52) — OK.
- "Gobernanza Óptima" / "Requiere Atención" / "Crítico" son claros ([sections/inicio.py:101-106](../../../sections/inicio.py#L101-L106)).
- **Jerga no glosada:** "Pipeline Agentic", "Evaluador ISO", "DAMA-DMBOK 2.0" en [calidad_pro.py:111-113](../../../sections/calidad_pro.py#L111-L113) — ciudadano no técnico no entiende.
- Expander "Metodología Técnica" existe ([calidad_pro.py:105](../../../sections/calidad_pro.py#L105)) pero está cerrado por defecto.

**Recomendación Fase 2:** Glosario tooltip en cada dimensión + abrir expander metodología por defecto en primera visita.

---

## H3 · Control y libertad del usuario — Severidad 2

**Hallazgos:**
- Navegación por query-param `?section=` es reversible (browser back funciona) — OK.
- Toggle tema dark/light en sidebar [dashboard_v3.py:143-145](../../../dashboard_v3.py#L143-L145) funciona.
- **Filtros no resetables:** [sections/datasets.py:278-292](../../../sections/datasets.py#L278-L292) no tiene botón "Limpiar filtros".
- No hay breadcrumb / "Back to results" después de click en alerta.
- `st.download_button` permite exportar sin confirmación — OK (acción no destructiva).

---

## H4 · Consistencia y estándares — Severidad 2

**Hallazgos:**
- Design tokens centralizados en [styles/global_css.py:68-150](../../../styles/global_css.py#L68-L150) (`_TOKENS_DARK`, `_TOKENS_LIGHT`).
- **Inconsistencia:** inline styles residuales masivos en [sections/organizaciones.py:136-144](../../../sections/organizaciones.py#L136-L144), [sections/organizaciones.py:332-338](../../../sections/organizaciones.py#L332-L338) — violan la regla design-system-pro "zero inline CSS".
- `_render_alerta_card()` en [sections/datasets.py:136-162](../../../sections/datasets.py#L136-L162) mezcla clases + inline — ambigüedad.
- Iconografía: Material Symbols Outlined consistente en todo el dashboard — OK.
- Fuentes: Playfair Display / DM Sans / DM Mono aplicadas según DESIGN.md — OK.

**Recomendación Fase 2:** Migrar inline styles en `organizaciones.py` a clases `.org-kpi-card`, `.org-row`, `.org-rank-item`.

---

## H5 · Prevención de errores — Severidad 2

**Hallazgos:**
- Path traversal bloqueado en [data_layer.py:643-646](../../../data_layer.py#L643-L646) — OK.
- SSRF bloqueado con allowlist en [data_layer.py:138-154](../../../data_layer.py#L138-L154) — OK.
- `html.escape()` aplicado en [sections/organizaciones.py](../../../sections/organizaciones.py) y [sections/datasets.py](../../../sections/datasets.py) — OK.
- **Riesgo:** `st.text_input` "Buscar" en [datasets.py:290](../../../sections/datasets.py#L290) sin sanitización antes de `str.contains(regex=False)` — OK por `regex=False` implícito pero no explícito.
- Sin confirmación ante descarga de CSV grande — aceptable.

---

## H6 · Reconocer vs recordar — Severidad 1

**Hallazgos:**
- Labels en selectbox/slider visibles — OK.
- **Placeholder oculta label:** "Buscar" usa `label_visibility="collapsed"` [datasets.py:291](../../../sections/datasets.py#L291) — placeholder "Nombre del dataset…" compensa.
- Iconos en nav acompañan texto — OK ([dashboard_v3.py:151-153](../../../dashboard_v3.py#L151-L153)).

---

## H7 · Flexibilidad y eficiencia — Severidad 1

**Hallazgos:**
- Deep linking `?section=` permite bookmarks — OK.
- **Sin shortcuts de teclado** documentados.
- Exportación CSV/JSON disponible en ambos tabs — OK.
- No hay vista "densa" vs "cómoda" en tabla.

---

## H8 · Estético y minimalista — Severidad 2

**Hallazgos:**
- Hero con ring gauge limpio ([inicio.py:108-139](../../../sections/inicio.py#L108-L139)) — OK.
- **Ruido visual:** Sidebar muestra simultáneamente 3 KPIs + badge de alertas + botón tema + título — denso ([dashboard_v3.py:91-145](../../../dashboard_v3.py#L91-L145)).
- Footer con 5 links + 3 separators — OK pero repetitivo (solo "Portal" es real, los demás son `href="#"`) ([dashboard_v3.py:252-256](../../../dashboard_v3.py#L252-L256)).
- Mapa visual en organizaciones con 10 overlays + 3 pills + 1 score badge + 1 glass card + 3 chips leyenda = **denso** ([organizaciones.py:494-562](../../../sections/organizaciones.py#L494-L562)).

---

## H9 · Diagnóstico y recuperación de errores — Severidad 3

**Hallazgos:**
- `st.error` + `st.stop()` si falta CSV ([dashboard_v3.py:46-52](../../../dashboard_v3.py#L46-L52)) — mensaje técnico, menciona paths internos (OK para dev, crudo para usuario final).
- `download_csv` silencia excepciones con `pass` ([data_layer.py:176-177](../../../data_layer.py#L176-L177)) — dificulta debugging.
- **Try/except muy amplio:** [calidad_pro.py:45-52](../../../sections/calidad_pro.py#L45-L52) captura `Exception` genérico sin clasificar.
- **Sin logging estructurado:** El proyecto usa `print()` en [data_layer.py:159](../../../data_layer.py#L159), no `logging`.
- Advertencia al dataset vacío ([dashboard_v3.py:54-56](../../../dashboard_v3.py#L54-L56)) — OK.

**Recomendación Fase 2:** Introducir módulo `observability.py` con `logging.getLogger()`, correlación de `run_id`, y taxonomía de errores.

---

## H10 · Ayuda y documentación — Severidad 3

**Hallazgos:**
- `DESIGN.md` existe y canoniza el sistema de diseño — OK para devs.
- **Ningún tooltip** sobre KPIs, dimensiones ISO, umbrales de tier en la UI.
- Expander "Metodología Técnica" [calidad_pro.py:105](../../../sections/calidad_pro.py#L105) — único punto de explicación.
- Footer link "Accesibilidad" = `href="#"` (placebo) ([dashboard_v3.py:256](../../../dashboard_v3.py#L256)).
- **No existe:** página /docs, página /about, página /methodology con referencia ISO 25012:2008.
- Ausencia de onboarding para primer acceso.

**Recomendación Fase 2:** (1) Página estática `sections/ayuda.py` con referencias normativas, (2) tooltips en cada KPI card usando `title="…"` + `aria-describedby`, (3) guided tour con `streamlit-tour` (ya disponible en PyPI).
