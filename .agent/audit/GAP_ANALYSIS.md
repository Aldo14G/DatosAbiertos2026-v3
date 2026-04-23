# GAP Analysis — Consolidado Fase 1

**Generado:** 2026-04-15 · **Pipeline bajo audit:** V2.1 · **Fuentes:** [ux/](ux/), [data/](data/), [governance/](governance/).

**Metodología:** cada hallazgo documentado en su reporte-fuente fue elevado aquí con severidad, esfuerzo y flag "Bloquea Fase 2". El objetivo de esta tabla es orientar la planificación de Fase 2 (infraestructura analítica) eliminando primero los bloqueadores.

---

## Leyenda

- **Severidad** — Crítica · Alta · Media · Baja
  - **Crítica**: riesgo de regresión o violación de compromiso público (accesibilidad, datos incorrectos).
  - **Alta**: introduce deuda que va a doler en Fase 2.
  - **Media**: mejora de calidad, no bloquea.
  - **Baja**: pulimento.
- **Esfuerzo** — S (1-2 días) · M (3-5 días) · L (1-2 semanas).
- **Bloquea Fase 2?** — Sí si NO resolverlo compromete la infraestructura analítica siguiente.

---

## Tabla consolidada

| ID | Categoría | Hallazgo | Evidencia | Severidad | Esfuerzo | Bloquea Fase 2? |
|---|---|---|---|---|---|---|
| **UX-01** | Accesibilidad | ~80 iconos `material-symbols-outlined` sin `aria-hidden="true"` ni `aria-label` — screen readers leen ligatures crudos | [wcag_2_1_aa.md § 1.1.1](ux/wcag_2_1_aa.md) | **Crítica** | S | **Sí** |
| **UX-02** | Accesibilidad | `.bar-track`/`.bar-fill` (dimensiones ISO) sin `role="progressbar"` ni `aria-valuenow` | [wcag_2_1_aa.md § 4.1.2](ux/wcag_2_1_aa.md), [inicio.py:74-84](../../sections/inicio.py#L74-L84) | **Crítica** | S | **Sí** |
| **UX-03** | Accesibilidad | Plotly charts sin `aria-label` ni texto alternativo | [wcag_2_1_aa.md § 1.1.1](ux/wcag_2_1_aa.md), [calidad_pro.py:192,226](../../sections/calidad_pro.py) | Alta | M | No |
| **UX-04** | Accesibilidad | `onmouseover`/`onmouseout` sin equivalente `:focus` → rompe keyboard-only | [wcag_2_1_aa.md § 2.1.1](ux/wcag_2_1_aa.md), 5 instancias en organizaciones.py + dashboard_v3.py | Alta | S | No |
| **UX-05** | Design system | 120 violaciones inline `style="..."` ≥30 chars — regla design-system-pro | [component_inventory.md § Inline CSS residual](ux/component_inventory.md) | Alta | M | **Sí** (dificulta Fase 2 theming) |
| **UX-06** | Design system | 7 bloques CSS huérfanos (`skeleton`, `bento-grid`, `heatmap-cell`, `stat-card`, `quote-block`, `comparison-table`, `gauge-container`, `pagination`) | [component_inventory.md § Huérfanos](ux/component_inventory.md) | Media | S | No |
| **UX-07** | UX heurística | Skeletons definidos pero NO consumidos → `load_data()` sin feedback de progreso | [heuristic_nielsen.md H1 · sev 3](ux/heuristic_nielsen.md), [global_css.py:1084-1110](../../styles/global_css.py#L1084-L1110) | Alta | S | No |
| **UX-08** | UX heurística | Zero tooltips / ayuda contextual (terminología ISO 25012 cruda frente a usuarios ciudadanos) | [heuristic_nielsen.md H10 · sev 3](ux/heuristic_nielsen.md) | Alta | M | No |
| **UX-09** | UX heurística | Manejo de errores: `print()` no `logging`; try/except amplios en [data_layer.py:26-31](../../data_layer.py#L26-L31); no hay "recovery actions" UI | [heuristic_nielsen.md H9 · sev 3](ux/heuristic_nielsen.md) | Alta | M | No |
| **UX-10** | UX heurística | Footer links `href="#"` → placebos que confunden a screen readers | [wcag_2_1_aa.md § 2.4.4](ux/wcag_2_1_aa.md), [dashboard_v3.py:253-256](../../dashboard_v3.py#L253-L256) | Media | S | No |
| **UX-11** | Accesibilidad | SVG ring gauge sin `<title>` ni `role="img"` | [wcag_2_1_aa.md § 1.1.1](ux/wcag_2_1_aa.md), [inicio.py:119-134](../../sections/inicio.py#L119-L134) | Media | S | No |
| **UX-12** | Accesibilidad | Glass overlays sobre imagen Unsplash → contraste variable <4.5:1 en zonas claras | [wcag_2_1_aa.md § 1.4.3](ux/wcag_2_1_aa.md), [organizaciones.py:475-479](../../sections/organizaciones.py#L475-L479) | Media | M | No |
| **DATA-01** | Pipeline | 3 de 5 dimensiones del pipeline avanzado tienen **varianza cero** (accuracy/conformidad=93.3, consistency/comprensibilidad=100, documentation/trazabilidad=100) — posible default artificial | [scoring_sensitivity.md § Conclusiones B](data/scoring_sensitivity.md) | **Crítica** | M | **Sí** (falsifica KPIs públicos) |
| **DATA-02** | Pipeline | Pipeline v1 ISO 25012 produce n=1 dataset en CSV/JSON → imposibilita análisis de sensibilidad real de los 7 pesos | [scoring_sensitivity.md § Blocker](data/scoring_sensitivity.md), [resultados_calidad_datos_nl.csv](../../resultados_calidad_datos_nl.csv) | **Crítica** | M | **Sí** |
| **DATA-03** | Pipeline | Completitud trata todas las columnas como equivalentes (NULL en `fecha_evento` == NULL en `comentarios_opcionales`) | [pipeline_audit.md § 1](data/pipeline_audit.md), [data_layer.py:207-220](../../data_layer.py#L207-L220) | Alta | M | No |
| **DATA-04** | Pipeline | Exactitud: heurística sin ground-truth, umbrales fijos no calibrados, constantes legítimas penalizadas | [pipeline_audit.md § 2](data/pipeline_audit.md) | Alta | L | No |
| **DATA-05** | Pipeline | Unicidad: `df.duplicated()` match exacto — no usa natural keys | [pipeline_audit.md § 4](data/pipeline_audit.md) | Media | S | No |
| **DATA-06** | Pipeline | Puntualidad depende de `metadata_modified` CKAN (puede reflejar edición de metadata, no de datos) y excluye dim si `NaN` | [pipeline_audit.md § 5](data/pipeline_audit.md) | Media | M | No |
| **DATA-07** | Pipeline | Apertura: CSV de 0 bytes puntúa 40 (no valida parseabilidad) | [pipeline_audit.md § 7](data/pipeline_audit.md) | Baja | S | No |
| **DATA-08** | Contratos | Pydantic v2 disponible pero sin schemas formales — `_validate_schema` es manual con `_REQUIRED_COLS` | [data_contracts_gap.md](data/data_contracts_gap.md), [data_layer.py:66-71](../../data_layer.py#L66-L71) | Alta | M | **Sí** (Fase 2 depende de contratos) |
| **DATA-09** | Contratos | No existe `DiccionarioDato` por dataset → Great Expectations sin expectations explícitas | [data_contracts_gap.md § 5](data/data_contracts_gap.md) | Alta | L | No (Fase 2 lo construye) |
| **DATA-10** | Observabilidad | [data_layer.py:159](../../data_layer.py#L159) usa `print()` no `logging` | [pipeline_audit.md § Issues transversales](data/pipeline_audit.md) | Media | S | No |
| **DATA-11** | Reproducibilidad | `fetch_portal_catalog` usa `@lru_cache(maxsize=1)` — cache de proceso, no reproducible entre runs | [pipeline_audit.md § Reproducibilidad](data/pipeline_audit.md) | Media | S | No |
| **DATA-12** | Reproducibilidad | No se archiva la versión de datos (CSV) que generó cada reporte | [pipeline_audit.md § Reproducibilidad](data/pipeline_audit.md) | Media | M | No |
| **GOV-01** | Docs | **`CONTRIBUTING.md` no existe** — convenciones dispersas | [docs_gap.md § 1](governance/docs_gap.md) | Alta | S | **Sí** |
| **GOV-02** | Docs | **`LICENSE` no existe** — código efectivamente "all rights reserved" | [docs_gap.md § 7](governance/docs_gap.md) | Alta | S | No (sí para publicación) |
| **GOV-03** | Docs | `docs/methodology.md` no existe → pesos ISO sin justificación publicable | [docs_gap.md § 8](governance/docs_gap.md) | Alta | M | No (sí para paper Fase 4) |
| **GOV-04** | Docs | `CHANGELOG.md` no existe (solo snapshot `MIGRATION_2026.md`) | [docs_gap.md § 2](governance/docs_gap.md) | Media | S | No |
| **GOV-05** | Docs | No hay ADRs — decisiones fundacionales (Streamlit, ISO 25012, pesos) no registradas | [docs_gap.md § 3](governance/docs_gap.md) | Media | M | No |
| **GOV-06** | Docs | `pipeline/README.md` no existe — "caja negra" de facto | [docs_gap.md § 6](governance/docs_gap.md) | Media | S | No |
| **GOV-07** | CI | **No hay CI** — tests pytest existen pero no se ejecutan automatizadamente | [ci_baseline.md](governance/ci_baseline.md) | Alta | M | **Sí** (Fase 2 ingresa Great Expectations sin gate) |
| **GOV-08** | CI | No hay `pyproject.toml` — lint/type config ad-hoc | [ci_baseline.md § 1](governance/ci_baseline.md) | Media | S | No |
| **GOV-09** | CI | No hay pre-commit hooks — regla "no tocar pipeline/" depende de memoria humana | [ci_baseline.md § 3](governance/ci_baseline.md) | Media | S | No |
| **GOV-10** | DoD | Definition of Done no formalizada por tipo de cambio | [definition_of_done.md](governance/definition_of_done.md) | Media | S | No |
| **GOV-11** | Docs | `SECURITY.md` ausente | [docs_gap.md § 4](governance/docs_gap.md) | Baja | S | No |

**Total:** 33 hallazgos — 3 críticos, 12 altos, 15 medios, 3 bajos.

---

## Bloqueadores de Fase 2 (priorizados)

Estos deben resolverse antes de arrancar la infraestructura analítica:

| ID | Hallazgo | Resolución propuesta |
|---|---|---|
| DATA-01 | 3 dimensiones con varianza cero en pipeline avanzado | Auditar early-returns en [pipeline/evaluator_v1.py](../../pipeline/evaluator_v1.py) (requiere sign-off por regla dura) o cambiar a pipeline v1 antes de publicar scores |
| DATA-02 | Pipeline v1 produce n=1 | Ejecutar v1 a full scale (~272 datasets) — ticket aparte |
| UX-01 + UX-02 | Accesibilidad crítica | Sprint de ARIA labels — S de esfuerzo, alto impacto |
| UX-05 | 120 inline styles | Bloque de migración a clases CSS — M de esfuerzo |
| DATA-08 | Sin schemas Pydantic | Crear `pipeline/contracts/` con `QualityReport` + `DatasetEntry` — diseño ya listo en data_contracts_gap.md |
| GOV-01 | Sin CONTRIBUTING | Escribir archivo — 1 día |
| GOV-07 | Sin CI | Adoptar pyproject.toml + GHA mínimo — plan detallado en ci_baseline.md |

---

## Plan sugerido de Fase 2 (3-4 semanas)

### Semana 1 — Unblock

- [ ] DATA-01: Auditar por qué 3 dimensiones son constantes en pipeline avanzado (sin modificar pipeline, solo diagnosticar).
- [ ] UX-01, UX-02: Sprint de ARIA labels + role="progressbar". PR único.
- [ ] GOV-01: Redactar `CONTRIBUTING.md`.
- [ ] GOV-07 parcial: Crear `pyproject.toml` y correr `ruff` localmente (capturar baseline de warnings).

### Semana 2 — Contratos y datos

- [ ] DATA-02: Ejecutar pipeline v1 a full scale (produce ~272 `QualityReport`).
- [ ] DATA-08: Implementar `pipeline/contracts/quality_report.py` con Pydantic v2.
- [ ] UX-05 parte 1: Migrar `organizaciones.py` (76 inline → clases CSS nuevas).

### Semana 3 — CI + accesibilidad restante

- [ ] GOV-07: Crear `.github/workflows/ci.yml` con jobs `lint`, `test`, `smoke`.
- [ ] UX-03, UX-04, UX-07, UX-08, UX-09: PR batch de mejoras UX.
- [ ] GOV-08, GOV-09: pre-commit hooks.

### Semana 4 — Great Expectations piloto

- [ ] DATA-09: Diccionario de datos para 3 datasets piloto.
- [ ] Suite GE por dataset piloto.
- [ ] Nueva tab "Validación" en sección Calidad Pro expone resultados GE.

---

## Métricas de éxito para cerrar Fase 2

- [ ] `git diff pipeline/` sigue vacío al cierre de Fase 2 (o cambios con sign-off explícito).
- [ ] `pytest pipeline/` verde en CI.
- [ ] `ruff check .` verde en CI.
- [ ] 0 iconos `material-symbols-outlined` sin `aria-hidden` o `aria-label` en grep.
- [ ] 0 `.bar-fill` sin `role="progressbar"`.
- [ ] ≥10 datasets con schema Pydantic validado.
- [ ] ≥3 datasets con suite Great Expectations.
- [ ] Skeletons consumidos en ≥1 sección.
- [ ] `CONTRIBUTING.md` + `CHANGELOG.md` vivos.
- [ ] Dashboard arranca sin regresiones en `run_local.sh`.

---

## Qué NO está en este GAP analysis (por diseño)

- Refactors de `pipeline/*` — regla dura.
- Propuestas de Fase 3/4 (forecasting, API pública, paper) — fuera de alcance de Fase 1.
- Usability testing con personas — requiere presupuesto/tiempo fuera de este audit.
- Migración a otro framework (Dash/Next.js) — fuera de alcance; Streamlit validado.

---

## Próximos pasos inmediatos (acciones hoy)

1. **Revisar este documento con stakeholders** — validar priorización y severidades.
2. **Decidir ticket por hallazgo crítico/bloqueador** (7 tickets recomendados).
3. **Commit de Fase 1:** `git add .agent/audit/ && git commit -m "docs(audit): Fase 1 Foundation Audit + Gap Analysis"`.
4. **Actualizar `.agent/audit/README.md`** con link a este consolidado (ya presente).
5. **Archivar este audit como baseline** — futuros audits compararán contra este estado V2.1.
