"""
data_layer.py  — v2.2
Capa de acceso a datos: portal Datos Abiertos NL (catalogodatos.nl.gob.mx).
Funciones puras, sin estado, cacheables.

Cambios v2.2:
  [FIX-1] compute_accuracy     : penalización proporcional al % de cols afectadas.
  [FIX-2] compute_consistency  : umbral IQR elevado a n >= 30 (robustez estadística).
  [FIX-3] load_results         : validación de esquema en fallback JSON; sin NaN silencioso.
  [FIX-4] compute_quality_scores: pesos configurables por dimensión (ISO 25012).
  [FIX-5] get_aggregations     : rename dinámico via dict; no se desalinea si falta puntualidad.
  [NEW-6] compute_timeliness   : 5ª dimensión — latencia de actualización vs declarada.
  [NEW-7] fetch_portal_catalog : evalúa TODOS los recursos CSV por dataset (no sólo el primero).
"""

import csv
import io
import json
import os
import time
import unicodedata
from urllib.parse import urlparse

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

CKAN_API = "https://catalogodatos.nl.gob.mx/api/3/action"
DELAY_SEC = 1.5

# Formatos soportados para descarga multiformato (Fase 2)
_MULTIFORMAT_PARSERS: frozenset[str] = frozenset(
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

# ── PESOS ISO 25012 ───────────────────────────────────────────
# Fuente única: config.py. No redefinir aquí.
from config import CLASIFICACION_DEFAULT, CLASIFICACION_THRESHOLDS, QUALITY_WEIGHTS  # noqa: E402
from quality_scorer import BREAKDOWN_SCORE_KEYS, QualityScorer  # noqa: E402
from pipeline.fetcher import validate_url  # noqa: E402

# Etiquetas de presentación para cada columna de dimensión.
# Las claves deben ser un subconjunto de BREAKDOWN_SCORE_KEYS  {"score_global"};
# el assert a continuación detecta desincronización en tiempo de importación.
DIM_LABEL_MAP: dict[str, str] = {
    "comp_completitud_global_pct": "Completitud",
    "acc_score_accuracy_pct": "Exactitud",
    "cons_score_consistency_pct": "Consistencia",
    "uniq_score_uniqueness_pct": "Unicidad",
    "time_score_timeliness_pct": "Puntualidad",
    "doc_score_documentation_pct": "Documentación",
    "open_score_openness_pct": "Apertura",
    "score_global": "Score Global",
}

_VALID_DIM_KEYS = BREAKDOWN_SCORE_KEYS | {"score_global"}
_UNKNOWN_DIM_KEYS = set(DIM_LABEL_MAP) - _VALID_DIM_KEYS
assert not _UNKNOWN_DIM_KEYS, (
    f"DIM_LABEL_MAP contiene claves desconocidas para BreakdownDict: {_UNKNOWN_DIM_KEYS}. "
    "Actualiza BREAKDOWN_SCORE_KEYS en quality_scorer.py o corrige DIM_LABEL_MAP."
)

_scorer = QualityScorer()

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
        # Fallback al método original si ckan_client no está disponible
        import logging

        logging.getLogger("data_layer").error(
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
                            rx.get("format", "").upper().strip() for rx in ds.get("resources", [])
                        ],
                        "resource_descs": [
                            rx.get("description", "") or "" for rx in ds.get("resources", [])
                        ],
                    }
                )
        start += len(results)
        if start >= total:
            break
        time.sleep(DELAY_SEC)
    return datasets


# ── 2. DESCARGA Y NORMALIZACIÓN ────────────────────────────────


