"""Tests for the alternative-part matching engine against the synthetic dataset.

Pure pandas logic -- no external services, safe to run in CI.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "task-3"))

from utils.find_alternative_parts_balanced import find_alternative_parts_balanced  # noqa: E402

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "Partscleaned.csv"

REQUIRED_COLUMNS = {
    "ID",
    "DESCRIPTION",
    "Attribut1",
    "Rated Current (A)",
    "Rated Voltage (V)",
    "Rated Voltage (VDC)",
    "Rated Breaking Capacity (A)",
    "Mounting",
    "Application",
}


@pytest.fixture(scope="module")
def df():
    data = pd.read_csv(DATA_PATH)
    data.columns = data.columns.str.strip()
    return data


def test_dataset_has_required_columns(df):
    assert REQUIRED_COLUMNS.issubset(set(df.columns))


def test_dataset_ids_are_unique(df):
    assert df["ID"].is_unique


def test_dataset_is_reasonably_sized(df):
    assert len(df) >= 1000


@pytest.mark.parametrize("tier", ["Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5"])
def test_every_tier_runs_without_error(df, tier):
    selected = df.iloc[0]
    alternatives = find_alternative_parts_balanced(selected, df.copy(), relaxation_tier=tier)
    assert isinstance(alternatives, pd.DataFrame)


def test_alternatives_never_include_the_selected_part_itself(df):
    selected = df.iloc[0]
    alternatives = find_alternative_parts_balanced(selected, df.copy(), relaxation_tier="Tier 5")
    assert selected["ID"] not in alternatives["ID"].values


def test_relaxation_tiers_find_at_least_as_many_as_the_previous_tier(df):
    """Each tier should be at least as permissive as the one before it."""
    selected = df.iloc[0]
    counts = [
        len(find_alternative_parts_balanced(selected, df.copy(), relaxation_tier=t))
        for t in ["Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5"]
    ]
    assert counts == sorted(counts)


def test_tier_5_can_return_a_different_fuse_type(df):
    """Regression test for the bug where Tier 5 never actually relaxed fuse type."""
    selected = df.iloc[0]
    alternatives = find_alternative_parts_balanced(selected, df.copy(), relaxation_tier="Tier 5")
    fuse_types = set(df.loc[df["ID"].isin(alternatives["ID"]), "Attribut1"])
    assert fuse_types - {selected["Attribut1"]}, "Tier 5 should be able to return a different fuse type"
