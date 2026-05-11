"""pipeline/persistence.py — Persistencia multi-formato de resultados.

Fase 4:
- Parquet particionado por run_date / formato / categoria
- JSON  (.antigravity/team/shared/quality_results.json) — compatibilidad legacy
- CSV   (resultados_calidad_datos_nl.csv) — compatibilidad dashboard
- Snapshots con timestamp + SHA256 (sistema canónico unificado)

Todas las rutas de salida se construyen a partir de constantes para evitar
path-traversal. Los archivos Parquet usan pyarrow nativo (ya en requirements.txt).
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Optional

import pandas as pd
import numpy as np

logger = logging.getLogger("persistence")

# ── Rutas de salida ───────────────────────────────────────────

PARQUET_BASE = os.path.join("data", "parquet")
JSON_OUTPUT  = os.path.join(".antigravity", "team", "shared", "quality_results.json")
CSV_OUTPUT   = "resultados_calidad_datos_nl.csv"
SNAPSHOT_DIR = "snapshots"


# ── Helpers ───────────────────────────────────────────────────

def _safe_makedirs(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _file_sha256(path: str) -> str:
    """SHA-256 hex digest of a file for integrity verification."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _json_default(obj: Any) -> Any:
    """JSON serializer for numpy / pandas scalars."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if pd.isna(obj):  # type: ignore[arg-type]
        return None
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


# ── Parquet (Fase 4 — particionado) ───────────────────────────

def save_parquet(
    df_records: pd.DataFrame,
    run_date: str,
    base_dir: str = PARQUET_BASE,
) -> list[str]:
    """Guarda registros normalizados en Parquet particionado.

    Partición: run_date= / formato= / categoria=
    Columnas mínimas esperadas: run_date, formato, categoria.

    Args:
        df_records: DataFrame con registros normalizados (fact_records_std).
        run_date:   Fecha de la corrida ISO (YYYY-MM-DD).
        base_dir:   Directorio raíz de Parquet.

    Returns:
        Lista de rutas absolutas de archivos escritos.
    """
    if df_records is None or df_records.empty:
        logger.warning("[persistence] No records to save as Parquet")
        return []

    df = df_records.copy()

    # Asegurar columnas de partición
    if "run_date" not in df.columns:
        df["run_date"] = run_date
    if "formato" not in df.columns:
        df["formato"] = "UNKNOWN"
    if "categoria" not in df.columns:
        df["categoria"] = "Sin categoría"

    # Sanitizar valores de partición (pyarrow no acepta "/" en nombres)
    df["formato"]   = df["formato"].astype(str).str.replace(r"[/\\]", "_", regex=True)
    df["categoria"] = df["categoria"].astype(str).str.replace(r"[/\\]", "_", regex=True)

    written: list[str] = []
    for (fmt, cat), group in df.groupby(["formato", "categoria"], observed=True):
        part_dir = os.path.join(
            base_dir,
            f"run_date={run_date}",
            f"formato={fmt}",
            f"categoria={cat}",
        )
        _safe_makedirs(part_dir)
        path = os.path.join(part_dir, "data.parquet")
        group.to_parquet(path, index=False, engine="pyarrow", compression="snappy")
        written.append(os.path.abspath(path))

    logger.info(
        "[persistence] Parquet saved: %d partition(s) in %s",
        len(written), base_dir,
    )
    return written


# ── JSON (legacy compat) ──────────────────────────────────────

def save_json(
    datasets_results: list[dict],
    run_id: str,
    pipeline_version: str = "3.1",
    out_path: str = JSON_OUTPUT,
) -> str:
    """Guarda resultados de calidad en quality_results.json.

    Formato compatible con data_layer.load_results() (fallback JSON).
    """
    _safe_makedirs(os.path.dirname(out_path))

    payload = {
        "generado"         : datetime.now(timezone.utc).isoformat(),
        "run_id"           : run_id,
        "pipeline_version" : pipeline_version,
        "dimensiones"      : 7,
        "datasets"         : datasets_results,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=_json_default)

    sha = _file_sha256(out_path)
    logger.info("[persistence] JSON saved: %s (SHA256: %s…)", out_path, sha[:16])
    return out_path


# ── CSV (legacy compat + dashboard) ──────────────────────────

def save_csv(
    df_quality: pd.DataFrame,
    out_path: str = CSV_OUTPUT,
) -> str:
    """Guarda el DataFrame de scores de calidad como CSV.

    Compatibilidad total con data_layer.load_results() (ruta primaria).
    """
    df_quality.to_csv(out_path, index=False, encoding="utf-8-sig")
    sha = _file_sha256(out_path)
    logger.info(
        "[persistence] CSV saved: %s (%d rows, SHA256: %s…)",
        out_path, len(df_quality), sha[:16],
    )
    return out_path


# ── Reporte de cobertura ──────────────────────────────────────

def save_coverage_report(report: dict, snap_dir: str) -> str:
    """Guarda coverage_report.json en el directorio del snapshot."""
    _safe_makedirs(snap_dir)
    path = os.path.join(snap_dir, "coverage_report.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=_json_default)
    return path


# ── Snapshot con hash ─────────────────────────────────────────

def save_snapshot(
    data: dict,
    snap_dir: str,
    filename: str = "quality_results.json",
) -> tuple[str, str]:
    """Guarda un snapshot con nombre de archivo por timestamp + sha256.txt.

    Formato canónico unificado:
    - <snap_dir>/<filename>   — payload JSON completo
    - <snap_dir>/sha256.txt   — SHA256 hex del archivo JSON

    Args:
        data:     Serializable dict a persistir.
        snap_dir: Directorio destino (se crea si no existe).
        filename: Nombre del archivo JSON (default: quality_results.json).

    Returns:
        (path_absoluto_snapshot, sha256_hex)
    """
    _safe_makedirs(snap_dir)
    snap_path = os.path.join(snap_dir, filename)
    with open(snap_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=_json_default)

    sha = _file_sha256(snap_path)
    with open(os.path.join(snap_dir, "sha256.txt"), "w", encoding="utf-8") as f:
        f.write(sha)

    logger.info("[persistence] Snapshot: %s (SHA256: %s…)", snap_path, sha[:16])
    return os.path.abspath(snap_path), sha


def load_latest_snapshot(
    prefix: str = "quality",
    base_dir: str = SNAPSHOT_DIR,
) -> Optional[dict]:
    """Carga el snapshot más reciente cuyo directorio de run empiece con prefix.

    Busca subdirectorios de <base_dir> con el patrón run_<prefix>* ordenados
    lexicográficamente (los timestamps ISO garantizan orden cronológico).
    Si no existen subdirectorios run_*, busca archivos <prefix>_*.json
    directamente en <base_dir> para compatibilidad con el formato legado de
    fetcher.py.

    Args:
        prefix:   Prefijo del run (ej. "quality", "advanced").
        base_dir: Directorio raíz de snapshots (default: SNAPSHOT_DIR).

    Returns:
        Dict parseado del JSON, o None si no existe ningún snapshot.
    """
    if not os.path.isdir(base_dir):
        return None

    # Estrategia 1: subdirectorios run_<ts>/ con quality_results.json
    run_dirs = sorted(
        d for d in os.listdir(base_dir)
        if d.startswith("run_") and os.path.isdir(os.path.join(base_dir, d))
    )
    for run_dir in reversed(run_dirs):
        snap_path = os.path.join(base_dir, run_dir, "quality_results.json")
        sha_path  = os.path.join(base_dir, run_dir, "sha256.txt")
        if not os.path.isfile(snap_path):
            continue
        # Verificar integridad si sha256.txt existe
        if os.path.isfile(sha_path):
            with open(sha_path, "r", encoding="utf-8") as f:
                expected_sha = f.read().strip()
            actual_sha = _file_sha256(snap_path)
            if actual_sha != expected_sha:
                logger.warning(
                    "[persistence] SHA256 mismatch en %s — saltando snapshot",
                    snap_path,
                )
                continue
        with open(snap_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # Estrategia 2 (legado): archivos <prefix>_<ts>.json en base_dir
    legacy_files = sorted(
        fn for fn in os.listdir(base_dir)
        if fn.startswith(prefix) and fn.endswith(".json")
    )
    if legacy_files:
        path = os.path.join(base_dir, legacy_files[-1])
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    return None
