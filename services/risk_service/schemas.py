from __future__ import annotations

from pydantic import BaseModel, Field


class Health(BaseModel):
    status: str
    service: str


class RiskRankingRow(BaseModel):
    process_id: int
    process_key: str
    entity_name: str
    priority_score: float | None = Field(default=None, ge=0, le=100)
    confidence_score: float | None = Field(default=None, ge=0, le=100)
    explanation: str | None = None
