"""Tests for pipeline/refresh_engine.py — isolated stage testing.

Covers:
  - run_discovery: catalogue fetching, limit enforcement, error propagation.
  - run_evaluation: score mapping, failure tolerance, schema correctness.
"""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from pipeline.refresh_engine import (
    DiscoveryError,
    ExtractionResult,
    PipelineConfig,
    _map_scores,
    run_discovery,
    run_evaluation,
)


# ── Fixtures ──────────────────────────────────────────────────

@pytest.fixture()
def default_config() -> PipelineConfig:
    return PipelineConfig(force=True)


@pytest.fixture()
def sample_meta() -> dict:
    return {
        "slug"           : "test-dataset",
        "dataset"        : "Test Dataset",
        "descripcion"    : "Desc de prueba",
        "categoria"      : "Educacion",
        "organizacion"   : "SEP NL",
        "formato"        : "CSV",
        "url"            : "https://example.com/data.csv",
        "recurso_id"     : "abc123456789",
        "modificado"     : "2025-01-01",
        "frecuencia_update": "Mensual",
    }


@pytest.fixture()
def sample_df() -> pd.DataFrame:
    return pd.DataFrame({
        "id"        : [1, 2, 3],
        "nombre"    : ["Alice", "Bob", None],
        "municipio" : ["Monterrey", "Guadalupe", "Apodaca"],
    })


@pytest.fixture()
def sample_scores() -> dict:
    return {
        "comp_completitud_global_pct" : 85.0,
        "acc_score_accuracy_pct"      : 90.0,
        "cons_score_consistency_pct"  : 75.0,
        "uniq_score_uniqueness_pct"   : 95.0,
        "time_score_timeliness_pct"   : 70.0,
        "doc_score_documentation_pct" : 60.0,
        "open_score_openness_pct"     : 80.0,
        "score_global"                : 79.5,
    }


# ── run_discovery tests ───────────────────────────────────────

class TestRunDiscovery:
    """Unit tests for Stage 1: Discovery."""

    def test_returns_full_catalog(self, default_config: PipelineConfig) -> None:
        """run_discovery returns all resources when limit=0."""
        fake_catalog = [{"slug": f"ds-{i}", "url": f"http://x/{i}"} for i in range(5)]
        with patch("pipeline.refresh_engine.data_layer") as mock_dl:
            mock_dl.fetch_portal_catalog.return_value = fake_catalog
            result = run_discovery(default_config)

        assert result == fake_catalog
        assert len(result) == 5

    def test_limit_enforced(self) -> None:
        """run_discovery truncates catalog when config.limit > 0."""
        fake_catalog = [{"slug": f"ds-{i}"} for i in range(10)]
        config = PipelineConfig(force=True, limit=3)
        with patch("pipeline.refresh_engine.data_layer") as mock_dl:
            mock_dl.fetch_portal_catalog.return_value = fake_catalog
            result = run_discovery(config)

        assert len(result) == 3
        assert result[0]["slug"] == "ds-0"
        assert result[2]["slug"] == "ds-2"

    def test_raises_discovery_error_on_fetch_failure(
        self, default_config: PipelineConfig
    ) -> None:
        """run_discovery raises DiscoveryError (CRITICAL) when CKAN fetch fails."""
        with patch("pipeline.refresh_engine.data_layer") as mock_dl:
            mock_dl.fetch_portal_catalog.side_effect = RuntimeError("CKAN down")
            with pytest.raises(DiscoveryError, match="CKAN down"):
                run_discovery(default_config)

    def test_limit_zero_returns_all(self, default_config: PipelineConfig) -> None:
        """limit=0 means no truncation — all catalog resources are returned."""
        fake_catalog = [{"slug": f"ds-{i}"} for i in range(50)]
        with patch("pipeline.refresh_engine.data_layer") as mock_dl:
            mock_dl.fetch_portal_catalog.return_value = fake_catalog
            result = run_discovery(default_config)

        assert len(result) == 50

    def test_empty_catalog(self, default_config: PipelineConfig) -> None:
        """run_discovery handles an empty catalog gracefully."""
        with patch("pipeline.refresh_engine.data_layer") as mock_dl:
            mock_dl.fetch_portal_catalog.return_value = []
            result = run_discovery(default_config)

        assert result == []


# ── run_evaluation tests ──────────────────────────────────────

