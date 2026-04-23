"""
pipeline/test_data_layer.py
Pruebas unitarias para validar los algoritmos de dimensiones de calidad (ISO 25012:2008). 
Verificación de edge cases, data frames vacíos y vectorización.
"""

import pytest
import pandas as pd
import numpy as np

# Se asume que sys.path ya incluye la raíz en un entorno real de pytest.
from data_layer import (
    compute_completeness,
    compute_accuracy,
    compute_consistency,
    compute_uniqueness,
    is_safe_url,
    load_coverage_report,
    get_resource_vs_unique_count,
)

def test_is_safe_url():
    """Valida la integridad de la protección SSRF."""
    assert is_safe_url("https://catalogodatos.nl.gob.mx/api") is True
    assert is_safe_url("http://datos.nl.gob.mx/resource") is True
    # Dominios maliciosos (subdomain spoofing o sufijo ciego)
    assert is_safe_url("https://malicious-catalogodatos.nl.gob.mx/api") is False
    assert is_safe_url("https://datos.nl.gob.mx.malicious.com") is False
    assert is_safe_url("ftp://datos.nl.gob.mx") is False

def test_compute_completeness():
    """Valida el cálculo de completitud con nulos."""
    # 2 rows, 2 cols (4 cells). 1 null => 3/4 = 75%
    df = pd.DataFrame({
        "A": [1, np.nan],
        "B": ["text", "text2"]
    })
    res = compute_completeness(df)
    assert res["comp_completitud_global_pct"] == 75.0
    assert res["comp_filas_incompletas_pct"] == 50.0  # 1 de 2 filas es incompleta

def test_compute_completeness_empty():
    df = pd.DataFrame()
    res = compute_completeness(df)
    assert res["comp_completitud_global_pct"] == 0.0

def test_compute_accuracy():
    """Valida detecciones de exactitud (espacios, constantes y tipos mixtos)."""
    # Constante: B
    # Espacios: A (fila 0)
    # Mixto: Num y str, pero pd.to_numeric coerce
    df = pd.DataFrame({
        "A": [" texto ", "limpio", "limpio"],
        "B": [5, 5, 5],
        "C": [1, "no-numeric", 3]
    })
    res = compute_accuracy(df)
    assert res["acc_columnas_constantes"] == 1
    assert res["acc_columnas_espacios"] == 1
    # Mixed is evaluated where numeric percent is > 0.05 and < 0.95
    # C has 2 numerics, 1 string. num_pct = 2/3 = 0.66 => mixed
    assert res["acc_columnas_tipo_mixto"] == 1

def test_compute_consistency():
    """Valida IQR > 0 para series numéricas (>= 30 elementos) e inconsistencias en texto."""
    # Para forzar IQR, creamos serie N > 30
    normal_data = list(range(10, 40))  # 30 elements
    normal_data.extend([1000, -1000])  # 2 clear outliers
    
    # Texto con diferencias de capitalización (inconsistencias)
    text_data = ["Monterrey", "monterrey", "MONTERREY"] * 10
    text_data.extend(["San Pedro", " san pedro "])
    
    df = pd.DataFrame({
        "numeros": normal_data,
        "texto": text_data
    })
    
    res = compute_consistency(df)
    assert res["cons_columnas_numericas"] == 1
    # Deberíamos encontrar 2 outliers (1000 y -1000) de 32 elementos -> p_out = 2 / 32 = 6.25%
    assert res["cons_pct_outliers"] > 0
    # Monterrey (3 únicas, 1 limpia) -> diff de 2
    # San pedro (2 únicas, 1 limpia) -> diff de 1
    # Total inconsistencias texto aportadas = 3
    assert res["cons_inconsistencias_texto"] == 3

def test_compute_consistency_small_dataset():
    """Valida que no calcula IQR para muestras N < 30."""
    df = pd.DataFrame({"numeros": [1, 2, 3, 100]})
    res = compute_consistency(df)
    assert res["cons_pct_outliers"] == 0

def test_compute_uniqueness():
    """Valida el cálculo de filas duplicadas exactas."""
    df = pd.DataFrame({
        "ID": [1, 2, 2, 4],
        "val": ["A", "B", "B", "D"]
    })
    res = compute_uniqueness(df)
    assert res["uniq_pct_duplicados"] == 25.0  # 1 duplicate in 4 rows


def test_load_coverage_report_returns_dict(tmp_path, monkeypatch):
    """Valida que load_coverage_report lee un snapshot valido."""
    import json

    run_dir = tmp_path / "snapshots" / "run_20260418_144034"
    run_dir.mkdir(parents=True)

    report = {
        "run_id": "20260418_144034",
        "total_catalogo": 282,
        "procesados_exitosos": 277,
        "fallidos": 5,
        "cobertura_pct": 98.2,
        "elapsed_total_s": 917.39,
        "avg_time_per_dataset_s": 3.31,
        "failed_details": [],
    }
    (run_dir / "coverage_report.json").write_text(
        json.dumps(report), encoding="utf-8",
    )

    monkeypatch.setattr("os.getcwd", lambda: str(tmp_path))
    result = load_coverage_report()
    assert result is not None
    assert result["total_catalogo"] == 282
    assert result["procesados_exitosos"] == 277
    assert result["cobertura_pct"] == 98.2


def test_load_coverage_report_missing_returns_none(tmp_path, monkeypatch):
    """Valida fallback graceful cuando no existen snapshots."""
    monkeypatch.setattr("os.getcwd", lambda: str(tmp_path))
    result = load_coverage_report()
    assert result is None


def test_get_resource_vs_unique_count():
    """Valida conteo de recursos vs datasets unicos."""
    result = get_resource_vs_unique_count()
    assert "resources_evaluated" in result
    assert "unique_datasets" in result
    assert result["resources_evaluated"] >= result["unique_datasets"]
