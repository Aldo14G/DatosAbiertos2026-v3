"""
data_layer.py
Capa de acceso a datos del portal Datos Abiertos NL.
Expone funciones puras que el dashboard consume directamente.
Principios: inmutable, sin estado, cacheable.
"""
import pandas as pd
import numpy as np
import requests
import json
import time
import io
from functools import lru_cache
from typing import Optional

CKAN_API  = "https://catalogodatos.nl.gob.mx/api/3/action"
DELAY_SEC = 1.5

# ── 1. DESCUBRIMIENTO DE DATASETS ────────────────────────────

@lru_cache(maxsize=1)
def fetch_portal_catalog() -> list[dict]:
    datasets, start = [], 0
    while True:
        r = requests.get(
            f"{CKAN_API}/package_search",
            params={"rows": 100, "start": start},
            timeout=30,
        )
        r.raise_for_status()
        data    = r.json()
        results = data["result"]["results"]
        total   = data["result"]["count"]

        if not results:
            break

        for ds in results:
            org    = (ds.get("organization") or {}).get("title", "Desconocida")
            grupos = [g.get("title","") for g in ds.get("groups", [])]
            cat    = grupos[0].strip().title() if grupos else "Sin categoría"

            for recurso in ds.get("resources", []):
                fmt = recurso.get("format","").upper().strip()
                if fmt in ("CSV", ".CSV"):
                    datasets.append({
                        "slug"        : ds.get("name",""),
                        "dataset"     : ds.get("title","Sin nombre"),
                        "organizacion": org,
                        "categoria"   : cat,
                        "formato"     : fmt,
                        "url"         : recurso.get("url",""),
                        "modificado"  : ds.get("metadata_modified",""),
                    })
                    break

        start += len(results)
        if start >= total:
            break
        time.sleep(DELAY_SEC)

    return datasets

# ── 2. DESCARGA Y PROCESAMIENTO ───────────────────────────────

def download_csv(url: str) -> Optional[pd.DataFrame]:
    try:
        r = requests.get(url, timeout=30,
                         headers={"User-Agent": "DatosAbiertosNL-Analyzer/2.0"})
        r.raise_for_status()
        for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
            try:
                return pd.read_csv(io.StringIO(r.content.decode(enc)),
                                   low_memory=False)
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
    except Exception:
        pass
    return None

def normalize_categories(df: pd.DataFrame) -> pd.DataFrame:
    corrections = {
        "Administración Y Finanzas"       : "Administración y Finanzas",
        "Arte Y Cultura"                  : "Arte y Cultura",
        "Perspectiva De Género E Interseccionalidad": "Perspectiva de Género",
        "Transparencia Y Combate A La Corrupción"   : "Transparencia y Anticorrupción",
        "Atención Ciudadana"              : "Atención Ciudadana",
    }
    df = df.copy()
    if "categoria" in df.columns:
        df["categoria"] = (df["categoria"]
                             .astype(str).str.strip().str.title()
                             .replace(corrections))
    return df

# ── 3. CÓMPUTO DE CALIDAD (4 DIMENSIONES) ────────────────────

def compute_completeness(df: pd.DataFrame) -> dict:
    total   = df.size
    nulos   = df.isnull().sum().sum()
    global_ = round((total - nulos) / total * 100, 2) if total else 0
    col_min = round((1 - df.isnull().mean()).min() * 100, 2) if total else 0
    col_med = round((1 - df.isnull().mean()).mean() * 100, 2) if total else 0
    filas_  = round(df.isnull().any(axis=1).mean() * 100, 2) if total else 0
    return {
        "comp_completitud_global_pct": global_,
        "comp_completitud_media_col" : col_med,
        "comp_completitud_min_col"   : col_min,
        "comp_filas_incompletas_pct" : filas_,
    }

def compute_accuracy(df: pd.DataFrame) -> dict:
    score, mixed, spaces, const = 100, 0, 0, 0
    for col in df.columns:
        serie = df[col].dropna()
        if serie.empty:
            continue
        if df[col].dtype == object:
            num_pct = pd.to_numeric(serie, errors="coerce").notna().mean()
            if 0.05 < num_pct < 0.95:
                mixed += 1; score -= 6
            if serie.astype(str).str.contains(r"^\s|\s$").any():
                spaces += 1; score -= 2
        if serie.nunique() == 1:
            const += 1; score -= 3
    return {
        "acc_score_accuracy_pct"    : max(0, round(score, 2)),
        "acc_columnas_tipo_mixto"   : mixed,
        "acc_columnas_espacios"     : spaces,
        "acc_columnas_constantes"   : const,
    }