def download_csv(url: str) -> pd.DataFrame | None:
    """Download CSV resources with robust charset detection and separator inference.
    Returns a pandas DataFrame or None on failure.
    """
    import logging as _logging
    _log = _logging.getLogger("data_layer")
    if not validate_url(url):
        _log.warning("URL rechazada por política de seguridad SSRF: %s", url)
        return None

    try:
        r = requests.get(
            url,
            timeout=30,
            headers={"User-Agent": "DatosAbiertosNL-Analyzer/2.2"},
        )
        r.raise_for_status()
        for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
            try:
                text = r.content.decode(enc)
            except UnicodeDecodeError:
                continue
            for sep in (None, ",", ";", "\t", "|"):
                try:
                    df = pd.read_csv(
                        io.StringIO(text),
                        sep=sep,
                        engine="python" if sep is None else "c",
                    )
                    if df.shape[1] >= 2 or sep is not None:
                        return df
                except (pd.errors.ParserError, ValueError, csv.Error):
                    continue
    except (requests.RequestException, UnicodeDecodeError, pd.errors.ParserError):
        pass
    return None


def download_resource(url: str, formato: str) -> pd.DataFrame | None:
    """[Fase 2] Descarga y parsea un recurso según su formato.

    Soporta: CSV, JSON, XLSX/XLS, GEOJSON, XML.
    PDF retorna None (sólo metadatos, sin extracción tabular).
    Todos los formatos pasan por validación SSRF antes de descargar.

    Cuando el formato declarado en CKAN no coincide con la extensión real
    de la URL (ej: declara CSV pero la URL termina en .xlsx), la extensión
    de la URL toma precedencia para elegir el parser correcto.
    """
    fmt = (formato or "").upper().strip()

    if fmt == "PDF":
        return None  # PDF: sólo metadatos

    # Resolver formato real desde extensión de URL cuando hay mismatch
    url_ext = os.path.splitext(urlparse(url).path)[1].upper().lstrip(".")
    _EXT_OVERRIDE: dict[str, str] = {
        "XLSX": "XLSX",
        "XLS": "XLS",
        "JSON": "JSON",
        "GEOJSON": "GEOJSON",
        "XML": "XML",
        "CSV": "CSV",
    }
    if url_ext in _EXT_OVERRIDE and _EXT_OVERRIDE[url_ext] != fmt.lstrip("."):
        fmt = _EXT_OVERRIDE[url_ext]

    if fmt in ("CSV", ".CSV"):
        return download_csv(url)

    if not validate_url(url):
        return None

    try:
        r = requests.get(
            url,
            timeout=(10, 60),
            headers={"User-Agent": "DatosAbiertosNL-Analyzer/2.2"},
        )
        r.raise_for_status()
        content = r.content
    except requests.RequestException:
        return None

    try:
        if fmt == "JSON":
            return _parse_json(content)
        if fmt in ("XLSX", "XLS"):
            return _parse_excel(content)
        if fmt == "GEOJSON":
            return _parse_geojson(content)
        if fmt == "XML":
            return _parse_xml(content)
    except Exception:
        pass
    return None


def _detect_encoding(content: bytes) -> str:
    """Detecta encoding por chardet o defaultea a utf-8."""
    try:
        import chardet

        result = chardet.detect(content[:10_000])
        return result.get("encoding") or "utf-8"
    except ImportError:
        return "utf-8"


def _parse_json(content: bytes) -> pd.DataFrame | None:
    import json as _json

    enc = _detect_encoding(content)
    data = _json.loads(content.decode(enc, errors="replace"))
    if isinstance(data, list):
        return pd.json_normalize(data, max_level=3)
    if isinstance(data, dict):
        # Find the largest array in the dict
        arrays = {k: v for k, v in data.items() if isinstance(v, list) and v}
        if arrays:
            key = max(arrays, key=lambda k: len(arrays[k]))
            return pd.json_normalize(arrays[key], max_level=3)
        return pd.json_normalize([data])
    return None


def _parse_excel(content: bytes) -> pd.DataFrame | None:
    sheets = pd.read_excel(io.BytesIO(content), sheet_name=None, engine="openpyxl")
    if not sheets:
        return None
    if len(sheets) == 1:
        return list(sheets.values())[0]
    # Return the sheet with most rows
    return max(sheets.values(), key=len)


