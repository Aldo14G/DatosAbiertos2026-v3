"""
Pipeline de Refresh Engine — Orquestador de calidad de datos.
v3.1: 7 dimensiones (5 ISO 25012 + Documentation + Openness).

Estructura de etapas:
  run_discovery   → obtiene lista de recursos del catálogo CKAN.
  run_extraction  → descarga y normaliza cada recurso a DataFrame.
  run_evaluation  → calcula scores ISO 25012 y mapea al esquema JSON.
  run_persistence → guarda JSON, CSV, Parquet y snapshot.
  run_pipeline    → orquesta las etapas anteriores (~30 líneas).
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import pandas as pd
import numpy as np

# Asegurar que el directorio raíz del proyecto esté en sys.path
# para importar data_layer y config cuando se ejecuta como script.
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import data_layer
from config import QUALITY_WEIGHTS
from pipeline.normalizer import normalize_df
from pipeline.persistence import (
    save_csv,
    save_json,
    save_parquet,
    save_snapshot,
    save_coverage_report,
)

# ai_enrichment se importa de forma opcional: depende de Vertex AI (GCP).
# Si las credenciales no están disponibles, el pipeline sigue sin enriquecer.
try:
    from pipeline.ai_enrichment import enrich_dataset_metadata as _enrich
    _AI_ENRICHMENT_AVAILABLE = True
except ImportError:
    _AI_ENRICHMENT_AVAILABLE = False

# ── Logging estructurado ──────────────────────────────────────
logger = logging.getLogger("refresh_engine")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"
    ))
    logger.addHandler(handler)

# ── Rutas de salida ───────────────────────────────────────────
OUTPUT_DIR           = os.path.join(".antigravity", "team", "shared")
OUTPUT_FILE          = os.path.join(OUTPUT_DIR, "quality_results.json")
ADVANCED_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "advanced_quality_results.json")
CSV_OUTPUT_FILE      = "resultados_calidad_datos_nl.csv"
PIPELINE_LOG_FILE    = os.path.join(OUTPUT_DIR, "pipeline_log.json")
SNAPSHOTS_DIR        = "snapshots"

_LAST_RUN_FILE = os.path.join(OUTPUT_DIR, "last_run.txt")


# ── PipelineConfig ────────────────────────────────────────────

@dataclass(frozen=True)
class PipelineConfig:
    """Configuración inmutable de una ejecución del pipeline.

    Todos los parámetros que antes se pasaban por variables de entorno
    o estaban hardcodeados se centralizan aquí.
    """

    force: bool = False
    """Ignorar el TTL de 24h y forzar ejecución."""

    limit: int = 0
    """Si > 0, procesar sólo los primeros N datasets (dry-run)."""

    snapshot_dir: str = ""
    """Directorio para guardar snapshot. Default: snapshots/run_<run_id>/."""

    output_dir: str = OUTPUT_DIR
    """Directorio de salida para archivos JSON y log."""

    output_file: str = OUTPUT_FILE
    """Ruta del archivo quality_results.json."""

    csv_output_file: str = CSV_OUTPUT_FILE
    """Ruta del archivo CSV de resultados."""

    pipeline_log_file: str = PIPELINE_LOG_FILE
    """Ruta del archivo pipeline_log.json."""

    snapshots_base_dir: str = SNAPSHOTS_DIR
    """Directorio raíz para snapshots."""

    use_bigquery: bool = field(
        default_factory=lambda: os.getenv("USE_BIGQUERY", "false").lower() == "true"
    )
    """Despachar resultados a BigQuery si True."""

    request_delay_s: float = 1.0
    """Pausa entre requests al servidor CKAN (segundos)."""

    coverage_warn_threshold: float = 90.0
    """Emitir WARNING si la cobertura del pipeline cae por debajo de este %."""


# ── TTL helpers ───────────────────────────────────────────────

def requires_refresh(hours: int = 24) -> bool:
    """Determina si el pipeline necesita re-ejecución (basado en TTL)."""
    if not os.path.exists(_LAST_RUN_FILE):
        return True
    try:
        with open(_LAST_RUN_FILE, "r") as f:
            ts = datetime.fromisoformat(f.read().strip())
        return (datetime.now(timezone.utc) - ts).total_seconds() > hours * 3600
    except Exception:
        return True


def _save_last_run() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(_LAST_RUN_FILE, "w") as f:
        f.write(datetime.now(timezone.utc).isoformat())


# ── Stage 1: Discovery ────────────────────────────────────────

class DiscoveryError(RuntimeError):
    """CRITICA: no se pudo obtener el catálogo — el pipeline no puede continuar."""


def run_discovery(config: PipelineConfig) -> list[dict]:
    """Descarga el catálogo completo desde la API CKAN.

    Etapa CRITICA: si falla, lanza DiscoveryError y el pipeline se detiene.

    Args:
        config: Configuración del pipeline.

    Returns:
        Lista de metadatos de recursos (dicts) del catálogo.
        Si config.limit > 0 devuelve sólo los primeros N elementos.
    """
    logger.info("Descargando catalogo desde CKAN API...")
    try:
        catalog: list[dict] = data_layer.fetch_portal_catalog()
    except Exception as exc:
        raise DiscoveryError(f"Error al descargar catalogo: {exc}") from exc

    if config.limit > 0:
        logger.info("Modo dry-run: procesando solo %d datasets", config.limit)
        catalog = catalog[: config.limit]

    logger.info("Descubrimiento: %d recursos encontrados", len(catalog))
    return catalog


# ── Stage 2: Extraction ───────────────────────────────────────

@dataclass
class ExtractionResult:
    """Resultado de la extracción de un recurso individual."""

    slug: str
    meta: dict
    df: pd.DataFrame | None
    error: str | None = None


def _extract_one(meta: dict, config: PipelineConfig) -> ExtractionResult:
    """Descarga y normaliza un único recurso.

    TOLERANTE: devuelve ExtractionResult con df=None si falla; el pipeline
    continúa con los demás recursos.
    """
    slug = meta.get("slug", "desconocido")
    url = meta.get("url")
    if not url:
        return ExtractionResult(slug=slug, meta=meta, df=None, error="No URL valida")

    formato = meta.get("formato", "CSV")
    df = data_layer.download_resource(url, formato)
    if df is None:
        return ExtractionResult(
            slug=slug, meta=meta, df=None,
            error=f"Fallo al descargar {formato}: {url}",
        )

    try:
        df = normalize_df(df, formato)
    except Exception as norm_exc:
        logger.warning("Normalizacion parcial (%s): %s", slug, norm_exc)

    return ExtractionResult(slug=slug, meta=meta, df=df)


def run_extraction(
    resources: list[dict],
    config: PipelineConfig,
) -> list[ExtractionResult]:
    """Descarga y normaliza todos los recursos del catálogo.

    Etapa TOLERANTE: los recursos que fallan se registran pero el pipeline
    sigue con los restantes.

    Args:
        resources: Lista de metadatos de recursos (salida de run_discovery).
        config:    Configuración del pipeline.

    Returns:
        Lista de ExtractionResult (uno por recurso, df=None si falló).
    """
    results: list[ExtractionResult] = []
    total = len(resources)

    for idx, meta in enumerate(resources, 1):
        slug = meta.get("slug", "desconocido")
        recurso_id = meta.get("recurso_id", "")
        logger.info(
            "[%d/%d] Descargando: %s (recurso: %s)",
            idx, total, slug, recurso_id[:8],
        )
        result = _extract_one(meta, config)
        if result.error:
            logger.warning("  Saltado/fallido %s: %s", slug, result.error)
        results.append(result)

        if result.df is not None and config.request_delay_s > 0:
            time.sleep(config.request_delay_s)

    return results


# ── Stage 3: Evaluation ───────────────────────────────────────

@dataclass
class EvaluationResult:
    """Scores ISO 25012 mapeados al esquema JSON de salida."""

    slug: str
    record: dict
    score_global: float
    log_entry: dict


def _map_scores(meta: dict, scores: dict, df: pd.DataFrame) -> dict:
    """Mapea scores crudos al esquema JSON estándar."""
    formato = meta.get("formato", "CSV")
    return {
        "slug"             : meta.get("slug", ""),
        "dataset"          : meta.get("dataset", ""),
        "descripcion"      : meta.get("descripcion", ""),
        "categoria"        : meta.get("categoria", ""),
        "organizacion"     : meta.get("organizacion", ""),
        "formato"          : formato,
        "filas"            : len(df),
        "columnas"         : len(df.columns),
        "metadata_modified": meta.get("modificado", ""),
        "frequency"        : meta.get("frecuencia_update", ""),
        "scores": {
            "completeness" : scores.get("comp_completitud_global_pct", 0),
            "accuracy"     : scores.get("acc_score_accuracy_pct", 0),
            "consistency"  : scores.get("cons_score_consistency_pct", 0),
            "uniqueness"   : scores.get("uniq_score_uniqueness_pct", 0),
            "timeliness"   : scores.get("time_score_timeliness_pct"),
            "documentation": scores.get("doc_score_documentation_pct", 0),
            "openness"     : scores.get("open_score_openness_pct", 0),
        },
    }


def run_evaluation(
    extractions: list[ExtractionResult],
    config: PipelineConfig,
) -> tuple[list[EvaluationResult], list[dict]]:
    """Calcula scores de calidad ISO 25012 para cada recurso extraído.

    Etapa TOLERANTE: los datasets que fallan en la evaluación se omiten
    del resultado final pero el pipeline continúa.

    Args:
        extractions: Lista de ExtractionResult (salida de run_extraction).
        config:      Configuración del pipeline.

    Returns:
        Tupla (lista de EvaluationResult exitosos, lista de dicts fallidos).
    """
    evaluated: list[EvaluationResult] = []
    failed: list[dict] = []

    for ext in extractions:
        if ext.df is None:
            failed.append({"slug": ext.slug, "reason": ext.error or "No DataFrame"})
            continue

        slug = ext.slug
        ds_start = time.time()

        try:
            scores = data_layer.compute_quality_scores(ext.meta, ext.df)
        except Exception as exc:
            failed.append({"slug": slug, "reason": f"Eval error: {exc}"})
            logger.error("  Error evaluando %s: %s", slug, exc)
            continue

        record = _map_scores(ext.meta, scores, ext.df)
        score_global = float(scores.get("score_global", 0))
        ds_elapsed = round(time.time() - ds_start, 2)

        log_entry: dict[str, Any] = {
            "slug"        : slug,
            "recurso_id"  : ext.meta.get("recurso_id", ""),
            "status"      : "success",
            "elapsed_s"   : ds_elapsed,
            "score_global": score_global,
            "error"       : None,
        }

        logger.info("  Score: %.1f%% (%.1fs)", score_global, ds_elapsed)
        evaluated.append(EvaluationResult(
            slug=slug,
            record=record,
            score_global=score_global,
            log_entry=log_entry,
        ))

    return evaluated, failed


# ── Stage 4: Persistence ──────────────────────────────────────

def _build_output_dataframe(records: list[dict]) -> pd.DataFrame:
    """Construye el DataFrame de scores con score_global vectorizado."""
    w = QUALITY_WEIGHTS
    score_cols: dict[str, str] = {
        "completeness":  "comp_completitud_global_pct",
        "accuracy":      "acc_score_accuracy_pct",
        "consistency":   "cons_score_consistency_pct",
        "uniqueness":    "uniq_score_uniqueness_pct",
        "documentation": "doc_score_documentation_pct",
        "openness":      "open_score_openness_pct",
    }

    csv_rows = []
    for d in records:
        s = d.get("scores", {})
        csv_rows.append({
            "dataset"                     : d.get("slug", ""),
            "categoria"                   : d.get("categoria", ""),
            "organizacion"                : d.get("organizacion", ""),
            "formato"                     : d.get("formato", "CSV"),
            "filas"                       : d.get("filas", 0),
            "columnas"                    : d.get("columnas", 0),
            "modificado"                  : d.get("metadata_modified", ""),
            "frecuencia_update"           : d.get("frequency", ""),
            "descripcion_ciudadana"       : d.get("descripcion_ciudadana", ""),
            "tags_sugeridos"              : str(d.get("tags_sugeridos", [])),
            "comp_completitud_global_pct" : float(s.get("completeness", 0) or 0),
            "acc_score_accuracy_pct"      : float(s.get("accuracy", 0) or 0),
            "cons_score_consistency_pct"  : float(s.get("consistency", 0) or 0),
            "uniq_score_uniqueness_pct"   : float(s.get("uniqueness", 0) or 0),
            "time_score_timeliness_pct"   : s.get("timeliness"),
            "doc_score_documentation_pct" : float(s.get("documentation", 0) or 0),
            "open_score_openness_pct"     : float(s.get("openness", 0) or 0),
            "score_global"                : 0.0,
        })

    df_out = pd.DataFrame(csv_rows)

    # Calcular score_global vectorizado
    weighted_sum = sum(
        df_out[col].fillna(0) * w[dim] for dim, col in score_cols.items()
    )
    total_w = sum(w[dim] for dim in score_cols)

    time_col = df_out["time_score_timeliness_pct"]
    has_time = time_col.notna()
    weighted_sum = weighted_sum.copy()
    weighted_sum.loc[has_time] += time_col[has_time] * w["timeliness"]
    total_weights = pd.Series(total_w, index=df_out.index)
    total_weights.loc[has_time] += w["timeliness"]

    df_out["score_global"] = (weighted_sum / total_weights).round(2)
    return df_out


def run_persistence(
    evaluated: list[EvaluationResult],
    failed: list[dict],
    pipeline_log: list[dict],
    run_id: str,
    t0: float,
    catalog_count: int,
    catalog_limit: int,
    config: PipelineConfig,
) -> dict:
    """Guarda todos los artefactos del pipeline y devuelve el reporte de cobertura.

    Etapa CRITICA para JSON y snapshot; TOLERANTE para CSV/Parquet/BigQuery.

    Args:
        evaluated:     Lista de resultados evaluados exitosamente.
        failed:        Lista de dicts con datasets fallidos.
        pipeline_log:  Log de ejecución por dataset.
        run_id:        Identificador único de la ejecución.
        t0:            Timestamp de inicio (time.time()).
        catalog_count: Total de recursos en el catálogo original.
        catalog_limit: Recursos efectivamente enviados al pipeline.
        config:        Configuración del pipeline.

    Returns:
        dict con reporte de cobertura.
    """
    records = [e.record for e in evaluated]
    processed_count = len(evaluated)
    total_elapsed = round(time.time() - t0, 2)

    os.makedirs(config.output_dir, exist_ok=True)

    # Enriquecimiento con IA (opcional — requiere Vertex AI / GCP credentials)
    if _AI_ENRICHMENT_AVAILABLE:
        logger.info("Enriqueciendo metadata con Vertex AI...")
        records = _enrich(records)
    else:
        for r in records:
            r.setdefault("descripcion_ciudadana", "")
            r.setdefault("tags_sugeridos", [])

    # JSON legado
    save_json(records, run_id, pipeline_version="3.1", out_path=config.output_file)

    # Pipeline log
    with open(config.pipeline_log_file, "w", encoding="utf-8") as f:
        json.dump(pipeline_log, f, ensure_ascii=False, indent=2)

    # CSV + Parquet
    try:
        df_out = _build_output_dataframe(records)
        save_csv(df_out, config.csv_output_file)

        run_date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        df_parquet = df_out.copy()
        df_parquet["run_date"] = run_date_str
        save_parquet(df_parquet, run_date=run_date_str)
        logger.info("Parquet guardado (particionado por run_date/formato/categoria)")

        if config.use_bigquery:
            logger.info("Despachando DataFrame hacia BigQuery...")
            try:
                data_layer.save_to_bigquery(df_out)
                logger.info("Resultados almacenados en BigQuery.")
            except Exception as bq_err:
                logger.error("Fallo al escribir a BigQuery: %s", bq_err)
    except Exception as exc:
        logger.warning("Error generando CSV/Parquet: %s", exc)

    # Snapshot
    snap_dir = config.snapshot_dir or os.path.join(
        config.snapshots_base_dir, f"run_{run_id}"
    )
    snap_data = {
        "generado"         : datetime.now(timezone.utc).isoformat(),
        "run_id"           : run_id,
        "pipeline_version" : "3.1",
        "dimensiones"      : 7,
        "datasets"         : records,
    }
    _, snap_hash = save_snapshot(snap_data, snap_dir)
    logger.info("Snapshot guardado en: %s (SHA256: %s)", snap_dir, snap_hash[:16])

    # Reporte de cobertura
    coverage_pct = (
        round(processed_count / catalog_count * 100, 1) if catalog_count else 0
    )
    coverage_report: dict[str, Any] = {
        "run_id"                : run_id,
        "total_catalogo"        : catalog_count,
        "procesados_limit"      : catalog_limit,
        "procesados_exitosos"   : processed_count,
        "fallidos"              : len(failed),
        "cobertura_pct"         : coverage_pct,
        "elapsed_total_s"       : total_elapsed,
        "avg_time_per_dataset_s": round(total_elapsed / max(processed_count, 1), 2),
        "failed_details"        : failed,
        "snapshot_dir"          : snap_dir,
        "snapshot_sha256"       : snap_hash,
    }

    save_coverage_report(coverage_report, snap_dir)

    if coverage_pct < config.coverage_warn_threshold:
        logger.warning(
            "ALERTA: Cobertura del pipeline %.1f%% — por debajo del umbral de %.0f%%.",
            coverage_pct, config.coverage_warn_threshold,
        )

    return coverage_report


# ── Orquestador principal ─────────────────────────────────────

def run_pipeline(
    force: bool = False,
    limit: int = 0,
    snapshot_dir: str = "",
    config: PipelineConfig | None = None,
) -> dict:
    """Ejecuta el pipeline de calidad de datos completo.

    Args:
        force:        Ignorar el TTL de 24h y forzar ejecucion.
        limit:        Si > 0, procesar solo los primeros N datasets (dry run).
        snapshot_dir: Directorio para guardar snapshot.
        config:       PipelineConfig opcional; si se provee, force/limit/
                      snapshot_dir se ignoran.

    Returns:
        dict con reporte de cobertura del pipeline.
    """
    if config is None:
        config = PipelineConfig(force=force, limit=limit, snapshot_dir=snapshot_dir)

    if not config.force and not requires_refresh():
        logger.info("Pipeline no requiere refresh (TTL activo).")
        return {"skipped": True}

    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    logger.info("Iniciando pipeline v3.1 — 7 dimensiones — Run ID: %s", run_id)
    t0 = time.time()

    # Stage 1: Discovery (CRITICA)
    try:
        catalog = run_discovery(config)
    except DiscoveryError as exc:
        logger.error("Error critico en Discovery: %s", exc)
        return {"error": str(exc)}

    catalog_count = len(catalog)

    # Stage 2: Extraction (TOLERANTE)
    extractions = run_extraction(catalog, config)

    # Build pipeline_log entries from extractions
    pipeline_log: list[dict] = []
    for idx, ext in enumerate(extractions, 1):
        entry: dict[str, Any] = {
            "index"      : idx,
            "slug"       : ext.slug,
            "recurso_id" : ext.meta.get("recurso_id", ""),
            "status"     : "skipped" if ext.df is None else "pending",
            "error"      : ext.error,
            "elapsed_s"  : 0,
        }
        pipeline_log.append(entry)

    # Stage 3: Evaluation (TOLERANTE)
    evaluated, failed = run_evaluation(extractions, config)

    # Update pipeline_log with evaluation results
    eval_by_slug = {e.slug: e for e in evaluated}
    for entry in pipeline_log:
        slug = entry["slug"]
        if slug in eval_by_slug:
            ev = eval_by_slug[slug]
            entry.update(ev.log_entry)

    # Stage 4: Persistence (CRITICA para snapshot, TOLERANTE para CSV/Parquet)
    coverage_report = run_persistence(
        evaluated=evaluated,
        failed=failed,
        pipeline_log=pipeline_log,
        run_id=run_id,
        t0=t0,
        catalog_count=catalog_count,
        catalog_limit=len(catalog),
        config=config,
    )

    _save_last_run()

    total_elapsed = coverage_report.get("elapsed_total_s", 0)
    logger.info(
        "Pipeline completado. %d datasets evaluados en %.1fs.",
        len(evaluated), total_elapsed,
    )
    _print_coverage_report(coverage_report)
    return coverage_report


# ── Human-readable report ─────────────────────────────────────

def _print_coverage_report(report: dict) -> None:
    """Imprime el reporte de cobertura en stdout (ASCII-safe para cmd)."""
    run_id       = report.get("run_id", "")
    cat_count    = report.get("total_catalogo", 0)
    proc_limit   = report.get("procesados_limit", 0)
    ok_count     = report.get("procesados_exitosos", 0)
    cov_pct      = report.get("cobertura_pct", 0)
    fail_count   = report.get("fallidos", 0)
    elapsed      = report.get("elapsed_total_s", 0)
    avg_time     = report.get("avg_time_per_dataset_s", 0)
    snap_dir     = report.get("snapshot_dir", "")
    failed_list  = report.get("failed_details", [])

    print("\n" + "=" * 60)
    print("  REPORTE DE COBERTURA DEL PIPELINE")
    print("=" * 60)
    print(f"  Run ID:               {run_id}")
    print(f"  Total en catalogo:     {cat_count}")
    print(f"  Procesados (limite):   {proc_limit}")
    print(f"  Exitosos:              {ok_count} ({cov_pct}%)")
    print(f"  Fallidos:              {fail_count}")
    print(f"  Tiempo total:          {elapsed:.1f}s")
    print(f"  Tiempo promedio/ds:    {avg_time:.1f}s")
    print(f"  Snapshot:              {snap_dir}")
    if failed_list:
        print(f"\n  [X] Datasets fallidos:")
        for fd in failed_list:
            print(f"     - {fd['slug']}: {fd['reason']}")
    print("=" * 60)


# ── Pipeline avanzado (agentes Extractor/Evaluador) ───────────

def run_advanced_pipeline(limit: int = 0) -> None:
    """Ejecuta el pipeline avanzado con los agentes Extractor y Evaluador
    (ISO 25012, ISO 8000, DAMA).
    """
    from pipeline.extractor import SkillExtractorDatasets
    from pipeline.evaluator import SkillEvaluadorDatos
    from pipeline.aesthetics import DataAesthetics, get_progress, console

    DataAesthetics.print_header("AGENTE DE CALIDAD 2026", "Pipeline Avanzado v3.1")
    DataAesthetics.print_log("Iniciando orquestacion de agentes con IA...", "info")

    CATALOG_URL = "https://catalogodatos.nl.gob.mx"

    with get_progress() as progress:
        task_extract = progress.add_task("[primary]Extrayendo catalogo...", total=100)
        extractor = SkillExtractorDatasets()
        resultados_extraccion = extractor.ejecutar(CATALOG_URL, limite_datasets=limit)
        progress.update(task_extract, completed=100)

        manifiesto = resultados_extraccion["manifiesto"]
        datos = resultados_extraccion["datos_extraidos"]
        total_ds = manifiesto["total_datasets_extraidos"]
        DataAesthetics.print_log(f"Extraccion completada: {total_ds} datasets listos.", "success")

        task_eval = progress.add_task(
            "[warning]Evaluando calidad multidimensional...", total=total_ds
        )
        evaluador = SkillEvaluadorDatos()
        reporte_global = evaluador.evaluar_catalogo(datos, manifiesto)
        progress.update(task_eval, completed=total_ds)

    stats = {
        "Total Datasets"      : total_ds,
        "Score Promedio"      : f"{reporte_global.score_promedio_catalogo:.1f}%",
        "Problemas Detectados": reporte_global.total_problemas_detectados,
        "Clasificacion"       : (
            list(reporte_global.distribucion_clasificacion.keys())[0]
            if reporte_global.distribucion_clasificacion else "N/A"
        ),
    }
    DataAesthetics.print_kpi_grid(stats)

    table = DataAesthetics.create_quality_table("TOP DATASETS (MEJOR CALIDAD)")
    top_datasets = sorted(
        reporte_global.reportes_datasets,
        key=lambda x: x.score_global,
        reverse=True,
    )[:5]
    for ds in top_datasets:
        table.add_row(
            ds.titulo[:40] + "...",
            ds.organizacion[:30],
            f"{ds.score_global}%",
            DataAesthetics.get_status_tag(ds.score_global),
        )
    console.print(table)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    import dataclasses

    def _json_default(obj: Any) -> Any:
        if dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, (np.integer, np.floating, np.bool_)):
            return obj.item()
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        raise TypeError(f"Type not serializable: {type(obj)}")

    with open(ADVANCED_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            dataclasses.asdict(reporte_global),
            f, ensure_ascii=False, indent=2, default=_json_default,
        )

    DataAesthetics.print_log(f"Resultados guardados en: {ADVANCED_OUTPUT_FILE}", "success")


# ── CLI entrypoint ────────────────────────────────────────────

if __name__ == "__main__":
    force_refresh = "--force" in sys.argv
    run_advanced  = "--advanced" in sys.argv

    limit_val = 0
    if "--limit" in sys.argv:
        try:
            idx = sys.argv.index("--limit")
            limit_val = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            limit_val = 5

    snap_dir = ""
    if "--snapshot-dir" in sys.argv:
        try:
            idx = sys.argv.index("--snapshot-dir")
            snap_dir = sys.argv[idx + 1]
        except (IndexError, ValueError):
            pass

    if run_advanced:
        run_advanced_pipeline(limit=limit_val)
    else:
        run_pipeline(force=force_refresh, limit=limit_val, snapshot_dir=snap_dir)
