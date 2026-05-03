"""Tests for section_data.build_section_data — verifies the view model contract."""

import pandas as pd
import pytest

from section_data import SectionData, build_section_data
from config import UMBRAL_EXCELENTE, UMBRAL_GOBERNANZA


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "dataset"                    : ["ds_a", "ds_b", "ds_c", "ds_d"],
        "organizacion"               : ["OrgA", "OrgA", "OrgB", "OrgC"],
        "formato"                    : ["CSV", "JSON", "CSV", "PDF"],
        "categoria"                  : ["Salud", "Salud", "Educación", "Educación"],
        "filas"                      : [100, 200, 50, 300],
        "score_global"               : [95.0, 75.0, 55.0, 80.0],
        "modificado"                 : ["2026-04-01", "2026-03-01", "2026-02-01", "2026-01-01"],
        "comp_completitud_global_pct": [90.0, 80.0, 70.0, 85.0],
    })


def test_returns_section_data_instance(sample_df):
    result = build_section_data(sample_df)
    assert isinstance(result, SectionData)


def test_scalar_counts(sample_df):
    data = build_section_data(sample_df)
    assert data.n_datasets == 4
    assert data.n_orgs == 3        # OrgA, OrgB, OrgC
    assert data.n_formats == 3     # CSV, JSON, PDF
    assert data.total_rows == 650  # 100+200+50+300


def test_score_scalars(sample_df):
    data = build_section_data(sample_df)
    assert abs(data.mean_score - 76.25) < 0.01   # (95+75+55+80)/4
    assert data.n_excellent == int((sample_df["score_global"] >= UMBRAL_EXCELENTE).sum())
    assert data.n_critical  == int((sample_df["score_global"] <  UMBRAL_GOBERNANZA).sum())
    assert data.n_good      == int(
        ((sample_df["score_global"] >= UMBRAL_GOBERNANZA) &
         (sample_df["score_global"] <  UMBRAL_EXCELENTE)).sum()
    )


def test_n_critical_plus_good_plus_excellent_equals_n_datasets(sample_df):
    data = build_section_data(sample_df)
    assert data.n_critical + data.n_good + data.n_excellent == data.n_datasets


def test_dim_means_populated(sample_df):
    data = build_section_data(sample_df)
    assert "Completitud" in data.dim_means
    assert abs(data.dim_means["Completitud"] - sample_df["comp_completitud_global_pct"].mean()) < 0.01


def test_org_stats_matches_agg_org_stats(sample_df):
    from data_layer import agg_org_stats
    data = build_section_data(sample_df)
    expected = agg_org_stats(sample_df)
    assert list(data.org_stats.columns) == list(expected.columns)
    assert len(data.org_stats) == len(expected)


def test_dim_means_by_cat_not_empty(sample_df):
    data = build_section_data(sample_df)
    assert not data.dim_means_by_cat.empty


def test_recent_datasets_top6(sample_df):
    data = build_section_data(sample_df)
    assert len(data.recent_datasets) <= 6
    assert "title" in data.recent_datasets.columns
    assert "metadata_modified" in data.recent_datasets.columns


def test_empty_dataframe_returns_zero_scalars():
    data = build_section_data(pd.DataFrame())
    assert data.n_datasets  == 0
    assert data.mean_score  == 0.0
    assert data.n_critical  == 0
    assert data.n_excellent == 0
    assert data.n_good      == 0
    assert data.total_rows  == 0
    assert data.dim_means   == {}
    assert data.org_stats.empty
    assert data.dim_means_by_cat.empty