def _parse_geojson(content: bytes) -> pd.DataFrame | None:
    import json as _json

    enc = _detect_encoding(content)
    data = _json.loads(content.decode(enc, errors="replace"))
    features = data.get("features", [])
    if not features:
        return None
    rows = []
    for f in features:
        row = dict(f.get("properties") or {})
        geo = f.get("geometry") or {}
        row["geometry_type"] = geo.get("type", "")
        rows.append(row)
    return pd.DataFrame(rows) if rows else None


def _parse_xml(content: bytes) -> pd.DataFrame | None:
    try:
        return pd.read_xml(io.BytesIO(content))
    except Exception:
        pass
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(content, "lxml-xml")
        tag_counts: dict[str, int] = {}
        for el in soup.find_all(True):
            tag_counts[el.name] = tag_counts.get(el.name, 0) + 1
        if not tag_counts:
            return None
        main_tag = max(tag_counts, key=tag_counts.get)  # type: ignore[arg-type]
        records = []
        for el in soup.find_all(main_tag):
            rec = {
                child.name: child.get_text(strip=True)
                for child in el.children
                if hasattr(child, "name") and child.name
            }
            if rec:
                records.append(rec)
        return pd.DataFrame(records) if records else None
    except Exception:
        return None


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
        df["categoria"] = df["categoria"].astype(str).str.strip().str.title().replace(corrections)
    return df


# ── 3. MÉTRICAS DE CALIDAD (delegado a QualityScorer) ─────────


def compute_quality_scores(meta: dict, df: pd.DataFrame) -> dict:
    result = _scorer.score(meta, df)
    row = {
        "dataset"          : meta.get("dataset", ""),
        "slug"             : meta.get("slug", ""),
        "recurso_id"       : meta.get("recurso_id", ""),
        "categoria"        : meta.get("categoria", ""),
        "organizacion"     : meta.get("organizacion", ""),
        "filas"            : len(df),
        "columnas"         : len(df.columns),
        "modificado"       : meta.get("modificado", ""),
        "frecuencia_update": meta.get("frecuencia_update", ""),
    }
    row.update(result["breakdown"])
    row["score_global"] = result["global_score"]
    return row


# ── 4. AGREGACIÓN ─────────────────────────────────────────────


def get_aggregations(df: pd.DataFrame, by: str = "categoria") -> pd.DataFrame:
    """
    [FIX-5] Rename dinámico via DIM_LABEL_MAP — no se desalinea si
    falta alguna dimensión (e.g. puntualidad en carga desde JSON).
    """
    dim_cols = list(DIM_LABEL_MAP.keys())
    cols_ok = [c for c in dim_cols if c in df.columns]

    agg = (
        df.groupby(by)[cols_ok]
        .mean()
        .round(1)
        .sort_values("score_global", ascending=False)
        .reset_index()
    )
    rename_map = {c: DIM_LABEL_MAP.get(c, c) for c in cols_ok}
    agg = agg.rename(columns=rename_map)

    # Agregar conteo de datasets por grupo
    counts = df.groupby(by).size().reset_index(name="n_datasets")
    agg = agg.merge(counts, on=by, how="left")
    return agg


