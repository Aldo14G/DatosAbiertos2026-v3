"""
data_discovery.py — Descubrimiento del portal y carga de resultados.

Responsabilidades:
  - Descarga del catálogo CKAN (fetch_portal_catalog y fallback legacy)
  - Carga de resultados desde CSV / JSON / BigQuery (load_results, _load_raw)
  - Normalización de categorías y deduplicación
  - Coverage report de snapshots
"""

import json
import os
import time

import numpy as np
import pandas as pd
import requests

try:
    from google.cloud import bigquery
    from google.cloud.exceptions import NotFound

    _BQ_AVAILABLE = True
except ImportError:
    _BQ_AVAILABLE = False

from functools import lru_cache

from config import QUALITY_WEIGHTS  # noqa: E402

CKAN_API = "https://catalogodatos.nl.gob.mx/api/3/action"
DELAY_SEC = 1.5

# Columnas mínimas para que el dashboard funcione
_REQUIRED_COLS = {
    "dataset",
    "categoria",
    "organizacion",
    "filas",
    "comp_completitud_global_pct",
    "acc_score_accuracy_pct",
    "cons_score_consistency_pct",
    "uniq_score_uniqueness_pct",
    "time_score_timeliness_pct",
    "doc_score_documentation_pct",
    "open_score_openness_pct",
    "score_global",
}

_ADVANCED_JSON_PATH = os.path.join(
    ".antigravity",
    "team",
    "shared",
    "advanced_quality_results.json",
)
_MAIN_JSON_PATH = os.path.join(
    ".antigravity",
    "team",
    "shared",
    "quality_results.json",
)


# ── 1. DESCUBRIMIENTO ─────────────────────────────────────────


@lru_cache(maxsize=1)
def fetch_portal_catalog() -> list[dict]:
    """[Fase 1] Descarga el catálogo CKAN completo vía ckan_client robusto.

    Usa retry + backoff + fallback package_list para garantizar descubrimiento
    completo. Retorna TODOS los formatos extractables (no sólo CSV).
    """
    try:
        from pipeline.ckan_client import discover_catalog

        return discover_catalog(use_fallback=True)
    except Exception as exc:
        import logging

        logging.getLogger("data_discovery").error(
            "ckan_client unavailable (%s) — falling back to legacy fetch", exc
        )
        return _legacy_fetch_portal_catalog()


