from __future__ import annotations

from fastapi import FastAPI, Query

from services.analytics_service.db import fetch_all
from services.analytics_service.schemas import Health

app = FastAPI(title="Transparencia360 Analytics Service", version="1.0.0")


@app.get("/health", response_model=Health)
def health() -> Health:
    return Health(status="ok", service="analytics_service")


@app.get("/analytics/overview")
def overview() -> list[dict]:
    return fetch_all(
        """
        SELECT d.name AS department,
               count(p.process_id) AS processes,
               avg(ra.priority_score)::float AS avg_priority_score,
               avg(ra.confidence_score)::float AS avg_confidence_score
        FROM procurement_process p
        JOIN public_entity e ON e.entity_id = p.entity_id
        LEFT JOIN department d ON d.department_id = e.department_id
        LEFT JOIN risk_assessment ra ON ra.process_id = p.process_id
        GROUP BY d.name
        ORDER BY processes DESC
        """
    )


@app.get("/analytics/entity-concentration")
def entity_concentration(limit: int = Query(default=100, ge=1, le=500)) -> list[dict]:
    return fetch_all(
        "SELECT * FROM v_entity_provider_concentration ORDER BY awarded_value DESC LIMIT %s",
        (limit,),
    )


@app.get("/analytics/plan-vs-execution")
def plan_vs_execution(limit: int = Query(default=100, ge=1, le=500)) -> list[dict]:
    return fetch_all(
        "SELECT * FROM v_plan_vs_execution ORDER BY confidence DESC NULLS LAST LIMIT %s",
        (limit,),
    )


@app.get("/analytics/outliers")
def outliers(limit: int = Query(default=100, ge=1, le=500)) -> list[dict]:
    return fetch_all(
        "SELECT * FROM v_value_outliers_by_modality ORDER BY value_percent_rank DESC LIMIT %s",
        (limit,),
    )


@app.get("/analytics/hierarchy/{entity_id}")
def hierarchy(entity_id: int) -> list[dict]:
    return fetch_all(
        """
        WITH RECURSIVE upward AS (
            SELECT node_id, parent_node_id, node_type, label, entity_id, 0 AS reverse_depth
            FROM administrative_hierarchy
            WHERE entity_id = %s
            UNION ALL
            SELECT parent.node_id,
                   parent.parent_node_id,
                   parent.node_type,
                   parent.label,
                   parent.entity_id,
                   upward.reverse_depth + 1
            FROM administrative_hierarchy parent
            JOIN upward ON upward.parent_node_id = parent.node_id
        )
        SELECT node_id,
               parent_node_id,
               node_type,
               label,
               entity_id,
               row_number() OVER (ORDER BY reverse_depth DESC) - 1 AS depth,
               string_agg(label, ' > ') OVER (
                   ORDER BY reverse_depth DESC
                   ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
               ) AS path
        FROM upward
        ORDER BY reverse_depth DESC
        """,
        (entity_id,),
    )