def apply_filters(
    df: pd.DataFrame,
    categorias: list[str] | None = None,
    organizaciones: list[str] | None = None,
    formatos: list[str] | None = None,
    score_min: float = 0,
    score_max: float = 100,
) -> pd.DataFrame:
    """Aplica filtros combinados sobre el DataFrame de resultados.

    Args:
        categorias:     Lista de categorías a incluir (None = todas).
        organizaciones: Lista de organizaciones a incluir (None = todas).
        formatos:       Lista de formatos a incluir (None = todos). [Fase 5]
        score_min/max:  Rango de score global [0, 100].
    """
    mask = pd.Series([True] * len(df), index=df.index)

    if categorias and "categoria" in df.columns and "Todas" not in categorias:
        mask &= df["categoria"].isin(categorias)
    if organizaciones and "organizacion" in df.columns and "Todas" not in organizaciones:
        mask &= df["organizacion"].isin(organizaciones)
    if formatos and "formato" in df.columns and "Todos" not in formatos:
        mask &= df["formato"].isin(formatos)
    if "score_global" in df.columns:
        mask &= (df["score_global"] >= score_min) & (df["score_global"] <= score_max)

    return df[mask].copy()


# ── 5. CARGA DE RESULTADOS ─────────────────────────────────────


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

    # [FIX] Clean data fragmentation: strip leading/trailing spaces from agency names
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
            f"No se encontró '{csv_path}' ni '{json_path}'. Ejecuta primero el pipeline de calidad."
        ) from exc

    rows = []
    for d in data.get("datasets", []):
        scores = d.get("scores")
        if scores is None:
            continue

        missing = {"completeness", "accuracy", "consistency", "uniqueness"} - set(scores)
        if missing:
            raise KeyError(f"Dataset '{d.get('slug')}' en el JSON le faltan claves: {missing}")

        # [FIX-4] Recalcular score_global con pesos disponibles
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

    # Asegurar que filas sea numérico para el sort
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


# ── 6. PIPELINE COVERAGE ─────────────────────────────────────


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

        # Incorporar SHA-256 desde archivo auxiliar si no esta en el JSON.
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


# ── 7. CLASIFICACION Y MERGE AVANZADO ──────────────────────────

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


def classify_score(score: float) -> str:
    """Deriva etiqueta de clasificacion desde score_global."""
    for threshold, label in CLASIFICACION_THRESHOLDS:
        if score >= threshold:
            return label
    return CLASIFICACION_DEFAULT


@lru_cache(maxsize=512)
def _normalize_title(title: str) -> str:
    """Normaliza titulo para join entre pipelines (lower + strip + ASCII)."""
    return unicodedata.normalize("NFKD", title.strip().lower()).encode("ascii", "ignore").decode()


@lru_cache(maxsize=1)
def _load_advanced_json() -> dict | None:
    """Lee advanced_quality_results.json una sola vez (cached en proceso)."""
    try:
        with open(_ADVANCED_JSON_PATH, encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError, PermissionError):
        return None


@lru_cache(maxsize=1)
def _build_slug_to_title_map() -> dict[str, str]:
    """Construye mapa slug→titulo desde el JSON principal del pipeline."""
    try:
        with open(_MAIN_JSON_PATH, encoding="utf-8") as fh:
            data = json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError, PermissionError):
        return {}

    return {
        d["slug"]: d["dataset"]
        for d in data.get("datasets", [])
        if d.get("slug") and d.get("dataset")
    }


def load_advanced_overlay() -> pd.DataFrame | None:
    """Retorna DataFrame de overlay multi-framework por dataset (Pipeline B).

    Columnas: ``_titulo_norm``, ``score_iso_25012``, ``score_iso_8000``,
    ``score_dama``, ``n_problemas``.  ``None`` si el archivo no existe.
    """
    data = _load_advanced_json()
    if data is None:
        return None

    reportes = data.get("reportes_datasets", [])
    if not reportes:
        return None

    rows = [
        {
            "_titulo_norm": _normalize_title(rd.get("titulo", "")),
            "score_iso_25012": float(rd.get("score_iso_25012", 0) or 0),
            "score_iso_8000": float(rd.get("score_iso_8000", 0) or 0),
            "score_dama": float(rd.get("score_dama", 0) or 0),
            "n_problemas": len(rd.get("problemas", [])),
            "_adv_global": float(rd.get("score_global", 0) or 0),
        }
        for rd in reportes
    ]

    return (
        pd.DataFrame(rows)
        .sort_values("_adv_global", ascending=False)
        .drop_duplicates(subset=["_titulo_norm"], keep="first")
        .drop(columns=["_adv_global"])
        .reset_index(drop=True)
    )


