"""
data_aggregation.py — Agregaciones, filtros y clasificación de scores.

Responsabilidades:
  - Scoring de calidad delegado a QualityScorer (compute_quality_scores)
  - Agregaciones por dimensión y organización (get_aggregations, agg_org_stats)
  - Filtros combinados sobre DataFrame de resultados (apply_filters)
  - Clasificación de scores (classify_score)
  - Merge con overlay avanzado multi-framework (merge_advanced_overlay)
"""

import json
import os
import unicodedata
from functools import lru_cache

import numpy as np
import pandas as pd

from config import CLASIFICACION_DEFAULT, CLASIFICACION_THRESHOLDS  # noqa: E402
from quality_scorer import QualityScorer  # noqa: E402

# Etiquetas de presentación para cada columna de dimensión
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

_scorer = QualityScorer()

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


# ── SCORING ───────────────────────────────────────────────────


def compute_quality_scores(meta: dict, df: pd.DataFrame) -> dict:
    result = _scorer.score(meta, df)
    row = {
        "dataset": meta.get("dataset", ""),
        "slug": meta.get("slug", ""),
        "recurso_id": meta.get("recurso_id", ""),
        "categoria": meta.get("categoria", ""),
        "organizacion": meta.get("organizacion", ""),
        "filas": len(df),
        "columnas": len(df.columns),
        "modificado": meta.get("modificado", ""),
        "frecuencia_update": meta.get("frecuencia_update", ""),
    }
    row.update(result["breakdown"])
    row["score_global"] = result["global_score"]
    return row


# ── CLASIFICACIÓN ──────────────────────────────────────────────


def classify_score(score: float) -> str:
    """Deriva etiqueta de clasificacion desde score_global."""
    for threshold, label in CLASIFICACION_THRESHOLDS:
        if score >= threshold:
            return label
    return CLASIFICACION_DEFAULT


@lru_cache(maxsize=512)
def _normalize_title(title: str) -> str:
    """Normaliza titulo para join entre pipelines (lower + strip + ASCII)."""
    return (
        unicodedata.normalize("NFKD", title.strip().lower())
        .encode("ascii", "ignore")
        .decode()
    )


# ── AGREGACIONES ──────────────────────────────────────────────


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


def agg_dim_means_by(
    df: pd.DataFrame,
    group_col: str,
    *,
    rename: bool = False,
) -> pd.DataFrame:
    """Agrupa df por `group_col` y calcula la media de las columnas de dimensión ISO.

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
        "n_datasets": ("dataset", "count"),
        "score_global": ("score_global", "mean"),
    }
    for col in DIM_LABEL_MAP:
        if col != "score_global" and col in df.columns:
            agg_dict[col] = (col, "mean")

    stats = df.groupby("organizacion", as_index=False).agg(**agg_dict)
    return (
        stats.sort_values("score_global", ascending=False).reset_index(drop=True).round(1)
    )


# ── OVERLAY AVANZADO ──────────────────────────────────────────


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
