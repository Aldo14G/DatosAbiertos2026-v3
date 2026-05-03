"""
section_data.py
View model for the NL 2026 dashboard.

build_section_data(df) is the single entry point — it pre-computes all
shared aggregations so sections receive pre-built values instead of
re-deriving them independently from raw DataFrames.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from config import UMBRAL_EXCELENTE, UMBRAL_GOBERNANZA
from data_layer import agg_dim_means_by, agg_org_stats

_DIM_MAPPING: dict[str, str] = {
    "Completitud"   : "comp_completitud_global_pct",
    "Exactitud"     : "acc_score_accuracy_pct",
    "Consistencia"  : "cons_score_consistency_pct",
    "Unicidad"      : "uniq_score_uniqueness_pct",
    "Puntualidad"   : "time_score_timeliness_pct",
    "Documentación" : "doc_score_documentation_pct",
    "Apertura"      : "open_score_openness_pct",
}


@dataclass
class SectionData:
    # Scalar summaries
    n_datasets: int
    n_orgs: int
    n_formats: int
    mean_score: float
    n_critical: int      # score < UMBRAL_GOBERNANZA
    n_excellent: int     # score >= UMBRAL_EXCELENTE
    n_good: int          # UMBRAL_GOBERNANZA <= score < UMBRAL_EXCELENTE
    total_rows: int
    # Per-dimension means keyed by display label (e.g. "Completitud")
    dim_means: dict[str, float]
    # Pre-aggregated tables
    recent_datasets: pd.DataFrame    # top 6 by modified date
    top_orgs_by_count: pd.Series     # value_counts().head(7) on organizacion
    org_stats: pd.DataFrame          # agg_org_stats(df)
    dim_means_by_cat: pd.DataFrame   # agg_dim_means_by(df, "categoria", rename=True)


def build_section_data(df: pd.DataFrame) -> SectionData:
    """Compute all shared dashboard aggregations once from the quality results DataFrame."""
    if df.empty:
        return SectionData(
            n_datasets=0,
            n_orgs=0,
            n_formats=0,
            mean_score=0.0,
            n_critical=0,
            n_excellent=0,
            n_good=0,
            total_rows=0,
            dim_means={},
            recent_datasets=pd.DataFrame(),
            top_orgs_by_count=pd.Series(dtype=float),
            org_stats=pd.DataFrame(),
            dim_means_by_cat=pd.DataFrame(),
        )

    scores = df["score_global"] if "score_global" in df.columns else pd.Series(dtype=float)
    mean_score  = float(scores.mean()) if not scores.empty else 0.0
    n_critical  = int((scores < UMBRAL_GOBERNANZA).sum())
    n_excellent = int((scores >= UMBRAL_EXCELENTE).sum())
    n_good      = int(((scores >= UMBRAL_GOBERNANZA) & (scores < UMBRAL_EXCELENTE)).sum())

    dim_means: dict[str, float] = {}
    for lbl, col in _DIM_MAPPING.items():
        if col in df.columns:
            vals = df[col].dropna()
            if not vals.empty:
                dim_means[lbl] = float(vals.mean())

    if "dataset" in df.columns:
        sort_col = "modificado" if "modificado" in df.columns else None
        df_r = df.sort_values(by=sort_col, ascending=False).head(6) if sort_col else df.head(6)
        recent_df = df_r.rename(columns={"dataset": "title", "organizacion": "organization"})
        keep = [c for c in ("title", "organization") if c in recent_df.columns]
        recent_df = recent_df[keep].copy()
        recent_df["metadata_modified"] = df_r["modificado"].values if "modificado" in df_r.columns else "N/A"
        recent_df["format"] = df_r["formato"].values if "formato" in df_r.columns else "CSV"
    else:
        recent_df = pd.DataFrame()

    return SectionData(
        n_datasets=len(df),
        n_orgs=int(df["organizacion"].nunique()) if "organizacion" in df.columns else 0,
        n_formats=int(df["formato"].nunique()) if "formato" in df.columns else 0,
        mean_score=mean_score,
        n_critical=n_critical,
        n_excellent=n_excellent,
        n_good=n_good,
        total_rows=int(df["filas"].sum()) if "filas" in df.columns else 0,
        dim_means=dim_means,
        recent_datasets=recent_df,
        top_orgs_by_count=(
            df["organizacion"].value_counts().head(7)
            if "organizacion" in df.columns
            else pd.Series(dtype=float)
        ),
        org_stats=agg_org_stats(df),
        dim_means_by_cat=agg_dim_means_by(df, "categoria", rename=True),
    )
