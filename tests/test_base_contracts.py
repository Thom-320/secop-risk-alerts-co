from __future__ import annotations

import pandas as pd
import pytest

from src.transform.build_process_master import validate_process_master


def test_validate_process_master_accepts_unique_keys() -> None:
    df = pd.DataFrame({"process_key": ["P1", "P2"]})
    validate_process_master(df)


def test_validate_process_master_rejects_duplicates() -> None:
    df = pd.DataFrame({"process_key": ["P1", "P1"]})
    with pytest.raises(ValueError):
        validate_process_master(df)
