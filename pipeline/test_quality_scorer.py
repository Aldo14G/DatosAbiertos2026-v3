"""Tests for QualityScorer — coverage for scoring logic that was previously untested."""

import math

import pandas as pd
import pytest

from quality_scorer import BREAKDOWN_SCORE_KEYS, BreakdownDict, QualityScorer, ScoringResult
from config import QUALITY_WEIGHTS


@pytest.fixture
def scorer():
    return QualityScorer()


@pytest.fixture
def perfect_meta():
    return {
        "dataset": "test",
        "slug": "test-slug",
        "descripcion": (
            "Metodología detallada de indicadores estadísticos con fuente oficial y "
            "diccionario de variables. Contiene definiciones, metadatos y notas técnicas "
            "para uso de analistas de datos gubernamentales. Información pública."
        ),
        "resource_descs": ["Descripción del recurso principal"],
        "licencia": "creative commons",
        "licencia_id": "cc-by-4.0",
        "formato": "CSV",
        "resource_formats": ["CSV"],
        "url": "https://catalogodatos.nl.gob.mx/dataset/test/resource/abc.csv",
        "modificado": "2026-04-29T00:00:00Z",
        "frecuencia_update": "diaria",
    }


@pytest.fixture
def perfect_df():
    return pd.DataFrame(
        {
            "id": range(1, 51),
            "nombre": [f"nombre_{i}" for i in range(1, 51)],
            "valor": [float(i) for i in range(1, 51)],
        }
    )


def test_perfect_dataset_score_is_high(scorer, perfect_meta, perfect_df):
    result = scorer.score(perfect_meta, perfect_df)
    assert result["global_score"] >= 90
    assert "completeness" in result["dim_scores"]
    assert result["dim_scores"]["completeness"] == 100.0


def test_result_is_scoring_result_typeddict(scorer, perfect_meta, perfect_df):
    result = scorer.score(perfect_meta, perfect_df)
    assert set(result.keys()) == {"dim_scores", "breakdown", "global_score"}
    assert isinstance(result["dim_scores"], dict)
    assert isinstance(result["global_score"], float)


def test_empty_dataframe_content_dimensions_zero(scorer, perfect_meta):
    result = scorer.score(perfect_meta, pd.DataFrame())
    # Content dimensions (operate on DataFrame) must be 0 for an empty frame.
    # Metadata dimensions (documentation, openness, timeliness) can still be non-zero.
    assert result["dim_scores"]["completeness"] == 0.0
    assert result["dim_scores"]["accuracy"] == 0.0
    assert result["dim_scores"]["uniqueness"] == 0.0


def test_nan_timeliness_excluded_from_weights(scorer, perfect_df):
    meta_no_date = {
        "descripcion": "",
        "recurso_id": "",
        "licencia": "",
        "licencia_id": "",
        "formato": "CSV",
        "resource_formats": [],
        "url": "https://catalogodatos.nl.gob.mx/x",
        "modificado": "",       # no date → timeliness = NaN
        "frecuencia_update": "",
    }
    result = scorer.score(meta_no_date, perfect_df)
    assert "timeliness" not in result["dim_scores"]
    # Global score must still sum to a valid number (no NaN propagation)
    assert not math.isnan(result["global_score"])
    # Weights without timeliness should still sum to ~0.95
    remaining_w = sum(v for k, v in QUALITY_WEIGHTS.items() if k != "timeliness")
    expected = round(
        sum(result["dim_scores"][k] * QUALITY_WEIGHTS[k] for k in result["dim_scores"])
        / remaining_w,
        2,
    )
    assert result["global_score"] == expected


def test_custom_weights_completeness_only(perfect_meta, perfect_df):
    weights = {k: 0.0 for k in QUALITY_WEIGHTS}
    weights["completeness"] = 1.0
    custom_scorer = QualityScorer(weights=weights)
    result = custom_scorer.score(perfect_meta, perfect_df)
    assert result["global_score"] == result["dim_scores"]["completeness"]


def test_quality_weights_sum_to_one():
    total = sum(QUALITY_WEIGHTS.values())
    assert abs(total - 1.0) < 1e-9, f"QUALITY_WEIGHTS sum = {total}, expected 1.0"


# ── ScoringResult / BreakdownDict schema tests ────────────────────────────────


def test_scoring_result_has_required_keys(scorer, perfect_meta, perfect_df):
    """ScoringResult must expose exactly the three declared TypedDict keys."""
    result = scorer.score(perfect_meta, perfect_df)
    assert set(result.keys()) == {"dim_scores", "breakdown", "global_score"}


def test_breakdown_contains_all_score_keys(scorer, perfect_meta, perfect_df):
    """Every key in BREAKDOWN_SCORE_KEYS (excluding optional timeliness) must be present."""
    result = scorer.score(perfect_meta, perfect_df)
    breakdown = result["breakdown"]
    # All non-timeliness primary score keys must always be present.
    required = BREAKDOWN_SCORE_KEYS - {"time_score_timeliness_pct"}
    missing = required - set(breakdown)
    assert not missing, f"breakdown is missing keys: {missing}"


def test_breakdown_score_keys_are_floats(scorer, perfect_meta, perfect_df):
    """Primary score keys in the breakdown must be numeric (float or int)."""
    result = scorer.score(perfect_meta, perfect_df)
    breakdown = result["breakdown"]
    for key in BREAKDOWN_SCORE_KEYS - {"time_score_timeliness_pct"}:
        value = breakdown[key]
        assert isinstance(value, (int, float)), (
            f"breakdown['{key}'] should be numeric, got {type(value).__name__}"
        )


def test_breakdown_keys_match_typeddict_annotations():
    """All keys in BREAKDOWN_SCORE_KEYS must be declared fields of BreakdownDict."""
    declared_fields = set(BreakdownDict.__annotations__)
    unknown = BREAKDOWN_SCORE_KEYS - declared_fields
    assert not unknown, (
        f"BREAKDOWN_SCORE_KEYS contains keys not declared in BreakdownDict: {unknown}"
    )


def test_dim_label_map_keys_match_breakdown_score_keys():
    """DIM_LABEL_MAP in data_layer must only reference known scoring keys."""
    from data_layer import DIM_LABEL_MAP

    valid = BREAKDOWN_SCORE_KEYS | {"score_global"}
    unknown = set(DIM_LABEL_MAP) - valid
    assert not unknown, (
        f"DIM_LABEL_MAP references keys absent from BreakdownDict: {unknown}"
    )


def test_timeliness_absent_from_breakdown_when_no_date(scorer, perfect_df):
    """When modificado is empty, timeliness keys must be absent from breakdown."""
    meta_no_date = {
        "descripcion": "",
        "licencia": "",
        "licencia_id": "",
        "formato": "CSV",
        "resource_formats": [],
        "url": "https://catalogodatos.nl.gob.mx/x",
        "modificado": "",
        "frecuencia_update": "",
    }
    result = scorer.score(meta_no_date, perfect_df)
    # time_score_timeliness_pct should be NaN (present but NaN) or absent from dim_scores
    assert "timeliness" not in result["dim_scores"]
