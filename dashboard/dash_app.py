from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import httpx
import pandas as pd
import plotly.express as px

from services.common.db import fetch_all
from src.utils.reporting import build_process_report_html

try:
    from dash import Dash, Input, Output, State, dash_table, dcc, html
except ImportError:  # Allows smoke imports before optional dependency install.
    Dash = None  # type: ignore[assignment]
    Input = Output = State = dcc = html = dash_table = None  # type: ignore[assignment]


CONTRACTS_SERVICE_URL = os.getenv("CONTRACTS_SERVICE_URL", "http://localhost:8001").rstrip("/")
RISK_SERVICE_URL = os.getenv("RISK_SERVICE_URL", "http://localhost:8002").rstrip("/")
ANALYTICS_SERVICE_URL = os.getenv("ANALYTICS_SERVICE_URL", "http://localhost:8003").rstrip("/")
DASH_ALLOW_DB_FALLBACK = os.getenv("DASH_ALLOW_DB_FALLBACK", "0").lower() in {"1", "true", "yes"}
MARTS_DIR = Path(__file__).resolve().parents[1] / "data" / "marts"
ETHICS_DISCLAIMER = (
    "Esta herramienta prioriza revision humana. No prueba corrupcion, fraude, "
    "responsabilidad fiscal ni responsabilidad juridica; requiere contraste con "
    "la fuente primaria."
)
EMPTY_DATA_MESSAGE = (
    "Esta vista no tiene registros para la seleccion actual. Cambia el proceso "
    "o vuelve al ranking para elegir un caso con evidencia disponible."
)
OVERVIEW_COLUMNS = [
    "department",
    "processes",
    "entities",
    "providers",
    "avg_priority_score",
    "avg_confidence_score",
]
RANKING_COLUMNS = [
    "process_id",
    "process_key",
    "process_reference",
    "entity_name",
    "department",
    "modality",
    "base_price",
    "priority_score",
    "confidence_score",
    "explanation",
    "has_comparables",
]
RANKING_DISPLAY_COLUMNS = [
    "process_reference",
    "entity_name",
    "department",
    "modality",
    "base_price",
    "priority_score",
    "confidence_score",
    "has_comparables",
]
PLAN_COLUMNS = [
    "item_key",
    "paa_description",
    "planned_value",
    "process_id",
    "process_key",
    "base_price",
    "method",
    "confidence",
    "match_status",
]
CONCENTRATION_COLUMNS = ["entity_name", "provider_name", "awarded_value"]


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


def ensure_columns(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=columns)
    for column in columns:
        if column not in frame:
            frame[column] = pd.NA
    return frame


def money_text(value: Any) -> str:
    amount = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(amount):
        return "Sin dato"
    return f"${float(amount):,.0f}"


def clipped_text(value: Any, max_length: int = 52) -> str:
    text = str(value or "Sin dato")
    if len(text) <= max_length:
        return text
    return text[: max_length - 1].rstrip() + "…"


def db_frame(sql: str) -> pd.DataFrame:
    if not DASH_ALLOW_DB_FALLBACK:
        return pd.DataFrame()
    try:
        return pd.DataFrame(fetch_all(sql))
    except Exception:
        return pd.DataFrame()


def mart_frame(name: str) -> pd.DataFrame:
    path = MARTS_DIR / f"{name}.parquet"
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_parquet(path)
    except Exception:
        return pd.DataFrame()


def overview_from_marts() -> pd.DataFrame:
    overview = mart_frame("overview")
    if overview.empty:
        ranking = mart_frame("ranking")
        if ranking.empty:
            return pd.DataFrame(columns=OVERVIEW_COLUMNS)
        overview = (
            ranking.groupby("department", dropna=False)
            .agg(
                processes=("process_key", "count"),
                entities=("entity_name", "nunique"),
                providers=("process_key", "count"),
                avg_priority_score=("priority_score", "mean"),
                avg_confidence_score=("confidence_score", "mean"),
            )
            .reset_index()
        )
    overview = overview.rename(columns={"processes_analyzed": "processes"})
    for column in ["entities", "providers", "avg_confidence_score"]:
        if column not in overview:
            overview[column] = 0
    return ensure_columns(overview, OVERVIEW_COLUMNS)