def _legacy_fetch_portal_catalog() -> list[dict]:
    """Descubrimiento CSV-only sin retry — usado como fallback de emergencia."""
    datasets, start = [], 0
    while True:
        r = requests.get(
            f"{CKAN_API}/package_search",
            params={"rows": 100, "start": start},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        results = data["result"]["results"]
        total = data["result"]["count"]
        if not results:
            break
        for ds in results:
            org = (ds.get("organization") or {}).get("title", "Desconocida")
            grupos = [g.get("title", "") for g in ds.get("groups", [])]
            cat = grupos[0].strip().title() if grupos else "Sin categoría"
            for recurso in ds.get("resources", []):
                fmt = recurso.get("format", "").upper().strip()
                if fmt not in ("CSV", ".CSV"):
                    continue
                datasets.append(
                    {
                        "slug": ds.get("name", ""),
                        "recurso_id": recurso.get("id", ""),
                        "dataset": ds.get("title", "Sin nombre"),
                        "organizacion": org,
                        "categoria": cat,
                        "formato": fmt,
                        "url": recurso.get("url", ""),
                        "modificado": ds.get("metadata_modified", ""),
                        "frecuencia_update": ds.get("frequency", "").lower().strip()
                        if isinstance(ds.get("frequency"), str)
                        else "",
                        "descripcion": ds.get("notes", "") or "",
                        "licencia": ds.get("license_title", "") or "",
                        "licencia_id": ds.get("license_id", "") or "",
                        "num_resources": len(ds.get("resources", [])),
                        "resource_formats": [
                            rx.get("format", "").upper().strip()
                            for rx in ds.get("resources", [])
                        ],
                        "resource_descs": [
                            rx.get("description", "") or ""
                            for rx in ds.get("resources", [])
                        ],
                    }
                )
        start += len(results)
        if start >= total:
            break
        time.sleep(DELAY_SEC)
    return datasets


# ── 2. NORMALIZACIÓN DE CATEGORÍAS ────────────────────────────


def normalize_categories(df: pd.DataFrame) -> pd.DataFrame:
    corrections = {
        "Administración Y Finanzas": "Administración y Finanzas",
        "Arte Y Cultura": "Arte y Cultura",
        "Perspectiva De Género E Interseccionalidad": "Perspectiva de Género",
        "Transparencia Y Combate A La Corrupción": "Transparencia y Anticorrupción",
        "Transparencia Y Anticorrupción": "Transparencia y Anticorrupción",
        "Atención Ciudadana": "Atención Ciudadana",
        "Gobierno Y Transparencia": "Gobierno y Transparencia",
        "Igualdad De Género": "Igualdad de Género",
        "Desarrollo Urbano": "Desarrollo Urbano",
        "Medio Ambiente": "Medio Ambiente",
        "Asistencia Social": "Asistencia Social",
    }
    df = df.copy()
    if "categoria" in df.columns:
        df["categoria"] = (
            df["categoria"].astype(str).str.strip().str.title().replace(corrections)
        )
    return df


# ── 3. CARGA DE RESULTADOS ─────────────────────────────────────


def load_results(path: str = "") -> pd.DataFrame:
    """
    [FIX-3] Carga datos desde CSV o fallback JSON.
    Valida el esquema antes de retornar; levanta error descriptivo si faltan columnas.
    [FIX-8] Deduplicación por slug: cuando un dataset tiene múltiples recursos CSV,
    se conserva sólo el registro con el mayor score_global para evitar inflación de KPIs.
    """
    df = _load_raw(path)
    df = normalize_categories(df)
    df = _deduplicate_by_slug(df)
    _validate_schema(df)

    if "organizacion" in df.columns:
        df["organizacion"] = df["organizacion"].astype(str).str.strip()

    return df


def _load_raw(path: str) -> pd.DataFrame:
    if os.getenv("USE_BIGQUERY", "false").lower() == "true":
        return _load_from_bigquery()

    if path:
        abs_path = os.path.abspath(path)
        base_dir = os.path.abspath(os.getcwd())
        if not abs_path.startswith(base_dir):
            raise PermissionError(
                "Path traversal detectado. Acceso denegado a rutas fuera del directorio de trabajo."
            )

    csv_path = path or "resultados_calidad_datos_nl.csv"
    try:
        return pd.read_csv(csv_path, encoding="utf-8-sig")
    except FileNotFoundError:
        pass

    json_path = ".antigravity/team/shared/quality_results.json"
    try:
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"No se encontró '{csv_path}' ni '{json_path}'. "
            "Ejecuta primero el pipeline de calidad."
        ) from exc

    rows = []
    for d in data.get("datasets", []):
        scores = d.get("scores")
        if scores is None:
            continue

        missing = {"completeness", "accuracy", "consistency", "uniqueness"} - set(scores)
        if missing:
            raise KeyError(
                f"Dataset '{d.get('slug')}' en el JSON le faltan claves: {missing}"
            )

        available_dims = {}
        for wk in QUALITY_WEIGHTS:
            if wk in scores and scores[wk] is not None:
                available_dims[wk] = scores[wk]
        if not available_dims:
            continue
        w_avail = {k: QUALITY_WEIGHTS[k] for k in available_dims}
        total_w = sum(w_avail.values())
        score_glob = round(
            sum(available_dims[k] * w_avail[k] for k in available_dims) / total_w,
            2,
        )

        rows.append(
            {
                "dataset": d.get("slug", ""),
                "categoria": d.get("categoria", ""),
                "organizacion": d.get("organizacion", ""),
                "filas": d.get("filas", 0),
                "columnas": d.get("columnas", 0),
                "modificado": d.get("metadata_modified", ""),
                "frecuencia_update": d.get("frequency", ""),
                "comp_completitud_global_pct": scores.get("completeness", 0),
                "acc_score_accuracy_pct": scores.get("accuracy", 0),
                "cons_score_consistency_pct": scores.get("consistency", 0),
                "uniq_score_uniqueness_pct": scores.get("uniqueness", 0),
                "time_score_timeliness_pct": scores.get("timeliness", np.nan),
                "doc_score_documentation_pct": scores.get("documentation", 0),
                "open_score_openness_pct": scores.get("openness", 0),
                "score_global": score_glob,
            }
        )

    return pd.DataFrame(rows)


