"""
data_parsers.py — Parsers de formato y descarga de recursos.

Responsabilidades:
  - Descarga de CSV con detección de encoding/separador (download_csv)
  - Descarga multiformato con dispatch por formato (download_resource)
  - Parsers individuales: JSON, Excel, GeoJSON, XML

La validación SSRF vive en pipeline.fetcher.validate_url (fuente única).
"""

import csv
import io
import os
from urllib.parse import urlparse

import pandas as pd
import requests

from pipeline.fetcher import validate_url

# ── DESCARGA ──────────────────────────────────────────────────


def download_csv(url: str) -> pd.DataFrame | None:
    """Download CSV resources with robust charset detection and separator inference.

    Returns a pandas DataFrame or None on failure.
    """
    if not validate_url(url):
        import logging

        logging.getLogger("data_parsers").warning(
            "URL rechazada por política de seguridad SSRF: %s", url
        )
        return None

    try:
        r = requests.get(
            url,
            timeout=30,
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
        return None

    url_ext = os.path.splitext(urlparse(url).path)[1].upper().lstrip(".")
    _EXT_OVERRIDE: dict[str, str] = {
        "XLSX": "XLSX",
        "XLS": "XLS",
        "JSON": "JSON",
        "GEOJSON": "GEOJSON",
        "XML": "XML",
        "CSV": "CSV",
    }
    if url_ext in _EXT_OVERRIDE and _EXT_OVERRIDE[url_ext] != fmt.lstrip("."):
        fmt = _EXT_OVERRIDE[url_ext]

    if fmt in ("CSV", ".CSV"):
        return download_csv(url)

    if not validate_url(url):
        return None

    try:
        r = requests.get(
            url,
            timeout=(10, 60),
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


# ── PARSERS INTERNOS ──────────────────────────────────────────


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
