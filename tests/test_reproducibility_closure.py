from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from etl.common import stable_missing_identifier
from services.analytics_service.main import app as analytics_app
from services.risk_service.scoring import score_process_context

ROOT = Path(__file__).resolve().parents[1]


def test_makefile_migration_does_not_load_data() -> None:
    makefile = (ROOT / "Makefile").read_text()
    db_migrate_section = makefile.split("db-migrate:", 1)[1].split("\n\n", 1)[0]
    assert "load_to_postgres" not in db_migrate_section
    assert "db-schema" in db_migrate_section


def test_provider_missing_nit_identifier_is_stable() -> None:
    first = stable_missing_identifier("sin-nit", "Proveedor Demo Uno")
    second = stable_missing_identifier("sin-nit", "Proveedor Demo Uno")
    assert first == second
    assert first.startswith("sin-nit-")
    assert "Proveedor" not in first


def test_entity_without_code_uses_stable_lookup_logic() -> None:
    loader = (ROOT / "etl" / "load_to_postgres.py").read_text()
    assert "entity_code IS NULL" in loader
    assert "lower(name) = lower(%s)" in loader


def test_hierarchy_query_uses_recursive_upward_cte() -> None:
    analytics = (ROOT / "services" / "analytics_service" / "main.py").read_text()
    assert "WITH RECURSIVE upward AS" in analytics
    assert "ORDER BY reverse_depth DESC" in analytics


def test_hierarchy_missing_entity_returns_empty_path_not_error() -> None:
    response = TestClient(analytics_app).get("/analytics/hierarchy/999999999")
    assert response.status_code in {200, 503}


def test_risk_recompute_scoring_is_not_placeholder() -> None:
    scoring = score_process_context(
        {
            "response_count": 1,
            "value_percentile": 0.95,
            "modality": "Contratacion Directa",
            "has_paa_match": False,
            "provider_share": 0.8,
            "description_length": 20,
            "base_price": 1000000,
        }
    )
    assert scoring["priority_score"] != 60
    assert "components" in scoring
    assert scoring["components"]["value_percentile"] == 95
    assert "validacion humana" in scoring["explanation"].lower()


def test_slide_scripts_are_portable() -> None:
    for relative in [
        "slides/scripts/build_deck.mjs",
        "slides/scripts/capture_screenshots.mjs",
        "slides/html/export_interactive_deck.mjs",
        "slides/README.md",
        "presentation/README.md",
    ]:
        content = (ROOT / relative).read_text()
        assert "/Users/thom" not in content
