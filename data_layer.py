"""
data_layer.py  — v2.3 (módulo de compatibilidad)
Re-exporta el API público desde los módulos especializados:

  data_discovery   — descubrimiento del portal + carga de resultados
  data_parsers     — parsers de formato (CSV, JSON, Excel, GeoJSON, XML)
  data_aggregation — agregaciones, filtros y clasificación

Este archivo NO define lógica propia. Existe únicamente para que los
callers existentes (dashboard_v3.py, sections/, pipeline/refresh_engine.py)
continúen resolviendo sus imports sin modificación.

Cambios históricos:
  v2.2: 7 dimensiones ISO 25012 (Completitud, Exactitud, Consistencia,
        Unicidad, Puntualidad, Documentación, Apertura).
  v2.3: split en data_discovery / data_parsers / data_aggregation.
        is_safe_url consolidado en pipeline.fetcher.validate_url (SSRF fix).
"""

# ── Constantes extra (acceso histórico desde data_layer) ──────
from config import CLASIFICACION_DEFAULT, CLASIFICACION_THRESHOLDS, QUALITY_WEIGHTS  # noqa: F401

# ── data_aggregation ──────────────────────────────────────────
from data_aggregation import (  # noqa: F401
    DIM_LABEL_MAP,
    _build_slug_to_title_map,
    _load_advanced_json,
    _normalize_title,
    agg_dim_means_by,
    agg_org_stats,
    apply_filters,
    classify_score,
    compute_quality_scores,
    get_aggregations,
    load_advanced_catalog_stats,
    load_advanced_overlay,
    merge_advanced_overlay,
)

# ── data_discovery ────────────────────────────────────────────
from data_discovery import (  # noqa: F401
    _REQUIRED_COLS,
    CKAN_API,
    DELAY_SEC,
    _deduplicate_by_slug,
    _legacy_fetch_portal_catalog,
    _load_from_bigquery,
    _load_raw,
    _validate_schema,
    fetch_portal_catalog,
    get_resource_vs_unique_count,
    load_coverage_report,
    load_results,
    normalize_categories,
    save_to_bigquery,
)

# ── data_parsers ──────────────────────────────────────────────
from data_parsers import (  # noqa: F401
    _detect_encoding,
    _parse_excel,
    _parse_geojson,
    _parse_json,
    _parse_xml,
    download_csv,
    download_resource,
)

# validate_url (SSRF) vive en pipeline.fetcher — importar desde allí directamente.
from pipeline.fetcher import validate_url  # noqa: F401
