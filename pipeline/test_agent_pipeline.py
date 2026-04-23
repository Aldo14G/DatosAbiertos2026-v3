import pytest
import pandas as pd
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from pipeline.extractor import SkillExtractorDatasets, EstadoExtraccion, FormatoDataset, TipoPlataforma, DatasetDescubierto, RecursoDescubierto, ManifiestoExtraccion, MotorDescarga
from pipeline.evaluator import SkillEvaluadorDatos, NivelAnalisis, MetricaCalidad, CategoriaProblema, MarcoReferencia

@pytest.fixture
def sample_dataset() -> DatasetDescubierto:
    recurso = RecursoDescubierto(
        recurso_id="res_1",
        nombre="test.csv",
        url_descarga="http://test.com/test.csv",
        formato=FormatoDataset.CSV
    )
    return DatasetDescubierto(
        dataset_id="ds_1",
        nombre="test-dataset",
        titulo="Test Dataset",
        recursos=[recurso],
        url_origen="http://test.com/"
    )

@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    return pd.DataFrame({
        "id": [1, 2, 3],
        "municipio": ["Monterrey", "San Pedro", None],
        "cve_ent": ["19", "19", "19"]
    })

def test_extractor_motor_parseo_csv():
    motor = MotorDescarga(directorio_cache="./tmp_cache")
    csv_content = b"id,nombre\n1,Juan\n2,Perez"
    
    recurso = RecursoDescubierto(
        recurso_id="res_1",
        nombre="test.csv",
        url_descarga="http://dummy",
        formato=FormatoDataset.CSV
    )

    # Simular la descarga
    with patch.object(motor, '_descargar', return_value=(csv_content, {"status_code": 200})):
        resultado = motor.extraer_recurso(recurso, "ds_1")
        
        assert resultado.estado == EstadoExtraccion.EXITOSO
        assert resultado.registros_extraidos == 2
        assert resultado.columnas == ["id", "nombre"]

def test_evaluador_iso25012_completitud(sample_dataframe):
    evaluador = SkillEvaluadorDatos()
    df = sample_dataframe
    metadata = {
        "dataset_id": "ds_1",
        "recurso_id": "res_1"
    }
    
    metricas, problemas = evaluador.iso25012.analizar(df, metadata)
    
    # Debe haber una métrica de completitud
    metrica_comp = next((m for m in metricas if m.nombre == "completitud_general"), None)
    assert metrica_comp is not None
    assert metrica_comp.valor < 100.0  # Hay un None en municipio

    # Debe marcar un problema por valor faltante
    prob_comp = next((p for p in problemas if "municipio" in p.columnas_afectadas), None)
    assert prob_comp is not None

def test_evaluador_dama_interoperabilidad(sample_dataframe):
    evaluador = SkillEvaluadorDatos()
    metadata = {"dataset_id": "ds_1", "recurso_id": "res_1"}
    manifiesto = {}
    
    metricas, problemas = evaluador.dama.analizar(sample_dataframe, metadata, manifiesto)
    
    metrica_interop = next((m for m in metricas if m.nombre == "interoperabilidad"), None)
    assert metrica_interop is not None
    # Como usa "cve_ent", score debe ser alto
    assert metrica_interop.valor == 100.0
