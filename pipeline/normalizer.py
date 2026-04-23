"""pipeline/normalizer.py — Normalización de DataFrames extraídos.

Fase 3:
- Limpieza de nulos canónicos (N/A, null, -, sin dato, …)
- Fechas → UTC ISO 8601 (columnas detectadas por nombre)
- Geoespacial → float validado, lat ∈ [-90, 90], lon ∈ [-180, 180]
- Municipio → nombre canónico NL + cve_municipio INEGI

Todas las funciones reciben y devuelven pd.DataFrame (CoW-compliant).
"""

from __future__ import annotations

import re
import logging
from datetime import timezone

import numpy as np
import pandas as pd
from dateutil import parser as dateutil_parser

logger = logging.getLogger("normalizer")

# ── Nulos canónicos ────────────────────────────────────────────

_NULL_SENTINELS: frozenset[str] = frozenset({
    "n/a", "na", "n.a.", "null", "none", "nil", "nan",
    "-", "--", "---", ".", "0000-00-00",
    "sin dato", "sin información", "sin informacion",
    "no aplica", "no disponible", "nd",
})

# ── Patrones de nombre para detección de columnas ─────────────

_DATE_RE   = re.compile(r"(fecha|date|created|modified|actualiz|registro|inicio|fin|año|year)", re.I)
_LAT_RE    = re.compile(r"(^lat$|latitud|latitude|coord_y|^y$)", re.I)
_LON_RE    = re.compile(r"(^lon$|^long$|longitud|longitude|coord_x|^x$)", re.I)
_MUN_RE    = re.compile(r"(municipio|municipality|muni)", re.I)
_CVE_RE    = re.compile(r"(cve_mun|cvemun|clave_mun)", re.I)

# ── Catálogo de municipios NL (nombre → cve_municipio INEGI) ──

_MUNICIPIOS_NL: dict[str, str] = {
    "abasolo": "19001", "agualeguas": "19002", "allende": "19004",
    "anahuac": "19005", "anáhuac": "19005", "apodaca": "19006",
    "aramberri": "19007", "bustamante": "19009", "cadereyta jimenez": "19010",
    "cadereyta jiménez": "19010", "cerralvo": "19011", "china": "19013",
    "cienega de flores": "19014", "ciénega de flores": "19014",
    "doctor arroyo": "19018", "doctor coss": "19019", "doctor gonzalez": "19020",
    "doctor gonzález": "19020", "el carmen": "19021", "galeana": "19022",
    "garcia": "19023", "garcía": "19023", "general bravo": "19024",
    "general escobedo": "19025", "general teran": "19026",
    "general terán": "19026", "general trevino": "19028",
    "general treviño": "19028", "general zaragoza": "19027",
    "general zuazua": "19029", "guadalupe": "19031", "hidalgo": "19032",
    "higueras": "19033", "hualahuises": "19034", "iturbide": "19035",
    "juarez": "19036", "juárez": "19036", "lampazos de naranjo": "19037",
    "linares": "19039", "los aldamas": "19040", "los herreras": "19041",
    "los ramones": "19042", "marin": "19043", "marín": "19043",
    "melchor ocampo": "19044", "mier y noriega": "19045", "mina": "19046",
    "montemorelos": "19047", "monterrey": "19039",
    "paras": "19048", "parás": "19048", "pesqueria": "19049",
    "pesquería": "19049", "rayones": "19050", "sabinas hidalgo": "19051",
    "salinas victoria": "19052", "san nicolas de los garza": "19053",
    "san nicolás de los garza": "19053", "san pedro garza garcia": "19054",
    "san pedro garza garcía": "19054", "santa catarina": "19055",
    "santiago": "19056", "vallecillo": "19057", "villaldama": "19058",
}

_CANONICAL_MUNICIPIO: dict[str, str] = {
    "19001": "Abasolo", "19002": "Agualeguas", "19004": "Allende",
    "19005": "Anáhuac", "19006": "Apodaca", "19007": "Aramberri",
    "19009": "Bustamante", "19010": "Cadereyta Jiménez", "19011": "Cerralvo",
    "19013": "China", "19014": "Ciénega de Flores", "19018": "Doctor Arroyo",
    "19019": "Doctor Coss", "19020": "Doctor González", "19021": "El Carmen",
    "19022": "Galeana", "19023": "García", "19024": "General Bravo",
    "19025": "General Escobedo", "19026": "General Terán", "19027": "General Zaragoza",
    "19028": "General Treviño", "19029": "General Zuazua", "19031": "Guadalupe",
    "19032": "Hidalgo", "19033": "Higueras", "19034": "Hualahuises",
    "19035": "Iturbide", "19036": "Juárez", "19037": "Lampazos de Naranjo",
    "19039": "Linares", "19040": "Los Aldamas", "19041": "Los Herreras",
    "19042": "Los Ramones", "19043": "Marín", "19044": "Melchor Ocampo",
    "19045": "Mier y Noriega", "19046": "Mina", "19047": "Montemorelos",
    "19048": "Parás", "19049": "Pesquería", "19050": "Rayones",
    "19051": "Sabinas Hidalgo", "19052": "Salinas Victoria",
    "19053": "San Nicolás de los Garza", "19054": "San Pedro Garza García",
    "19055": "Santa Catarina", "19056": "Santiago", "19057": "Vallecillo",
    "19058": "Villaldama",
}


# ── Limpieza de nulos canónicos ────────────────────────────────