def ranking_from_marts(limit: int = 500) -> pd.DataFrame:
    ranking = mart_frame("ranking")
    if ranking.empty:
        return pd.DataFrame(columns=RANKING_COLUMNS)
    ranking = ranking.copy()
    if "process_id" not in ranking:
        ranking["process_id"] = range(1, len(ranking) + 1)
    if "explanation" not in ranking:
        ranking["explanation"] = ranking.get(
            "reasons",
            "Priorizacion explicable para revision humana; no prueba conductas indebidas.",
        )
    return ensure_columns(ranking.head(limit), RANKING_COLUMNS)


def load_overview() -> pd.DataFrame:
    frame = frame_from_service(ANALYTICS_SERVICE_URL, "/analytics/overview")
    if not frame.empty:
        if "avg_priority_score" in frame and frame["avg_priority_score"].notna().sum() == 0:
            return overview_from_marts()
        for column in ["entities", "providers"]:
            if column not in frame:
                frame[column] = 0
        return ensure_columns(frame, OVERVIEW_COLUMNS)
    db_result = ensure_columns(
        db_frame(
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
        ),
        OVERVIEW_COLUMNS,
    )
    return db_result if not db_result.empty else overview_from_marts()


def load_ranking() -> pd.DataFrame:
    frame = frame_from_service(RISK_SERVICE_URL, "/risk/ranking", {"limit": 500})
    if not frame.empty:
        if "priority_score" not in frame or frame["priority_score"].notna().sum() == 0:
            return ranking_from_marts()
        return ensure_columns(frame, RANKING_COLUMNS)
    db_result = ensure_columns(
        db_frame(
            """
            SELECT process_id, process_key, process_reference, entity_name, department, modality,
                   base_price::float AS base_price,
                   priority_score::float AS priority_score,
                   confidence_score::float AS confidence_score,
                   explanation,
                   EXISTS (
                       SELECT 1
                       FROM semantic_comparable sc
                       WHERE sc.process_id = v_ranking_processes.process_id
                   ) AS has_comparables
            FROM v_ranking_processes
            ORDER BY has_comparables DESC,
                     priority_score DESC NULLS LAST,
                     confidence_score DESC NULLS LAST
            LIMIT 500
            """
        ),
        RANKING_COLUMNS,
    )
    return db_result if not db_result.empty else ranking_from_marts()


def load_plan_vs_execution() -> pd.DataFrame:
    frame = frame_from_service(
        ANALYTICS_SERVICE_URL,
        "/analytics/plan-vs-execution",
        {"limit": 500},
    )
    if not frame.empty:
        return ensure_columns(frame, PLAN_COLUMNS)
    return ensure_columns(
        db_frame(
            """
            SELECT item_key, paa_description, planned_value::float AS planned_value,
                   process_id, process_key, base_price::float AS base_price,
                   method, confidence::float AS confidence, match_status
            FROM v_plan_vs_execution
            ORDER BY confidence DESC NULLS LAST
            LIMIT 500
            """
        ),
        PLAN_COLUMNS,
    )


