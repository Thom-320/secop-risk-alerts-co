from __future__ import annotations

from fastapi.testclient import TestClient

from services.analytics_service.main import app as analytics_app
from services.contracts_service.main import app as contracts_app
from services.risk_service.main import app as risk_app


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
