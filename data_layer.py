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
from datetime import UTC, datetime
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

CKAN_API  = "https://catalogodatos.nl.gob.mx/api/3/action"
DELAY_SEC = 1.5

# Formatos soportados para descarga multiformato (Fase 2)
_MULTIFORMAT_PARSERS: frozenset[str] = frozenset({
    "CSV", ".CSV", "JSON", "XLSX", "XLS", "GEOJSON", "XML",
})

# ── PESOS ISO 25012 ───────────────────────────────────────────
# Fuente única: config.py. No redefinir aquí.
from config import CLASIFICACION_DEFAULT, CLASIFICACION_THRESHOLDS, QUALITY_WEIGHTS

# Etiquetas de presentación para cada columna de dimensión
DIM_LABEL_MAP: dict[str, str] = {
    "comp_completitud_global_pct": "Completitud",
    "acc_score_accuracy_pct":      "Exactitud",
    "cons_score_consistency_pct":  "Consistencia",
    "uniq_score_uniqueness_pct":   "Unicidad",
    "time_score_timeliness_pct":   "Puntualidad",
    "doc_score_documentation_pct": "Documentación",
    "open_score_openness_pct":     "Apertura",
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
        data    = r.json()
        results = data["result"]["results"]
        total   = data["result"]["count"]
        if not results:
            break
        for ds in results:
            org    = (ds.get("organization") or {}).get("title", "Desconocida")
            grupos = [g.get("title", "") for g in ds.get("groups", [])]
            cat    = grupos[0].strip().title() if grupos else "Sin categoría"
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
                    "frecuencia_update": ds.get("frequency", "").lower().strip()
                                        if isinstance(ds.get("frequency"), str) else "",
                    "descripcion"      : ds.get("notes", "") or "",
                    "licencia"         : ds.get("license_title", "") or "",
                    "licencia_id"      : ds.get("license_id", "") or "",
                    "num_resources"    : len(ds.get("resources", [])),
                    "resource_formats" : [rx.get("format", "").upper().strip()
                                          for rx in ds.get("resources", [])],
                    "resource_descs"   : [rx.get("description", "") or ""
                                          for rx in ds.get("resources", [])],
                })
        start += len(results)
        if start >= total:
            break
        time.sleep(DELAY_SEC)
    return datasets


# ── 2. DESCARGA Y NORMALIZACIÓN ────────────────────────────────

def is_safe_url(url: str) -> bool:
    """Verifica dominios permitidos para evitar SSRF."""
    from config import DOMINIOS_PERMITIDOS
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False

        # Validación estricta: coincidencia exacta o subdominio válido
        netloc = parsed.netloc.lower()
        # Eliminar el puerto si está presente
        if ":" in netloc:
            netloc = netloc.split(":")[0]

        return any(netloc == d or netloc.endswith("." + d) for d in DOMINIOS_PERMITIDOS)
    except Exception:
        return False


