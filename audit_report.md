# Audit Report — Fase 1 Integral · DatosAbiertos2026

**Generado:** 2026-04-16
**Auditor:** Claude Code (Opus 4.6)
**Alcance acordado:** Auditoría integral read-only — pipeline + evaluador + tests + dashboard + multi-agent infra + docs.
**Marco de referencia:** ISO/IEC 25012:2008 (5 dimensiones intrínsecas + governance/mantenibilidad).
**Regla dura:** cero modificaciones a código de producción. Sólo lectura, búsqueda y escritura de este reporte.

> Este documento **complementa y no duplica** los reportes existentes en [.agent/audit/](.agent/audit/). Cuando un hallazgo ya está documentado allí, se cita por ID (`UX-XX`, `DATA-XX`, `GOV-XX`). Los hallazgos nuevos descubiertos en esta auditoría se prefijan `NEW-XX`.

---

## 1. Executive Summary

El proyecto **DatosAbiertos2026** evalúa la calidad de datasets del portal de gobierno abierto de Nuevo León (`catalogodatos.nl.gob.mx`) usando el marco ISO/IEC 25012:2008 y presenta resultados en un dashboard Streamlit con Material Design 3. El código base está **bien estructurado y documentado** (AGENTS.md exhaustivo, separación clara pipeline/sections/styles, reportes de auditoría previos en [.agent/audit/](.agent/audit/) que cubren UX, datos y governance).

Sin embargo, esta auditoría descubre **causas raíz no documentadas** de problemas previamente identificados (notablemente `DATA-01`: la "varianza cero" del pipeline avanzado se debe a **7 métodos `_evaluar_*` que devuelven listas vacías**), una **dependencia faltante** (`vertexai`) que rompe el motor de enriquecimiento, **inconsistencias documentales** entre AGENTS.md y la realidad del repo (Python 3.13+ vs 3.11, `requirements-dev.txt` referenciado pero ausente), y **5/6 tareas del equipo multi-agent académico aún PENDING**.

### Conteo de hallazgos (esta auditoría + reportes previos)

| Severidad | Nuevos (NEW) | Previos (cited) | Total |
|-----------|--------------|-----------------|-------|
| 🔴 Crítica | 3 | 3 (UX-01, UX-02, DATA-01, DATA-02) | 7 |
| 🟠 Alta | 5 | 12 | 17 |
| 🟡 Media | 5 | 15 | 20 |
| 🟢 Baja | 3 | 3 | 6 |
| **Totales** | **16** | **33** | **50** |

### Top 3 acciones bloqueadoras

