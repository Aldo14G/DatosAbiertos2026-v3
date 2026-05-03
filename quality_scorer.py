"""
quality_scorer.py
ISO/IEC 25012 quality scoring.

Module-level functions: pure stateless dimension computations (testable in isolation).
QualityScorer class: orchestrates all 7 dimensions, applies injected weights, returns ScoringResult.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, TypedDict

import numpy as np
import pandas as pd

from config import QUALITY_WEIGHTS

_UPDATE_FREQ_DAYS: dict[str, int] = {
    "diaria": 1,
    "daily": 1,
    "semanal": 7,
    "weekly": 7,
    "quincenal": 15,
    "mensual": 30,
    "monthly": 30,
    "trimestral": 90,
    "quarterly": 90,
    "semestral": 180,
    "anual": 365,
    "yearly": 365,
}


class ScoringResult(TypedDict):
    dim_scores: dict[str, float]
    breakdown: dict[str, Any]
    global_score: float


# ── Dimension functions (pure, no I/O) ──────────────────────────────────────


def compute_completeness(df: pd.DataFrame) -> dict:
    total = df.size
    if not total:
        return {
            k: 0.0
            for k in [
                "comp_completitud_global_pct",
                "comp_completitud_media_col",
                "comp_completitud_min_col",
                "comp_filas_incompletas_pct",
            ]
        }
    nulos = df.isnull().sum().sum()
    col_pct = 1 - df.isnull().mean()
    return {
        "comp_completitud_global_pct": round((total - nulos) / total * 100, 2),
        "comp_completitud_media_col" : round(col_pct.mean() * 100, 2),
        "comp_completitud_min_col"   : round(col_pct.min() * 100, 2),
        "comp_filas_incompletas_pct" : round(df.isnull().any(axis=1).mean() * 100, 2),
    }


def compute_accuracy(df: pd.DataFrame) -> dict:
    n_cols = len(df.columns)
    if n_cols == 0:
        return {
            "acc_score_accuracy_pct"  : 0,
            "acc_columnas_tipo_mixto" : 0,
            "acc_columnas_espacios"   : 0,
            "acc_columnas_constantes" : 0,
        }

    const = int((df.nunique() == 1).sum())
    mixed = spaces = 0
    obj_cols = df.select_dtypes(include=["object", "string"]).columns

    if len(obj_cols) > 0:
        df_obj = df[obj_cols]
        has_spaces = df_obj.apply(
            lambda x: x.astype(str).str.strip().ne(x.astype(str)).any()
        )
        spaces = int(has_spaces.sum())

        def is_mixed(s):
            s_val = s.dropna()
            if len(s_val) < 3:
                return False
            converted = pd.to_numeric(s_val, errors="coerce")
            pct_num = converted.notna().mean()
            return 0.05 < pct_num < 0.95

        mixed = int(df_obj.apply(is_mixed).sum())

    score = max(
        0,
        round(
            100
            - (mixed / n_cols) * 40
            - (spaces / n_cols) * 15
            - (const / n_cols) * 20,
            2,
        ),
    )
    return {
        "acc_score_accuracy_pct"  : score,
        "acc_columnas_tipo_mixto" : mixed,
        "acc_columnas_espacios"   : spaces,
        "acc_columnas_constantes" : const,
    }


def compute_consistency(df: pd.DataFrame) -> dict:
    total_out = total_num = incons_txt = 0

    cols_num = df.select_dtypes(include=[np.number]).columns
    if len(cols_num) > 0:
        df_num = df[cols_num]
        counts = df_num.count()
        valid_cols = counts[counts >= 30].index

        if len(valid_cols) > 0:
            df_valid = df_num[valid_cols]
            Q1 = df_valid.quantile(0.25)
            Q3 = df_valid.quantile(0.75)
            IQR = Q3 - Q1

            valid_iqr = IQR[IQR > 0].index
            if len(valid_iqr) > 0:
                df_calc = df_valid[valid_iqr]
                bounds_lower = Q1[valid_iqr] - 1.5 * IQR[valid_iqr]
                bounds_upper = Q3[valid_iqr] + 1.5 * IQR[valid_iqr]
                outliers_mask = (df_calc < bounds_lower) | (df_calc > bounds_upper)
                total_out = int(outliers_mask.sum().sum())
                total_num = int(df_calc.count().sum())

    cols_txt = df.select_dtypes(include=["object", "string"]).columns
    if len(cols_txt) > 0:
        df_txt = df[cols_txt].astype(str)
        raw_nunique = df_txt.nunique()
        clean_nunique = df_txt.apply(lambda x: x.str.strip().str.lower()).nunique()
        diff = raw_nunique - clean_nunique
        incons_txt = int(diff[diff > 0].sum())

    pct_out = round(total_out / total_num * 100, 2) if total_num else 0
    score = max(0, round(100 - pct_out * 2 - min(incons_txt * 0.5, 20), 2))
    return {
        "cons_score_consistency_pct" : score,
        "cons_pct_outliers"          : pct_out,
        "cons_inconsistencias_texto" : incons_txt,
        "cons_columnas_numericas"    : len(cols_num),
    }


def compute_uniqueness(df: pd.DataFrame) -> dict:
    n = len(df)
    if not n:
        return {
            "uniq_score_uniqueness_pct": 0,
            "uniq_pct_duplicados"      : 0,
            "uniq_duplicados_exactos"  : 0,
            "uniq_cardinalidad_media"  : 0,
        }
    dups = df.duplicated().sum()
    pct_dup = round(dups / n * 100, 2)
    card_med = round((df.nunique() / n * 100).mean(), 2)
    return {
        "uniq_score_uniqueness_pct": max(0, round(100 - pct_dup * 2, 2)),
        "uniq_pct_duplicados"      : pct_dup,
        "uniq_duplicados_exactos"  : int(dups),
        "uniq_cardinalidad_media"  : card_med,
    }


def compute_timeliness(meta: dict) -> dict:
    modificado = meta.get("modificado", "") or ""
    freq_key = (meta.get("frecuencia_update") or "").lower().strip()
    freq_dias = _UPDATE_FREQ_DAYS.get(freq_key, 0)

    no_date_result = {
        "time_score_timeliness_pct"  : np.nan,
        "time_dias_desde_modificado" : None,
        "time_frecuencia_declarada"  : freq_key or "desconocida",
    }

    if not modificado:
        return no_date_result

    try:
        dt_mod = datetime.fromisoformat(modificado.replace("Z", "+00:00")).replace(tzinfo=UTC)
        dias = (datetime.now(UTC) - dt_mod).days
    except (ValueError, TypeError):
        return no_date_result

    if freq_dias == 0:
        score = max(0.0, round(100 - (dias / 365) * 20, 2))
    elif dias <= freq_dias:
        score = 100.0
    elif dias >= freq_dias * 2:
        score = 0.0
    else:
        ratio = (dias - freq_dias) / freq_dias
        score = round(max(0.0, 100 - ratio * 100), 2)

    return {
        "time_score_timeliness_pct"  : score,
        "time_dias_desde_modificado" : dias,
        "time_frecuencia_declarada"  : freq_key or "desconocida",
    }


def compute_documentation(meta: dict) -> dict:
    score = 0.0
    details: dict = {}

    desc = str(meta.get("descripcion", "") or "").strip()
    desc_len = len(desc)
    if desc_len >= 200:
        desc_pts = 30.0
    elif desc_len >= 50:
        desc_pts = 20.0
    elif desc_len > 0:
        desc_pts = 10.0
    else:
        desc_pts = 0.0
    score += desc_pts
    details["doc_descripcion_len"] = desc_len
    details["doc_descripcion_pts"] = desc_pts

    resource_descs = meta.get("resource_descs", [])
    if resource_descs:
        described = sum(1 for d in resource_descs if (d or "").strip())
        res_pts = round(described / len(resource_descs) * 30, 2)
    else:
        res_pts = 0.0
    score += res_pts
    details["doc_resources_described"] = res_pts

    licencia    = str(meta.get("licencia",    "") or "").strip()
    licencia_id = str(meta.get("licencia_id", "") or "").strip()
    lic_pts = 20.0 if (licencia or licencia_id) else 0.0
    score += lic_pts
    details["doc_licencia"]     = licencia or licencia_id or "sin especificar"
    details["doc_licencia_pts"] = lic_pts

    texto_buscar = desc.lower()
    keywords_found: list[str] = [
        kw
        for kw in [
            "metodolog", "fuente", "diccionario", "glosario", "nota",
            "definici", "metadat", "variable", "indicador",
        ]
        if kw in texto_buscar
    ]
    meth_pts = min(20.0, len(keywords_found) * 5.0)
    score += meth_pts
    details["doc_keywords_found"]    = keywords_found
    details["doc_metodologia_pts"]   = meth_pts

    return {"doc_score_documentation_pct": round(score, 2), **details}


def compute_openness(meta: dict) -> dict:
    score = 0.0
    details: dict = {}

    formatos = meta.get("resource_formats", [])
    formato_actual = str(meta.get("formato", "")).upper()
    all_formats = set(formatos) | {formato_actual}

    OPEN_FORMATS = {"CSV", "JSON", "GEOJSON", "XML", "RDF", "SPARQL", "TSV"}
    SEMI_OPEN    = {"XLS", "XLSX", "ODS"}
    CLOSED       = {"PDF", "DOC", "DOCX", "PPT", "PPTX", "ZIP"}

    if all_formats & OPEN_FORMATS:
        fmt_pts = 40.0
    elif all_formats & SEMI_OPEN:
        fmt_pts = 20.0
    elif all_formats & CLOSED:
        fmt_pts = 5.0
    else:
        fmt_pts = 0.0
    score += fmt_pts
    details["open_formatos"]    = list(all_formats - {""})
    details["open_formato_pts"] = fmt_pts

    licencia    = str(meta.get("licencia",    "") or "").lower()
    licencia_id = str(meta.get("licencia_id", "") or "").lower()
    lic_text    = f"{licencia} {licencia_id}"

    OPEN_LIC_KEYWORDS = [
        "creative commons", "cc-by", "cc0", "open", "libre",
        "abierta", "datos abiertos", "public domain", "dominio público",
    ]
    if any(kw in lic_text for kw in OPEN_LIC_KEYWORDS):
        lic_pts = 35.0
    elif licencia or licencia_id:
        lic_pts = 15.0
    else:
        lic_pts = 0.0
    score += lic_pts
    details["open_licencia"]     = licencia or licencia_id or "sin especificar"
    details["open_licencia_pts"] = lic_pts

    url = str(meta.get("url", "") or "")
    access_pts = 25.0 if url.startswith(("http://", "https://")) else 0.0
    score += access_pts
    details["open_acceso_directo"] = bool(url)
    details["open_acceso_pts"]     = access_pts

    return {"open_score_openness_pct": round(score, 2), **details}


# ── Orchestrator ─────────────────────────────────────────────────────────────


class QualityScorer:
    def __init__(self, weights: dict[str, float] | None = None) -> None:
        self._weights = dict(weights or QUALITY_WEIGHTS)

    def score(self, meta: dict, df: pd.DataFrame) -> ScoringResult:
        breakdown: dict[str, Any] = {}
        breakdown.update(compute_completeness(df))
        breakdown.update(compute_accuracy(df))
        breakdown.update(compute_consistency(df))
        breakdown.update(compute_uniqueness(df))
        breakdown.update(compute_timeliness(meta))
        breakdown.update(compute_documentation(meta))
        breakdown.update(compute_openness(meta))

        dim_scores: dict[str, float] = {
            "completeness" : breakdown.get("comp_completitud_global_pct", 0) or 0,
            "accuracy"     : breakdown.get("acc_score_accuracy_pct",       0) or 0,
            "consistency"  : breakdown.get("cons_score_consistency_pct",   0) or 0,
            "uniqueness"   : breakdown.get("uniq_score_uniqueness_pct",    0) or 0,
            "documentation": breakdown.get("doc_score_documentation_pct",  0) or 0,
            "openness"     : breakdown.get("open_score_openness_pct",      0) or 0,
        }

        weights = dict(self._weights)
        timeliness = breakdown.get("time_score_timeliness_pct")
        if timeliness is None or (isinstance(timeliness, float) and np.isnan(timeliness)):
            weights.pop("timeliness", None)
        else:
            dim_scores["timeliness"] = float(timeliness)

        total_w = sum(weights.values())
        global_score = round(
            sum(dim_scores[k] * weights[k] for k in weights) / total_w, 2
        )

        return ScoringResult(dim_scores=dim_scores, breakdown=breakdown, global_score=global_score)
