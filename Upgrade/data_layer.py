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

import pandas as pd
import numpy as np
import requests
import json
import time
import io
from datetime import datetime, timezone
from functools import lru_cache
from typing import Optional

CKAN_API  = "https://catalogodatos.nl.gob.mx/api/3/action"
DELAY_SEC = 1.5

# ── PESOS ISO 25012 ───────────────────────────────────────────
# Completitud y Exactitud tienen mayor peso en datos gubernamentales
# según ISO/IEC 25012:2008 y Wang & Strong (1996). Suma = 1.0.
QUALITY_WEIGHTS: dict[str, float] = {
    "completeness": 0.35,
    "accuracy":     0.30,
    "consistency":  0.20,
    "uniqueness":   0.10,
    "timeliness":   0.05,
}

# Etiquetas de presentación para cada columna de dimensión
DIM_LABEL_MAP: dict[str, str] = {
    "comp_completitud_global_pct": "Completitud",
    "acc_score_accuracy_pct":      "Exactitud",
    "cons_score_consistency_pct":  "Consistencia",
    "uniq_score_uniqueness_pct":   "Unicidad",
    "time_score_timeliness_pct":   "Puntualidad",
    "score_global":                "Score Global",
}

# Días esperados entre publicaciones para cada frecuencia declarada
_UPDATE_FREQ_DAYS: dict[str, int] = {
    "diaria":     1,    "daily":      1,
    "semanal":    7,    "weekly":     7,
    "quincenal":  15,
    "mensual":    30,   "monthly":    30,
    "trimestral": 90,   "quarterly":  90,
    "semestral":  180,
    "anual":      365,  "yearly":     365,
}

# Columnas mínimas para que el dashboard funcione
_REQUIRED_COLS = {
    "dataset", "categoria", "organizacion", "filas",
    "comp_completitud_global_pct", "acc_score_accuracy_pct",
    "cons_score_consistency_pct",  "uniq_score_uniqueness_pct",
    "score_global",
}


# ── 1. DESCUBRIMIENTO ─────────────────────────────────────────

@lru_cache(maxsize=1)
def fetch_portal_catalog() -> list[dict]:
    """
    [NEW-7] Descarga el catálogo CKAN completo y extrae TODOS los recursos
    CSV de cada dataset (no sólo el primero). Cada recurso genera una fila.
    """
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
            grupos = [g.get("title", "") for g in ds.get("groups", [])]
            cat    = grupos[0].strip().title() if grupos else "Sin categoría"

            # [NEW-7] Iterar sobre TODOS los recursos CSV
            for recurso in ds.get("resources", []):
                fmt = recurso.get("format", "").upper().strip()
                if fmt not in ("CSV", ".CSV"):
                    continue
                datasets.append({
                    "slug"             : ds.get("name", ""),
                    "recurso_id"       : recurso.get("id", ""),
                    "dataset"          : ds.get("title", "Sin nombre"),
                    "organizacion"     : org,
                    "categoria"        : cat,
                    "formato"          : fmt,
                    "url"              : recurso.get("url", ""),
                    "modificado"       : ds.get("metadata_modified", ""),
                    "frecuencia_update": ds.get("frequency", "").lower().strip(),
                })

        start += len(results)
        if start >= total:
            break
        time.sleep(DELAY_SEC)

    return datasets


# ── 2. DESCARGA Y NORMALIZACIÓN ────────────────────────────────

def download_csv(url: str) -> Optional[pd.DataFrame]:
    try:
        r = requests.get(
            url, timeout=30,
            headers={"User-Agent": "DatosAbiertosNL-Analyzer/2.2"},
        )
        r.raise_for_status()
        for enc in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
            try:
                return pd.read_csv(
                    io.StringIO(r.content.decode(enc)),
                    low_memory=False,
                )
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
    except Exception:
        pass
    return None


