# Governance · Documentation Gap

**Scope:** documentación de proyecto fuera del código. Qué existe, qué falta, qué está desactualizado.

## Inventario actual (raíz)

| Archivo | Propósito | Estado |
|---|---|---|
| [README.md](../../../README.md) | Entry-point público | ✅ Existe (3.5 KB) — verificar que refleje V2.1 |
| [DESIGN.md](../../../DESIGN.md) | Design system canónico NL 2026 | ✅ Existe (3.8 KB) — canónico tras última refactor |
| [AGENTS.md](../../../AGENTS.md) | Protocolo multiagente | ✅ Existe (7.5 KB) |
| [LLM_INIT.md](../../../LLM_INIT.md) | Contexto rápido para LLMs | ✅ Existe (4.8 KB) |
| [MIGRATION_2026.md](../../../MIGRATION_2026.md) | Changelog migración dashboard | ✅ Existe — promover a `CHANGELOG.md` |
| [UX_QA_CHECKLIST.md](../../../UX_QA_CHECKLIST.md) | Checklist de QA visual | ✅ Existe (2.3 KB) |
| [README_CALIDAD_PRO.md](../../../README_CALIDAD_PRO.md) | Docs sección Calidad Pro | ✅ Existe (2.3 KB) |
| [AGENT_SKILL_INVENTORY.md](../../../AGENT_SKILL_INVENTORY.md) | Catálogo de skills locales | ✅ Existe (86 KB) |

---

## Gaps identificados

### 1 · `CONTRIBUTING.md` — **NO EXISTE** · Bloquea Fase 2

**Por qué importa:** Sin contribution guide, cualquier colaborador (humano o agente) inventa convenciones. El proyecto ya tiene reglas duras (NO tocar `pipeline/`, NO inline CSS, NO emojis) dispersas en `AGENTS.md` y skills, pero no accesibles para un PR externo.