def compute_consistency(df: pd.DataFrame) -> dict:
    cols_num = df.select_dtypes(include=[np.number]).columns
    cols_txt = df.select_dtypes(include=["object"]).columns
    total_out, total_num, incons_txt = 0, 0, 0

    for col in cols_num:
        s = df[col].dropna()
        if len(s) < 4: continue
        Q1, Q3 = s.quantile(.25), s.quantile(.75)
        IQR = Q3 - Q1
        if IQR > 0:
            total_out += ((s < Q1 - 1.5*IQR) | (s > Q3 + 1.5*IQR)).sum()
        total_num += len(s)

    for col in cols_txt:
        s = df[col].dropna().astype(str)
        orig, norm = s.nunique(), s.str.strip().str.lower().nunique()
        incons_txt += max(0, orig - norm)

    pct_out = round(total_out / total_num * 100, 2) if total_num else 0
    score   = max(0, round(100 - pct_out * 2 - min(incons_txt * 0.5, 20), 2))
    return {
        "cons_score_consistency_pct": score,
        "cons_pct_outliers"         : pct_out,
        "cons_inconsistencias_texto": incons_txt,
        "cons_columnas_numericas"   : len(cols_num),
    }

def compute_uniqueness(df: pd.DataFrame) -> dict:
    n        = len(df)
    dups     = df.duplicated().sum()
    pct_dup  = round(dups / n * 100, 2) if n else 0
    card_med = round((df.nunique() / n * 100).mean(), 2) if n else 0
    score    = max(0, round(100 - pct_dup * 2, 2))
    return {
        "uniq_score_uniqueness_pct": score,
        "uniq_pct_duplicados"      : pct_dup,
        "uniq_duplicados_exactos"  : int(dups),
        "uniq_cardinalidad_media"  : card_med,
    }

def compute_quality_scores(meta: dict, df: pd.DataFrame) -> dict:
    row = {
        "dataset"     : meta.get("dataset", ""),
        "slug"        : meta.get("slug", ""),
        "categoria"   : meta.get("categoria", ""),
        "organizacion": meta.get("organizacion", ""),
        "filas"       : len(df),
        "columnas"    : len(df.columns),
        "modificado"  : meta.get("modificado",""),
    }
    for fn in [compute_completeness, compute_accuracy,
               compute_consistency,  compute_uniqueness]:
        row.update(fn(df))

    scores = [
        row.get("comp_completitud_global_pct", 0),
        row.get("acc_score_accuracy_pct",      0),
        row.get("cons_score_consistency_pct",  0),
        row.get("uniq_score_uniqueness_pct",   0),
    ]
    row["score_global"] = round(float(np.mean(scores)), 2)
    return row

# ── 4. AGREGACIÓN EN TIEMPO REAL ──────────────────────────────

def get_aggregations(df: pd.DataFrame, by: str = "categoria") -> pd.DataFrame:
    dim_cols = [
        "comp_completitud_global_pct",
        "acc_score_accuracy_pct",
        "cons_score_consistency_pct",
        "uniq_score_uniqueness_pct",
        "score_global",
    ]
    cols_ok = [c for c in dim_cols if c in df.columns]
    agg = (df.groupby(by)[cols_ok]
             .mean()
             .round(1)
             .sort_values("score_global", ascending=False)
             .reset_index())
    agg.columns = [by, "Completitud", "Exactitud",
                   "Consistencia", "Unicidad", "Score Global"][:len(agg.columns)]
    return agg

def apply_filters(
    df: pd.DataFrame,
    categorias:    list[str] = None,
    organizaciones:list[str] = None,
    score_min:     float     = 0,
    score_max:     float     = 100,
) -> pd.DataFrame:
    mask = pd.Series([True] * len(df), index=df.index)

    if categorias and "categoria" in df.columns:
        if "Todas" not in categorias:
            mask &= df["categoria"].isin(categorias)
    if organizaciones and "organizacion" in df.columns:
        if "Todas" not in organizaciones:
            mask &= df["organizacion"].isin(organizaciones)
    if "score_global" in df.columns:
        mask &= (df["score_global"] >= score_min) & (df["score_global"] <= score_max)

    return df[mask].copy()

def load_results(path: str = "") -> pd.DataFrame:
    # We will load from our existing pipeline results if CSV does not exist
    try:
        df = pd.read_csv("resultados_calidad_datos_nl.csv", encoding="utf-8-sig")
    except FileNotFoundError:
        with open('.antigravity/team/shared/quality_results.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        rows = []
        for d in data['datasets']:
            if d.get('scores') is not None:
                rows.append({
                    'dataset': d.get('slug', ''),
                    'categoria': d.get('categoria', ''),
                    'organizacion': d.get('organizacion', ''),
                    'filas': d.get('filas', 0),
                    'comp_completitud_global_pct': d['scores'].get('completeness', 0),
                    'acc_score_accuracy_pct': d['scores'].get('accuracy', 0),
                    'cons_score_consistency_pct': d['scores'].get('consistency', 0),
                    'uniq_score_uniqueness_pct': d['scores'].get('uniqueness', 0),
                    'score_global': d['scores'].get('global', 0)
                })
        df = pd.DataFrame(rows)
    return normalize_categories(df)
