"""
Pipeline de Refresh Engine — Orquestador de calidad de datos.
v3.0: 7 dimensiones (5 ISO 25012 + Documentation + Openness) + instrumentación.
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timezone
from enum import Enum

# Asegurar que el directorio raíz del proyecto esté en sys.path
# para importar data_layer y config cuando se ejecuta como script.
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import data_layer

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


def _save_last_run():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(_LAST_RUN_FILE, "w") as f:
        f.write(datetime.now(timezone.utc).isoformat())


# ── Pipeline estándar con instrumentación ─────────────────────

def run_pipeline(force: bool = False, limit: int = 0, snapshot_dir: str = "") -> dict:
    """Ejecuta el pipeline de calidad de datos completo con instrumentación.

    Args:
        force: Ignorar el TTL de 24h y forzar ejecución.
        limit: Si > 0, procesar solo los primeros N datasets (dry run).
        snapshot_dir: Directorio para guardar snapshot (default: snapshots/).

    Returns:
        dict con reporte de cobertura del pipeline.
    """
    if not force and not requires_refresh():
        logger.info("Pipeline no requiere refresh (TTL activo).")
        return {"skipped": True}

    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    logger.info("🚀 Iniciando pipeline v3.0 — 7 dimensiones — Run ID: %s", run_id)

    # ── 1. Descubrimiento ─────────────────────────────────────
    logger.info("📥 Descargando catálogo desde CKAN API...")
    t0 = time.time()
    try:
        catalog = data_layer.fetch_portal_catalog()
    except Exception as e:
        logger.error("❌ Error al descargar catálogo: %s", e)
        return {"error": str(e)}

    catalog_count = len(catalog)
    discovery_elapsed = round(time.time() - t0, 2)
    logger.info("📊 Descubrimiento: %d recursos (multiformato) en %.1fs", catalog_count, discovery_elapsed)

    if limit > 0:
        catalog = catalog[:limit]
        logger.info("🔬 Modo dry-run: procesando solo %d datasets", limit)

    # ── 2. Procesamiento con contadores ───────────────────────
    datasets_results = []
    pipeline_log = []
    failed_datasets = []
    processed_count = 0

    for idx, meta in enumerate(catalog, 1):
        slug = meta.get("slug", "desconocido")
        recurso_id = meta.get("recurso_id", "")
        ds_start = time.time()
        log_entry = {
            "index": idx,
            "slug": slug,
            "recurso_id": recurso_id,
            "status": "pending",
            "error": None,
            "elapsed_s": 0,
        }

        logger.info("[%d/%d] Procesando: %s (recurso: %s)", idx, len(catalog), slug, recurso_id[:8])

        url = meta.get("url")
        if not url:
            log_entry["status"] = "skipped"
            log_entry["error"] = "No hay URL válida"
            failed_datasets.append({"slug": slug, "reason": "No URL"})
            logger.warning("  ⏭️  Saltando %s: No hay URL válida.", slug)
            pipeline_log.append(log_entry)
            continue

        # [Fase 2] Descarga multiformato — usa formato declarado en CKAN
        formato = meta.get("formato", "CSV")
        df = data_layer.download_resource(url, formato)
        if df is None:
            log_entry["status"] = "download_failed"
            log_entry["error"] = f"Fallo al descargar {formato}: {url}"
            failed_datasets.append({"slug": slug, "reason": f"Download failed ({formato}): {url}"})
            logger.error("  ❌ Fallo al descargar [%s]: %s", formato, url)
            pipeline_log.append(log_entry)
            continue

        # [Fase 3] Normalización: nulos canónicos, fechas UTC, geo, municipio
        try:
            from pipeline.normalizer import normalize_df
            df = normalize_df(df, formato)
        except Exception as norm_exc:
            logger.warning("  ⚠️  Normalización parcial (%s): %s", slug, norm_exc)

        try:
            scores = data_layer.compute_quality_scores(meta, df)
        except Exception as e:
            log_entry["status"] = "evaluation_failed"
            log_entry["error"] = str(e)
            failed_datasets.append({"slug": slug, "reason": f"Eval error: {e}"})
            logger.error("  ❌ Error evaluando %s: %s", slug, e)
            pipeline_log.append(log_entry)
            continue

        # Mapear al esquema JSON — incluye formato para trazabilidad (Fase 2)
        mapped_result = {
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

        datasets_results.append(mapped_result)
        processed_count += 1

        ds_elapsed = round(time.time() - ds_start, 2)
        log_entry["status"] = "success"
        log_entry["elapsed_s"] = ds_elapsed
        log_entry["score_global"] = scores.get("score_global", 0)
        pipeline_log.append(log_entry)

        logger.info("  ✅ Score: %.1f%% (%.1fs)", scores.get("score_global", 0), ds_elapsed)

        # Pausa entre requests para no saturar al servidor
        time.sleep(1)

    # ── 3. Guardar resultados ─────────────────────────────────
    total_elapsed = round(time.time() - t0, 2)
    logger.info("💾 Guardando resultados de calidad...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # [Fase 4] JSON + pipeline log via persistence module
    from pipeline.persistence import save_json, save_csv, save_parquet, save_snapshot, save_coverage_report
    save_json(datasets_results, run_id, pipeline_version="3.1", out_path=OUTPUT_FILE)

    with open(PIPELINE_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(pipeline_log, f, ensure_ascii=False, indent=2)

    # ── 4. Generar CSV + Parquet para dashboard ───────────────
    try:
        import pandas as pd
        import numpy as np
        from config import QUALITY_WEIGHTS

        # Integrar Enriquecimiento con IA (Vertex AI/Gemini)
        from pipeline.ai_enrichment import enrich_dataset_metadata
        logger.info("🧠 Enriqueciendo metadata con Vertex AI...")
        datasets_results = enrich_dataset_metadata(datasets_results)

        csv_rows = []
        for d in datasets_results:
            s = d.get("scores", {})
            csv_rows.append({
                "dataset":                     d.get("slug", ""),
                "categoria":                   d.get("categoria", ""),
                "organizacion":                d.get("organizacion", ""),
                "formato":                     d.get("formato", "CSV"),
                "filas":                       d.get("filas", 0),
                "columnas":                    d.get("columnas", 0),
                "modificado":                  d.get("metadata_modified", ""),
                "frecuencia_update":           d.get("frequency", ""),
                "descripcion_ciudadana":       d.get("descripcion_ciudadana", ""),
                "tags_sugeridos":              str(d.get("tags_sugeridos", [])),
                "comp_completitud_global_pct": float(s.get("completeness", 0) or 0),
                "acc_score_accuracy_pct":      float(s.get("accuracy", 0) or 0),
                "cons_score_consistency_pct":  float(s.get("consistency", 0) or 0),
                "uniq_score_uniqueness_pct":   float(s.get("uniqueness", 0) or 0),
                "time_score_timeliness_pct":   s.get("timeliness"),
                "doc_score_documentation_pct": float(s.get("documentation", 0) or 0),
                "open_score_openness_pct":     float(s.get("openness", 0) or 0),
                "score_global":                0.0,
            })

        df_out = pd.DataFrame(csv_rows)

        # Calcular score_global vectorizado
        w = QUALITY_WEIGHTS
        score_cols = {
            "completeness":  "comp_completitud_global_pct",
            "accuracy":      "acc_score_accuracy_pct",
            "consistency":   "cons_score_consistency_pct",
            "uniqueness":    "uniq_score_uniqueness_pct",
            "documentation": "doc_score_documentation_pct",
            "openness":      "open_score_openness_pct",
        }
        weighted_sum = sum(
            df_out[col].fillna(0) * w[dim] for dim, col in score_cols.items()
        )
        total_w = sum(w[dim] for dim in score_cols)

        # Agregar timeliness donde esté disponible
        time_col = df_out["time_score_timeliness_pct"]
        has_time = time_col.notna()
        weighted_sum = weighted_sum.copy()
        weighted_sum.loc[has_time] += time_col[has_time] * w["timeliness"]
        total_weights = pd.Series(total_w, index=df_out.index)
        total_weights.loc[has_time] += w["timeliness"]

        df_out["score_global"] = (weighted_sum / total_weights).round(2)

        # [Fase 4] CSV via persistence module
        save_csv(df_out, CSV_OUTPUT_FILE)

        # [Fase 4] Parquet particionado: run_date / formato / categoria
        run_date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        df_parquet = df_out.copy()
        df_parquet["run_date"] = run_date_str
        save_parquet(df_parquet, run_date=run_date_str)
        logger.info("📦 Parquet guardado (particionado por run_date/formato/categoria)")

        # Despachar a BigQuery si está habilitado
        if os.getenv("USE_BIGQUERY", "false").lower() == "true":
            logger.info("🗄️ Despachando Dataframe hacia BigQuery...")
            try:
                data_layer.save_to_bigquery(df_out)
                logger.info("✅ Resultados almacenados en BigQuery de forma exitosa.")
            except Exception as bq_err:
                logger.error("❌ Fallo al escribir a BigQuery: %s", bq_err)
    except Exception as e:
        logger.warning("⚠️  Error generando CSV: %s", e)

    # ── 5. Snapshot ────────────────────────────────────────────
    snap_dir = snapshot_dir or os.path.join(SNAPSHOTS_DIR, f"run_{run_id}")
    snap_data = {
        "generado"         : datetime.now(timezone.utc).isoformat(),
        "run_id"           : run_id,
        "pipeline_version" : "3.1",
        "dimensiones"      : 7,
        "datasets"         : datasets_results,
    }
    _, snap_hash = save_snapshot(snap_data, snap_dir)
    logger.info("📸 Snapshot guardado en: %s (SHA256: %s)", snap_dir, snap_hash[:16])

    # ── 6. Reporte de cobertura ────────────────────────────────
    coverage_pct = round(processed_count / catalog_count * 100, 1) if catalog_count else 0
    coverage_report = {
        "run_id": run_id,
        "total_catalogo": catalog_count,
        "procesados_limit": len(catalog),
        "procesados_exitosos": processed_count,
        "fallidos": len(failed_datasets),
        "cobertura_pct": coverage_pct,
        "elapsed_total_s": total_elapsed,
        "avg_time_per_dataset_s": round(total_elapsed / max(processed_count, 1), 2),
        "failed_details": failed_datasets,
        "snapshot_dir": snap_dir,
        "snapshot_sha256": snap_hash,
    }

    # Guardar reporte
    report_path = os.path.join(snap_dir, "coverage_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(coverage_report, f, ensure_ascii=False, indent=2)

    # Imprimir reporte human-readable, forzando ascii/safe-chars para evitar cp1252 errors en cmd
    print("\n" + "=" * 60)
    print("  REPORTE DE COBERTURA DEL PIPELINE")
    print("=" * 60)
    print(f"  Run ID:               {run_id}")
    print(f"  Total en catálogo:     {catalog_count}")
    print(f"  Procesados (límite):   {len(catalog)}")
    print(f"  Exitosos:              {processed_count} ({coverage_pct}%)")
    print(f"  Fallidos:              {len(failed_datasets)}")
    print(f"  Tiempo total:          {total_elapsed:.1f}s")
    print(f"  Tiempo promedio/ds:    {coverage_report['avg_time_per_dataset_s']:.1f}s")
    print(f"  Snapshot:              {snap_dir}")
    if failed_datasets:
        print(f"\n  [X] Datasets fallidos:")
        for fd in failed_datasets:
            print(f"     - {fd['slug']}: {fd['reason']}")
    print("=" * 60)

    # Warning si cobertura < 90%
    if coverage_pct < 90:
        logger.warning(
            "⚠️  ALERTA: Cobertura del pipeline %.1f%% — por debajo del umbral de 90%%.",
            coverage_pct,
        )

    _save_last_run()
    logger.info(
        "✅ Pipeline completado. %d datasets evaluados en %.1fs.",
        processed_count, total_elapsed,
    )
    return coverage_report


def run_advanced_pipeline(limit: int = 0):
    """Ejecuta el pipeline avanzado con los agentes Extractor y Evaluador (ISO 25012, ISO 8000, DAMA)."""
    from pipeline.extractor import SkillExtractorDatasets
    from pipeline.evaluator import SkillEvaluadorDatos

    logger.info("🚀 Iniciando pipeline avanzado de agentes...")

    CATALOG_URL = "https://catalogodatos.nl.gob.mx"

    extractor = SkillExtractorDatasets()
    resultados_extraccion = extractor.ejecutar(CATALOG_URL, limite_datasets=limit)

    manifiesto = resultados_extraccion["manifiesto"]
    datos = resultados_extraccion["datos_extraidos"]

    logger.info("📥 Extracción completada. %d datasets procesados.", manifiesto["total_datasets_extraidos"])

    evaluador = SkillEvaluadorDatos()
    reporte_global = evaluador.evaluar_catalogo(datos, manifiesto)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    import dataclasses
    import numpy as np

    def json_default(obj):
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
        json.dump(dataclasses.asdict(reporte_global), f, ensure_ascii=False, indent=2, default=json_default)

    logger.info("✅ Pipeline avanzado completado. Resultados guardados en: %s", ADVANCED_OUTPUT_FILE)


if __name__ == "__main__":
    force_refresh = "--force" in sys.argv
    run_advanced = "--advanced" in sys.argv

    # Parse --limit N
    limit_val = 0
    if "--limit" in sys.argv:
        try:
            idx = sys.argv.index("--limit")
            limit_val = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            limit_val = 5

    # Parse --snapshot-dir <path>
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