class TestRunEvaluation:
    """Unit tests for Stage 3: Evaluation."""

    def test_successful_evaluation_maps_scores(
        self,
        default_config: PipelineConfig,
        sample_meta: dict,
        sample_df: pd.DataFrame,
        sample_scores: dict,
    ) -> None:
        """run_evaluation correctly maps scores into the output schema."""
        extractions = [
            ExtractionResult(slug="test-dataset", meta=sample_meta, df=sample_df)
        ]
        with patch("pipeline.refresh_engine.data_layer") as mock_dl:
            mock_dl.compute_quality_scores.return_value = sample_scores
            evaluated, failed = run_evaluation(extractions, default_config)

        assert len(evaluated) == 1
        assert len(failed) == 0

        ev = evaluated[0]
        assert ev.slug == "test-dataset"
        assert ev.score_global == pytest.approx(79.5)
        assert ev.record["scores"]["completeness"] == pytest.approx(85.0)
        assert ev.record["scores"]["accuracy"] == pytest.approx(90.0)
        assert ev.record["filas"] == 3
        assert ev.record["columnas"] == 3

    def test_failed_extraction_goes_to_failed_list(
        self,
        default_config: PipelineConfig,
        sample_meta: dict,
    ) -> None:
        """Extractions with df=None are added to the failed list, not evaluated."""
        extractions = [
            ExtractionResult(
                slug="broken-dataset",
                meta=sample_meta,
                df=None,
                error="Download failed",
            )
        ]
        evaluated, failed = run_evaluation(extractions, default_config)

        assert len(evaluated) == 0
        assert len(failed) == 1
        assert failed[0]["slug"] == "broken-dataset"
        assert "Download failed" in failed[0]["reason"]

    def test_evaluation_exception_is_tolerated(
        self,
        default_config: PipelineConfig,
        sample_meta: dict,
        sample_df: pd.DataFrame,
    ) -> None:
        """An exception in compute_quality_scores adds to failed without crashing."""
        extractions = [
            ExtractionResult(slug="bad-eval", meta=sample_meta, df=sample_df)
        ]
        with patch("pipeline.refresh_engine.data_layer") as mock_dl:
            mock_dl.compute_quality_scores.side_effect = ValueError("Scoring bug")
            evaluated, failed = run_evaluation(extractions, default_config)

        assert len(evaluated) == 0
        assert len(failed) == 1
        assert "Scoring bug" in failed[0]["reason"]

    def test_mixed_batch(
        self,
        default_config: PipelineConfig,
        sample_meta: dict,
        sample_df: pd.DataFrame,
        sample_scores: dict,
    ) -> None:
        """A batch with both good and failed extractions is handled correctly."""
        ok_meta   = {**sample_meta, "slug": "good-ds"}
        fail_meta = {**sample_meta, "slug": "fail-ds"}
        extractions = [
            ExtractionResult(slug="good-ds", meta=ok_meta, df=sample_df),
            ExtractionResult(slug="fail-ds", meta=fail_meta, df=None, error="No URL"),
        ]
        with patch("pipeline.refresh_engine.data_layer") as mock_dl:
            mock_dl.compute_quality_scores.return_value = sample_scores
            evaluated, failed = run_evaluation(extractions, default_config)

        assert len(evaluated) == 1
        assert len(failed) == 1
        assert evaluated[0].slug == "good-ds"
        assert failed[0]["slug"] == "fail-ds"

    def test_timeliness_none_is_preserved(
        self,
        default_config: PipelineConfig,
        sample_meta: dict,
        sample_df: pd.DataFrame,
    ) -> None:
        """timeliness=None in scores is preserved as None in the output record."""
        scores_no_time = {
            "comp_completitud_global_pct" : 80.0,
            "acc_score_accuracy_pct"      : 90.0,
            "cons_score_consistency_pct"  : 70.0,
            "uniq_score_uniqueness_pct"   : 85.0,
            "time_score_timeliness_pct"   : None,
            "doc_score_documentation_pct" : 65.0,
            "open_score_openness_pct"     : 75.0,
            "score_global"                : 77.5,
        }
        extractions = [
            ExtractionResult(slug="no-time-ds", meta=sample_meta, df=sample_df)
        ]
        with patch("pipeline.refresh_engine.data_layer") as mock_dl:
            mock_dl.compute_quality_scores.return_value = scores_no_time
            evaluated, failed = run_evaluation(extractions, default_config)

        assert len(evaluated) == 1
        assert evaluated[0].record["scores"]["timeliness"] is None


# ── PipelineConfig tests ──────────────────────────────────────

class TestPipelineConfig:
    """Validates PipelineConfig defaults and immutability."""

    def test_defaults(self) -> None:
        cfg = PipelineConfig()
        assert cfg.force is False
        assert cfg.limit == 0
        assert cfg.snapshot_dir == ""
        assert cfg.request_delay_s == pytest.approx(1.0)
        assert cfg.coverage_warn_threshold == pytest.approx(90.0)

    def test_frozen(self) -> None:
        """PipelineConfig must be immutable."""
        cfg = PipelineConfig(force=True)
        with pytest.raises((AttributeError, TypeError)):
            cfg.force = False  # type: ignore[misc]

    def test_custom_values(self) -> None:
        cfg = PipelineConfig(force=True, limit=10, snapshot_dir="/tmp/snap")
        assert cfg.force is True
        assert cfg.limit == 10
        assert cfg.snapshot_dir == "/tmp/snap"
