"""pipeline/ckan_client.py — Robust CKAN API client.

Fase 1: Centraliza todas las llamadas HTTP al portal CKAN con:
- Retry / backoff / 429 via fetcher.fetch_with_retry (SSRF-protegido)
- Validación de contrato CKAN (success / result / results / count)
- Fallback automático: package_search → package_list + package_show
- Descubrimiento de TODOS los formatos (no sólo CSV)
"""

from __future__ import annotations

import logging
import time
from typing import Optional

logger = logging.getLogger("ckan_client")

CKAN_BASE: str = "https://catalogodatos.nl.gob.mx/api/3/action"
PAGE_SIZE: int = 100
INTER_REQUEST_DELAY: float = 0.8  # seconds between paginated requests

# Formatos que el pipeline puede intentar extraer (Fase 2)
EXTRACTABLE_FORMATS: frozenset[str] = frozenset(
    {
        "CSV",
        ".CSV",
        "JSON",
        "XLSX",
        "XLS",
        "GEOJSON",
        "XML",
    }
)


# ── HTTP helpers ───────────────────────────────────────────────


def _get(action: str, params: dict | None = None) -> Optional[dict]:
    """GET /api/3/action/{action} vía fetcher (SSRF-protegido, retry, backoff).

    Returns parsed result dict or None on failure.
    """
    from pipeline.fetcher import fetch_with_retry

    url = f"{CKAN_BASE}/{action}"
    resp = fetch_with_retry(url, params=params or {})
    if resp is None:
        return None
    try:
        data = resp.json()
    except Exception as exc:
        logger.error("[ckan] JSON parse error %s: %s", action, exc)
        return None
    return _validate(data, action)


def _validate(data: dict | None, action: str) -> Optional[dict]:
    """Validate CKAN contract: {success: bool, result: ...}."""
    if not isinstance(data, dict):
        logger.error("[ckan] %s returned non-dict: %r", action, type(data))
        return None
    if not data.get("success"):
        err = data.get("error", "unknown")
        logger.error("[ckan] %s failed: %s", action, err)
        return None
    return data.get("result")


# ── Resource / dataset parsing ─────────────────────────────────


def _get_frequency(ds: dict) -> str:
    """Extract update frequency from top-level field or extras list."""
    freq = ds.get("frequency") or ""
    if isinstance(freq, str) and freq.strip():
        return freq.lower().strip()
    # CKAN extras: [{"key": "frequency", "value": "mensual"}, ...]
    for extra in ds.get("extras", []) or []:
        if not isinstance(extra, dict):
            continue
        key = (extra.get("key") or "").lower()
        if key in ("frequency", "frecuencia", "actualización", "actualizacion"):
            val = (extra.get("value") or "").strip()
            if val:
                return val.lower()
    return ""


def _parse_resource(r: dict, ds: dict, org_name: str, categoria: str) -> dict | None:
    """Build a normalized resource record from CKAN raw data.

    Returns None when the format is not in EXTRACTABLE_FORMATS.
    """
    fmt = (r.get("format") or "").upper().strip()
    if fmt not in EXTRACTABLE_FORMATS:
        return None

    return {
        "slug": ds.get("name", ""),
        "recurso_id": r.get("id", ""),
        "dataset": ds.get("title", "Sin nombre"),
        "organizacion": org_name,
        "categoria": categoria,
        "formato": fmt,
        "url": r.get("url", ""),
        "modificado": ds.get("metadata_modified", ""),
        "frecuencia_update": _get_frequency(ds),
        "descripcion": ds.get("notes", "") or "",
        "licencia": ds.get("license_title", "") or "",
        "licencia_id": ds.get("license_id", "") or "",
        "num_resources": len(ds.get("resources", [])),
        "resource_formats": [
            (rx.get("format") or "").upper().strip() for rx in (ds.get("resources") or [])
        ],
        "resource_descs": [(rx.get("description") or "") for rx in (ds.get("resources") or [])],
    }


def _extract_resources(ds: dict) -> list[dict]:
    """Extract all extractable resource records from a CKAN dataset dict."""
    org = ds.get("organization") or {}
    org_name = org.get("title", org.get("name", "")) if isinstance(org, dict) else ""

    grupos = ds.get("groups") or []
    if grupos and isinstance(grupos[0], dict):
        categoria = grupos[0].get("display_name") or grupos[0].get("title") or "Sin categoría"
    else:
        categoria = "Sin categoría"

    records: list[dict] = []
    for r in ds.get("resources") or []:
        rec = _parse_resource(r, ds, org_name, categoria)
        if rec is not None:
            records.append(rec)
    return records


# ── Discovery strategies ───────────────────────────────────────


def discover_via_search() -> list[dict]:
    """Strategy 1: package_search with full pagination.

    Fast because each page returns complete dataset metadata including resources.
    """
    # Get total count first (rows=0 is efficient)
    probe = _get("package_search", {"rows": 0, "start": 0})
    if probe is None:
        logger.warning("[ckan] package_search probe failed")
        return []

    total = probe.get("count", 0)
    logger.info("[ckan] package_search: %d total datasets in catalog", total)

    records: list[dict] = []
    start = 0

    while start < total:
        result = _get("package_search", {"rows": PAGE_SIZE, "start": start})
        if result is None:
            logger.warning("[ckan] package_search failed at offset %d — aborting page", start)
            break

        page_datasets = result.get("results") or []
        if not page_datasets:
            logger.info("[ckan] Empty page at offset %d — stopping", start)
            break

        for ds in page_datasets:
            records.extend(_extract_resources(ds))

        start += len(page_datasets)
        logger.info(
            "[ckan] Offset %d/%d — %d extractable resources so far",
            start,
            total,
            len(records),
        )
        time.sleep(INTER_REQUEST_DELAY)

    return records


def discover_via_list() -> list[dict]:
    """Strategy 2 (fallback): package_list + package_show per dataset.

    Slower but more reliable when package_search has pagination issues.
    """
    all_slugs = _get("package_list", {"limit": 100000})
    if not isinstance(all_slugs, list):
        logger.error("[ckan] package_list returned unexpected type: %r", type(all_slugs))
        return []

    logger.info("[ckan] package_list: %d dataset slugs", len(all_slugs))
    records: list[dict] = []

    for i, slug in enumerate(all_slugs, 1):
        ds = _get("package_show", {"id": slug})
        if ds is None:
            logger.warning("[ckan] package_show failed for '%s' — skipping", slug)
            continue

        records.extend(_extract_resources(ds))

        if i % 50 == 0:
            logger.info(
                "[ckan] Processed %d/%d datasets (%d resources)",
                i,
                len(all_slugs),
                len(records),
            )
        time.sleep(INTER_REQUEST_DELAY)

    return records


# ── Public API ─────────────────────────────────────────────────


def discover_catalog(use_fallback: bool = True) -> list[dict]:
    """Discover all extractable resources from the CKAN portal.

    Strategy:
      1. package_search with pagination (fast, full metadata per page).
      2. If result is empty AND use_fallback is True, try package_list + package_show.

    Returns:
        List of resource dicts compatible with data_layer.py (same schema as
        fetch_portal_catalog). Only formats in EXTRACTABLE_FORMATS are included.
    """
    logger.info("[ckan] Starting catalog discovery via package_search...")
    records = discover_via_search()

    if not records and use_fallback:
        logger.warning(
            "[ckan] package_search returned 0 extractable resources — "
            "falling back to package_list + package_show"
        )
        records = discover_via_list()

    logger.info("[ckan] Discovery complete: %d extractable resources", len(records))
    return records