def clean_null_sentinels(df: pd.DataFrame) -> pd.DataFrame:
    """Reemplaza strings que representan nulos por pd.NA.

    Aplica sólo a columnas object/string; numéricos y fechas no se tocan.
    CoW-compliant: opera sobre copia.
    """
    df = df.copy()
    obj_cols = df.select_dtypes(include=["object", "string"]).columns
    if not len(obj_cols):
        return df

    def _replace(s: pd.Series) -> pd.Series:
        return s.where(
            ~s.str.strip().str.lower().isin(_NULL_SENTINELS),
            other=pd.NA,
        )

    df[obj_cols] = df[obj_cols].apply(
        lambda s: _replace(s.astype(str).mask(s.isna()))
    )
    return df


# ── Normalización de fechas → UTC ISO 8601 ────────────────────

def _to_utc_iso(val: object) -> object:
    """Convierte un valor a string UTC ISO 8601, o devuelve pd.NA."""
    if pd.isna(val) or val == "":  # type: ignore[arg-type]
        return pd.NA
    try:
        dt = dateutil_parser.parse(str(val), dayfirst=False)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return pd.NA


def normalize_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte columnas con nombres tipo fecha a UTC ISO 8601.

    Detección por patrón de nombre de columna (_DATE_RE).
    No modifica columnas ya en formato datetime64.
    """
    df = df.copy()
    for col in df.columns:
        if not _DATE_RE.search(col):
            continue
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            # Ya es datetime — sólo localizar a UTC como string
            df[col] = (
                df[col]
                .dt.tz_localize("UTC", ambiguous="NaT", nonexistent="NaT")
                .dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            )
        else:
            df[col] = df[col].apply(_to_utc_iso)
    return df


# ── Normalización geoespacial ──────────────────────────────────

def normalize_geo(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte columnas de latitud/longitud a float y valida rangos.

    Lat ∈ [-90, 90], Lon ∈ [-180, 180].
    Valores fuera de rango o no numéricos → pd.NA.
    """
    df = df.copy()

    for col in df.columns:
        is_lat = bool(_LAT_RE.search(col))
        is_lon = bool(_LON_RE.search(col))
        if not (is_lat or is_lon):
            continue

        numeric = pd.to_numeric(df[col], errors="coerce")
        if is_lat:
            valid = numeric.between(-90, 90, inclusive="both")
        else:
            valid = numeric.between(-180, 180, inclusive="both")

        out_of_range = (~valid) & numeric.notna()
        if out_of_range.any():
            logger.debug(
                "[normalizer] %s: %d geo values out of range → NA",
                col, int(out_of_range.sum()),
            )
        df[col] = numeric.where(valid, other=pd.NA)

    return df


# ── Normalización de municipio NL ─────────────────────────────

def normalize_municipio(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza columnas de municipio y agrega cve_municipio INEGI.

    - Detecta columnas por _MUN_RE y _CVE_RE.
    - Convierte nombre libre → cve_municipio (19XXX) → nombre canónico.
    - Agrega columna `cve_municipio` si no existe.
    - No sobreescribe `cve_municipio` si ya existe y tiene valores válidos.
    """
    df = df.copy()

    mun_cols = [c for c in df.columns if _MUN_RE.search(c) and not _CVE_RE.search(c)]
    cve_cols = [c for c in df.columns if _CVE_RE.search(c)]

    if not mun_cols and not cve_cols:
        return df

    def _lookup_cve(val: object) -> object:
        if pd.isna(val):
            return pd.NA
        key = str(val).strip().lower()
        # Remove accents for matching
        key_clean = _strip_accents(key)
        return _MUNICIPIOS_NL.get(key, _MUNICIPIOS_NL.get(key_clean, pd.NA))

    def _lookup_canonical(cve: object) -> object:
        if pd.isna(cve):
            return pd.NA
        return _CANONICAL_MUNICIPIO.get(str(cve).strip(), pd.NA)

    # Normalize municipality name columns
    for col in mun_cols:
        cve_series = df[col].apply(_lookup_cve)
        canonical  = cve_series.apply(_lookup_canonical)
        # Only overwrite where we have a match
        matched = canonical.notna()
        if matched.any():
            df.loc[matched, col] = canonical[matched]

        # Add cve_municipio column if not present
        if "cve_municipio" not in df.columns:
            df["cve_municipio"] = cve_series
        else:
            # Fill missing values
            missing_mask = df["cve_municipio"].isna()
            df.loc[missing_mask, "cve_municipio"] = cve_series[missing_mask]

    # If only cve_cols exist, validate format and add canonical name
    for col in cve_cols:
        df["cve_municipio"] = df[col].astype(str).str.strip()
        if "municipio_nombre" not in df.columns:
            df["municipio_nombre"] = df["cve_municipio"].apply(_lookup_canonical)

    return df


def _strip_accents(s: str) -> str:
    """Remove common Spanish accent characters for fuzzy matching."""
    return (
        s.replace("á", "a").replace("é", "e").replace("í", "i")
         .replace("ó", "o").replace("ú", "u").replace("ü", "u")
         .replace("ñ", "n")
    )


# ── Orquestador principal ──────────────────────────────────────

def normalize_df(df: pd.DataFrame, formato: str = "") -> pd.DataFrame:
    """Aplica pipeline de normalización completo sobre un DataFrame extraído.

    Orden:
      1. Limpieza de nulos canónicos
      2. Normalización de fechas → UTC ISO 8601
      3. Normalización geoespacial (lat/lon)
      4. Normalización de municipio NL

    Args:
        df:      DataFrame extraído por el motor de descarga.
        formato: Formato del recurso (CSV, JSON, etc.) — informativo.

    Returns:
        DataFrame normalizado (copia independiente).
    """
    if df is None or df.empty:
        return df

    df = clean_null_sentinels(df)
    df = normalize_dates(df)
    df = normalize_geo(df)
    df = normalize_municipio(df)
    return df
