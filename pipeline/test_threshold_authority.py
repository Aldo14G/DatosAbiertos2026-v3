"""Boundary tests for CLASIFICACION_THRESHOLDS — verifies the threshold authority contract.

Each test pins one score boundary so a future config change produces a failing test,
not a silent mis-classification in production data.
"""

import pytest

from config import CLASIFICACION_DEFAULT, CLASIFICACION_THRESHOLDS


def _classify(score: float) -> str:
    return next(
        (label for threshold, label in CLASIFICACION_THRESHOLDS if score >= threshold),
        CLASIFICACION_DEFAULT,
    )


@pytest.mark.parametrize("score,expected", [
    (90.0, "Excelente"),   # exact floor of Excelente
    (80.0, "Bueno"),       # exact floor of Bueno
    (70.0, "Aceptable"),   # exact floor of Aceptable
    (50.0, "Deficiente"),  # exact floor of Deficiente
    (49.9, "Crítico"),     # one tick below Deficiente → default
])
def test_classification_boundaries(score, expected):
    assert _classify(score) == expected


def test_thresholds_are_strictly_descending():
    values = [t for t, _ in CLASIFICACION_THRESHOLDS]
    assert values == sorted(values, reverse=True), (
        "CLASIFICACION_THRESHOLDS must be ordered highest-first for next() to work correctly"
    )


def test_default_is_critico():
    assert CLASIFICACION_DEFAULT == "Crítico"
