from __future__ import annotations

import pandas as pd
from fastapi.testclient import TestClient

import src.api.main as api_main
from src.api.main import app


def test_parquet_api_health() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def _empty_assets() -> dict[str, pd.DataFrame]:
    return {
        "overview": pd.DataFrame(),
        "ranking": pd.DataFrame(),
        "process_detail": pd.DataFrame({"process_key": []}),
        "comparables": pd.DataFrame({"process_key": [], "rank": []}),
    }


def test_parquet_api_missing_process_returns_404(monkeypatch) -> None:
    monkeypatch.setattr(api_main, "load_assets", _empty_assets)
    response = TestClient(app).get("/process/no-existe")
    assert response.status_code == 404


def test_parquet_api_review_missing_process_returns_404(monkeypatch) -> None:
    monkeypatch.setattr(api_main, "load_assets", _empty_assets)
    response = TestClient(app).post(
        "/reviews",
        json={"process_key": "no-existe", "notes": "revision demo"},
    )
    assert response.status_code == 404
