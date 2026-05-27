from __future__ import annotations

import pandas as pd

from src.features.process_features import (
    compute_anomaly_component,
    compute_peer_deviation_component,
    compute_peer_statistics,
)


def sample_processes(rows: int = 40) -> pd.DataFrame:
    values = []
    for idx in range(rows):
        values.append(
            {
                "process_key": f"P{idx}",
                "entity_name": "Entidad A" if idx < rows / 2 else "Entidad B",
                "department": "Meta" if idx % 2 == 0 else "Casanare",
                "process_year": 2025,
                "modality_family": "contratacion_directa",
                "category_code": "80111600",
                "base_price": 1_000_000 + idx * 10_000,
                "awarded_total": 900_000 + idx * 10_000,
                "duration_days": 30 + idx,
                "response_count": 1 if idx < rows - 1 else 0,
                "invited_suppliers": 3,
                "unique_suppliers": 1,
                "adjudicado_flag": True,
                "rpmr_linked": idx % 3 == 0,
            }
        )
    values[-1]["base_price"] = 50_000_000
    values[-1]["duration_days"] = 365
    return pd.DataFrame(values)


def test_peer_statistics_build_expected_columns() -> None:
    frame = compute_peer_statistics(sample_processes())
    assert {"peer_group_key", "peer_group_size", "peer_price_median"}.issubset(frame.columns)


def test_peer_deviation_component_stays_bounded() -> None:
    frame = compute_peer_deviation_component(sample_processes())
    assert frame["peer_deviation_score"].between(0, 100).all()


def test_anomaly_component_stays_bounded() -> None:
    scores = compute_anomaly_component(sample_processes())
    assert scores.between(0, 100).all()
