from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

import pandas as pd
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from src.utils.config import get_settings
from src.utils.reporting import build_process_report_html

app = FastAPI(title="ContratIA Abierta API", version="0.1.0")
REVIEWS: list[dict[str, Any]] = []


def public_read_only_enabled() -> bool:
    return os.getenv("PUBLIC_READ_ONLY", "true").lower() not in {"0", "false", "no"}


def require_demo_write_token(token: str | None) -> None:
    expected = os.getenv("DEMO_WRITE_TOKEN")
    if public_read_only_enabled():
        raise HTTPException(
            status_code=403,
            detail="PUBLIC_READ_ONLY=true bloquea endpoints mutables en demo publica.",
        )
    if expected and token != expected:
        raise HTTPException(status_code=403, detail="Token de escritura demo invalido.")


class ReviewRequest(BaseModel):
    process_key: str
    reviewer_label: str = "reviewer_demo"
    review_status: str = Field(
        default="reviewed",
        pattern="^(pending|in_review|reviewed|dismissed)$",
    )
    priority_decision: str = Field(
        default="keep_priority",
        pattern="^(keep_priority|lower_priority|raise_priority|needs_more_data)$",
    )
    notes: str = ""


@lru_cache(maxsize=1)
def load_assets() -> dict[str, pd.DataFrame]:
    settings = get_settings()
    assets = {}
    for name in ("overview", "ranking", "process_detail", "comparables"):
        path = settings.marts_dir / f"{name}.parquet"
        if not path.exists():
            raise FileNotFoundError(f"Falta artefacto requerido: {path}")
        assets[name] = pd.read_parquet(path)
    return assets


def row_to_dict(row: pd.Series) -> dict[str, Any]:
    payload = row.where(pd.notna(row), None).to_dict()
    for key, value in list(payload.items()):
        if isinstance(value, pd.Timestamp):
            payload[key] = value.isoformat()
    return payload


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/overview")
def overview() -> list[dict[str, Any]]:
    frame = load_assets()["overview"]
    return frame.fillna("").to_dict(orient="records")


@app.get("/ranking")
def ranking(
    department: str | None = None,
    entity: str | None = None,
    modality: str | None = None,
    min_score: int = Query(default=0, ge=0, le=100),
    min_confidence: int = Query(default=0, ge=0, le=100),
    limit: int = Query(default=100, ge=1, le=500),
) -> list[dict[str, Any]]:
    frame = load_assets()["ranking"].copy()
    if department:
        frame = frame[frame["department"] == department]
    if entity:
        frame = frame[frame["entity_name"] == entity]
    if modality:
        frame = frame[frame["modality"] == modality]
    frame = frame[
        frame["priority_score"].fillna(0).ge(min_score)
        & frame["confidence_score"].fillna(0).ge(min_confidence)
    ]
    return frame.head(limit).fillna("").to_dict(orient="records")


@app.get("/process/{process_key}")
def process_detail(process_key: str) -> dict[str, Any]:
    frame = load_assets()["process_detail"]
    match = frame[frame["process_key"] == process_key]
    if match.empty:
        raise HTTPException(status_code=404, detail="Proceso no encontrado")
    return row_to_dict(match.iloc[0])


@app.get("/process/{process_key}/comparables")
def process_comparables(process_key: str) -> list[dict[str, Any]]:
    frame = load_assets()["comparables"]
    match = frame[frame["process_key"] == process_key].sort_values("rank")
    return match.fillna("").to_dict(orient="records")


@app.get("/process/{process_key}/report", response_class=HTMLResponse)
def process_report(process_key: str) -> str:
    assets = load_assets()
    detail = assets["process_detail"]
    comparables = assets["comparables"]
    match = detail[detail["process_key"] == process_key]
    if match.empty:
        raise HTTPException(status_code=404, detail="Proceso no encontrado")
    row = row_to_dict(match.iloc[0])
    row["reasons_text"] = row.get("reasons") or row.get("reasons_text")
    comparable_rows = []
    comparable_keys = (
        comparables[comparables["process_key"] == process_key]
        .sort_values("rank")["comparable_process_key"]
        .tolist()
    )
    if comparable_keys:
        comparable_rows = (
            detail[detail["process_key"].isin(comparable_keys)]
            .sort_values("priority_score", ascending=False)
            .to_dict(orient="records")
        )
    return build_process_report_html(row, comparable_rows)


@app.post("/reviews")
def create_review(
    review: ReviewRequest,
    x_demo_write_token: str | None = Header(default=None),
) -> dict[str, Any]:
    require_demo_write_token(x_demo_write_token)
    process_detail(review.process_key)
    payload = review.model_dump()
    REVIEWS[:] = [
        item
        for item in REVIEWS
        if not (
            item["process_key"] == review.process_key
            and item["reviewer_label"] == review.reviewer_label
        )
    ]
    REVIEWS.append(payload)
    return payload


@app.get("/reviews/{process_key}")
def reviews(process_key: str) -> list[dict[str, Any]]:
    process_detail(process_key)
    return [item for item in REVIEWS if item["process_key"] == process_key]
