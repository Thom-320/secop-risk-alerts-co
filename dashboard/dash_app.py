from __future__ import annotations

import os
from typing import Any

import httpx
import pandas as pd
import plotly.express as px

from services.common.db import fetch_all

try:
    from dash import Dash, Input, Output, dash_table, dcc, html
except ImportError:  # Allows smoke imports before optional dependency install.
    Dash = None  # type: ignore[assignment]
    Input = Output = dcc = html = dash_table = None  # type: ignore[assignment]


CONTRACTS_SERVICE_URL = os.getenv("CONTRACTS_SERVICE_URL", "http://localhost:8001").rstrip("/")
RISK_SERVICE_URL = os.getenv("RISK_SERVICE_URL", "http://localhost:8002").rstrip("/")
ANALYTICS_SERVICE_URL = os.getenv("ANALYTICS_SERVICE_URL", "http://localhost:8003").rstrip("/")
DASH_ALLOW_DB_FALLBACK = os.getenv("DASH_ALLOW_DB_FALLBACK", "0").lower() in {"1", "true", "yes"}


def service_json(base_url: str, path: str, params: dict[str, Any] | None = None) -> Any:
    with httpx.Client(timeout=4.0) as client:
        response = client.get(f"{base_url}{path}", params=params)
        response.raise_for_status()
        return response.json()


def frame_from_service(
    base_url: str,
    path: str,
    params: dict[str, Any] | None = None,
) -> pd.DataFrame:
    try:
        payload = service_json(base_url, path, params)
        return pd.DataFrame(payload if isinstance(payload, list) else [payload])
    except Exception:
        return pd.DataFrame()