def load_comparables(process_id: int) -> pd.DataFrame:
    frame = frame_from_service(
        RISK_SERVICE_URL,
        f"/risk/process/{int(process_id)}/comparables",
    )
    if not frame.empty:
        return frame
    db_result = db_frame(
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
    if not db_result.empty:
        return db_result
    ranking = ranking_from_marts(limit=20000)
    comparables = mart_frame("comparables")
    if ranking.empty or comparables.empty:
        return pd.DataFrame()
    row = ranking[ranking["process_id"] == process_id]
    if row.empty:
        return pd.DataFrame()
    process_key = row.iloc[0]["process_key"]
    matches = comparables[comparables["process_key"] == process_key].copy()
    if matches.empty:
        return matches
    matches = matches.drop(columns=["process_key"], errors="ignore")
    return matches.rename(
        columns={
            "comparable_process_key": "process_key",
            "comparable_title": "title",
            "comparable_value": "base_price",
        }
    )


def concentration_from_ranking(ranking: pd.DataFrame) -> pd.DataFrame:
    if ranking.empty or not {"entity_name", "base_price"}.issubset(ranking.columns):
        return pd.DataFrame(columns=CONCENTRATION_COLUMNS)
    fallback = (
        ranking.groupby("entity_name", dropna=False)
        .agg(awarded_value=("base_price", "sum"))
        .reset_index()
        .sort_values("awarded_value", ascending=False)
        .head(30)
    )
    fallback["provider_name"] = "Procesos agregados por entidad"
    return fallback[CONCENTRATION_COLUMNS]


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


def top_review_candidate(ranking: pd.DataFrame) -> dict[str, Any]:
    if ranking.empty:
        return {}
    ordered = ranking.copy()
    if "has_comparables" in ordered.columns:
        ordered["has_comparables"] = ordered["has_comparables"].fillna(False).astype(bool)
        sort_columns = ["has_comparables", "priority_score", "confidence_score"]
        ascending = [False, False, False]
    else:
        sort_columns = ["priority_score", "confidence_score"]
        ascending = [False, False]
    ordered = ordered.sort_values(sort_columns, ascending=ascending, na_position="last")
    return ordered.iloc[0].to_dict()


def filtered_ranking_records(
    ranking: pd.DataFrame,
    min_score: int | float | None,
) -> list[dict[str, Any]]:
    if ranking.empty:
        return []
    threshold = float(min_score or 0)
    filtered = ranking[ranking["priority_score"].fillna(0) >= threshold]
    return filtered.to_dict("records")


def ranking_csv_text(ranking: pd.DataFrame, min_score: int | float | None) -> str:
    records = filtered_ranking_records(ranking, min_score)
    columns = [column for column in RANKING_COLUMNS if column in ranking.columns]
    return pd.DataFrame(records, columns=columns).to_csv(index=False)


def ranking_table_frame(ranking: pd.DataFrame) -> pd.DataFrame:
    if ranking.empty:
        return pd.DataFrame(columns=RANKING_DISPLAY_COLUMNS)
    columns = [column for column in RANKING_DISPLAY_COLUMNS if column in ranking.columns]
    frame = ranking[columns].copy()
    if "base_price" in frame:
        frame["base_price"] = pd.to_numeric(frame["base_price"], errors="coerce").fillna(0)
        frame["base_price"] = frame["base_price"].map(lambda value: f"${value:,.0f}")
    return frame.rename(
        columns={
            "process_reference": "Referencia",
            "entity_name": "Entidad",
            "department": "Departamento",
            "modality": "Modalidad",
            "base_price": "Valor base",
            "priority_score": "Score",
            "confidence_score": "Confianza",
            "has_comparables": "Comparables",
        }
    )


def concentration_table_frame(concentration: pd.DataFrame) -> pd.DataFrame:
    if concentration.empty:
        return pd.DataFrame(columns=["Entidad", "Proveedor/contexto", "Valor agregado"])
    frame = concentration[CONCENTRATION_COLUMNS].copy()
    frame["awarded_value"] = pd.to_numeric(frame["awarded_value"], errors="coerce").fillna(0)
    frame["awarded_value"] = frame["awarded_value"].map(lambda value: f"${value:,.0f}")
    return frame.rename(
        columns={
            "entity_name": "Entidad",
            "provider_name": "Proveedor/contexto",
            "awarded_value": "Valor agregado",
        }
    )


def process_detail_payload(ranking: pd.DataFrame, process_id: int | None) -> dict[str, Any] | None:
    if process_id is None or ranking.empty:
        return None
    row = ranking[ranking["process_id"] == process_id]
    if row.empty:
        return None
    detail = row.iloc[0].to_dict()
    service_detail = frame_from_service(CONTRACTS_SERVICE_URL, f"/processes/{int(process_id)}")
    if not service_detail.empty:
        detail = {**detail, **service_detail.iloc[0].to_dict()}
    return detail


def process_report_html(ranking: pd.DataFrame, process_id: int | None) -> str:
    detail = process_detail_payload(ranking, process_id)
    if detail is None:
        return build_process_report_html(
            {"process_key": "Sin proceso seleccionado", "reasons": EMPTY_DATA_MESSAGE},
            [],
        )
    comparables = load_comparables(int(process_id))
    comparable_records = comparables.to_dict("records") if not comparables.empty else []
    return build_process_report_html(detail, comparable_records)


def empty_state(title: str, body: str = EMPTY_DATA_MESSAGE, command: str | None = None) -> Any:
    children = [html.Strong(title), html.P(body)]
    if command:
        children.append(html.Code(command))
    return html.Section(
        children,
        className="empty-state",
    )


def metric_card(value: str, label: str) -> Any:
    return html.Div([html.Strong(value), html.Span(label)], className="metric-card")


def comparables_table(comparables: pd.DataFrame) -> Any:
    if comparables.empty:
        return empty_state(
            "Sin comparables para este proceso",
            "Este proceso no tiene pares suficientes en la carga actual. "
            "Puedes seleccionar otro proceso del ranking para mostrar comparables.",
        )
    columns = [
        column
        for column in ["rank", "similarity", "process_key", "title"]
        if column in comparables
    ]
    return html.Table(
        [
            html.Thead(html.Tr([html.Th(column) for column in columns])),
            html.Tbody(
                [
                    html.Tr([html.Td(str(row.get(column, ""))) for column in columns])
                    for row in comparables[columns].head(5).to_dict("records")
                ]
            ),
        ],
        className="simple-table",
    )


def concentration_table(concentration: pd.DataFrame) -> Any:
    if concentration.empty:
        return empty_state(
            "Concentración no disponible para esta selección",
            "La base académica está encendida, pero esta consulta no devolvió "
            "adjudicaciones agregadas para la selección actual.",
        )
    return html.Section(
        [
            html.Div(
                [
                    html.Span(
                        clipped_text(row.get("entity_name"), 70),
                        className="concentration-entity",
                    ),
                    html.Strong(money_text(row.get("awarded_value"))),
                    html.P(clipped_text(row.get("provider_name"), 80)),
                ],
                className="concentration-card",
            )
            for row in concentration.head(10).to_dict("records")
        ],
        className="concentration-list",
    )


def decision_card(label: str, value: str, note: str) -> Any:
    return html.Div(
        [
            html.Span(label, className="card-label"),
            html.Strong(value),
            html.P(note),
        ],
        className="decision-card",
    )


def plot_or_empty(frame: pd.DataFrame, figure: Any, title: str) -> Any:
    if frame.empty:
        return empty_state(title)
    return dcc.Graph(figure=figure, className="chart-panel")


def selected_process_markdown(
    detail: dict[str, Any],
    comparables: pd.DataFrame,
) -> str:
    comparable_text = "Sin comparables disponibles en la carga actual."
    if not comparables.empty:
        rows = []
        for row in comparables.head(5).to_dict("records"):
            rows.append(
                "- "
                + str(row.get("process_key") or row.get("comparable_process_key") or "sin llave")
                + f" | similitud: {row.get('similarity', 'sin dato')}"
            )
        comparable_text = "\n".join(rows)
    return f"""# Evidencia de revisión — ContratIA Abierta

El sistema no acusa, no prueba corrupción y no reemplaza auditoría jurídica o fiscal;
prioriza revisión humana con evidencia trazable.

## Proceso

- Proceso: {detail.get("process_key", "sin dato")}
- Referencia: {detail.get("process_reference", "sin dato")}
- Entidad: {detail.get("entity_name", "sin dato")}
- Departamento: {detail.get("department", "sin dato")}
- Modalidad: {detail.get("modality", "sin dato")}
- Valor base: {detail.get("base_price", "sin dato")}

## Score

- Score de prioridad: {detail.get("priority_score", "sin dato")}
- Confianza: {detail.get("confidence_score", "sin dato")}
- Explicación: {detail.get("explanation", "sin explicación disponible")}

## Contexto PAA

- Estado/método PAA: {detail.get("paa_match_status", detail.get("match_status", "sin dato"))}
- Texto PAA: {detail.get("paa_text", detail.get("paa_description", "sin dato"))}

## Comparables

{comparable_text}

## Limitación

Este archivo es una ayuda para revisión humana. Debe contrastarse con SECOP, PAA,
documentos fuente y criterio profesional antes de tomar cualquier decisión.
"""


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

    app = Dash(__name__, title="ContratIA Abierta")
    overview = coerce_numeric(
        load_overview(),
        ["processes", "entities", "providers", "avg_priority_score", "avg_confidence_score"],
    )
    overview_for_chart = overview.copy()
    if not overview_for_chart.empty and "department" in overview_for_chart:
        valid_department = (
            overview_for_chart["department"]
            .fillna("")
            .astype(str)
            .str.strip()
            .ne("Sin departamento PAA")
        )
        filtered_overview = overview_for_chart[valid_department].copy()
        if not filtered_overview.empty:
            overview_for_chart = filtered_overview
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
    if concentration.empty:
        concentration = concentration_from_ranking(ranking)
    concentration = ensure_columns(concentration, CONCENTRATION_COLUMNS)
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
    top_candidate = top_review_candidate(ranking)
    top_score = top_candidate.get("priority_score")
    top_confidence = top_candidate.get("confidence_score")

    overview_figure = None
    if not overview_for_chart.empty:
        overview_for_chart = overview_for_chart.sort_values("processes", ascending=True)
        overview_figure = px.bar(
            overview_for_chart,
            x="processes",
            y="department",
            color="avg_priority_score",
            title="Procesos por departamento",
            orientation="h",
            color_continuous_scale=["#dce8f4", "#2f6fbb"],
        )
        overview_figure.update_layout(
            paper_bgcolor="#f8fafc",
            plot_bgcolor="#ffffff",
            height=max(430, 42 * len(overview_for_chart) + 160),
            margin={"l": 150, "r": 24, "t": 56, "b": 42},
            font={"family": "Inter, system-ui, sans-serif", "color": "#1f2937"},
        )
        overview_figure.update_xaxes(tickfont={"color": "#1f2937"}, title_font={"color": "#1f2937"})
        overview_figure.update_yaxes(tickfont={"color": "#1f2937"}, title_font={"color": "#1f2937"})
    if not concentration.empty:
        concentration = concentration.sort_values("awarded_value", ascending=False).head(12)

    tab_items = [
        dcc.Tab(
            label="Panorama",
            className="app-tab",
            selected_className="app-tab app-tab--selected",
            children=[
                html.Section(
                    [
                        decision_card(
                            "Que revisar primero",
                            str(top_candidate.get("process_key") or "Sin procesos cargados"),
                            "Primer candidato ordenado por score y confianza.",
                        ),
                        decision_card(
                            "Por que esta priorizado",
                            "Score alto + soporte visible",
                            "La prioridad ordena revision; la confianza indica cobertura.",
                        ),
                        decision_card(
                            "Accion humana siguiente",
                            "Abrir detalle y contrastar fuente",
                            "Registrar criterio antes de escalar la revision.",
                        ),
                        metric_card(
                            f"{float(top_score):.1f}" if top_score is not None else "Sin dato",
                            "Score del primer candidato",
                        ),
                        metric_card(
                            f"{float(top_confidence):.1f}"
                            if top_confidence is not None
                            else "Sin dato",
                            "Confianza del primer candidato",
                        ),
                    ],
                    className="decision-strip",
                ),
                html.Section(
                    [
                        metric_card(f"{total_processes:,}", "Procesos"),
                        metric_card(f"{total_entities:,}", "Entidades"),
                        metric_card(f"{total_providers:,}", "Proveedores"),
                        metric_card(f"{high_priority_share:.1%}", "Alta prioridad"),
                        metric_card(f"{paa_match_share:.1%}", "Match PAA fuerte"),
                    ],
                    className="metric-grid",
                ),
                plot_or_empty(overview, overview_figure, "Panorama sin datos cargados"),
            ],
        ),
        dcc.Tab(
            label="Ranking",
            className="app-tab",
            selected_className="app-tab app-tab--selected",
            children=[
                html.Div(ETHICS_DISCLAIMER, className="inline-disclaimer"),
                html.Div(
                    [
                        html.Label("Score minimo"),
                        dcc.Slider(0, 100, 5, value=50, id="score-filter"),
                        html.Button("Descargar CSV", id="download-ranking-button"),
                        dcc.Download(id="ranking-download"),
                    ],
                    className="filter-row",
                ),
                (
                    dash_table.DataTable(
                        id="ranking-table",
                        columns=[
                            {"name": col, "id": col}
                            for col in ranking_table_frame(ranking).columns
                        ],
                        data=ranking_table_frame(ranking).to_dict("records"),
                        page_size=12,
                        sort_action="native",
                        filter_action="native",
                        style_as_list_view=True,
                    )
                    if not ranking.empty
                    else empty_state("Ranking sin procesos")
                ),
            ],
        ),
        dcc.Tab(
            label="Detalle",
            className="app-tab",
            selected_className="app-tab app-tab--selected",
            children=[
                html.Div(ETHICS_DISCLAIMER, className="inline-disclaimer"),
                html.Div(
                    [
                        html.Label("Proceso"),
                        dcc.Dropdown(
                            id="process-detail-dropdown",
                            options=[
                                {
                                    "label": f"{row['process_key']} - {row['entity_name']}",
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
                html.Button("Descargar HTML", id="download-detail-button"),
                dcc.Download(id="detail-download"),
            ],
        ),
        dcc.Tab(
            label="Concentración secundaria",
            className="app-tab app-tab-secondary",
            selected_className="app-tab app-tab--selected",
            children=[
                html.Div(
                    "Vista secundaria para contexto, no para acusar proveedores.",
                    className="inline-disclaimer",
                ),
                concentration_table(concentration),
            ],
        ),
        dcc.Tab(
            label="Metodologia",
            className="app-tab",
            selected_className="app-tab app-tab--selected",
            children=[
                html.Article(
                    [
                        html.H2("Metodologia"),
                        html.P(
                            "El sistema combina reglas explicables, desviacion frente "
                            "a pares, senal de anomalia y confianza de datos para "
                            "ordenar revision humana."
                        ),
                        html.P(
                            "La salida no acusa personas ni entidades. Solo ayuda a "
                            "decidir que procesos revisar primero."
                        ),
                    ],
                    className="methodology",
                )
            ],
        ),
        dcc.Tab(
            label="Calidad de datos",
            className="app-tab",
            selected_className="app-tab app-tab--selected",
            children=[
                html.Article(
                    [
                        html.H2("Calidad de datos"),
                        html.P(
                            "Estado operativo de fuentes, servicios y evidencia de carga."
                        ),
                        dash_table.DataTable(
                            columns=[
                                {"name": col, "id": col}
                                for col in load_data_quality().columns
                            ],
                            data=load_data_quality().to_dict("records"),
                            page_size=10,
                            style_as_list_view=True,
                        ),
                    ],
                    className="methodology",
                )
            ],
        ),
        dcc.Tab(
            label="Revision humana",
            className="app-tab",
            selected_className="app-tab app-tab--selected",
            children=[
                html.Article(
                    [
                        html.H2("Revision humana"),
                        html.P(
                            "Flujo para mantener, subir o bajar prioridad con notas "
                            "trazables. En presentacion publica debe operar en modo lectura."
                        ),
                        html.Ul(
                            [
                                html.Li("Contrastar SECOP y PAA."),
                                html.Li("Registrar criterio humano."),
                                html.Li("Exportar evidencia para seguimiento."),
                            ]
                        ),
                    ],
                    className="methodology",
                )
            ],
        ),
    ]

    app.layout = html.Div(
        [
            html.Header(
                [
                    html.Div("ContratIA Abierta", className="app-eyebrow"),
                    html.H1("Cola explicable de revision contractual"),
                    html.P(
                        "Herramienta para ordenar procesos SECOP, abrir evidencia y "
                        "decidir que revisar primero."
                    ),
                    html.P(ETHICS_DISCLAIMER, className="ethics-note"),
                ],
                className="app-header",
            ),
            dcc.Tabs(
                tab_items,
                parent_className="app-tabs",
                className="app-tabs-container",
            ),
        ]
    )

    @app.callback(Output("ranking-table", "data"), Input("score-filter", "value"))
    def filter_ranking(min_score: int) -> list[dict[str, Any]]:
        return ranking_table_frame(
            pd.DataFrame(filtered_ranking_records(ranking, min_score))
        ).to_dict("records")

    @app.callback(
        Output("ranking-download", "data"),
        Input("download-ranking-button", "n_clicks"),
        State("score-filter", "value"),
        prevent_initial_call=True,
    )
    def download_ranking(_n_clicks: int | None, min_score: int) -> dict[str, str] | None:
        return {
            "content": ranking_csv_text(ranking, min_score),
            "filename": "contratia-ranking.csv",
            "type": "text/csv",
        }

    @app.callback(
        Output("process-detail-panel", "children"),
        Input("process-detail-dropdown", "value"),
    )
    def render_process_detail(process_id: int | None) -> list[Any]:
        if process_id is None or ranking.empty:
            return [empty_state("Sin proceso seleccionado")]
        detail = process_detail_payload(ranking, process_id)
        if detail is None:
            return [empty_state("Proceso no encontrado", "Selecciona otro registro del ranking.")]
        comparables = load_comparables(int(process_id))
        return [
            html.Section(
                [
                    html.Span("Ficha ejecutiva", className="card-label"),
                    html.H2(str(detail["process_key"])),
                    html.P(str(detail.get("explanation", "Sin explicacion disponible."))),
                ],
                className="detail-card",
            ),
            html.Section(
                [
                    metric_card(str(detail.get("entity_name", "")), "Entidad"),
                    metric_card(str(detail.get("department", "")), "Departamento"),
                    metric_card(str(detail.get("modality", "")), "Modalidad"),
                    metric_card(str(detail.get("priority_score", "")), "Score"),
                    metric_card(str(detail.get("confidence_score", "")), "Confianza"),
                ],
                className="metric-grid detail-metrics",
            ),
            html.Section(
                [
                    html.H3("Que revisar manualmente"),
                    html.Ul(
                        [
                            html.Li("Objeto, valor, modalidad y estado en SECOP."),
                            html.Li("Coherencia con PAA y comparables."),
                            html.Li("Soporte documental antes de escalar."),
                        ]
                    ),
                ],
                className="review-checklist",
            ),
            html.H3("Comparables"),
            comparables_table(comparables),
        ]

    @app.callback(
        Output("detail-download", "data"),
        Input("download-detail-button", "n_clicks"),
        State("process-detail-dropdown", "value"),
        prevent_initial_call=True,
    )
    def download_process_detail(
        _n_clicks: int | None,
        process_id: int | None,
    ) -> dict[str, str] | None:
        detail = process_detail_payload(ranking, process_id)
        if detail is None:
            return None
        process_key = str(detail.get("process_key", process_id))
        return {
            "content": process_report_html(ranking, process_id),
            "filename": f"contratia-evidencia-{process_key}.html",
            "type": "text/html",
        }

    return app


app = create_app()
server = app.server if app is not None else None


if __name__ == "__main__":
    port = int(os.getenv("DASH_PORT", "8050"))
    debug = os.getenv("DASH_DEBUG", "0").lower() in {"1", "true", "yes"}
    if app is None:
        raise SystemExit("Dash no esta instalado. Ejecuta `uv sync --python 3.11 --extra dev`.")
    app.run(debug=debug, host="0.0.0.0", port=port)
