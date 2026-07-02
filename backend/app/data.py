"""Shared paths and the parts dataset loader.

REPO_ROOT is computed from this file's own location rather than assumed from
the process's current working directory, so the backend works the same
whether it's launched from the repo root or from backend/.
"""

from functools import lru_cache
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
PARTS_CSV = REPO_ROOT / "data" / "Partscleaned.csv"


@lru_cache
def load_parts_df() -> pd.DataFrame:
    df = pd.read_csv(PARTS_CSV)
    df.columns = df.columns.str.strip()
    return df
