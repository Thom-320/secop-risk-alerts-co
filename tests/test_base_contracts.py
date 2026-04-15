from __future__ import annotations

import pandas as pd
import pytest

from src.transform.build_base_contracts import validate_base_contracts


def test_validate_base_contracts_accepts_unique_ids() -> None:
    df = pd.DataFrame({"id_contrato": ["A", "B"]})
    validate_base_contracts(df)


def test_validate_base_contracts_rejects_duplicates() -> None:
    df = pd.DataFrame({"id_contrato": ["A", "A"]})
    with pytest.raises(ValueError):
        validate_base_contracts(df)
