from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

from src.api.main import app
from src.features.process_features import (
    compute_confidence_score,
    rule_score_from_row,
    stable_missing_identifier,
)

ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# 1. stable_missing_identifier — moved from etl.common to src.features
# ---------------------------------------------------------------------------

def test_stable_missing_identifier() -> None:
    first = stable_missing_identifier("sin-nit", "Proveedor Demo Uno")
    second = stable_missing_identifier("sin-nit", "Proveedor Demo Uno")
    assert first == second
    assert first.startswith("sin-nit-")
    assert "Proveedor" not in first


# ---------------------------------------------------------------------------
# 2. Scoring is not a placeholder — uses rule_score_from_row
# ---------------------------------------------------------------------------

def test_scoring_is_not_placeholder() -> None:
    row = pd.Series(
        {
            "value_deviation_ratio": 2.5,
            "duration_deviation_ratio": 1.8,
            "response_gap": 3,
            "paa_match_status": "none",
        }
    )
    score = rule_score_from_row(row, paa_signal_mode="full")
    assert score > 0
    assert score <= 100.0
    # Specific structural check: the value-deviation ≥ 2.5 bonus is 35
    # plus duration ≥ 1.8 bonus of 15 plus response_gap ≥ 3 bonus of 20
    # plus paa_match_status="none" in full mode bonus of 20 = 90
    assert score == 90.0


# ---------------------------------------------------------------------------
# 3. Confidence score formula — base 45 + conditional bonuses
# ---------------------------------------------------------------------------

def test_confidence_score_formula() -> None:
    df = pd.DataFrame(
        {
            "text_sufficient": [True, False, True],
            "peer_group_size": [10, 3, 8],
            "semantic_comparable_count": [5, 1, 3],
            "rpmr_linked": [True, False, False],
            "paa_match_confidence": [0.8, 0.2, 0.5],
        }
    )
    scores = compute_confidence_score(df)

    # Row 0: 45 + 15(text) + 15(peer≥8) + 10(semantic≥3) + 5(rpmr) + 8(paa) = 98
    assert scores.iloc[0] == 98.0

    # Row 1: 45 + 0 + 0 + 0 + 0 + 2(paa*10) = 47
    assert scores.iloc[1] == 47.0

    # Row 2: 45 + 15(text) + 15(peer≥8) + 10(semantic≥3) + 0 + 5(paa*10) = 90
    assert scores.iloc[2] == 90.0


# ---------------------------------------------------------------------------
# 4. Slide scripts are portable (no /Users/thom hardcoded)
# ---------------------------------------------------------------------------

def test_slide_scripts_are_portable() -> None:
    for relative in [
        "slides/html/contratia_abierta.html",
        "slides/html/deck-stage.js",
        "slides/README.md",
        "presentation/README.md",
    ]:
        content = (ROOT / relative).read_text()
        assert "/Users/thom" not in content


# ---------------------------------------------------------------------------
# 5. Public scripts do not pin local user path
# ---------------------------------------------------------------------------

def test_public_scripts_do_not_pin_local_user_path() -> None:
    for relative in ["scripts/launch_overnight_agents.sh"]:
        content = (ROOT / relative).read_text()
        assert "/Users/thom" not in content


# ---------------------------------------------------------------------------
# 6. Gitignored generated files are not tracked
# ---------------------------------------------------------------------------

def test_ignored_generated_files_are_not_tracked() -> None:
    result = subprocess.run(
        ["git", "ls-files", "-ci", "--exclude-standard"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert result.stdout.strip() == ""


# ---------------------------------------------------------------------------
# 7. NEW: API health endpoint returns 200
# ---------------------------------------------------------------------------

def test_api_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body.get("status") == "ok"


# ---------------------------------------------------------------------------
# 8. NEW: No absolute local paths in src/
# ---------------------------------------------------------------------------

def test_no_absolute_paths_in_src() -> None:
    result = subprocess.run(
        ["git", "grep", "-rn", "/Users/thom", "src/"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert result.stdout.strip() == "", (
        "Hardcoded /Users/thom found in src/:\n" + result.stdout
    )


# ---------------------------------------------------------------------------
# Legacy tests (source validation / download order) still check etl/ source
# ---------------------------------------------------------------------------

def test_source_validation_fails_below_demo_volume() -> None:
    validator = (ROOT / "etl" / "validate_sources.py").read_text()
    assert "meets_10000_process_requirement" in validator
    assert "raise SystemExit" in validator


def test_download_mode_is_checked_before_tiny_sample_fixtures() -> None:
    common = (ROOT / "etl" / "common.py").read_text()
    assert common.index("_download_demo_sources_if_requested(limit)") < common.index(
        "readers = (_read_generated_sources, _read_sample_sources)"
    )
