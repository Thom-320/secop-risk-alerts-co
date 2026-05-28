from __future__ import annotations

from pydantic import BaseModel, Field


class Health(BaseModel):
    status: str
    service: str


class RiskRankingRow(BaseModel):
    process_id: int
    process_key: str
    process_reference: str | None = None
    entity_name: str
    department: str | None = None
    modality: str | None = None
    base_price: float | None = None
    priority_score: float | None = Field(default=None, ge=0, le=100)
    confidence_score: float | None = Field(default=None, ge=0, le=100)
    explanation: str | None = None
    has_comparables: bool = False
    national_rank: int | None = None
    score_percentile: float | None = Field(default=None, ge=0, le=100)
