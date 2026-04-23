"""pipeline/test_ckan_client.py — Tests del cliente CKAN y contrato API.

Fase 6: Verifica contrato CKAN (success/result/results/count),
parseo de recursos multiformato, y la lógica de fallback.
No realiza llamadas de red reales — usa monkeypatching.
"""

import pytest
from unittest.mock import MagicMock, patch

import os
import sys
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from pipeline.ckan_client import (
    _validate,
    _get_frequency,
    _parse_resource,
    _extract_resources,
)


# ── _validate ──────────────────────────────────────────────────

def test_validate_success() -> None:
    data = {"success": True, "result": {"count": 5, "results": []}}
    assert _validate(data, "test") == {"count": 5, "results": []}


def test_validate_failure_flag() -> None:
    data = {"success": False, "error": {"message": "Not found"}}
    assert _validate(data, "test") is None


def test_validate_non_dict() -> None:
    assert _validate(None, "test") is None
    assert _validate([], "test") is None   # type: ignore[arg-type]
    assert _validate("bad", "test") is None  # type: ignore[arg-type]


def test_validate_missing_success_key() -> None:
    # Absence of 'success' key → falsy → None
    assert _validate({"result": {}}, "test") is None


# ── _get_frequency ─────────────────────────────────────────────

def test_get_frequency_top_level() -> None:
    ds = {"frequency": "Mensual"}
    assert _get_frequency(ds) == "mensual"


def test_get_frequency_from_extras() -> None:
    ds = {"extras": [{"key": "frequency", "value": "Semanal"}]}
    assert _get_frequency(ds) == "semanal"


def test_get_frequency_empty() -> None:
    assert _get_frequency({}) == ""
    assert _get_frequency({"frequency": None}) == ""


# ── _parse_resource ────────────────────────────────────────────

def _make_ds(resources: list[dict]) -> dict:
    return {
        "name": "test-dataset",
        "title": "Test Dataset",
        "notes": "Descripción",
        "license_title": "CC BY 4.0",
        "license_id": "cc-by",
        "metadata_modified": "2026-04-01T00:00:00",
        "organization": {"title": "DTIC NL", "name": "dtic-nl"},
        "groups": [{"display_name": "Gobierno y Transparencia"}],
        "resources": resources,
    }


def test_parse_resource_csv() -> None:
    ds = _make_ds([])
    r = {
        "id": "abc-123",
        "format": "CSV",
        "url": "https://catalogodatos.nl.gob.mx/data.csv",
        "description": "Datos",
    }
    result = _parse_resource(r, ds, "DTIC NL", "Gobierno y Transparencia")
    assert result is not None
    assert result["formato"] == "CSV"
    assert result["recurso_id"] == "abc-123"
    assert result["organizacion"] == "DTIC NL"


def test_parse_resource_json() -> None:
    ds = _make_ds([])
    r = {"id": "def-456", "format": "JSON", "url": "https://catalogodatos.nl.gob.mx/data.json"}
    result = _parse_resource(r, ds, "DTIC NL", "Gobierno")
    assert result is not None
    assert result["formato"] == "JSON"


def test_parse_resource_pdf_excluded() -> None:
    ds = _make_ds([])
    r = {"id": "ghi-789", "format": "PDF", "url": "https://catalogodatos.nl.gob.mx/doc.pdf"}
    result = _parse_resource(r, ds, "DTIC NL", "Gobierno")
    assert result is None


def test_parse_resource_unknown_excluded() -> None:
    ds = _make_ds([])
    r = {"id": "jkl-000", "format": "ZIP", "url": "https://catalogodatos.nl.gob.mx/file.zip"}
    result = _parse_resource(r, ds, "DTIC NL", "Gobierno")
    assert result is None


# ── _extract_resources ─────────────────────────────────────────

def test_extract_resources_mixed_formats() -> None:
    resources = [
        {"id": "r1", "format": "CSV",  "url": "https://catalogodatos.nl.gob.mx/a.csv"},
        {"id": "r2", "format": "JSON", "url": "https://catalogodatos.nl.gob.mx/b.json"},
        {"id": "r3", "format": "PDF",  "url": "https://catalogodatos.nl.gob.mx/c.pdf"},
        {"id": "r4", "format": "ZIP",  "url": "https://catalogodatos.nl.gob.mx/d.zip"},
    ]
    ds = _make_ds(resources)
    records = _extract_resources(ds)
    # Only CSV and JSON should be included
    assert len(records) == 2
    assert {r["formato"] for r in records} == {"CSV", "JSON"}


def test_extract_resources_no_org() -> None:
    ds = {
        "name": "no-org", "title": "No Org", "notes": "",
        "license_title": "", "license_id": "", "metadata_modified": "",
        "organization": None, "groups": [],
        "resources": [{"id": "x1", "format": "CSV", "url": "https://catalogodatos.nl.gob.mx/x.csv"}],
    }
    records = _extract_resources(ds)
    assert len(records) == 1
    assert records[0]["organizacion"] == ""
    assert records[0]["categoria"] == "Sin categoría"


# ── discover_catalog smoke (mocked network) ────────────────────

def test_discover_catalog_uses_fallback_on_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    """When package_search returns 0 resources, fallback must be triggered."""
    call_log: list[str] = []

    def mock_discover_via_search() -> list[dict]:
        call_log.append("search")
        return []  # Empty — triggers fallback

    def mock_discover_via_list() -> list[dict]:
        call_log.append("list")
        return [{"slug": "test", "formato": "CSV", "recurso_id": "1",
                 "dataset": "Test", "organizacion": "Org", "categoria": "Cat",
                 "url": "https://catalogodatos.nl.gob.mx/t.csv", "modificado": "",
                 "frecuencia_update": "", "descripcion": "", "licencia": "",
                 "licencia_id": "", "num_resources": 1,
                 "resource_formats": ["CSV"], "resource_descs": [""]}]

    import pipeline.ckan_client as cc
    monkeypatch.setattr(cc, "discover_via_search", mock_discover_via_search)
    monkeypatch.setattr(cc, "discover_via_list",   mock_discover_via_list)

    result = cc.discover_catalog(use_fallback=True)
    assert "search" in call_log
    assert "list" in call_log
    assert len(result) == 1


def test_discover_catalog_no_fallback_when_results(monkeypatch: pytest.MonkeyPatch) -> None:
    """When package_search returns data, fallback must NOT be called."""
    call_log: list[str] = []

    record = {"slug": "ds1", "formato": "CSV", "recurso_id": "1",
              "dataset": "DS", "organizacion": "Org", "categoria": "Cat",
              "url": "https://catalogodatos.nl.gob.mx/ds.csv", "modificado": "",
              "frecuencia_update": "", "descripcion": "", "licencia": "",
              "licencia_id": "", "num_resources": 1,
              "resource_formats": ["CSV"], "resource_descs": [""]}

    def mock_search() -> list[dict]:
        call_log.append("search")
        return [record]

    def mock_list() -> list[dict]:
        call_log.append("list")
        return []

    import pipeline.ckan_client as cc
    monkeypatch.setattr(cc, "discover_via_search", mock_search)
    monkeypatch.setattr(cc, "discover_via_list",   mock_list)

    result = cc.discover_catalog(use_fallback=True)
    assert "search" in call_log
    assert "list" not in call_log
    assert len(result) == 1