def normalize_categories(df: pd.DataFrame) -> pd.DataFrame:
    corrections = {
        "Administración Y Finanzas"                      : "Administración y Finanzas",
        "Arte Y Cultura"                                 : "Arte y Cultura",
        "Perspectiva De Género E Interseccionalidad"     : "Perspectiva de Género",
        "Transparencia Y Combate A La Corrupción"        : "Transparencia y Anticorrupción",
        "Transparencia Y Anticorrupción"                 : "Transparencia y Anticorrupción",
        "Atención Ciudadana"                             : "Atención Ciudadana",
        "Gobierno Y Transparencia"                       : "Gobierno y Transparencia",
        "Igualdad De Género"                             : "Igualdad de Género",
        "Desarrollo Urbano"                              : "Desarrollo Urbano",
        "Medio Ambiente"                                 : "Medio Ambiente",
        "Asistencia Social"                              : "Asistencia Social",
    }
    df = df.copy()
    if "categoria" in df.columns:
        df["categoria"] = (
            df["categoria"]
            .astype(str).str.strip().str.title()
            .replace(corrections)
        )
    return df


# ── 3. MÉTRICAS DE CALIDAD (5 DIMENSIONES) ────────────────────

def compute_completeness(df: pd.DataFrame) -> dict:
    total = df.size
    if not total:
        return {k: 0.0 for k in [
            "comp_completitud_global_pct", "comp_completitud_media_col",
            "comp_completitud_min_col", "comp_filas_incompletas_pct"]}
    nulos   = df.isnull().sum().sum()
    col_pct = 1 - df.isnull().mean()
    return {
        "comp_completitud_global_pct": round((total - nulos) / total * 100, 2),
        "comp_completitud_media_col" : round(col_pct.mean() * 100, 2),
        "comp_completitud_min_col"   : round(col_pct.min()  * 100, 2),
        "comp_filas_incompletas_pct" : round(df.isnull().any(axis=1).mean() * 100, 2),
    }


def compute_accuracy(df: pd.DataFrame) -> dict:
    """
    [FIX-1] Penalización proporcional al % de columnas afectadas.
    Un dataset de 3 cols mixtas y uno de 300 cols mixtas obtienen scores
    comparables, proporcionales a su severidad real.

    Fórmulas:
        penalty_mixed  = (cols_mixtas  / total_cols) * 40
        penalty_spaces = (cols_espacios / total_cols) * 15
        penalty_const  = (cols_const   / total_cols) * 20
    """
    n_cols = len(df.columns)
    if n_cols == 0:
        return {"acc_score_accuracy_pct": 0, "acc_columnas_tipo_mixto": 0,
                "acc_columnas_espacios": 0,   "acc_columnas_constantes": 0}

    mixed = spaces = const = 0
    for col in df.columns:
        serie = df[col].dropna()
        if serie.empty:
            continue
        if df[col].dtype == object:
            num_pct = pd.to_numeric(serie, errors="coerce").notna().mean()
            if 0.05 < num_pct < 0.95:
                mixed += 1
            if serie.astype(str).str.contains(r"^\s|\s$", regex=True).any():
                spaces += 1
        if serie.nunique() == 1:
            const += 1

    score = max(0, round(
        100
        - (mixed  / n_cols) * 40
        - (spaces / n_cols) * 15
        - (const  / n_cols) * 20,
        2,
    ))
    return {
        "acc_score_accuracy_pct" : score,
        "acc_columnas_tipo_mixto": mixed,
        "acc_columnas_espacios"  : spaces,
        "acc_columnas_constantes": const,
    }