def download_csv(url: str) -> pd.DataFrame | None:
    if not is_safe_url(url):
        print(f"URL rechazada por política de seguridad SSRF: {url}")
        return None

    try:
        r = requests.get(
            url, timeout=30,
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
        "XLSX": "XLSX", "XLS": "XLS",
        "JSON": "JSON", "GEOJSON": "GEOJSON",
        "XML": "XML", "CSV": "CSV",
    }
    if url_ext in _EXT_OVERRIDE and _EXT_OVERRIDE[url_ext] != fmt.lstrip("."):
        fmt = _EXT_OVERRIDE[url_ext]

    if fmt in ("CSV", ".CSV"):
        return download_csv(url)

    if not is_safe_url(url):
        return None

    try:
        r = requests.get(
            url, timeout=(10, 60),
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


# ── 3. MÉTRICAS DE CALIDAD (7 DIMENSIONES) ────────────────────

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
    Refactorizado a procesamiento vectorizado Pandas.
    """
    n_cols = len(df.columns)
    if n_cols == 0:
        return {"acc_score_accuracy_pct": 0, "acc_columnas_tipo_mixto": 0,
                "acc_columnas_espacios": 0,   "acc_columnas_constantes": 0}

    # Vectorizado a nivel Dataframe
    const = int((df.nunique() == 1).sum())

    mixed = spaces = 0
    obj_cols = df.select_dtypes(include=["object", "string"]).columns

    if len(obj_cols) > 0:
        df_obj = df[obj_cols]

        # Detección vectorizada de espacios
        has_spaces = df_obj.apply(lambda x: x.astype(str).str.contains(r"^\s|\s$", regex=True).any())
        spaces = int(has_spaces.sum())

        # Tipos mixtos (numérico vs string en misma columna)
        def is_mixed(s):
            s_val = s.dropna()
            if s_val.empty: return False
            pct = pd.to_numeric(s_val, errors="coerce").notna().mean()
            return 0.05 < pct < 0.95

        mixed = int(df_obj.apply(is_mixed).sum())

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
    Refactorizado a procesamiento vectorial Pandas completo.
    """
    total_out = total_num = incons_txt = 0

    # 1. Outliers en numéricos (Vectorizado matricial)
    cols_num = df.select_dtypes(include=[np.number]).columns
    if len(cols_num) > 0:
        df_num = df[cols_num]
        counts = df_num.count()
        valid_cols = counts[counts >= 30].index

        if len(valid_cols) > 0:
            df_valid = df_num[valid_cols]
            Q1 = df_valid.quantile(.25)
            Q3 = df_valid.quantile(.75)
            IQR = Q3 - Q1

            valid_iqr = IQR[IQR > 0].index
            if len(valid_iqr) > 0:
                df_calc = df_valid[valid_iqr]
                bounds_lower = Q1[valid_iqr] - 1.5 * IQR[valid_iqr]
                bounds_upper = Q3[valid_iqr] + 1.5 * IQR[valid_iqr]

                # Operación booleana matricial global
                outliers_mask = (df_calc < bounds_lower) | (df_calc > bounds_upper)
                total_out = int(outliers_mask.sum().sum())
                total_num = int(df_calc.count().sum())

    # 2. Inconsistencias en texto (Vectorizado)
    cols_txt = df.select_dtypes(include=["object", "string"]).columns
    if len(cols_txt) > 0:
        df_txt = df[cols_txt].astype(str)
        raw_nunique = df_txt.nunique()
        clean_nunique = df_txt.apply(lambda x: x.str.strip().str.lower()).nunique()

        diff = raw_nunique - clean_nunique
        incons_txt = int(diff[diff > 0].sum())

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
        ).replace(tzinfo=UTC)
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
        "time_score_timeliness_pct": score,
        "time_dias_desde_modificado": dias,
        "time_frecuencia_declarada" : freq_key or "desconocida",
    }


def compute_documentation(meta: dict) -> dict:
    """
    [NEW-8] 6ª dimensión — Documentación del dataset.
    Evalúa a nivel catálogo/metadatos CKAN (no contenido del CSV).

    Componentes (0-100):
        - Descripción del dataset (30 pts)
        - Descripción de campos/recursos (30 pts)
        - Licencia explícita (20 pts)
        - Notas metodológicas (20 pts)
    """
    score = 0.0
    details: dict = {}

    # 1. Descripción del dataset (30 pts)
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

    # 2. Descripción de recursos (30 pts)
    resource_descs = meta.get("resource_descs", [])
    if resource_descs:
        described = sum(1 for d in resource_descs if (d or "").strip())
        ratio = described / len(resource_descs)
        res_pts = round(ratio * 30, 2)
    else:
        res_pts = 0.0
    score += res_pts
    details["doc_resources_described"] = res_pts

    # 3. Licencia explícita (20 pts)
    licencia = str(meta.get("licencia", "") or "").strip()
    licencia_id = str(meta.get("licencia_id", "") or "").strip()
    if licencia or licencia_id:
        lic_pts = 20.0
    else:
        lic_pts = 0.0
    score += lic_pts
    details["doc_licencia"] = licencia or licencia_id or "sin especificar"
    details["doc_licencia_pts"] = lic_pts

    # 4. Notas metodológicas (20 pts)
    texto_buscar = desc.lower()
    keywords_found: list[str] = []
    for kw in ["metodolog", "fuente", "diccionario", "glosario", "nota",
               "definici", "metadat", "variable", "indicador"]:
        if kw in texto_buscar:
            keywords_found.append(kw)
    meth_pts = min(20.0, len(keywords_found) * 5.0)
    score += meth_pts
    details["doc_keywords_found"] = keywords_found
    details["doc_metodologia_pts"] = meth_pts

    return {
        "doc_score_documentation_pct": round(score, 2),
        **details,
    }


