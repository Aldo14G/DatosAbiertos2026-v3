# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased] — Pre-deployment hardening

### Added
- **`Dockerfile`** + **`.dockerignore`** — production image targeting Cloud
  Run (Python 3.13-slim, non-root user, healthcheck, XSRF protection,
  telemetry disabled).
- **`DEPLOYMENT.md`** — end-to-end deployment guide (Firebase App Hosting
  for the landing, Cloud Run for the dashboard, CI/CD via Workload Identity
  Federation, rollback procedure).
- **`SECURITY.md`** — threat model, pre-deployment hardening checklist,
  incident-response runbook.
- **`.env.example`** — environment-variable template (no real values).
- **`quality_scorer.py`** + **`section_data.py`** — extracted scoring core
  and section-level aggregation primitives, decoupling UI sections from
  pipeline internals.
- **`pipeline/__init__.py`**, **`pipeline/aesthetics.py`**, plus three
  test modules (`test_quality_scorer.py`, `test_section_data.py`,
  `test_threshold_authority.py`) raising coverage on scoring contracts.
- **`scripts/sync_weights.py`** — utility to keep `landing/lib/quality_weights.json`
  in sync with `config.QUALITY_WEIGHTS` (single source of truth).
- **Responsive typography & spacing scale** in `styles/global_css.py` —
  17 new design tokens (`--fs-*`, `--lh-*`, `--fw-*`, `--gap-*`,
  `--pad-card`, `--margin-after-header`) with media-query overrides at
  ≤1024 px and ≤640 px. Applied throughout `.section-title`, `.hero-title`,
  `.editorial-container p`, `.nl-section`, `.nl-section-break`,
  `.nl-subsection-header`, `.nl-stat-card`, `.nl-chart-card`, plus the
  global `h1/h2/h3` reset.
- **Saluddinstitucional** landing section (`SaludInstitucionalSection.tsx`)
  + `useInView` hook for scroll-triggered animations.

### Changed
- **`.gitignore`** — comprehensive rewrite covering AI agent caches
  (`.antigravity/`, `.claude/`, `.gemini/`, `.agent/`), pipeline runtime
  artifacts (`data/parquet/`, `snapshots/`), Node/Next.js build output,
  editor temp files, and credentials patterns.
- **`README.md`** — replaced the Firebase Studio placeholder with a real
  pointer to `DEPLOYMENT.md` + `SECURITY.md`; removed references to the
  retired `.agent/` and `.gemini/` directories.
- Pipeline modules (`ckan_client.py`, `evaluator.py`, `extractor.py`,
  `refresh_engine.py`) refined — see commit history for specifics.
- Section renderers (`sections/*.py`) updated to use new design tokens
  and the extracted `section_data` primitive.
- Landing page components — typography refresh, animation polish,
  data-binding cleanup against the new `quality_weights.json`.

### Removed
- `.agent/` directory — content migrated to `docs/audit/`.
- `.gemini/skills/` — superseded by the unified `.claude/` workflow
  (now ignored, not committed).
- `config/thresholds.toml` — thresholds consolidated into `config.py`.
- 26 stale editor temp files (`*.tmp.*`) from `sections/` and `styles/`.
- Three landing components no longer in use:
  `Illustration.tsx`, `liquid-glass-button.tsx`, `web-gl-shader.tsx`.

### Security
- `.gitignore` now blocks `.env*`, `*-credentials*.json`,
  `*service-account*.json`, `*.pem`, `*.key`, and `secrets/` patterns.
- `Dockerfile` runs as non-root user `app`, enables Streamlit XSRF
  protection, disables CORS by default, and disables Streamlit usage
  telemetry.
- `.dockerignore` strips secrets, git history, and dev artifacts before
  the image layer is built.

---

[Unreleased]: https://github.com/Aldo14G/DatosAbiertos2026-v3/compare/main...HEAD