def coerce_numeric(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    for column in columns:
        if column in frame:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


def db_frame(sql: str) -> pd.DataFrame:
    if not DASH_ALLOW_DB_FALLBACK:
        return pd.DataFrame()
    try:
        return pd.DataFrame(fetch_all(sql))
    except Exception:
        return pd.DataFrame()


def load_overview() -> pd.DataFrame:
    frame = frame_from_service(ANALYTICS_SERVICE_URL, "/analytics/overview")
    if not frame.empty:
        for column in ["entities", "providers"]:
            if column not in frame:
                frame[column] = 0
        return frame
    return db_frame(
        """
        SELECT d.name AS department,
               count(p.process_id) AS processes,
               count(DISTINCT e.entity_id) AS entities,
               count(DISTINCT p.provider_id) AS providers,
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


def load_ranking() -> pd.DataFrame:
    frame = frame_from_service(RISK_SERVICE_URL, "/risk/ranking", {"limit": 500})
    if not frame.empty:
        for column in ["department", "modality", "base_price"]:
            if column not in frame:
                frame[column] = ""
        return frame
    return db_frame(
        """
        SELECT process_id, process_key, entity_name, department, modality,
               base_price::float AS base_price,
               priority_score::float AS priority_score,
               confidence_score::float AS confidence_score,
               explanation
        FROM v_ranking_processes
        ORDER BY priority_score DESC NULLS LAST, confidence_score DESC NULLS LAST
        LIMIT 500
        """
    )


def load_plan_vs_execution() -> pd.DataFrame:
    frame = frame_from_service(
        ANALYTICS_SERVICE_URL,
        "/analytics/plan-vs-execution",
        {"limit": 500},
    )
    if not frame.empty:
        return frame
    return db_frame(
        """
        SELECT item_key, paa_description, planned_value::float AS planned_value,
               process_id, process_key, base_price::float AS base_price,
               method, confidence::float AS confidence, match_status
        FROM v_plan_vs_execution
        ORDER BY confidence DESC NULLS LAST
        LIMIT 500
        """
    )


def load_comparables(process_id: int) -> pd.DataFrame:
    frame = frame_from_service(
        RISK_SERVICE_URL,
        f"/risk/process/{int(process_id)}/comparables",
    )
    if not frame.empty:
        return frame
    return db_frame(
        f"""
        SELECT sc.rank, sc.similarity::float AS similarity,
               p.process_key, p.title, p.base_price::float AS base_price
        FROM semantic_comparable sc
        JOIN procurement_process p ON p.process_id = sc.comparable_process_id
        WHERE sc.process_id = {int(process_id)}
        ORDER BY sc.rank
        LIMIT 5
        """
    )


def load_data_quality() -> pd.DataFrame:
    if not DASH_ALLOW_DB_FALLBACK:
        statuses = []
        for name, base_url in [
            ("contracts_service", CONTRACTS_SERVICE_URL),
            ("risk_service", RISK_SERVICE_URL),
            ("analytics_service", ANALYTICS_SERVICE_URL),
        ]:
            try:
                payload = service_json(base_url, "/health")
                statuses.append({"metric": name, "value": payload.get("status", "unknown")})
            except Exception as exc:
                statuses.append({"metric": name, "value": f"unavailable: {exc}"})
        return pd.DataFrame(statuses)
    return db_frame(
        """
        SELECT 'processes' AS metric, count(*)::text AS value FROM procurement_process
        UNION ALL
        SELECT 'risk_assessments', count(*)::text FROM risk_assessment
        UNION ALL
        SELECT 'paa_matches', count(*)::text FROM paa_process_match
        UNION ALL
        SELECT 'audit_events', count(*)::text FROM audit_log
        """
    )


def fallback_layout() -> Any:
    if html is None:
        return None
    return html.Main(
        [
            html.H1("Transparencia360"),
            html.P(
                "Instala Dash con `uv sync --python 3.11 --extra dev` "
                "para ejecutar la interfaz."
            ),
        ],
        className="page",
    )


def create_app() -> Any:
    if Dash is None:
        return None

    app = Dash(__name__, title="Transparencia360")
    overview = coerce_numeric(
        load_overview(),
        ["processes", "entities", "providers", "avg_priority_score", "avg_confidence_score"],
    )
    ranking = coerce_numeric(load_ranking(), ["priority_score", "confidence_score"])
    plan_matches = coerce_numeric(load_plan_vs_execution(), ["confidence"])
    concentration = frame_from_service(
        ANALYTICS_SERVICE_URL,
        "/analytics/entity-concentration",
        {"limit": 30},
    )
    if concentration.empty:
        concentration = db_frame(
            "SELECT entity_name, provider_name, awarded_value::float AS awarded_value "
            "FROM v_entity_provider_concentration "
            "ORDER BY awarded_value DESC LIMIT 30"
        )
    concentration = coerce_numeric(concentration, ["awarded_value"])

    total_processes = int(overview["processes"].sum()) if not overview.empty else 0
    total_entities = int(overview["entities"].sum()) if "entities" in overview else 0
    total_providers = int(overview["providers"].sum()) if "providers" in overview else 0
    high_priority_share = (
        float((ranking["priority_score"].fillna(0) >= 70).mean()) if not ranking.empty else 0.0
    )
    paa_match_share = (
        float(plan_matches["confidence"].fillna(0).ge(0.75).mean())
        if not plan_matches.empty
        else 0.0
    )

    app.layout = html.Div(
        [
            html.Header(
                [
                    html.H1("Transparencia360 / ContratIA Abierta"),
                    html.P(
                        "Priorizacion explicable de revision contractual. "
                        "No prueba conductas indebidas ni reemplaza auditoria humana."
                    ),
                ],
                className="app-header",
            ),
            dcc.Tabs(
                [
                    dcc.Tab(
                        label="Panorama",
                        children=[
                            html.Section(
                                [
                                    html.Div(
                                        [
                                            html.Strong(f"{total_processes:,}"),
                                            html.Span("Procesos"),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Strong(f"{total_entities:,}"),
                                            html.Span("Entidades"),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Strong(f"{total_providers:,}"),
                                            html.Span("Proveedores"),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Strong(f"{high_priority_share:.1%}"),
                                            html.Span("Alta prioridad"),
                                        ]
                                    ),
                                    html.Div(
                                        [
                                            html.Strong(f"{paa_match_share:.1%}"),
                                            html.Span("Match PAA fuerte"),
                                        ]
                                    ),
                                ],
                                className="metric-grid",
                            ),
                            dcc.Graph(
                                figure=px.bar(
                                    overview,
                                    x="department",
                                    y="processes",
                                    color="avg_priority_score",
                                    title="Procesos por departamento",
                                )
                                if not overview.empty
                                else {},
                            ),
                        ],
                    ),
                    dcc.Tab(
                        label="Ranking",
                        children=[
                            html.Div(
                                [
                                    html.Label("Score minimo"),
                                    dcc.Slider(0, 100, 5, value=50, id="score-filter"),
                                ],
                                className="filter-row",
                            ),
                            dash_table.DataTable(
                                id="ranking-table",
                                columns=[{"name": col, "id": col} for col in ranking.columns],
                                data=ranking.to_dict("records"),
                                page_size=12,
                                sort_action="native",
                                filter_action="native",
                            ),
                        ],
                    ),
                    dcc.Tab(
                        label="Detalle",
                        children=[
                            html.Div(
                                [
                                    html.Label("Proceso"),
                                    dcc.Dropdown(
                                        id="process-detail-dropdown",
                                        options=[
                                            {
                                                "label": (
                                                    f"{row['process_key']} - "
                                                    f"{row['entity_name']}"
                                                ),
                                                "value": row["process_id"],
                                            }
                                            for row in ranking.head(100).to_dict("records")
                                        ],
                                        value=(
                                            int(ranking.iloc[0]["process_id"])
                                            if not ranking.empty
                                            else None
                                        ),
                                    ),
                                ],
                                className="filter-row",
                            ),
                            html.Div(id="process-detail-panel", className="methodology"),
                        ],
                    ),
                    dcc.Tab(
                        label="Concentracion",
                        children=[
                            dcc.Graph(
                                figure=(
                                    px.bar(
                                        concentration,
                                        x="provider_name",
                                        y="awarded_value",
                                        color="entity_name",
                                        title="Top proveedores por valor adjudicado",
                                    )
                                    if not concentration.empty
                                    else px.bar(title="Sin contratos cargados en la demo")
                                )
                            )
                        ],
                    ),
                    dcc.Tab(
                        label="Metodologia",
                        children=[
                            html.Article(
                                [
                                    html.H2("Metodologia"),
                                    html.P(
                                        "El sistema combina reglas explicables, "
                                        "desviacion frente a pares, senal de anomalia "
                                        "y confianza de datos para ordenar revision humana."
                                    ),
                                    html.P(
                                        "La salida no acusa personas ni entidades. "
                                        "Solo ayuda a ordenar que procesos revisar primero."
                                    ),
                                ],
                                className="methodology",
                            )
                        ],
                    ),
                    dcc.Tab(
                        label="Calidad de datos",
                        children=[
                            html.Article(
                                [
                                    html.H2("Calidad de datos"),
                                    html.P(
                                        "La demo registra volumen cargado, matches PAA, "
                                        "evaluaciones de prioridad y auditoria de cambios."
                                    ),
                                    dash_table.DataTable(
                                        columns=[
                                            {"name": col, "id": col}
                                            for col in load_data_quality().columns
                                        ],
                                        data=load_data_quality().to_dict("records"),
                                        page_size=10,
                                    ),
                                ],
                                className="methodology",
                            )
                        ],
                    ),
                    dcc.Tab(
                        label="Revision humana demo",
                        children=[
                            html.Article(
                                [
                                    html.H2("Revision humana demo"),
                                    html.P(
                                        "El flujo esperado permite que un revisor mantenga, "
                                        "suba o baje la prioridad y deje notas trazables."
                                    ),
                                    html.P(
                                        "Para registrar revisiones por API usa POST /reviews "
                                        "y consulta GET /reviews/{process_id}."
                                    ),
                                ],
                                className="methodology",
                            )
                        ],
                    ),
                ]
            ),
        ]
    )

    @app.callback(Output("ranking-table", "data"), Input("score-filter", "value"))
    def filter_ranking(min_score: int) -> list[dict[str, Any]]:
        if ranking.empty:
            return []
        filtered = ranking[ranking["priority_score"].fillna(0) >= min_score]
        return filtered.to_dict("records")

    @app.callback(
        Output("process-detail-panel", "children"),
        Input("process-detail-dropdown", "value"),
    )
    def render_process_detail(process_id: int | None) -> list[Any]:
        if process_id is None or ranking.empty:
            return [html.P("No hay procesos cargados.")]
        row = ranking[ranking["process_id"] == process_id]
        if row.empty:
            return [html.P("Proceso no encontrado.")]
        detail = row.iloc[0]
        service_detail = frame_from_service(CONTRACTS_SERVICE_URL, f"/processes/{int(process_id)}")
        if not service_detail.empty:
            detail = {**detail.to_dict(), **service_detail.iloc[0].to_dict()}
        else:
            detail = detail.to_dict()
        comparables = load_comparables(int(process_id))
        return [
            html.H2(str(detail["process_key"])),
            html.P(str(detail["explanation"])),
            html.Ul(
                [
                    html.Li(f"Entidad: {detail.get('entity_name', '')}"),
                    html.Li(f"Departamento: {detail.get('department', '')}"),
                    html.Li(f"Modalidad: {detail.get('modality', '')}"),
                    html.Li(f"Score: {detail.get('priority_score', '')}"),
                    html.Li(f"Confianza: {detail.get('confidence_score', '')}"),
                ]
            ),
            html.H3("Comparables"),
            dash_table.DataTable(
                columns=[{"name": col, "id": col} for col in comparables.columns],
                data=comparables.to_dict("records"),
                page_size=5,
            ),
        ]

    return app


app = create_app()
server = app.server if app is not None else None


if __name__ == "__main__":
    port = int(os.getenv("DASH_PORT", "8050"))
    debug = os.getenv("DASH_DEBUG", "0").lower() in {"1", "true", "yes"}
    if app is None:
        raise SystemExit("Dash no esta instalado. Ejecuta `uv sync --python 3.11 --extra dev`.")
    app.run(debug=debug, host="0.0.0.0", port=port)
