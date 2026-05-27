from __future__ import annotations

import pandas as pd
from fastapi.testclient import TestClient

import services.contracts_service.main as contracts_main
import services.risk_service.main as risk_main
from services.analytics_service.main import app as analytics_app
from services.contracts_service.main import app as contracts_app
from services.risk_service.main import app as risk_app
from services.risk_service.schemas import RiskRankingRow


def test_contracts_health() -> None:
    response = TestClient(contracts_app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_risk_health() -> None:
    response = TestClient(risk_app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analytics_health() -> None:
    response = TestClient(analytics_app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_dashboard_imports() -> None:
    import dashboard.dash_app as dash_app

    assert hasattr(dash_app, "create_app")
    assert "prioriza revision humana" in dash_app.ETHICS_DISCLAIMER.lower()


def test_dashboard_export_helpers_reuse_reporting(monkeypatch) -> None:
    import dashboard.dash_app as dash_app

    ranking = pd.DataFrame(
        [
            {
                "process_id": 1,
                "process_key": "PROC-1",
                "process_reference": "REF-1",
                "entity_name": "Entidad Demo",
                "department": "Meta",
                "modality": "Licitacion publica",
                "base_price": 1000000.0,
                "priority_score": 72.0,
                "confidence_score": 80.0,
                "explanation": "Priorizacion de revision humana.",
            },
            {
                "process_id": 2,
                "process_key": "PROC-2",
                "process_reference": "REF-2",
                "entity_name": "Entidad Baja",
                "department": "Caldas",
                "modality": "Minima cuantia",
                "base_price": 200000.0,
                "priority_score": 30.0,
                "confidence_score": 55.0,
                "explanation": "Sin prioridad alta.",
            },
        ]
    )
    monkeypatch.setattr(dash_app, "load_comparables", lambda _process_id: pd.DataFrame())
    monkeypatch.setattr(dash_app, "frame_from_service", lambda *_args, **_kwargs: pd.DataFrame())

    csv_text = dash_app.ranking_csv_text(ranking, 50)
    html_text = dash_app.process_report_html(ranking, 1)

    assert "PROC-1" in csv_text
    assert "PROC-2" not in csv_text
    assert "Reporte ContratIA Abierta" in html_text
    assert "No prueba corrupcion" in html_text


def test_risk_ranking_schema_accepts_dashboard_columns() -> None:
    row = RiskRankingRow(
        process_id=1,
        process_key="PROC-1",
        process_reference="REF-1",
        entity_name="Entidad Demo",
        department="Meta",
        modality="Licitacion publica",
        base_price=1000000,
        priority_score=72,
        confidence_score=80,
        explanation="Priorizacion de revision humana.",
    )

    assert row.process_reference == "REF-1"
    assert row.department == "Meta"
    assert row.modality == "Licitacion publica"
    assert row.base_price == 1000000


def test_risk_ranking_endpoint_returns_dashboard_columns(monkeypatch) -> None:
    captured: dict[str, str] = {}

    def fake_fetch_all(sql: str, params: tuple[object, ...]) -> list[dict[str, object]]:
        captured["sql"] = sql
        assert params == (10,)
        return [
            {
                "process_id": 1,
                "process_key": "PROC-1",
                "process_reference": "REF-1",
                "entity_name": "Entidad Demo",
                "department": "Meta",
                "modality": "Licitacion publica",
                "base_price": 1000000.0,
                "priority_score": 72.0,
                "confidence_score": 80.0,
                "explanation": "Priorizacion de revision humana.",
            }
        ]

    monkeypatch.setattr(risk_main, "fetch_all", fake_fetch_all)
    response = TestClient(risk_app).get("/risk/ranking", params={"limit": 10})

    assert response.status_code == 200
    payload = response.json()[0]
    for column in [
        "process_id",
        "process_key",
        "process_reference",
        "entity_name",
        "department",
        "modality",
        "base_price",
        "priority_score",
        "confidence_score",
        "explanation",
    ]:
        assert column in payload
        assert column in captured["sql"]


def test_public_read_only_blocks_risk_recompute(monkeypatch) -> None:
    monkeypatch.setenv("PUBLIC_READ_ONLY", "true")
    response = TestClient(risk_app).post("/risk/recompute/1")

    assert response.status_code == 403


def test_public_read_only_blocks_contract_reviews(monkeypatch) -> None:
    monkeypatch.setenv("PUBLIC_READ_ONLY", "true")

    def fail_execute(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("execute should not be called in read-only mode")

    monkeypatch.setattr(contracts_main, "execute", fail_execute)
    response = TestClient(contracts_app).post(
        "/reviews",
        json={"process_id": 1, "reviewer_label": "demo"},
    )

    assert response.status_code == 403
