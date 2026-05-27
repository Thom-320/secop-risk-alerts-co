from __future__ import annotations

from pydantic import BaseModel


class Health(BaseModel):
    status: str
    service: str


class ProcessSummary(BaseModel):
    process_id: int
    process_key: str
    title: str
    entity_name: str
    status: str
    base_price: float


class EntitySummary(BaseModel):
    entity_id: int
    name: str
    department: str | None = None


class ProviderDetail(BaseModel):
    provider_id: int
    name: str
    nit: str | None = None


class HumanReviewRequest(BaseModel):
    process_id: int
    reviewer_label: str = "reviewer_demo"
    review_status: str = "reviewed"
    priority_decision: str = "keep_priority"
    notes: str = ""


class HumanReviewResponse(BaseModel):
    human_review_id: int
    process_id: int
    reviewer_label: str
    review_status: str
    priority_decision: str
    notes: str
