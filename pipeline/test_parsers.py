"""pipeline/test_parsers.py — Tests unitarios por parser multiformato.

Fase 6: Verifica que cada parser de data_layer devuelva un DataFrame válido
con las columnas y tipos esperados. No requiere red — usa datos en memoria.
"""

import io
import json
import pytest
import pandas as pd

# Ensure project root is in path when running directly from pipeline/
import os
import sys
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from data_layer import (
    _parse_json,
    _parse_excel,
    _parse_geojson,
    _parse_xml,
    download_resource,
    is_safe_url,
)


# ── Fixtures ───────────────────────────────────────────────────

@pytest.fixture()
def csv_bytes() -> bytes:
    return b"nombre,valor\nalfa,1\nbeta,2\ngamma,3\n"


@pytest.fixture()
def json_list_bytes() -> bytes:
    data = [{"id": 1, "municipio": "Monterrey"}, {"id": 2, "municipio": "Apodaca"}]
    return json.dumps(data).encode("utf-8")


@pytest.fixture()
def json_dict_bytes() -> bytes:
    data = {"count": 2, "results": [{"id": 1, "val": "a"}, {"id": 2, "val": "b"}]}
    return json.dumps(data).encode("utf-8")


@pytest.fixture()
def geojson_bytes() -> bytes:
    data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-100.3, 25.7]},
                "properties": {"nombre": "Monterrey", "poblacion": 1135000},
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-100.1, 25.8]},
                "properties": {"nombre": "Apodaca", "poblacion": 650000},
            },
        ],
    }
    return json.dumps(data).encode("utf-8")


@pytest.fixture()
def xml_bytes() -> bytes:
    return b"""<?xml version="1.0" encoding="UTF-8"?>
<root>
  <item><id>1</id><municipio>Monterrey</municipio></item>
  <item><id>2</id><municipio>Apodaca</municipio></item>
</root>"""


@pytest.fixture()
def excel_bytes() -> bytes:
    df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
    buf = io.BytesIO()
    df.to_excel(buf, index=False, engine="openpyxl")
    return buf.getvalue()


# ── JSON parser ────────────────────────────────────────────────

def test_parse_json_list(json_list_bytes: bytes) -> None:
    df = _parse_json(json_list_bytes)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "municipio" in df.columns


def test_parse_json_dict_with_results_array(json_dict_bytes: bytes) -> None:
    df = _parse_json(json_dict_bytes)
    assert df is not None
    assert len(df) == 2
    assert "val" in df.columns


def test_parse_json_empty_list() -> None:
    df = _parse_json(b"[]")
    # Empty list → empty DataFrame is acceptable
    assert df is not None
    assert isinstance(df, pd.DataFrame)


# ── Excel parser ───────────────────────────────────────────────

def test_parse_excel(excel_bytes: bytes) -> None:
    df = _parse_excel(excel_bytes)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["A", "B"]
    assert len(df) == 3


# ── GeoJSON parser ─────────────────────────────────────────────

def test_parse_geojson(geojson_bytes: bytes) -> None:
    df = _parse_geojson(geojson_bytes)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "nombre" in df.columns
    assert "geometry_type" in df.columns
    assert df["geometry_type"].iloc[0] == "Point"


def test_parse_geojson_empty_features() -> None:
    data = {"type": "FeatureCollection", "features": []}
    df = _parse_geojson(json.dumps(data).encode())
    assert df is None


# ── XML parser ─────────────────────────────────────────────────

def test_parse_xml(xml_bytes: bytes) -> None:
    df = _parse_xml(xml_bytes)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 1


# ── download_resource dispatch ─────────────────────────────────

def test_download_resource_pdf_returns_none() -> None:
    """PDF should always return None (metadata-only per spec)."""
    result = download_resource("https://catalogodatos.nl.gob.mx/fake.pdf", "PDF")
    assert result is None


def test_download_resource_rejected_ssrf() -> None:
    """URLs outside allowed domains must be rejected (SSRF protection)."""
    result = download_resource("https://evil.example.com/data.json", "JSON")
    assert result is None


def test_download_resource_unknown_format_rejected() -> None:
    """Unknown format outside SSRF domain should also be rejected."""
    result = download_resource("https://attacker.io/file.bin", "BIN")
    assert result is None


# ── SSRF guard (data_layer.is_safe_url) ───────────────────────

@pytest.mark.parametrize("url,expected", [
    ("https://catalogodatos.nl.gob.mx/api/3/action/package_list", True),
    ("https://datos.nl.gob.mx/resource/abc.csv",                  True),
    ("https://evil.catalogodatos.nl.gob.mx.attacker.com/x",       False),
    ("https://notcatalogodatos.nl.gob.mx/data",                   False),
    ("http://localhost/data",                                      False),
    ("ftp://datos.nl.gob.mx/data",                                False),
])
def test_is_safe_url(url: str, expected: bool) -> None:
    assert is_safe_url(url) is expected
