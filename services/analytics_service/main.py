from __future__ import annotations

from fastapi import FastAPI, Query

from services.analytics_service.db import fetch_all
from services.analytics_service.schemas import Health

app = FastAPI(title="Transparencia360 Analytics Service", version="1.0.0")


@app.get("/health", response_model=Health)
def health() -> Health:
    return Health(status="ok", service="analytics_service")


@app.get("/analytics/overview")
def overview(department: str | None = Query(default=None)) -> list[dict]:
    """Panorama por departamento sobre el universo SCOREADO real.

    INNER JOIN a risk_assessment: solo entran procesos con score, lo que
    descarta filas de muestra antiguas sin evaluar y garantiza una sola
    fuente de verdad coherente con el ranking.
    """
    return fetch_all(
        """
        SELECT d.name AS department,
               count(p.process_id) AS processes,
               count(DISTINCT e.entity_id) AS entities,
               count(DISTINCT p.provider_id) AS providers,
               avg(ra.priority_score)::float AS avg_priority_score,
               avg(ra.confidence_score)::float AS avg_confidence_score,
               (100.0 * sum((ra.priority_score >= 70)::int) / count(*))::float
                   AS pct_high_priority
        FROM procurement_process p
        JOIN public_entity e ON e.entity_id = p.entity_id
        LEFT JOIN department d ON d.department_id = e.department_id
        JOIN risk_assessment ra ON ra.process_id = p.process_id
        WHERE (%s::text IS NULL OR d.name = %s::text)
        GROUP BY d.name
        ORDER BY processes DESC
        """,
        (department, department),
    )


@app.get("/analytics/agr-enrichment")
def agr_enrichment() -> dict:
    """Experimento de validación: ¿los procesos de entidades vigiladas por
    el control fiscal (AGR) puntúan más alto que el resto?

    AGR (`wasc-xi4h`) es contexto, NO etiqueta del modelo. Una entidad
    vigilada no implica conducta indebida probada; mide selección para
    revisión fiscal. Si el score enriquece ese grupo, el triage es útil.
    """
    rows = fetch_all(
        """
        WITH flagged AS (
            SELECT DISTINCT fcs.entity_id
            FROM fiscal_finding ff
            JOIN fiscal_control_subject fcs
              ON fcs.fiscal_subject_id = ff.fiscal_subject_id
            WHERE fcs.entity_id IS NOT NULL
        ),
        proc AS (
            SELECT ra.priority_score,
                   (f.entity_id IS NOT NULL) AS is_flagged
            FROM procurement_process p
            JOIN risk_assessment ra ON ra.process_id = p.process_id
            LEFT JOIN flagged f ON f.entity_id = p.entity_id
        )
        SELECT is_flagged,
               count(*) AS n_processes,
               round(avg(priority_score)::numeric, 2)::float AS mean_score,
               round(percentile_cont(0.5) WITHIN GROUP (
                   ORDER BY priority_score)::numeric, 1)::float AS median_score,
               round((100.0 * sum((priority_score >= 70)::int)
                   / count(*))::numeric, 2)::float AS pct_high_priority
        FROM proc
        GROUP BY is_flagged
        """
    )
    flagged = next((r for r in rows if r["is_flagged"]), {})
    baseline = next((r for r in rows if not r["is_flagged"]), {})
    lift = None
    if flagged.get("pct_high_priority") and baseline.get("pct_high_priority"):
        lift = round(
            flagged["pct_high_priority"] / baseline["pct_high_priority"], 2
        )
    return {
        "flagged": flagged,
        "baseline": baseline,
        "enrichment_lift": lift,
        "note": (
            "Auditoria AGR no prueba conducta indebida; mide seleccion para "
            "revision fiscal. Senal de validacion, no de culpabilidad."
        ),
    }


@app.get("/analytics/score-distribution")
def score_distribution(department: str | None = Query(default=None)) -> list[dict]:
    """Histograma de la distribución del score (forma de triage)."""
    return fetch_all(
        """
        SELECT bucket,
               (bucket * 10) || '-' || (bucket * 10 + 10) AS range_label,
               count(*) AS n_processes
        FROM (
            SELECT least(floor(ra.priority_score / 10)::int, 9) AS bucket
            FROM procurement_process p
            JOIN public_entity e ON e.entity_id = p.entity_id
            LEFT JOIN department d ON d.department_id = e.department_id
            JOIN risk_assessment ra ON ra.process_id = p.process_id
            WHERE (%s::text IS NULL OR d.name = %s::text)
        ) b
        GROUP BY bucket
        ORDER BY bucket
        """,
        (department, department),
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
