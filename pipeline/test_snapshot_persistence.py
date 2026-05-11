"""pipeline/test_snapshot_persistence.py — Tests for the unified snapshot system.

Verifies that persistence.save_snapshot() and persistence.load_latest_snapshot()
form a coherent round-trip with SHA256 integrity checking, and that the legacy
fallback for flat JSON files also works.
"""

from __future__ import annotations

import hashlib
import json
import os

import pytest

from pipeline.persistence import (
    SNAPSHOT_DIR,
    load_latest_snapshot,
    save_snapshot,
)


# ── Helpers ───────────────────────────────────────────────────


def _sha256_of_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# ── save_snapshot ─────────────────────────────────────────────


def test_save_snapshot_creates_json_and_sha(tmp_path):
    """save_snapshot escribe el JSON y sha256.txt en el directorio indicado."""
    snap_dir = str(tmp_path / "snapshots" / "run_test")
    data = {"run_id": "test_001", "datasets": []}

    snap_path, sha = save_snapshot(data, snap_dir)

    assert os.path.isfile(snap_path), "El archivo de snapshot debe existir"
    sha_path = os.path.join(snap_dir, "sha256.txt")
    assert os.path.isfile(sha_path), "sha256.txt debe existir junto al snapshot"

    with open(sha_path, "r", encoding="utf-8") as f:
        stored_sha = f.read().strip()

    assert sha == stored_sha, "SHA retornado debe coincidir con sha256.txt"
    assert sha == _sha256_of_file(snap_path), "SHA debe ser el digest real del archivo"


def test_save_snapshot_content_is_valid_json(tmp_path):
    """El archivo guardado debe ser JSON válido y recuperable."""
    snap_dir = str(tmp_path / "run_json")
    payload = {"run_id": "r1", "dimensiones": 7, "datasets": [{"slug": "ds-1"}]}

    snap_path, _ = save_snapshot(payload, snap_dir)

    with open(snap_path, "r", encoding="utf-8") as f:
        loaded = json.load(f)

    assert loaded["run_id"] == "r1"
    assert loaded["dimensiones"] == 7
    assert loaded["datasets"][0]["slug"] == "ds-1"


def test_save_snapshot_returns_absolute_path(tmp_path):
    """save_snapshot debe retornar una ruta absoluta."""
    snap_dir = str(tmp_path / "run_abs")
    snap_path, _ = save_snapshot({"x": 1}, snap_dir)
    assert os.path.isabs(snap_path), "La ruta del snapshot debe ser absoluta"


def test_save_snapshot_custom_filename(tmp_path):
    """El parámetro filename debe controlar el nombre del archivo JSON."""
    snap_dir = str(tmp_path / "run_custom")
    snap_path, _ = save_snapshot({"x": 1}, snap_dir, filename="advanced_results.json")
    assert snap_path.endswith("advanced_results.json")
    assert os.path.isfile(snap_path)


# ── load_latest_snapshot ──────────────────────────────────────


def test_load_latest_snapshot_round_trip(tmp_path):
    """save + load debe devolver el mismo payload."""
    base = str(tmp_path / "snapshots")
    snap_dir = os.path.join(base, "run_20260510_120000")
    payload = {"run_id": "20260510_120000", "datasets": [{"slug": "a"}]}

    save_snapshot(payload, snap_dir)
    result = load_latest_snapshot(base_dir=base)

    assert result is not None
    assert result["run_id"] == "20260510_120000"
    assert result["datasets"][0]["slug"] == "a"


def test_load_latest_snapshot_picks_newest_run(tmp_path):
    """load_latest_snapshot debe cargar el run_dir más reciente."""
    base = str(tmp_path / "snapshots")
    for run_id in ("run_20260101_000000", "run_20260510_000000", "run_20260201_000000"):
        save_snapshot({"run_id": run_id}, os.path.join(base, run_id))

    result = load_latest_snapshot(base_dir=base)
    assert result is not None
    # Lexicográficamente el más reciente es run_20260510_000000
    assert result["run_id"] == "run_20260510_000000"


def test_load_latest_snapshot_returns_none_when_empty(tmp_path):
    """Retorna None si el directorio no existe o no tiene snapshots."""
    result = load_latest_snapshot(base_dir=str(tmp_path / "nonexistent"))
    assert result is None


def test_load_latest_snapshot_skips_corrupted_sha(tmp_path):
    """Snapshots con SHA256 inválido son ignorados; se cae al siguiente."""
    base = str(tmp_path / "snapshots")

    # run más reciente — SHA corrupto
    corrupt_dir = os.path.join(base, "run_20260510_200000")
    os.makedirs(corrupt_dir)
    with open(os.path.join(corrupt_dir, "quality_results.json"), "w", encoding="utf-8") as f:
        json.dump({"run_id": "corrupt"}, f)
    with open(os.path.join(corrupt_dir, "sha256.txt"), "w", encoding="utf-8") as f:
        f.write("0000000000000000000000000000000000000000000000000000000000000000")

    # run anterior — íntegro
    good_dir = os.path.join(base, "run_20260501_000000")
    save_snapshot({"run_id": "good"}, good_dir)

    result = load_latest_snapshot(base_dir=base)
    assert result is not None
    assert result["run_id"] == "good"


def test_load_latest_snapshot_legacy_flat_files(tmp_path):
    """Compatibilidad con snapshots planos del formato legado de fetcher.py."""
    base = str(tmp_path / "snapshots")
    os.makedirs(base)

    # Simular archivos legados: quality_<ts>.json directamente en base
    for name, payload in (
        ("quality_20260101T120000Z.json", {"legacy": "old"}),
        ("quality_20260510T090000Z.json", {"legacy": "newest"}),
    ):
        with open(os.path.join(base, name), "w", encoding="utf-8") as f:
            json.dump(payload, f)

    result = load_latest_snapshot(prefix="quality", base_dir=base)
    assert result is not None
    assert result["legacy"] == "newest"


# ── SNAPSHOT_DIR constant ─────────────────────────────────────


def test_snapshot_dir_constant_is_string():
    """SNAPSHOT_DIR debe ser un string no vacío."""
    assert isinstance(SNAPSHOT_DIR, str) and len(SNAPSHOT_DIR) > 0
