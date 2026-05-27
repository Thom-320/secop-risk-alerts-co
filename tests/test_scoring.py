from __future__ import annotations

import pandas as pd

from src.features.process_features import confidence_band, priority_band, rule_score_from_row
from src.utils.reporting import build_process_report_html


def test_rule_score_respects_paa_modes() -> None:
    row = pd.Series(
        {
            "value_deviation_ratio": 2.7,
            "duration_deviation_ratio": 1.9,
            "response_gap": 3,
            "paa_match_status": "none",
        }
    )
    full = rule_score_from_row(row, "full")
    secondary = rule_score_from_row(row, "secondary")
    visible_only = rule_score_from_row(row, "visible_only")
    assert full >= secondary >= visible_only


def test_priority_and_confidence_bands() -> None:
    assert priority_band(90) == "alerta prioritaria"
    assert priority_band(50) == "observacion"
    assert confidence_band(80) == "alta"
    assert confidence_band(40) == "baja"


def test_html_report_contains_process_and_disclaimer() -> None:
    html = build_process_report_html(
        {
            "process_key": "P1",
            "process_reference": "REF-001",
            "entity_name": "Entidad Demo",
            "priority_score": 82,
            "confidence_score": 71,
            "reasons": "monto atipico frente a pares",
            "base_price": 1500000,
            "paa_match_status": "strong",
        },
        [
            {
                "comparable_label": "REF-002 | Entidad Demo",
                "comparable_value": 1200000,
                "similarity": 0.81,
            }
        ],
    )
    assert "REF-001" in html
    assert "prioriza revision humana" in html.lower()
