from __future__ import annotations

from fastapi import FastAPI, Query

from services.risk_service.db import execute, fetch_all, fetch_one
from services.risk_service.schemas import Health, RiskRankingRow
from services.risk_service.scoring import score_process_context

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
    context = fetch_one(
        """
        WITH target AS (
            SELECT p.*, e.department_id, m.name AS modality
            FROM procurement_process p
            JOIN public_entity e ON e.entity_id = p.entity_id
            LEFT JOIN modality m ON m.modality_id = p.modality_id
            WHERE p.process_id = %s
        ),
        peer_stats AS (
            SELECT
                COALESCE(
                    (
                        SELECT avg((p.base_price <= target.base_price)::int)::float
                        FROM procurement_process p
                        JOIN public_entity e ON e.entity_id = p.entity_id
                        WHERE p.modality_id IS NOT DISTINCT FROM target.modality_id
                          AND e.department_id IS NOT DISTINCT FROM target.department_id
                    ),
                    0.5
                ) AS value_percentile
            FROM target
        ),
        provider_stats AS (
            SELECT
                CASE WHEN target.provider_id IS NULL THEN 0
                     ELSE COALESCE(
                         (
                             SELECT avg((p.provider_id = target.provider_id)::int)::float
                             FROM procurement_process p
                             WHERE p.entity_id = target.entity_id
                         ),
                         0
                     )
                END AS provider_share
            FROM target
        )
        SELECT target.process_id,
               target.response_count,
               target.base_price::float AS base_price,
               target.modality,
               length(COALESCE(target.description, '')) AS description_length,
               EXISTS (
                   SELECT 1 FROM paa_process_match ppm
                   WHERE ppm.process_id = target.process_id
               ) AS has_paa_match,
               peer_stats.value_percentile,
               provider_stats.provider_share
        FROM target
        CROSS JOIN peer_stats
        CROSS JOIN provider_stats
        """,
        (process_id,),
    )
    scoring = score_process_context(context)
    inserted = execute(
        """
        INSERT INTO risk_assessment(
            process_id, priority_score, confidence_score, anomaly_score,
            peer_deviation_score, rule_score, explanation
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING risk_assessment_id, process_id, priority_score::float AS priority_score
        """,
        (
            process_id,
            scoring["priority_score"],
            scoring["confidence_score"],
            scoring["anomaly_score"],
            scoring["peer_deviation_score"],
            scoring["rule_score"],
            scoring["explanation"],
        ),
    )
    return {
        **inserted,
        "confidence_score": scoring["confidence_score"],
        "components": scoring["components"],
        "explanation": scoring["explanation"],
    }


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
