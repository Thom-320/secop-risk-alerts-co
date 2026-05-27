from __future__ import annotations

from fastapi import FastAPI, Query

from services.risk_service.db import execute, fetch_all, fetch_one
from services.risk_service.schemas import Health, RiskRankingRow

app = FastAPI(title="Transparencia360 Risk Service", version="1.0.0")


@app.get("/health", response_model=Health)
def health() -> Health:
    return Health(status="ok", service="risk_service")


@app.get("/risk/ranking", response_model=list[RiskRankingRow])
def ranking(limit: int = Query(default=100, ge=1, le=500)) -> list[dict]:
    return fetch_all(
        """
        SELECT process_id, process_key, entity_name,
               priority_score::float AS priority_score,
               confidence_score::float AS confidence_score,
               explanation
        FROM v_ranking_processes
        ORDER BY priority_score DESC NULLS LAST, confidence_score DESC NULLS LAST
        LIMIT %s
        """,
        (limit,),
    )


@app.get("/risk/process/{process_id}")
def process_risk(process_id: int) -> dict:
    return fetch_one(
        """
        SELECT ra.*, p.process_key
        FROM risk_assessment ra
        JOIN procurement_process p ON p.process_id = ra.process_id
        WHERE ra.process_id = %s
        ORDER BY ra.assessed_at DESC
        LIMIT 1
        """,
        (process_id,),
    )


@app.post("/risk/recompute/{process_id}")
def recompute(process_id: int) -> dict:
    return execute(
        """
        INSERT INTO risk_assessment(
            process_id, priority_score, confidence_score, anomaly_score,
            peer_deviation_score, rule_score, explanation
        )
        SELECT process_id, 60, 75, 55, 60, 65,
               'Recalculo demo: priorizacion de revision humana, no acusacion.'
        FROM procurement_process
        WHERE process_id = %s
        RETURNING risk_assessment_id, process_id, priority_score::float AS priority_score
        """,
        (process_id,),
    )


@app.get("/risk/process/{process_id}/comparables")
def comparables(process_id: int) -> list[dict]:
    return fetch_all(
        """
        SELECT sc.rank, sc.similarity::float AS similarity, p.process_id, p.process_key, p.title
        FROM semantic_comparable sc
        JOIN procurement_process p ON p.process_id = sc.comparable_process_id
        WHERE sc.process_id = %s
        ORDER BY sc.rank
        """,
        (process_id,),
    )


@app.get("/risk/rules")
def rules() -> list[dict]:
    return fetch_all(
        "SELECT code, name, description, weight::float AS weight, active "
        "FROM risk_rule ORDER BY code"
    )