def compute_consistency(df: pd.DataFrame) -> dict:
    """
    [FIX-2] Umbral IQR elevado de n >= 4 a n >= 30.
    Series cortas (5-10 valores) generaban IQR inestable y falsas alertas.
    """
    cols_num = df.select_dtypes(include=[np.number]).columns
    cols_txt = df.select_dtypes(include=["object"]).columns
    total_out = total_num = incons_txt = 0

    for col in cols_num:
        s = df[col].dropna()
        if len(s) < 30:          # [FIX-2] umbral estadístico robusto
            continue
        Q1, Q3 = s.quantile(.25), s.quantile(.75)
        IQR = Q3 - Q1
        if IQR > 0:
            total_out += int(((s < Q1 - 1.5 * IQR) | (s > Q3 + 1.5 * IQR)).sum())
        total_num += len(s)

    for col in cols_txt:
        s = df[col].dropna().astype(str)
        incons_txt += max(0, s.nunique() - s.str.strip().str.lower().nunique())

    pct_out = round(total_out / total_num * 100, 2) if total_num else 0
    score   = max(0, round(100 - pct_out * 2 - min(incons_txt * 0.5, 20), 2))
    return {
        "cons_score_consistency_pct": score,
        "cons_pct_outliers"         : pct_out,
        "cons_inconsistencias_texto": incons_txt,
        "cons_columnas_numericas"   : len(cols_num),
    }


def compute_uniqueness(df: pd.DataFrame) -> dict:
    n = len(df)
    if not n:
        return {"uniq_score_uniqueness_pct": 0, "uniq_pct_duplicados": 0,
                "uniq_duplicados_exactos": 0,   "uniq_cardinalidad_media": 0}
    dups     = df.duplicated().sum()
    pct_dup  = round(dups / n * 100, 2)
    card_med = round((df.nunique() / n * 100).mean(), 2)
    return {
        "uniq_score_uniqueness_pct": max(0, round(100 - pct_dup * 2, 2)),
        "uniq_pct_duplicados"      : pct_dup,
        "uniq_duplicados_exactos"  : int(dups),
        "uniq_cardinalidad_media"  : card_med,
    }


def compute_timeliness(meta: dict) -> dict:
    """
    [NEW-6] 5ª dimensión — puntualidad de actualización.
    Compara días desde la última modificación vs frecuencia declarada en CKAN.

    Score:
        - Sin fecha de modificación            → 50.0  (neutral, sin penalizar)
        - latencia <= frecuencia declarada      → 100.0
        - latencia >= 2× frecuencia declarada   → 0.0
        - Interpolación lineal entre ambos extremos
        - Sin frecuencia declarada              → penalización leve por año sin actualizar
    """
    modificado = meta.get("modificado", "") or ""
    freq_key   = (meta.get("frecuencia_update") or "").lower().strip()
    freq_dias  = _UPDATE_FREQ_DAYS.get(freq_key, 0)

    no_date_result = {
        "time_score_timeliness_pct": np.nan,
        "time_dias_desde_modificado": None,
        "time_frecuencia_declarada" : freq_key or "desconocida",
    }

    if not modificado:
        return no_date_result

    try:
        dt_mod = datetime.fromisoformat(
            modificado.replace("Z", "+00:00")
        ).replace(tzinfo=timezone.utc)
        dias = (datetime.now(timezone.utc) - dt_mod).days
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
        "time_score_timeliness_pct": score,
        "time_dias_desde_modificado": dias,
        "time_frecuencia_declarada" : freq_key or "desconocida",
    }


def compute_quality_scores(meta: dict, df: pd.DataFrame) -> dict:
    """
    [FIX-4] Score global con pesos configurables ISO 25012.
    Incluye la 5ª dimensión de puntualidad si hay datos de fecha.
    """
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

    for fn in [compute_completeness, compute_accuracy,
               compute_consistency,  compute_uniqueness]:
        row.update(fn(df))

    row.update(compute_timeliness(meta))

    # Score ponderado ISO 25012
    dim_score_map = {
        "completeness": row.get("comp_completitud_global_pct", 0) or 0,
        "accuracy"    : row.get("acc_score_accuracy_pct",      0) or 0,
        "consistency" : row.get("cons_score_consistency_pct",  0) or 0,
        "uniqueness"  : row.get("uniq_score_uniqueness_pct",   0) or 0,
    }
    timeliness_score = row.get("time_score_timeliness_pct")
    weights = dict(QUALITY_WEIGHTS)

    if timeliness_score is None or (isinstance(timeliness_score, float) and np.isnan(timeliness_score)):
        weights.pop("timeliness", None)
    else:
        dim_score_map["timeliness"] = timeliness_score

    total_w = sum(weights.values())
    row["score_global"] = round(
        sum(dim_score_map[k] * weights[k] for k in weights) / total_w, 2
    )
    return row