1. **Implementar 7 stubs de evaluación** en [pipeline/evaluator_v1.py](pipeline/evaluator_v1.py#L204) — explica `DATA-01` y bloquea cualquier KPI público basado en pipeline avanzado.
2. **Añadir `google-cloud-aiplatform` a requirements.txt** o aislar import — evita ImportError en arranque del pipeline.
3. **Reconciliar AGENTS.md vs realidad** — Python version, `requirements-dev.txt`, dimensiones (4 PDF vs 5 código vs 7 implementadas).

---

## 2. Metodología de Auditoría

### 2.1. Marco ISO/IEC 25012:2008

Las 5 dimensiones intrínsecas del estándar son:

| Dimensión     | Definición ISO 25012                               | Implementado en | Evaluado por pipeline avanzado |
|---------------|-----------------------------------------------------|-----------------|--------------------------------|
| Completeness  | Grado de presencia de valores requeridos            | [data_layer.py](data_layer.py) | ✓ (parcial — DATA-03) |
| Accuracy      | Grado en que los datos representan la realidad      | [data_layer.py](data_layer.py) | ⚠ **stub** ([evaluator_v1.py:204-207](pipeline/evaluator_v1.py#L204-L207)) |
| Consistency   | Grado en que los datos son coherentes entre sí      | [data_layer.py](data_layer.py) | ⚠ **stub** ([evaluator_v1.py:209-212](pipeline/evaluator_v1.py#L209-L212)) |
| Uniqueness    | Grado en que no hay duplicados                      | [data_layer.py](data_layer.py) | ✓ ([evaluator_v1.py:381-395](pipeline/evaluator_v1.py#L381-L395)) |
| Timeliness    | Grado en que los datos están actualizados           | [data_layer.py](data_layer.py) | ⚠ **stub** ([evaluator_v1.py:214-217](pipeline/evaluator_v1.py#L214-L217)) |

El proyecto añade **2 dimensiones adicionales** de governance (no ISO 25012 estricto):

| Dimensión       | Marco         | Estado |
|-----------------|---------------|--------|
| Documentation   | Catálogo NL   | ✓      |
| Openness        | 5★ Tim B-L    | ✓      |

Y **3 dimensiones extendidas** del pipeline avanzado, también stubs:

| Dimensión              | Marco       | Estado |
|------------------------|-------------|--------|
| Precision              | ISO 25012   | ⚠ **stub** ([evaluator_v1.py:346-348](pipeline/evaluator_v1.py#L346-L348)) |
| Conformidad sintáctica | ISO 8000    | ⚠ **stub** ([evaluator_v1.py:397-399](pipeline/evaluator_v1.py#L397-L399)) |
| Integridad referencial | ISO 8000    | ⚠ **stub** ([evaluator_v1.py:401-403](pipeline/evaluator_v1.py#L401-L403)) |
| Trazabilidad           | ISO 8000    | ⚠ **stub** ([evaluator_v1.py:405-407](pipeline/evaluator_v1.py#L405-L407)) |

### 2.2. Matriz de severidad

- **🔴 Crítica** — bloquea funcionalidad declarada, viola compromiso público, o falsifica métricas mostradas a usuarios.
- **🟠 Alta** — introduce deuda técnica significativa, compromete mantenibilidad o produce fallos silenciosos.
- **🟡 Media** — duplicación, inconsistencias menores, gaps de documentación recuperables.
- **🟢 Baja** — pulimento, mejoras de DX.

### 2.3. Trazabilidad

Cada hallazgo cita `archivo:línea` verificable mediante el patrón `[archivo](archivo#Lxx)`.

---

## 3. Inventario del Sistema

### 3.1. Mapa de módulos

```
DatosAbiertos2026/                        16 archivos .py de producción + 3 de test
├── dashboard_v3.py                       Streamlit entry point
├── data_layer.py                         ETL + 7 dimensiones de calidad (data_layer)
├── config.py                             Constantes globales (UMBRAL, QUALITY_WEIGHTS)
├── generate_academic_doc.py              Generador de documento académico
├── generate_llm_context.py               Utilidad de contexto LLM
│
├── pipeline/                             Pipeline avanzado (refresh_engine + evaluator)
│   ├── fetcher.py                        HTTP fetcher con SSRF allowlist + retry
│   ├── extractor_v1.py                   Discovery CKAN/Socrata + descarga (962 LOC)
│   ├── evaluator_v1.py                   ISO 25012/8000/DAMA — 7 stubs aquí
│   ├── refresh_engine.py                 Orquestador (run_pipeline, run_advanced_pipeline)
│   ├── ai_enrichment.py                  Vertex AI/Gemini metadata enrichment
│   ├── anomaly_detector.py               Detección anomalías
│   ├── test_anomaly_detector.py          3 tests
│   ├── test_data_layer.py                7 tests
│   └── test_agent_pipeline.py            (no inspeccionado en detalle)
│
├── sections/                             4 secciones del dashboard
│   ├── inicio.py / datasets.py / calidad_pro.py / organizaciones.py
│
├── styles/global_css.py                  Material Design 3 token injection
│
├── config/thresholds.toml                Umbrales TOML
│
├── .agent/audit/                         11 reportes previos de auditoría
├── .antigravity/                         Multi-agent infra (agentes + skills + team)
└── (Lecturas/, lecturas_txt/, etc.)
```

### 3.2. Diagrama de flujo de datos

```
catalogodatos.nl.gob.mx (CKAN)
        │
        ▼
fetch_portal_catalog()  ← data_layer.py + pipeline/extractor_v1.py
        │
        ▼
download_csv()  ← SSRF check + encoding fallback
        │
        ▼
compute_*()  ← 7 dimensiones (data_layer)
        │  +  AnalizadorISO25012/8000/DAMA  ← evaluator_v1.py (7 stubs ⚠)
        │
        ▼
resultados_calidad_datos_nl.csv (1 dataset, dev)
quality_results.json + advanced_quality_results.json (272 datasets)
        │
        ▼
ai_enrichment.py  ← Vertex AI (silent failure si no hay deps)
        │
        ▼
dashboard_v3.py + sections/{inicio, datasets, calidad_pro, organizaciones}
```

### 3.3. Inventario de Skills y agentes

**SKILL.md (7 archivos):**

| Path | Trigger | Propósito (1-line) |
|------|---------|--------------------|
| [.agent/skills/caveman/SKILL.md](.agent/skills/caveman/SKILL.md) | `/caveman` | Caveman-speak para comprimir tokens |
| [.agent/skills/design-system-pro/SKILL.md](.agent/skills/design-system-pro/SKILL.md) | design system, CSS | Design system NL 2026 (Midnight/Teal/Gold/Rose) |
| [.agent/skills/ui-ux-pro-max/SKILL.md](.agent/skills/ui-ux-pro-max/SKILL.md) | UI/UX work | 67 estilos, 96 paletas, 99 UX guidelines |
| [.opencode/skills/ui-ux-pro-max/SKILL.md](.opencode/skills/ui-ux-pro-max/SKILL.md) | UI/UX work | Duplicado del anterior (NEW-15) |
| [.antigravity/skills/coding-standards/SKILL.md](.antigravity/skills/coding-standards/SKILL.md) | code review, TS/JS | Estándares TS/JS/React/Node |
| [.antigravity/skills/frontend-patterns/SKILL.md](.antigravity/skills/frontend-patterns/SKILL.md) | React, Next.js | Patrones frontend |
| [.antigravity/skills/python-patterns/SKILL.md](.antigravity/skills/python-patterns/SKILL.md) | Python, PEP 8 | Patrones idiomáticos Python |

**Agentes activos (.antigravity/agents/, 6 roles):** data-quality-analyst, architect, python-reviewer, report-generator, loop-operator, tdd-guide.

**Equipo de investigación académica (.antigravity/team/, 6 roles):** director, agente_fuentes, agente_metodologia, agente_variables, agente_redactor, agente_revisor.

---

## 4. Hallazgos Críticos (🔴)

### NEW-C1 · Pipeline avanzado: 7 métodos `_evaluar_*` son stubs vacíos

**Archivo:** [pipeline/evaluator_v1.py](pipeline/evaluator_v1.py)

| Método | Líneas | Marco ISO | Comentario en código |
|--------|--------|-----------|----------------------|
| `_evaluar_exactitud` | [204-207](pipeline/evaluator_v1.py#L204-L207) | ISO 25012 — Accuracy | "Similar simplification for brevity and structure." |
| `_evaluar_consistencia` | [209-212](pipeline/evaluator_v1.py#L209-L212) | ISO 25012 — Consistency | "Logic here..." |
| `_evaluar_actualidad` | [214-217](pipeline/evaluator_v1.py#L214-L217) | ISO 25012 — Timeliness | "Logic here..." |
| `_evaluar_precision` | [346-348](pipeline/evaluator_v1.py#L346-L348) | ISO 25012 — Precision | (sin comentario) |
| `_evaluar_conformidad_sintactica` | [397-399](pipeline/evaluator_v1.py#L397-L399) | ISO 8000 | (sin comentario) |
| `_evaluar_integridad_referencial` | [401-403](pipeline/evaluator_v1.py#L401-L403) | ISO 8000 | (sin comentario) |
| `_evaluar_trazabilidad` | [405-407](pipeline/evaluator_v1.py#L405-L407) | ISO 8000 | (sin comentario) |

**Justificación ISO 25012:** estos métodos son llamados desde `AnalizadorISO25012.analizar()` y `AnalizadorISO8000.analizar()` (mismo archivo, líneas 366-378) y devuelven `(metricas=[], problemas=[])`. Esto significa que las dimensiones **Accuracy, Consistency y Timeliness del estándar ISO 25012 NO se evalúan** en el pipeline avanzado, a pesar de aparecer como "evaluadas" en el dashboard `Calidad Pro`.

**Causa raíz documentada:** explica directamente el hallazgo previo `DATA-01` ("3 de 5 dimensiones del pipeline avanzado tienen varianza cero"). Las dimensiones constantes son consecuencia mecánica de los stubs.

**Impacto:** los KPIs mostrados en [sections/calidad_pro.py](sections/calidad_pro.py) son artefactos de defaults, no evaluación real → riesgo reputacional si se publica.

**Verificable con:** `Grep "return metricas, problemas" pipeline/evaluator_v1.py` → 7 matches dentro de métodos `_evaluar_*`.

### NEW-C2 · `google-cloud-aiplatform` / `vertexai` no listado en `requirements.txt`

**Evidencia:**
- [requirements.txt](requirements.txt) — `Grep` `vertexai|google-cloud-aiplatform|google.cloud` → **0 matches**.
- [pipeline/ai_enrichment.py](pipeline/ai_enrichment.py) importa `vertexai` y se invoca desde [pipeline/refresh_engine.py](pipeline/refresh_engine.py) en `run_advanced_pipeline()`.

**Impacto:** `pip install -r requirements.txt` produce un entorno donde `from pipeline.ai_enrichment import enrich_dataset_metadata` lanza `ModuleNotFoundError`. La instalación queda en un estado roto silencioso hasta que un usuario intenta correr el pipeline avanzado.

**Justificación ISO 25012 (governance/mantenibilidad):** viola el principio de "instalación reproducible" implícito en AGENTS.md sección "Build / Run Commands".

### NEW-C3 · Equipo multi-agent académico: 5/6 tareas PENDING

**Archivo:** [.antigravity/team/tasks.json](.antigravity/team/tasks.json)

| ID | Tarea | Agente | Estado | Deps |
|----|-------|--------|--------|------|
| 1 | Verificar 9 citas del PDF | agente_fuentes | ✅ COMPLETED (2026-03-21) | — |
| 2 | Buscar literatura adicional 2020-2026 | agente_metodologia | ⏳ PENDING | — |
| 3 | Mapear variables PDF ↔ data_layer.py | agente_variables | ⏳ PENDING | [1] |
| 4 | Redactar secciones 11.1–11.5 + Sección 7 | agente_redactor | ⏳ PENDING | [1, 2, 3] |
| 5 | Revisar documento (checklist 20 puntos) | agente_revisor | ⏳ PENDING | [4] |
| 6 | Consolidar `protocolo_investigacion_NL2026_v2.md` | director | ⏳ PENDING | [5] |

**Impacto:** la salida final declarada (protocolo de investigación con citaciones APA 7 verificadas) **no existe**. El proyecto académico está bloqueado en task 1 desde hace ~26 días (último commit completed: 2026-03-21).

**Justificación:** governance/cumplimiento de roadmap.

### Hallazgos críticos previos citados

- **UX-01** — ~80 iconos `material-symbols-outlined` sin `aria-hidden`/`aria-label` ([wcag_2_1_aa.md](.agent/audit/ux/wcag_2_1_aa.md)).
- **UX-02** — `.bar-fill` sin `role="progressbar"` ([inicio.py:74-84](sections/inicio.py#L74-L84)).
- **DATA-01** — 3 dimensiones con varianza cero (causa raíz: NEW-C1).
- **DATA-02** — Pipeline v1 produce n=1 dataset en CSV/JSON.

---

## 5. Hallazgos Altos (🟠)

### NEW-A1 · Cobertura de tests ≈ 19% (3 archivos test / 16 producción)

**Archivos test:** [test_anomaly_detector.py](pipeline/test_anomaly_detector.py) (3 tests), [test_data_layer.py](pipeline/test_data_layer.py) (7 tests), [test_agent_pipeline.py](pipeline/test_agent_pipeline.py).

**Sin tests:**
- [pipeline/fetcher.py](pipeline/fetcher.py) — SSRF allowlist, retry, snapshot
- [pipeline/extractor_v1.py](pipeline/extractor_v1.py) — 962 LOC, parsing CKAN/Socrata
- [pipeline/refresh_engine.py](pipeline/refresh_engine.py) — orquestador
- [pipeline/evaluator_v1.py](pipeline/evaluator_v1.py) — el motor avanzado (incluye stubs)
- [pipeline/ai_enrichment.py](pipeline/ai_enrichment.py) — Vertex AI
- [data_layer.py](data_layer.py) — ETL + scoring (parcial: 7 tests)
- [dashboard_v3.py](dashboard_v3.py) y `sections/*` (esperable: tests UI son costosos)

**Justificación ISO 25012 (governance):** sin tests sobre `evaluator_v1.py`, los stubs de NEW-C1 nunca pudieron ser detectados por CI.

### NEW-A2 · Sin tests de integración end-to-end del pipeline

No existe test que ejecute `fetch → parse → evaluate → store` con un fixture conocido. Cada test unitario aísla una función; un cambio en `refresh_engine.py` puede romper la cadena sin alertar.

### NEW-A3 · Vertex AI silent failure en [pipeline/ai_enrichment.py:21-31](pipeline/ai_enrichment.py#L21-L31)

`init_vertex()` captura `Exception` genérico, loguea y devuelve `False`. Aguas abajo, el dataset se devuelve **sin enriquecer** silenciosamente. El usuario en el dashboard no sabe si la ausencia de `descripcion_ciudadana` es por bug, por proyecto GCP no configurado, o por dataset realmente sin descripción.

### NEW-A4 · Discrepancia Python version: AGENTS.md dice 3.13+, requirements.txt dice 3.11

- [AGENTS.md:13](AGENTS.md#L13) — "Python 3.13+ (type-checked, pyright compatible)"
- [requirements.txt:3](requirements.txt#L3) — "Python mínimo: 3.11"
- [.agent/audit/README.md:38](.agent/audit/README.md#L38) — "Python mínimo: 3.11" (alineado con requirements)

**Impacto:** un agente leyendo AGENTS.md como contrato puede sumar features 3.13-only (e.g., `type` aliases) que rompen instalaciones 3.11.

### NEW-A5 · `requirements-dev.txt` referenciado pero NO existe

- [AGENTS.md:28](AGENTS.md#L28) — `pip install -r requirements-dev.txt`
- [requirements.txt:31-34](requirements.txt#L31-L34) — comenta "separar en requirements-dev.txt" pero el archivo no existe en el repo.

**Impacto:** cualquier nuevo contributor que siga AGENTS.md falla en el paso 2 de setup.

### Hallazgos altos previos citados

UX-03, UX-04, UX-05, UX-07, UX-08, UX-09, DATA-03, DATA-04, DATA-08, GOV-01, GOV-02, GOV-03, GOV-07 — ver [GAP_ANALYSIS.md](.agent/audit/GAP_ANALYSIS.md).

---

## 6. Hallazgos Medios (🟡)

### NEW-M1 · Duplicación de boilerplate HTTP (3 lugares)

| Lugar | Patrón |
|-------|--------|
| [pipeline/extractor_v1.py:230-233](pipeline/extractor_v1.py#L230-L233) | `Session()` + UA `"DataExtractor-NL/1.0 (Gobierno Abierto)"` |
| [pipeline/extractor_v1.py:413-416](pipeline/extractor_v1.py#L413-L416) | `Session()` + UA `"DataExtractor-NL/1.0"` (95% idéntico al anterior) |
| [data_layer.py:158-167](data_layer.py#L158-L167) | Headers per-request (sin Session pooling) |

**Recomendación:** factory en [pipeline/fetcher.py](pipeline/fetcher.py).

### NEW-M2 · Encoding fallback duplicado

- [pipeline/extractor_v1.py:572-596](pipeline/extractor_v1.py#L572-L596) — fallback `["latin-1", "iso-8859-1", "cp1252", "utf-8-sig"]`
- [data_layer.py:169-173](data_layer.py#L169-L173) — fallback `["utf-8", "utf-8-sig", "latin-1", "cp1252"]`

Listas distintas → cuando uno se actualice el otro queda atrás.

### NEW-M3 · Límites de descarga inconsistentes

- [config.py:29](config.py#L29) — `MAX_DOWNLOAD_MB: int = 50`
- [pipeline/extractor_v1.py:407](pipeline/extractor_v1.py#L407) — `MAX_TAMANO_BYTES = 500 * 1024 * 1024` (500 MB)

**Discrepancia 10×.** ¿Cuál es la política real? Documentar y converger en `config.py`.

### NEW-M4 · User-Agent strings inconsistentes

- `pipeline/fetcher.py` — `"DatosAbiertosNL-Fetcher/3.0"`
- `pipeline/extractor_v1.py:230` — `"DataExtractor-NL/1.0 (Gobierno Abierto)"`
- `pipeline/extractor_v1.py:413` — `"DataExtractor-NL/1.0"`

Sin un UA consistente, los logs del portal CKAN no permiten atribuir tráfico al proyecto.

### NEW-M5 · `MUNICIPIOS_NL` hardcoded en [pipeline/evaluator_v1.py:124-139](pipeline/evaluator_v1.py#L124-L139)

Lista de municipios de NL embebida en el evaluador. Pertenece a `config.py` o a un archivo de datos de referencia.

### Hallazgos medios previos citados

UX-06, UX-10, UX-11, UX-12, DATA-05, DATA-06, DATA-10, DATA-11, DATA-12, GOV-04, GOV-05, GOV-06, GOV-08, GOV-09, GOV-10 — ver [GAP_ANALYSIS.md](.agent/audit/GAP_ANALYSIS.md).

---

## 7. Hallazgos Bajos (🟢)

### NEW-B1 · Faltan docstrings en `data_layer.py:compute_*`

Funciones `compute_timeliness`, `compute_documentation`, `compute_openness` carecen de la sección `Returns:` requerida por AGENTS.md §5.

### NEW-B2 · Discrepancia documental: 4 dimensiones (PDF) vs 5 ISO (código) vs 7 totales (config)

- PDF original (referenciado en `SKILL_academic_research_multiagent.md`): 4 dimensiones.
- ISO 25012 estándar: 5 dimensiones intrínsecas.
- [config.py:15-23](config.py#L15-L23) — `QUALITY_WEIGHTS` lista 7 dimensiones (5 ISO + Documentation + Openness).

Necesita una nota metodológica oficial (acordado por agente_variables, task 3).

### NEW-B3 · Documentación multi-agent dispersa entre dos ecosistemas paralelos

`.antigravity/agents/` (6 agentes activos) y `.antigravity/team/` (6 agentes académicos) son sistemas separados. Ningún `README.md` los relaciona. Un onboarding pierde 30+ minutos averiguándolo.

### Hallazgos bajos previos citados

DATA-07, GOV-11 — ver [GAP_ANALYSIS.md](.agent/audit/GAP_ANALYSIS.md).

---

## 8. Cobertura ISO/IEC 25012 — Estado por Dimensión

| Dimensión       | data_layer.py | evaluator_v1.py (avanzado) | Severidad gap | Hallazgo |
|-----------------|---------------|----------------------------|---------------|----------|
| Completeness    | ✓ (DATA-03)   | ✓ ([191-202](pipeline/evaluator_v1.py#L191-L202)) | Alta | DATA-03 |
| Accuracy        | ✓             | ⚠ stub                     | **Crítica**   | NEW-C1, DATA-04 |
| Consistency     | ✓             | ⚠ stub                     | **Crítica**   | NEW-C1 |
| Uniqueness      | ✓             | ✓ ([381-395](pipeline/evaluator_v1.py#L381-L395)) | Media | DATA-05 |
| Timeliness      | ✓             | ⚠ stub                     | **Crítica**   | NEW-C1, DATA-06 |
| Documentation   | ✓             | n/a                         | —             | — |
| Openness        | ✓             | n/a                         | Baja          | DATA-07 |

**Conclusión:** 3/5 dimensiones del estándar ISO 25012 **no son evaluadas** por el pipeline avanzado. El dashboard `Calidad Pro` muestra 0/100 o 100/100 artificialmente para Accuracy, Consistency, Timeliness.

---

## 9. Datasets no cubiertos

| Fuente | Datasets | Comentario |
|--------|----------|-----------|
| Portal NL CKAN (estimado) | ~272 | discovered en `advanced_quality_results.json` |
| `resultados_calidad_datos_nl.csv` | 1 | dev-only ([.agent/audit/README.md:40](.agent/audit/README.md#L40)) |
| `quality_results.json` | 1 | snapshot puntual (Solicitudes-de-Informacion-Linea3) |
| `advanced_quality_results.json` | 272 | pero con 3 dimensiones inválidas por NEW-C1 |

**Gap:** la diferencia entre **n=1 (CSV de producción)** y **n=272 (JSON de desarrollo)** ya está identificada como `DATA-02`. **NUEVO**: aunque el JSON tiene 272, **3/5 dimensiones son ruido constante** por NEW-C1 → realmente solo 2/5 dimensiones son explotables analíticamente.

---

## 10. Gaps de Documentación

| Gap | Evidencia | Severidad |
|-----|-----------|-----------|
| AGENTS.md inconsistente con requirements.txt (Python version) | NEW-A4 | Alta |
| `requirements-dev.txt` referenciado pero ausente | NEW-A5 | Alta |
| Sin runbook para configurar Vertex AI | implícito en NEW-A3 | Media |
| Sin diagrama oficial de arquitectura | — | Media |
| Sin nota metodológica para 4 vs 5 vs 7 dimensiones | NEW-B2 | Baja |
| Sin README en `.antigravity/agents/` ni en `.antigravity/team/` | NEW-B3 | Baja |
| `CONTRIBUTING.md`, `LICENSE`, `CHANGELOG.md`, ADRs ausentes | GOV-01, GOV-02, GOV-04, GOV-05 | Alta |

---

## 11. Roadmap de Remediación (informativo, sin implementar)

### P1 — Bloqueadores (sprint 1, ~5-8 días)

1. **NEW-C1** — Implementar 7 stubs `_evaluar_*` en `evaluator_v1.py`. Diseño preliminar:
   - `_evaluar_exactitud`: detectar tipos mixtos en columnas object, espacios al inicio/fin, valores constantes legítimos vs error.
   - `_evaluar_consistencia`: outliers IQR en columnas numéricas, normalización de mayúsculas/acentos en categóricas.
   - `_evaluar_actualidad`: latencia de actualización vs `frequency` declarada en metadata CKAN.
   - `_evaluar_precision`: precisión decimal declarada vs observada.
   - `_evaluar_conformidad_sintactica` / `_evaluar_integridad_referencial` / `_evaluar_trazabilidad`: ver [data_contracts_gap.md](.agent/audit/data/data_contracts_gap.md).
2. **NEW-C2** — Añadir `google-cloud-aiplatform` a `requirements.txt` o aislar import dentro de try/except con feature flag.
3. **NEW-A4 + NEW-A5** — Consolidar AGENTS.md + crear `requirements-dev.txt` real (`black`, `ruff`, `flake8`, `pytest`, `pyright`).
4. **UX-01 + UX-02** — Sprint ARIA labels + `role="progressbar"`.

### P2 — Calidad de tests (sprint 2, ~5 días)

5. **NEW-A1, NEW-A2** — Tests para `fetcher.py` (mock con `responses`), `extractor_v1.py` (fixtures CKAN), tests de integración E2E.

### P3 — Limpieza (sprint 3, ~3 días)

6. **NEW-M1, NEW-M2, NEW-M3, NEW-M4** — Refactor a factory HTTP compartido en `fetcher.py`; consolidar encoding y límites en `config.py`.
7. **NEW-M5** — Mover `MUNICIPIOS_NL` a `config.py` o `data/municipios_nl.json`.

### P4 — Documentación (sprint 4, paralelo, ~3 días)

8. **GOV-01, GOV-02, GOV-04** — `CONTRIBUTING.md`, `LICENSE`, `CHANGELOG.md`.
9. **NEW-B2, NEW-B3** — Nota metodológica de dimensiones + README en `.antigravity/`.
10. **NEW-C3** — Reactivar tareas 2-6 del equipo académico o cerrarlas formalmente.

---

## 12. Apéndices

### A. Inventario completo SKILL.md

Ver tabla en sección 3.3.

### B. Inventario `.antigravity/agents/` (6 roles activos)

`data-quality-analyst.md`, `architect.md`, `python-reviewer.md`, `report-generator.md`, `loop-operator.md`, `tdd-guide.md`.

### C. Estado `.antigravity/team/tasks.json`

Ver sección 4 NEW-C3.

### D. Referencias cruzadas a [.agent/audit/](.agent/audit/) existentes

| Archivo | Cobertura |
|---------|-----------|
| [.agent/audit/README.md](.agent/audit/README.md) | Índice general Fase 1 |
| [.agent/audit/GAP_ANALYSIS.md](.agent/audit/GAP_ANALYSIS.md) | 33 hallazgos consolidados con `Bloquea Fase 2?` |
| [.agent/audit/data/pipeline_audit.md](.agent/audit/data/pipeline_audit.md) | 7 dimensiones × método actual vs Great Expectations |
| [.agent/audit/data/data_contracts_gap.md](.agent/audit/data/data_contracts_gap.md) | Schemas Pydantic propuestos |
| [.agent/audit/data/scoring_sensitivity.md](.agent/audit/data/scoring_sensitivity.md) | Sensitivity analysis (blocker n=1) |
| [.agent/audit/governance/docs_gap.md](.agent/audit/governance/docs_gap.md) | CONTRIBUTING/CHANGELOG/ADRs |
| [.agent/audit/governance/ci_baseline.md](.agent/audit/governance/ci_baseline.md) | `pyproject.toml` + GHA propuestos |
| [.agent/audit/governance/definition_of_done.md](.agent/audit/governance/definition_of_done.md) | DoD por tipo de change |
| [.agent/audit/ux/heuristic_nielsen.md](.agent/audit/ux/heuristic_nielsen.md) | 10 heurísticas Nielsen |
| [.agent/audit/ux/wcag_2_1_aa.md](.agent/audit/ux/wcag_2_1_aa.md) | WCAG 2.1 AA con file:line |
| [.agent/audit/ux/component_inventory.md](.agent/audit/ux/component_inventory.md) | CSS definidos vs consumidos |

---

## 13. Verificación de este reporte

Para reproducir las verificaciones:

| Hallazgo | Comando |
|----------|---------|
| NEW-C1 (7 stubs) | `Read pipeline/evaluator_v1.py` líneas 204-217, 346-348, 397-407 — confirmar `return metricas, problemas` con cuerpo vacío. |
| NEW-C2 (vertexai missing) | `Grep "vertexai\|google-cloud-aiplatform" requirements.txt` → 0 matches. |
| NEW-C3 (5/6 PENDING) | `Read .antigravity/team/tasks.json` — contar `"estado": "PENDING"`. |
| NEW-A1 (cobertura) | `Glob "{*.py,pipeline/*.py,sections/*.py,styles/*.py}"` → 19 .py; de los cuales 3 son `test_*.py`. Ratio 3/16 = 18.75%. |
| NEW-A4 (Python ver) | Comparar [AGENTS.md:13](AGENTS.md#L13) con [requirements.txt:3](requirements.txt#L3). |
| NEW-A5 (req-dev ausente) | `Glob "requirements-dev.txt"` → 0 resultados. |
| NEW-M3 (límites) | `Grep "MAX_TAMANO_BYTES\|MAX_DOWNLOAD_MB"` → 50 (config.py:29) vs 500 MB (extractor_v1.py:407). |

---

*Fin del reporte — Auditoría Integral Fase 1.*
*Próximo paso recomendado: revisar NEW-C1, NEW-C2, NEW-C3 con el director del proyecto antes de Fase 2.*