def _load_from_bigquery() -> pd.DataFrame:
    """Carga los resultados directamente desde BigQuery en GCP."""
    if not _BQ_AVAILABLE:
        raise ImportError("google-cloud-bigquery no está instalado.")
    client = bigquery.Client()
    project = os.getenv("GOOGLE_CLOUD_PROJECT", "datos-abiertos-nl")
    dataset = os.getenv("BQ_DATASET", "catalogo_datasets")
    table = os.getenv("BQ_TABLE", "resultados_calidad")
    query = f"SELECT * FROM `{project}.{dataset}.{table}`"
    try:
        return client.query(query).to_dataframe()
    except NotFound:
        return pd.DataFrame()


def save_to_bigquery(df: pd.DataFrame) -> None:
    """Despacha (vía append) el DataFrame de resultados a BigQuery."""
    if not _BQ_AVAILABLE:
        raise ImportError("google-cloud-bigquery no está instalado.")
    client = bigquery.Client()
    project = os.getenv("GOOGLE_CLOUD_PROJECT", "datos-abiertos-nl")
    dataset = os.getenv("BQ_DATASET", "catalogo_datasets")
    table = os.getenv("BQ_TABLE", "resultados_calidad")
    table_id = f"{project}.{dataset}.{table}"
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()


def _deduplicate_by_slug(df: pd.DataFrame) -> pd.DataFrame:
    """[FIX-8] Deduplica múltiples recursos del mismo dataset.

    Un dataset CKAN puede tener varios recursos (ej. diccionario + datos).
    Priorizamos el recurso con mayor número de filas (datos principales)
    y usamos el score_global como criterio de desempate.
    """
    if "dataset" not in df.columns or "score_global" not in df.columns:
        return df

    if "filas" in df.columns:
        df["filas"] = pd.to_numeric(df["filas"], errors="coerce").fillna(0)

    deduped = (
        df.sort_values(by=["filas", "score_global"], ascending=[False, False])
        .drop_duplicates(subset=["dataset"], keep="first")
        .reset_index(drop=True)
    )
    return deduped


def _validate_schema(df: pd.DataFrame) -> None:
    missing = _REQUIRED_COLS - set(df.columns)
    if missing:
        raise ValueError(
            f"DataFrame de resultados sin columnas requeridas: {missing}. "
            "Verifica compatibilidad del CSV o JSON con data_layer v2.2."
        )


# ── 4. PIPELINE COVERAGE ─────────────────────────────────────


def load_coverage_report() -> dict | None:
    """Carga el coverage report del snapshot de pipeline mas reciente.

    Escanea ``snapshots/`` buscando directorios ``run_*`` (orden
    descendente = mas reciente primero) y lee ``coverage_report.json``
    del primer directorio valido encontrado.

    Returns
    -------
    dict | None
        Claves: run_id, total_catalogo, procesados_exitosos, fallidos,
        cobertura_pct, elapsed_total_s, avg_time_per_dataset_s,
        failed_details, snapshot_sha256.
        ``None`` si no existe ningun snapshot legible.
    """
    snapshots_dir = os.path.join(os.getcwd(), "snapshots")
    try:
        entries = sorted(
            [e for e in os.listdir(snapshots_dir) if e.startswith("run_")],
            reverse=True,
        )
    except FileNotFoundError:
        return None

    for entry in entries:
        report_path = os.path.join(snapshots_dir, entry, "coverage_report.json")
        try:
            with open(report_path, encoding="utf-8") as fh:
                report = json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError, PermissionError):
            continue

        if "snapshot_sha256" not in report:
            sha_path = os.path.join(snapshots_dir, entry, "sha256.txt")
            try:
                with open(sha_path, encoding="utf-8") as sf:
                    report["snapshot_sha256"] = sf.read().strip()
            except (FileNotFoundError, PermissionError):
                pass

        return report

    return None


def get_resource_vs_unique_count(path: str = "") -> dict[str, int]:
    """Retorna conteo de recursos pre-dedup vs datasets unicos post-dedup.

    Util para mostrar en UI la diferencia entre recursos evaluados por
    el pipeline (277) y datasets unicos tras deduplicacion (105).

    Returns
    -------
    dict[str, int]
        ``{"resources_evaluated": int, "unique_datasets": int}``
    """
    raw = _load_raw(path)
    raw = normalize_categories(raw)
    deduped = _deduplicate_by_slug(raw)
    return {
        "resources_evaluated": len(raw),
        "unique_datasets": len(deduped),
    }