# ── 4. AGREGACIÓN ─────────────────────────────────────────────

def get_aggregations(df: pd.DataFrame, by: str = "categoria") -> pd.DataFrame:
    """
    [FIX-5] Rename dinámico via DIM_LABEL_MAP — no se desalinea si
    falta alguna dimensión (e.g. puntualidad en carga desde JSON).
    """
    dim_cols = list(DIM_LABEL_MAP.keys())
    cols_ok  = [c for c in dim_cols if c in df.columns]

    agg = (
        df.groupby(by)[cols_ok]
        .mean()
        .round(1)
        .sort_values("score_global", ascending=False)
        .reset_index()
    )
    agg.columns = [by] + [DIM_LABEL_MAP.get(c, c) for c in cols_ok]

    # Agregar conteo de datasets por grupo
    counts = df.groupby(by).size().reset_index(name="n_datasets")
    agg    = agg.merge(counts, on=by, how="left")
    return agg


def apply_filters(
    df: pd.DataFrame,
    categorias:     list[str] = None,
    organizaciones: list[str] = None,
    score_min:      float     = 0,
    score_max:      float     = 100,
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


# ── 5. CARGA DE RESULTADOS ─────────────────────────────────────

def load_results(path: str = "") -> pd.DataFrame:
    """
    [FIX-3] Carga datos desde CSV o fallback JSON.
    Valida el esquema antes de retornar; levanta error descriptivo si faltan columnas.
    """
    df = _load_raw(path)
    df = normalize_categories(df)
    _validate_schema(df)
    return df


def _load_raw(path: str) -> pd.DataFrame:
    csv_path = path or "resultados_calidad_datos_nl.csv"
    try:
        return pd.read_csv(csv_path, encoding="utf-8-sig")
    except FileNotFoundError:
        pass

    json_path = ".antigravity/team/shared/quality_results.json"
    try:
        with open(json_path, "r", encoding="utf-8") as f:
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

        # [FIX-4] Recalcular score_global con pesos ISO 25012 (sin timeliness)
        w4         = {k: v for k, v in QUALITY_WEIGHTS.items() if k != "timeliness"}
        total_w4   = sum(w4.values())
        score_glob = round(
            (scores["completeness"] * w4["completeness"]
             + scores["accuracy"]    * w4["accuracy"]
             + scores["consistency"] * w4["consistency"]
             + scores["uniqueness"]  * w4["uniqueness"]) / total_w4,
            2,
        )

        rows.append({
            "dataset"                    : d.get("slug", ""),
            "categoria"                  : d.get("categoria", ""),
            "organizacion"               : d.get("organizacion", ""),
            "filas"                      : d.get("filas", 0),
            "columnas"                   : d.get("columnas", 0),
            "modificado"                 : d.get("metadata_modified", ""),
            "frecuencia_update"          : d.get("frequency", ""),
            "comp_completitud_global_pct": scores.get("completeness", 0),
            "acc_score_accuracy_pct"     : scores.get("accuracy", 0),
            "cons_score_consistency_pct" : scores.get("consistency", 0),
            "uniq_score_uniqueness_pct"  : scores.get("uniqueness", 0),
            # timeliness = NaN cuando no hay fecha de modificación en el JSON
            "time_score_timeliness_pct"  : scores.get("timeliness", np.nan),
            "score_global"               : score_glob,
        })

    return pd.DataFrame(rows)


def _validate_schema(df: pd.DataFrame) -> None:
    missing = _REQUIRED_COLS - set(df.columns)
    if missing:
        raise ValueError(
            f"DataFrame de resultados sin columnas requeridas: {missing}. "
            "Verifica compatibilidad del CSV o JSON con data_layer v2.2."
        )