def merge_advanced_overlay(df: pd.DataFrame) -> pd.DataFrame:
    """Une el DataFrame canonico (Pipeline A) con el overlay avanzado (Pipeline B).

    Agrega columnas multi-framework y clasificacion derivada a cada dataset.
    Degrada graciosamente si el JSON avanzado no existe (columnas ISO/DAMA = NaN).
    """
    result = df.copy()
    result["clasificacion"] = result["score_global"].apply(classify_score)

    slug_to_title = _build_slug_to_title_map()
    if slug_to_title and "dataset" in result.columns:
        result["_titulo_norm"] = result["dataset"].map(
            lambda s: _normalize_title(slug_to_title.get(s, s))
        )
    else:
        result["_titulo_norm"] = result["dataset"].apply(_normalize_title)

    overlay = load_advanced_overlay()
    if overlay is not None and not overlay.empty:
        result = result.merge(overlay, on="_titulo_norm", how="left")
        result["has_advanced"] = result["score_iso_25012"].notna()
    else:
        result["score_iso_25012"] = np.nan
        result["score_iso_8000"] = np.nan
        result["score_dama"] = np.nan
        result["n_problemas"] = np.nan
        result["has_advanced"] = False

    return result.drop(columns=["_titulo_norm"], errors="ignore")


def load_advanced_catalog_stats() -> dict | None:
    """Retorna metricas de catalogo del JSON avanzado (valor unico de Pipeline B).

    Claves: ``total_problemas_detectados``, ``problemas_por_severidad``,
    ``problemas_por_categoria``, ``score_promedio_avanzado``.
    """
    data = _load_advanced_json()
    if data is None:
        return None

    return {
        "total_problemas_detectados": int(data.get("total_problemas_detectados", 0) or 0),
        "problemas_por_severidad": data.get("problemas_por_severidad", {}),
        "problemas_por_categoria": data.get("problemas_por_categoria", {}),
        "score_promedio_avanzado": float(data.get("score_promedio_catalogo", 0) or 0),
    }


# ── Helpers de agregación reutilizables ───────────────────────


def agg_dim_means_by(
    df: pd.DataFrame,
    group_col: str,
    *,
    rename: bool = False,
) -> pd.DataFrame:
    """Agrupa df por `group_col` y calcula la media de las columnas de dimensión ISO disponibles.

    Con rename=True las columnas se renombran al label de visualización (DIM_LABEL_MAP).
    Retorna DataFrame vacío si no hay columnas de dimensión en df o group_col no existe.
    """
    dim_map = {k: v for k, v in DIM_LABEL_MAP.items() if k != "score_global"}
    available = {k: v for k, v in dim_map.items() if k in df.columns}
    if not available or group_col not in df.columns:
        return pd.DataFrame()

    result = df.groupby(group_col)[list(available.keys())].mean()
    if rename:
        result = result.rename(columns=available)
    return result


def agg_org_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega estadísticas de calidad por organización.

    Retorna un DataFrame con columnas: organizacion, n_datasets, score_global
    y todas las dimensiones ISO disponibles. Ordenado por score_global descendente,
    redondeado a 1 decimal.
    """
    if "organizacion" not in df.columns:
        return pd.DataFrame()

    agg_dict: dict = {
        "n_datasets"  : ("dataset",      "count"),
        "score_global": ("score_global", "mean"),
    }
    for col in DIM_LABEL_MAP:
        if col != "score_global" and col in df.columns:
            agg_dict[col] = (col, "mean")

    stats = df.groupby("organizacion", as_index=False).agg(**agg_dict)
    return stats.sort_values("score_global", ascending=False).reset_index(drop=True).round(1)