def compute_openness(meta: dict) -> dict:
    """
    [NEW-9] 7ª dimensión — Apertura del dataset.
    Evalúa nivel de apertura según principios de Open Data.

    Componentes (0-100):
        - Formato abierto (40 pts): CSV/JSON/GeoJSON/XML = 40, XLS/XLSX = 20, PDF = 5
        - Licencia abierta (35 pts): creative commons / open / libre = 35
        - Acceso sin registro (25 pts): URL directa HTTP(S) = 25
    """
    score = 0.0
    details: dict = {}

    # 1. Formato abierto (40 pts)
    formatos = meta.get("resource_formats", [])
    formato_actual = str(meta.get("formato", "")).upper()
    all_formats = set(formatos) | {formato_actual}

    OPEN_FORMATS = {"CSV", "JSON", "GEOJSON", "XML", "RDF", "SPARQL", "TSV"}
    SEMI_OPEN = {"XLS", "XLSX", "ODS"}
    CLOSED = {"PDF", "DOC", "DOCX", "PPT", "PPTX", "ZIP"}

    if all_formats & OPEN_FORMATS:
        fmt_pts = 40.0
    elif all_formats & SEMI_OPEN:
        fmt_pts = 20.0
    elif all_formats & CLOSED:
        fmt_pts = 5.0
    else:
        fmt_pts = 0.0
    score += fmt_pts
    details["open_formatos"] = list(all_formats - {""})
    details["open_formato_pts"] = fmt_pts

    # 2. Licencia abierta (35 pts)
    licencia = str(meta.get("licencia", "") or "").lower()
    licencia_id = str(meta.get("licencia_id", "") or "").lower()
    lic_text = f"{licencia} {licencia_id}"

    OPEN_LIC_KEYWORDS = ["creative commons", "cc-by", "cc0", "open",
                         "libre", "abierta", "datos abiertos",
                         "public domain", "dominio público"]
    if any(kw in lic_text for kw in OPEN_LIC_KEYWORDS):
        lic_pts = 35.0
    elif licencia or licencia_id:
        lic_pts = 15.0  # Tiene licencia pero no explícitamente abierta
    else:
        lic_pts = 0.0
    score += lic_pts
    details["open_licencia"] = licencia or licencia_id or "sin especificar"
    details["open_licencia_pts"] = lic_pts

    # 3. Acceso sin registro (25 pts)
    url = str(meta.get("url", "") or "")
    if url.startswith(("http://", "https://")):
        access_pts = 25.0
    else:
        access_pts = 0.0
    score += access_pts
    details["open_acceso_directo"] = bool(url)
    details["open_acceso_pts"] = access_pts

    return {
        "open_score_openness_pct": round(score, 2),
        **details,
    }