**Contenido propuesto:**
```markdown
# Contributing to DatosAbiertos2026

## Hard rules
- NEVER modify `pipeline/*` without explicit owner sign-off (scrapers stable).
- NEVER add inline `style="..."` (≥30 chars) — use `styles/global_css.py` classes.
- NEVER add emojis in user-facing UI or code.
- NEVER commit data files >1 MB; use CKAN fetch or external storage.
- ALL new sections must use design tokens from `_TOKENS_DARK` / `_TOKENS_LIGHT`.

## Local setup
- Python 3.11
- `pip install -r requirements.txt`
- `bash run_local.sh` → http://localhost:8501

## Testing
- `pytest pipeline/` — unit tests for data layer.
- `python -m pyflakes sections/ dashboard_v3.py` — syntax check.
- Visual QA: follow [UX_QA_CHECKLIST.md](UX_QA_CHECKLIST.md).

## Commit style
- Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`.
- Co-Authored-By footer when AI-assisted.

## PR checklist
- [ ] Matches DESIGN.md tokens
- [ ] WCAG 2.1 AA compliant (no new ARIA violations)
- [ ] Pipeline tests pass
- [ ] CHANGELOG.md updated
```

### 2 · `CHANGELOG.md` — **NO EXISTE** · No bloquea

**Por qué importa:** Hoy el historial de cambios vive en commits + `MIGRATION_2026.md` (snapshot único). Un `CHANGELOG.md` estilo [keep-a-changelog](https://keepachangelog.com) rastrea versiones semánticamente (V2.1 ya está en uso pero sin registro formal de qué cambió).

**Acción Fase 2:** Migrar `MIGRATION_2026.md` a `CHANGELOG.md` con secciones `[Unreleased]`, `[2.1] — 2026-04-15`, `[2.0] — 2026-03-xx`.

### 3 · `ADR/` (Architectural Decision Records) — **NO EXISTE** · No bloquea

**Por qué importa:** Decisiones grandes (por qué Streamlit y no Dash, por qué ISO 25012 y no DAMA, por qué 7 pesos específicos) no están registradas. Futuro yo/colaborador va a re-abrir debates ya cerrados.

**Propuesta:** `docs/adr/` con plantilla [MADR](https://adr.github.io/madr/):
- `0001-use-streamlit.md`
- `0002-iso-25012-scoring.md`
- `0003-pipeline-immutable.md`
- `0004-dark-first-nl2026-palette.md`
- `0005-quality-weights.md` (capturar la justificación Wang & Strong 1996 ya referenciada en [config.py](../../../config.py))

### 4 · `SECURITY.md` — **NO EXISTE** · No bloquea

**Por qué importa:** Proyecto público de datos gubernamentales. Aunque no maneja PII, conviene documentar: política de reporte de vulnerabilidades, dependencias auditadas, contacto de seguridad.

**Mínimo viable:**
```markdown
# Security Policy
- Reportar vulnerabilidades a: <contacto>
- Python deps auditadas mensualmente con `pip-audit`.
- Sin PII en datos procesados (solo open data CKAN).
```

### 5 · Docs por sección (`sections/README.md`) — PARCIAL

- ✅ `README_CALIDAD_PRO.md` (raíz) documenta Calidad Pro.
- ❌ No hay equivalente para `inicio`, `datasets`, `organizaciones`.
- **Propuesta Fase 2:** mover docs por-sección a `sections/README.md` con subsección por archivo.

### 6 · Docs de pipeline — **DISPERSAS**

- `pipeline/` tiene docstrings Python pero no README.
- `pipeline_audit.md` (este audit) documenta las 7 dimensiones, pero no cómo correr el pipeline end-to-end.
- **Propuesta Fase 2:** `pipeline/README.md` con:
  - Comando `python -m pipeline.evaluator_v1 --dataset <slug>`
  - Diagrama de flujo: extractor → evaluator → anomaly_detector → refresh_engine
  - Formato de salida (referenciar `data_contracts_gap.md`)

### 7 · `LICENSE` — **NO DETECTADO** · Crítico si se publica

**Por qué importa:** Proyecto marcado como open data/gobernanza pero sin archivo de licencia. Sin licencia, código es "all rights reserved" por defecto y nadie puede reusar legalmente.

**Acción:** Añadir `MIT` o `Apache-2.0` antes de publicación externa.

### 8 · `docs/methodology.md` — **NO EXISTE** · Bloquea publicación académica

**Por qué importa:** Referenciado implícitamente por los pesos ISO 25012 pero inexistente. Sin este documento no hay justificación publicable de los 7 pesos y las heurísticas del evaluator.

**Contenido propuesto:**
- Wang & Strong (1996) — mapping de dimensiones
- ISO/IEC 25012:2008 — 15 dimensiones oficiales → 7 seleccionadas (trazabilidad de la reducción)
- Justificación de pesos: proceso Delphi interno / reutilización de trabajos previos / ajuste empírico
- Descripción de heurísticas de evaluator (IQR×1.5, n≥30, etc.)

### 9 · Roadmap público — **IMPLÍCITO**

**Hoy:** el roadmap de 4 fases vive en conversaciones LLM + plan files. No hay un `ROADMAP.md` commiteado.

**Propuesta:** `ROADMAP.md` con las 4 fases del plan original, marcando Fase 1 como ✅ al finalizar este audit.

---

## Resumen priorizado

| Gap | Severidad | Bloquea Fase 2 | Esfuerzo |
|---|---|---|---|
| `CONTRIBUTING.md` | Alta | **Sí** | S (1 día) |
| `LICENSE` | Alta | No (sí si publicación) | S |
| `docs/methodology.md` | Alta | No | M (3 días) |
| `CHANGELOG.md` | Media | No | S |
| `ADR/` | Media | No | M (progresivo) |
| `pipeline/README.md` | Media | No | S |
| `SECURITY.md` | Baja | No | S |
| `sections/README.md` | Baja | No | S |
| `ROADMAP.md` | Baja | No | S |
