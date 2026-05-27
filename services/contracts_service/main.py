from __future__ import annotations

import os

from fastapi import FastAPI, HTTPException, Query

from services.contracts_service.db import execute, fetch_all, fetch_one
from services.contracts_service.schemas import (
    EntitySummary,
    Health,
    HumanReviewRequest,
    HumanReviewResponse,
    ProcessSummary,
    ProviderDetail,
)

app = FastAPI(title="Transparencia360 Contracts Service", version="1.0.0")


def public_read_only_enabled() -> bool:
    return os.getenv("PUBLIC_READ_ONLY", "false").lower() in {"1", "true", "yes"}


def reject_mutation_when_public() -> None:
    if public_read_only_enabled():
        raise HTTPException(
            status_code=403,
            detail="PUBLIC_READ_ONLY=true bloquea endpoints mutables en modo publico.",
        )


@app.get("/health", response_model=Health)
def health() -> Health:
    return Health(status="ok", service="contracts_service")


@app.get("/processes", response_model=list[ProcessSummary])
def processes(limit: int = Query(default=100, ge=1, le=500)) -> list[dict]:
    return fetch_all(
        """
        SELECT p.process_id, p.process_key, p.title, e.name AS entity_name, p.status,
               p.base_price::float AS base_price
        FROM procurement_process p
        JOIN public_entity e ON e.entity_id = p.entity_id
        ORDER BY p.process_id
        LIMIT %s
        """,
        (limit,),
    )


@app.get("/processes/{process_id}")
def process_detail(process_id: int) -> dict:
    return fetch_one(
        """
        SELECT p.*, e.name AS entity_name, m.name AS modality, ct.name AS contract_type
        FROM procurement_process p
        JOIN public_entity e ON e.entity_id = p.entity_id
        LEFT JOIN modality m ON m.modality_id = p.modality_id
        LEFT JOIN contract_type ct ON ct.contract_type_id = p.contract_type_id
        WHERE p.process_id = %s
        """,
        (process_id,),
    )


@app.get("/entities", response_model=list[EntitySummary])
def entities(limit: int = Query(default=100, ge=1, le=500)) -> list[dict]:
    return fetch_all(
        """
        SELECT e.entity_id, e.name, d.name AS department
        FROM public_entity e
        LEFT JOIN department d ON d.department_id = e.department_id
        ORDER BY e.name
        LIMIT %s
        """,
        (limit,),
    )


@app.get("/providers/{provider_id}", response_model=ProviderDetail)
def provider(provider_id: int) -> dict:
    return fetch_one(
        "SELECT provider_id, name, nit FROM provider WHERE provider_id = %s",
        (provider_id,),
    )


@app.get("/processes/{process_id}/history")
def process_history(process_id: int) -> list[dict]:
    return fetch_all(
        """
        SELECT state_history_id, old_status, new_status, changed_at, changed_by
        FROM process_state_history
        WHERE process_id = %s
        ORDER BY changed_at
        """,
        (process_id,),
    )


@app.post("/reviews", response_model=HumanReviewResponse)
def create_review(review: HumanReviewRequest) -> dict:
    reject_mutation_when_public()
    return execute(
        """
        INSERT INTO human_review(
            process_id, reviewer_label, review_status, priority_decision, notes
        )
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (process_id, reviewer_label) DO UPDATE
        SET review_status = EXCLUDED.review_status,
            priority_decision = EXCLUDED.priority_decision,
            notes = EXCLUDED.notes,
            updated_at = now()
        RETURNING human_review_id, process_id, reviewer_label, review_status,
                  priority_decision, notes
        """,
        (
            review.process_id,
            review.reviewer_label,
            review.review_status,
            review.priority_decision,
            review.notes,
        ),
    )


@app.get("/reviews/{process_id}", response_model=list[HumanReviewResponse])
def reviews(process_id: int) -> list[dict]:
    return fetch_all(
        """
        SELECT human_review_id, process_id, reviewer_label, review_status,
               priority_decision, notes
        FROM human_review
        WHERE process_id = %s
        ORDER BY updated_at DESC
        """,
        (process_id,),
    )