def compute_quality_scores(meta: dict, df: pd.DataFrame) -> dict:
    """
    [FIX-4] Score global con pesos configurables — 7 dimensiones.
    5 ISO 25012 (contenido) + 2 catálogo (documentation, openness).
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

    # Dimensiones de contenido (operan sobre DataFrame)
    for fn in [compute_completeness, compute_accuracy,
               compute_consistency,  compute_uniqueness]:
        row.update(fn(df))

    # Dimensiones de catálogo (operan sobre metadatos CKAN)
    row.update(compute_timeliness(meta))
    row.update(compute_documentation(meta))
    row.update(compute_openness(meta))

    # Score ponderado — 7 dimensiones
    dim_score_map = {
        "completeness" : row.get("comp_completitud_global_pct", 0) or 0,
        "accuracy"     : row.get("acc_score_accuracy_pct",      0) or 0,
        "consistency"  : row.get("cons_score_consistency_pct",  0) or 0,
        "uniqueness"   : row.get("uniq_score_uniqueness_pct",   0) or 0,
        "documentation": row.get("doc_score_documentation_pct", 0) or 0,
        "openness"     : row.get("open_score_openness_pct",     0) or 0,
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
    rename_map = {c: DIM_LABEL_MAP.get(c, c) for c in cols_ok}
    agg = agg.rename(columns=rename_map)

    # Agregar conteo de datasets por grupo
    counts = df.groupby(by).size().reset_index(name="n_datasets")
    agg    = agg.merge(counts, on=by, how="left")
    return agg


def apply_filters(
    df: pd.DataFrame,
    categorias:     list[str] | None = None,
    organizaciones: list[str] | None = None,
    formatos:       list[str] | None = None,
    score_min:      float            = 0,
    score_max:      float            = 100,
) -> pd.DataFrame:
    """Aplica filtros combinados sobre el DataFrame de resultados.

    Args:
        categorias:     Lista de categorías a incluir (None = todas).
        organizaciones: Lista de organizaciones a incluir (None = todas).
        formatos:       Lista de formatos a incluir (None = todos). [Fase 5]
        score_min/max:  Rango de score global [0, 100].
    """
    mask = pd.Series([True] * len(df), index=df.index)

    if categorias and "categoria" in df.columns:
        if "Todas" not in categorias:
            mask &= df["categoria"].isin(categorias)
    if organizaciones and "organizacion" in df.columns:
        if "Todas" not in organizaciones:
            mask &= df["organizacion"].isin(organizaciones)
    if formatos and "formato" in df.columns:
        if "Todos" not in formatos:
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
    return df


def _load_raw(path: str) -> pd.DataFrame:
    if os.getenv("USE_BIGQUERY", "false").lower() == "true":
        return _load_from_bigquery()

    if path:
        abs_path = os.path.abspath(path)
        base_dir = os.path.abspath(os.getcwd())
        if not abs_path.startswith(base_dir):
            raise PermissionError("Path traversal detectado. Acceso denegado a rutas fuera del directorio de trabajo.")

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

        # [FIX-4] Recalcular score_global con pesos disponibles
        available_dims = {}
        for wk in QUALITY_WEIGHTS:
            if wk in scores and scores[wk] is not None:
                available_dims[wk] = scores[wk]
        if not available_dims:
            continue
        w_avail    = {k: QUALITY_WEIGHTS[k] for k in available_dims}
        total_w    = sum(w_avail.values())
        score_glob = round(
            sum(available_dims[k] * w_avail[k] for k in available_dims) / total_w,
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
            "time_score_timeliness_pct"  : scores.get("timeliness", np.nan),
            "doc_score_documentation_pct": scores.get("documentation", 0),
            "open_score_openness_pct"    : scores.get("openness", 0),
            "score_global"               : score_glob,
        })

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
    """[FIX-8] Deduplica múltiples recursos CSV del mismo dataset.

    Un dataset CKAN puede tener varios recursos CSV (ej. diccionario + datos).
    El pipeline los registra a todos; aquí conservamos sólo el que obtenga el
    score_global más alto, evitando que los KPIs de Resumen dupliquen entradas.
    """
    if "dataset" not in df.columns or "score_global" not in df.columns:
        return df
    deduped = (
        df.sort_values("score_global", ascending=False)
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
    ".antigravity", "team", "shared", "advanced_quality_results.json",
)
_MAIN_JSON_PATH = os.path.join(
    ".antigravity", "team", "shared", "quality_results.json",
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
