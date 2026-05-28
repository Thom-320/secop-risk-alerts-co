from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import httpx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from services.common.db import fetch_all
from src.utils.reporting import build_process_report_html

try:
    from dash import (
        Dash,
        Input,
        Output,
        State,
        dash_table,
        dcc,
        html,
    )
except ImportError:
    Dash = None  # type: ignore[assignment]
    Input = Output = State = None  # type: ignore[assignment]
    dcc = html = dash_table = None  # type: ignore[assignment]


CONTRACTS_URL = os.getenv(
    "CONTRACTS_SERVICE_URL", "http://localhost:8001",
).rstrip("/")
RISK_URL = os.getenv(
    "RISK_SERVICE_URL", "http://localhost:8002",
).rstrip("/")
ANALYTICS_URL = os.getenv(
    "ANALYTICS_SERVICE_URL", "http://localhost:8003",
).rstrip("/")
DB_FALLBACK = os.getenv(
    "DASH_ALLOW_DB_FALLBACK", "0",
).lower() in {"1", "true", "yes"}
MARTS_DIR = Path(__file__).resolve().parents[1] / "data" / "marts"

DISCLAIMER = (
    "Esta herramienta prioriza revision humana. No prueba corrupcion, fraude, "
    "responsabilidad fiscal ni responsabilidad juridica; requiere contraste con "
    "la fuente primaria."
)
ETHICS_DISCLAIMER = DISCLAIMER
EMPTY_MSG = (
    "Esta vista no tiene registros para la seleccion actual. Cambia el proceso "
    "o vuelve al ranking para elegir un caso con evidencia disponible."
)

OVERVIEW_COLS = [
    "department", "processes", "entities",
    "providers", "avg_priority_score", "avg_confidence_score",
]
RANKING_COLS = [
    "process_id", "process_key", "process_reference",
    "entity_name", "department", "modality", "base_price",
    "priority_score", "confidence_score", "explanation", "has_comparables",
]
DISPLAY_COLS = [
    "process_reference", "entity_name", "department", "modality",
    "base_price", "priority_score", "confidence_score", "has_comparables",
]
PLAN_COLS = [
    "item_key", "paa_description", "planned_value", "process_id",
    "process_key", "base_price", "method", "confidence", "match_status",
]
CONC_COLS = ["entity_name", "provider_name", "awarded_value"]

# ── MongoDB project context ───────────────────────────────────


def load_project_context() -> list[dict]:
    """Load project context from MongoDB."""
    try:
        import pymongo
        mongo_uri = os.getenv("MONGO_URL", "mongodb://localhost:27018/contratia")
        client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        db = client.get_default_database()
        docs = list(db.project_context.find({}, {"_id": 0}).sort("order", 1))
        return docs if docs else _default_context()
    except Exception:
        return _default_context()


def _default_context() -> list[dict]:
    return [
        {"key": "what_is_it", "title": "Qué es ContratIA Abierta",
         "content": "Sistema de priorización de revisión contractual usando datos abiertos SECOP."},
        {"key": "problem", "title": "Problema",
         "content": "En Colombia se publican más de 2M procesos/año. Las oficinas de control no pueden revisarlos todos."},
    ]


# ── Data helpers ──────────────────────────────────────────────


def svc_json(url: str, path: str, params: dict | None = None) -> Any:
    with httpx.Client(timeout=4.0) as c:
        r = c.get(f"{url}{path}", params=params)
        r.raise_for_status()
        return r.json()


def svc_frame(url: str, path: str, params: dict | None = None) -> pd.DataFrame:
    try:
        payload = svc_json(url, path, params)
        return pd.DataFrame(payload if isinstance(payload, list) else [payload])
    except Exception:
        return pd.DataFrame()


# Backward-compatible aliases for tests
service_json = svc_json
frame_from_service = svc_frame


def coerce(frame: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for c in cols:
        if c in frame:
            frame[c] = pd.to_numeric(frame[c], errors="coerce")
    return frame


def ensure(frame: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame(columns=cols)
    for c in cols:
        if c not in frame:
            frame[c] = pd.NA
    return frame


def money(v: Any) -> str:
    amt = pd.to_numeric(pd.Series([v]), errors="coerce").iloc[0]
    if pd.isna(amt):
        return "Sin dato"
    return f"${float(amt):,.0f}"


def clip(v: Any, n: int = 52) -> str:
    t = str(v or "Sin dato")
    return t if len(t) <= n else t[: n - 1].rstrip() + "\u2026"


def db_sql(sql: str) -> pd.DataFrame:
    if not DB_FALLBACK:
        return pd.DataFrame()
    try:
        return pd.DataFrame(fetch_all(sql))
    except Exception:
        return pd.DataFrame()


def mart(name: str) -> pd.DataFrame:
    p = MARTS_DIR / f"{name}.parquet"
    if not p.exists():
        return pd.DataFrame()
    try:
        return pd.read_parquet(p)
    except Exception:
        return pd.DataFrame()


# ── Data loading ──────────────────────────────────────────────


def load_overview() -> pd.DataFrame:
    f = svc_frame(ANALYTICS_URL, "/analytics/overview")
    if not f.empty:
        if "avg_priority_score" in f and f["avg_priority_score"].notna().sum() == 0:
            return _overview_from_marts()
        return ensure(f, OVERVIEW_COLS)
    db = ensure(db_sql("""
        SELECT d.name AS department, count(p.process_id) AS processes,
               count(DISTINCT e.entity_id) AS entities,
               count(DISTINCT p.provider_id) AS providers,
               avg(ra.priority_score)::float AS avg_priority_score,
               avg(ra.confidence_score)::float AS avg_confidence_score
        FROM procurement_process p
        JOIN public_entity e ON e.entity_id = p.entity_id
        LEFT JOIN department d ON d.department_id = e.department_id
        LEFT JOIN risk_assessment ra ON ra.process_id = p.process_id
        GROUP BY d.name ORDER BY processes DESC
    """), OVERVIEW_COLS)
    return db if not db.empty else _overview_from_marts()


def _overview_from_marts() -> pd.DataFrame:
    ov = mart("overview")
    if ov.empty:
        rk = mart("ranking")
        if rk.empty:
            return pd.DataFrame(columns=OVERVIEW_COLS)
        ov = rk.groupby("department", dropna=False).agg(
            processes=("process_key", "count"),
            entities=("entity_name", "nunique"),
            providers=("process_key", "count"),
            avg_priority_score=("priority_score", "mean"),
            avg_confidence_score=("confidence_score", "mean"),
        ).reset_index()
    ov = ov.rename(columns={"processes_analyzed": "processes"})
    for c in ["entities", "providers", "avg_confidence_score"]:
        if c not in ov:
            ov[c] = 0
    return ensure(ov, OVERVIEW_COLS)


def load_ranking(limit: int = 500) -> pd.DataFrame:
    f = svc_frame(RISK_URL, "/risk/ranking", {"limit": limit})
    if not f.empty:
        if "priority_score" not in f or f["priority_score"].notna().sum() == 0:
            return _ranking_from_marts()
        return ensure(f, RANKING_COLS)
    db = ensure(db_sql("""
        SELECT process_id, process_key, process_reference,
               entity_name, department, modality,
               base_price::float AS base_price,
               priority_score::float AS priority_score,
               confidence_score::float AS confidence_score,
               explanation,
               EXISTS (SELECT 1 FROM semantic_comparable sc
                       WHERE sc.process_id = v_ranking_processes.process_id
               ) AS has_comparables
        FROM v_ranking_processes
        ORDER BY has_comparables DESC,
                 priority_score DESC NULLS LAST,
                 confidence_score DESC NULLS LAST
        LIMIT 500
    """), RANKING_COLS)
    return db if not db.empty else _ranking_from_marts()


def _ranking_from_marts() -> pd.DataFrame:
    rk = mart("ranking")
    if rk.empty:
        return pd.DataFrame(columns=RANKING_COLS)
    rk = rk.copy()
    if "process_id" not in rk:
        rk["process_id"] = range(1, len(rk) + 1)
    if "explanation" not in rk:
        rk["explanation"] = rk.get("reasons", "")
    return ensure(rk.head(500), RANKING_COLS)


def load_plan() -> pd.DataFrame:
    f = svc_frame(ANALYTICS_URL, "/analytics/plan-vs-execution", {"limit": 500})
    if not f.empty:
        return ensure(f, PLAN_COLS)
    return ensure(db_sql("""
        SELECT item_key, paa_description, planned_value::float AS planned_value,
               process_id, process_key, base_price::float AS base_price,
               method, confidence::float AS confidence, match_status
        FROM v_plan_vs_execution
        ORDER BY confidence DESC NULLS LAST LIMIT 500
    """), PLAN_COLS)


def load_comparables(pid: int) -> pd.DataFrame:
    f = svc_frame(RISK_URL, f"/risk/process/{pid}/comparables")
    if not f.empty:
        return f
    db = db_sql(f"""
        SELECT sc.rank, sc.similarity::float AS similarity,
               p.process_key, p.title, p.base_price::float AS base_price
        FROM semantic_comparable sc
        JOIN procurement_process p ON p.process_id = sc.comparable_process_id
        WHERE sc.process_id = {pid}
        ORDER BY sc.rank LIMIT 5
    """)
    if not db.empty:
        return db
    rk = _ranking_from_marts()
    comp = mart("comparables")
    if rk.empty or comp.empty:
        return pd.DataFrame()
    row = rk[rk["process_id"] == pid]
    if row.empty:
        return pd.DataFrame()
    pk = row.iloc[0]["process_key"]
    m = comp[comp["process_key"] == pk].copy()
    if m.empty:
        return m
    m = m.drop(columns=["process_key"], errors="ignore")
    return m.rename(columns={
        "comparable_process_key": "process_key",
        "comparable_title": "title",
        "comparable_value": "base_price",
    })


def load_concentration(ranking: pd.DataFrame) -> pd.DataFrame:
    f = svc_frame(ANALYTICS_URL, "/analytics/entity-concentration", {"limit": 30})
    if not f.empty:
        return ensure(f, CONC_COLS)
    db = db_sql(
        "SELECT entity_name, provider_name, awarded_value::float AS awarded_value "
        "FROM v_entity_provider_concentration "
        "ORDER BY awarded_value DESC LIMIT 30",
    )
    if not db.empty:
        return ensure(db, CONC_COLS)
    if ranking.empty or "entity_name" not in ranking.columns:
        return pd.DataFrame(columns=CONC_COLS)
    fb = ranking.groupby("entity_name", dropna=False).agg(
        awarded_value=("base_price", "sum"),
    ).reset_index().sort_values("awarded_value", ascending=False).head(30)
    fb["provider_name"] = "Procesos agregados por entidad"
    return fb[CONC_COLS]


def load_quality() -> pd.DataFrame:
    if not DB_FALLBACK:
        rows = []
        for name, url in [
            ("contracts", CONTRACTS_URL),
            ("risk", RISK_URL),
            ("analytics", ANALYTICS_URL),
        ]:
            try:
                h = svc_json(url, "/health")
                rows.append({"servicio": name, "estado": h.get("status", "?")})
            except Exception as e:
                rows.append({"servicio": name, "estado": f"error: {e}"})
        return pd.DataFrame(rows)
    return db_sql("""
        SELECT 'procesos' AS metrica, count(*)::text AS valor
        FROM procurement_process
        UNION ALL SELECT 'evaluaciones_riesgo', count(*)::text
        FROM risk_assessment
        UNION ALL SELECT 'matches_paa', count(*)::text
        FROM paa_process_match
        UNION ALL SELECT 'eventos_auditoria', count(*)::text
        FROM audit_log
    """)


# ── Helpers ───────────────────────────────────────────────────


def top_candidate(ranking: pd.DataFrame) -> dict:
    if ranking.empty:
        return {}
    o = ranking.copy()
    if "has_comparables" in o.columns:
        o["has_comparables"] = o["has_comparables"].fillna(False).astype(bool)
        o = o.sort_values(
            ["has_comparables", "priority_score", "confidence_score"],
            ascending=[False, False, False], na_position="last",
        )
    else:
        o = o.sort_values(
            ["priority_score", "confidence_score"],
            ascending=[False, False], na_position="last",
        )
    return o.iloc[0].to_dict()


def action_text(score: float | None, conf: float | None) -> str:
    if score is None or pd.isna(score):
        return "Validar datos"
    s = float(score)
    c = 0 if conf is None or pd.isna(conf) else float(conf)
    if s >= 70 and c >= 60:
        return "Abrir SECOP y contrastar"
    if s >= 70:
        return "Validar soporte antes de escalar"
    if s >= 40:
        return "Revisar en contexto"
    return "Monitorear"


def reason_short(text: str | None, n: int = 60) -> str:
    if not text or pd.isna(text):
        return "Sin señales"
    t = str(text)
    return t if len(t) <= n else t[: n - 1].rstrip() + "\u2026"


def filtered_records(ranking: pd.DataFrame, min_s: int | None) -> list[dict]:
    if ranking.empty:
        return []
    th = float(min_s or 0)
    return ranking[ranking["priority_score"].fillna(0) >= th].to_dict("records")


def ranking_csv(ranking: pd.DataFrame, min_s: int | None) -> str:
    recs = filtered_records(ranking, min_s)
    cols = [c for c in RANKING_COLS if c in ranking.columns]
    return pd.DataFrame(recs, columns=cols).to_csv(index=False)


# Backward-compatible alias for tests
ranking_csv_text = ranking_csv


def ranking_table(ranking: pd.DataFrame) -> pd.DataFrame:
    if ranking.empty:
        return pd.DataFrame(columns=[
            "Referencia", "Entidad", "Depto", "Modalidad",
            "Valor base", "Score", "Confianza", "Accion",
        ])
    f = ranking.copy()
    if "base_price" in f:
        f["base_price"] = pd.to_numeric(f["base_price"], errors="coerce").fillna(0)
        f["base_price"] = f["base_price"].map(lambda v: f"${v:,.0f}")
    f["Accion"] = f.apply(
        lambda r: action_text(r.get("priority_score"), r.get("confidence_score")),
        axis=1,
    )
    out = f[[
        "process_reference", "entity_name", "department", "modality",
        "base_price", "priority_score", "confidence_score", "Accion",
    ]].copy()
    return out.rename(columns={
        "process_reference": "Referencia",
        "entity_name": "Entidad",
        "department": "Depto",
        "modality": "Modalidad",
        "base_price": "Valor base",
        "priority_score": "Score",
        "confidence_score": "Confianza",
    })


def cola_table(ranking: pd.DataFrame) -> pd.DataFrame:
    """Top 10 for weekly review queue."""
    if ranking.empty:
        return pd.DataFrame()
    top = ranking.nlargest(10, "priority_score").copy()
    top["Accion"] = top.apply(
        lambda r: action_text(r.get("priority_score"), r.get("confidence_score")),
        axis=1,
    )
    top["Razon"] = top["explanation"].map(lambda v: reason_short(v, 55))
    if "base_price" in top:
        top["base_price"] = pd.to_numeric(top["base_price"], errors="coerce").fillna(0)
        top["base_price"] = top["base_price"].map(lambda v: f"${v:,.0f}")
    out = top[[
        "process_reference", "entity_name", "department", "modality",
        "base_price", "priority_score", "confidence_score", "Razon", "Accion",
    ]].copy()
    out.insert(0, "#", range(1, len(out) + 1))
    return out.rename(columns={
        "process_reference": "Referencia",
        "entity_name": "Entidad",
        "department": "Depto",
        "modality": "Modalidad",
        "base_price": "Valor base",
        "priority_score": "Score",
        "confidence_score": "Conf",
        "Razon": "Razon principal",
    })


def conc_table(conc: pd.DataFrame) -> pd.DataFrame:
    if conc.empty:
        return pd.DataFrame(columns=["Entidad", "Proveedor/contexto", "Valor agregado"])
    f = conc[CONC_COLS].copy()
    f["awarded_value"] = pd.to_numeric(f["awarded_value"], errors="coerce").fillna(0)
    f["awarded_value"] = f["awarded_value"].map(lambda v: f"${v:,.0f}")
    return f.rename(columns={
        "entity_name": "Entidad",
        "provider_name": "Proveedor/contexto",
        "awarded_value": "Valor agregado",
    })


# ── Dash components ──────────────────────────────────────────


def empty_state(title: str, body: str = EMPTY_MSG) -> Any:
    return html.Section(
        [html.Strong(title), html.P(body)],
        className="empty-state",
    )


def metric(value: str, label: str) -> Any:
    return html.Div(
        [html.Strong(value), html.Span(label)],
        className="metric-card",
    )


def decision(label: str, value: str, note: str) -> Any:
    return html.Div(
        [html.Span(label, className="card-label"), html.Strong(value), html.P(note)],
        className="decision-card",
    )


def plot_or(frame: pd.DataFrame, fig: Any, title: str) -> Any:
    if frame.empty or fig is None:
        return empty_state(title)
    return html.Div(
        dcc.Graph(
            figure=fig, config={"displayModeBar": False, "responsive": False},
            style={"height": "420px", "width": "100%"},
        ),
        className="chart-panel",
    )


def comps_table(comps: pd.DataFrame) -> Any:
    if comps.empty:
        return empty_state(
            "Sin comparables para este proceso",
            "Selecciona otro proceso del ranking para mostrar comparables.",
        )
    cols = [c for c in ["rank", "similarity", "process_key", "title"] if c in comps]
    return html.Table(
        [
            html.Thead(html.Tr([html.Th(c) for c in cols])),
            html.Tbody([
                html.Tr([html.Td(str(row.get(c, ""))) for c in cols])
                for row in comps[cols].head(5).to_dict("records")
            ]),
        ],
        className="simple-table",
    )


def score_breakdown(detail: dict) -> Any:
    """Show score components as a visual breakdown."""
    anomaly = float(detail.get("anomaly_score", 0) or 0)
    peer = float(detail.get("peer_deviation_score", 0) or 0)
    rule = float(detail.get("rule_score", 0) or 0)
    total = float(detail.get("priority_score", 0) or 0)
    conf = float(detail.get("confidence_score", 0) or 0)
    return html.Section(
        [
            html.H3("Componentes del score"),
            html.Div(
                [
                    html.Div([
                        html.Span("ANOMALIA (45%)", className="breakdown-label"),
                        html.Strong(f"{anomaly:.0f}", className="breakdown-value"),
                        html.Span("IsolationForest: detecta procesos estructuralmente raros", className="breakdown-note"),
                    ], className="breakdown-item"),
                    html.Div([
                        html.Span("DESVIACION PARES (35%)", className="breakdown-label"),
                        html.Strong(f"{peer:.0f}", className="breakdown-value"),
                        html.Span("Valor, duracion y competencia vs procesos similares", className="breakdown-note"),
                    ], className="breakdown-item"),
                    html.Div([
                        html.Span("REGLAS (20%)", className="breakdown-label"),
                        html.Strong(f"{rule:.0f}", className="breakdown-value"),
                        html.Span("Thresholds explicables: valor >2.5x, duracion >2.5x, etc.", className="breakdown-note"),
                    ], className="breakdown-item"),
                    html.Div([
                        html.Span("SCORE TOTAL", className="breakdown-label"),
                        html.Strong(f"{total:.0f}", className="breakdown-value breakdown-total"),
                        html.Span(f"Confianza: {conf:.0f} (soporte de datos)", className="breakdown-note"),
                    ], className="breakdown-item"),
                ],
                className="breakdown-grid",
            ),
            html.Div(
                [
                    html.P(
                        f"Score {total:.0f} = {anomaly:.0f} x 0.45 + {peer:.0f} x 0.35 + {rule:.0f} x 0.20",
                        className="formula-text",
                    ),
                ],
                className="formula-strip",
            ),
        ],
        className="breakdown-section",
    )


def paa_badge(status: str | None) -> Any:
    s = str(status or "none")
    if s == "strong":
        return html.Span("PAA: fuerte", className="score-pill score-pill--typical")
    if s == "weak":
        return html.Span("PAA: debil", className="score-pill score-pill--notable")
    return html.Span("PAA: sin match", className="score-pill score-pill--mild")


def detail_panel(detail: dict, comps: pd.DataFrame) -> list[Any]:
    if detail is None:
        return [empty_state("Sin proceso seleccionado")]

    # Parse explanation into individual reasons
    explanation = str(detail.get("explanation", ""))
    reasons = [r.strip() for r in explanation.split("|") if r.strip()]

    # Build rich reason cards
    reason_cards = _build_reason_cards(detail, reasons)

    # SECOP link
    secop_url = detail.get("process_url") or detail.get("source_url")
    secop_btn = []
    if secop_url and str(secop_url).startswith("http"):
        secop_btn = [html.A(
            "Abrir en SECOP \u2197",
            href=str(secop_url), target="_blank",
            className="secop-link",
        )]

    # Process description
    desc = str(detail.get("description") or detail.get("process_description") or "")
    if len(desc) > 300:
        desc = desc[:297] + "..."

    return [
        # Header with title and key info
        html.Section(
            [
                html.Span("Proceso", className="card-label"),
                html.H2(str(detail.get("process_title") or detail.get("process_key", ""))),
                html.P(desc, className="detail-description"),
                html.Div(
                    [
                        html.Span(str(detail.get("entity_name", "")), className="detail-entity"),
                        html.Span(f" \u00b7 {detail.get('department', '')}", className="detail-dept"),
                        html.Span(f" \u00b7 {detail.get('modality', '')}", className="detail-modality"),
                    ],
                    className="detail-meta",
                ),
                html.Div(secop_btn, className="detail-actions"),
            ],
            className="detail-card detail-card--hero",
        ),
        # Key metrics
        html.Section(
            [
                _value_metric(
                    detail.get("base_price"),
                    "Valor base",
                    detail.get("peer_price_median"),
                    "Mediana de pares",
                ),
                _ratio_metric(
                    detail.get("value_deviation_ratio"),
                    "Desviacion vs pares",
                    "Cuanto mas caro que procesos similares",
                ),
                _simple_metric(detail.get("priority_score"), "Score"),
                _simple_metric(detail.get("confidence_score"), "Confianza"),
            ],
            className="metric-grid detail-metrics",
        ),
        # PAA badge
        html.Div(
            [paa_badge(detail.get("paa_match_status"))],
            className="detail-badges",
        ),
        # Score breakdown
        score_breakdown(detail),
        # Why this process was flagged
        html.Section(
            [
                html.H3("Por que este proceso fue flagged"),
                html.P(
                    "El sistema comparo este proceso con otros similares "
                    "(misma modalidad, categoria y departamento). Estas son "
                    "las senales que encontr:",
                    className="section-intro",
                ),
                *reason_cards,
            ],
            className="reasons-section",
        ),
        # What to review
        html.Section(
            [
                html.H3("Que revisar manualmente"),
                html.Ul([
                    html.Li("Abrir el proceso en SECOP y revisar objeto, valor y estado."),
                    html.Li("Verificar si el valor justifica la desviacion vs pares."),
                    html.Li("Revisar coherencia con PAA si existe planificacion."),
                    html.Li("Consultar comparables para contexto."),
                ]),
            ],
            className="review-checklist",
        ),
        # Comparables
        html.H3("Comparables semanticos", className="comps-heading"),
        comps_table(comps),
    ]


def _value_metric(
    value: Any, label: str,
    reference: Any, ref_label: str,
) -> Any:
    """Show a value with its reference for comparison."""
    v = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    r = pd.to_numeric(pd.Series([reference]), errors="coerce").iloc[0]
    v_text = f"${v:,.0f}" if not pd.isna(v) else "Sin dato"
    r_text = f"${r:,.0f}" if not pd.isna(r) else "Sin dato"
    return html.Div(
        [
            html.Span(label, className="card-label"),
            html.Strong(v_text, className="metric-value-main"),
            html.Span(f"{ref_label}: {r_text}", className="metric-reference"),
        ],
        className="metric-card metric-card--comparison",
    )


def _ratio_metric(
    ratio: Any, label: str, note: str,
) -> Any:
    """Show a deviation ratio with explanation."""
    r = pd.to_numeric(pd.Series([ratio]), errors="coerce").iloc[0]
    if pd.isna(r):
        text = "Sin dato"
        level = "neutral"
    elif r >= 2.5:
        text = f"{r:.1f}x la mediana"
        level = "high"
    elif r >= 1.8:
        text = f"{r:.1f}x la mediana"
        level = "medium"
    else:
        text = f"{r:.1f}x la mediana"
        level = "low"
    return html.Div(
        [
            html.Span(label, className="card-label"),
            html.Strong(text, className=f"metric-ratio metric-ratio--{level}"),
            html.Span(note, className="metric-reference"),
        ],
        className="metric-card metric-card--ratio",
    )


def _simple_metric(value: Any, label: str) -> Any:
    v = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    text = f"{v:.0f}" if not pd.isna(v) else "Sin dato"
    return html.Div(
        [
            html.Span(label, className="card-label"),
            html.Strong(text, className="metric-value-main"),
        ],
        className="metric-card",
    )


def _build_reason_cards(detail: dict, reasons: list[str]) -> list[Any]:
    """Build detailed reason cards with specific data."""
    cards = []
    for reason in reasons:
        if "monto" in reason.lower() or "valor" in reason.lower():
            cards.append(_amount_reason_card(detail, reason))
        elif "duracion" in reason.lower() or "duraci" in reason.lower():
            cards.append(_duration_reason_card(detail, reason))
        elif "paa" in reason.lower() or "plan" in reason.lower():
            cards.append(_paa_reason_card(detail, reason))
        elif "competencia" in reason.lower() or "respuesta" in reason.lower():
            cards.append(_competition_reason_card(detail, reason))
        else:
            cards.append(_generic_reason_card(reason))
    return cards


def _amount_reason_card(detail: dict, reason: str) -> Any:
    price = pd.to_numeric(pd.Series([detail.get("base_price")]), errors="coerce").iloc[0]
    median = pd.to_numeric(pd.Series([detail.get("peer_price_median")]), errors="coerce").iloc[0]
    ratio = pd.to_numeric(pd.Series([detail.get("value_deviation_ratio")]), errors="coerce").iloc[0]
    return html.Div(
        [
            html.Div("MONTO", className="reason-tag"),
            html.Strong(
                f"${price:,.0f}" if not pd.isna(price) else "Sin dato",
                className="reason-value",
            ),
            html.P(
                f"Este proceso tiene un valor {ratio:.1f}x mas alto que la mediana "
                f"de procesos comparables (${median:,.0f}). "
                f"Los procesos comparables son de la misma modalidad, "
                f"categoria y departamento.",
                className="reason-explanation",
            ),
        ],
        className="reason-card",
    )


def _duration_reason_card(detail: dict, reason: str) -> Any:
    duration = pd.to_numeric(pd.Series([detail.get("duration_days")]), errors="coerce").iloc[0]
    median = pd.to_numeric(pd.Series([detail.get("peer_duration_median")]), errors="coerce").iloc[0]
    ratio = pd.to_numeric(pd.Series([detail.get("duration_deviation_ratio")]), errors="coerce").iloc[0]
    return html.Div(
        [
            html.Div("DURACION", className="reason-tag"),
            html.Strong(
                f"{duration:.0f} dias" if not pd.isna(duration) else "Sin dato",
                className="reason-value",
            ),
            html.P(
                f"La duracion es {ratio:.1f}x la mediana de procesos "
                f"similares ({median:.0f} dias).",
                className="reason-explanation",
            ),
        ],
        className="reason-card",
    )


def _paa_reason_card(detail: dict, reason: str) -> Any:
    return html.Div(
        [
            html.Div("PAA", className="reason-tag"),
            html.Strong("Sin match", className="reason-value"),
            html.P(
                "Este proceso no encontro un item correspondiente en el "
                "Plan Anual de Adquisiciones. Esto puede indicar que fue "
                "una compra no planificada, o que la referencia no coincide "
                "con el PAA cargado.",
                className="reason-explanation",
            ),
        ],
        className="reason-card",
    )


def _competition_reason_card(detail: dict, reason: str) -> Any:
    responses = pd.to_numeric(pd.Series([detail.get("response_count")]), errors="coerce").iloc[0]
    return html.Div(
        [
            html.Div("COMPETENCIA", className="reason-tag"),
            html.Strong(
                f"{responses:.0f} respuestas" if not pd.isna(responses) else "Sin dato",
                className="reason-value",
            ),
            html.P(
                "Pocas respuestas al procedimiento pueden indicar baja "
                "competencia entre proveedores.",
                className="reason-explanation",
            ),
        ],
        className="reason-card",
    )


def _generic_reason_card(reason: str) -> Any:
    return html.Div(
        [
            html.Div("SEÑAL", className="reason-tag"),
            html.Strong(reason, className="reason-value"),
        ],
        className="reason-card",
    )


# ── Chart builders ───────────────────────────────────────────


def build_dept_chart(overview: pd.DataFrame) -> go.Figure | None:
    if overview.empty or "department" not in overview:
        return None
    df = overview.copy()
    df = df[df["department"].fillna("").str.strip().ne("Sin departamento PAA")]
    if df.empty:
        return None
    df = df.sort_values("processes", ascending=True)
    fig = px.bar(df, x="processes", y="department", orientation="h", text="processes")
    fig.update_traces(
        marker_color="#103A5C", marker_line_color="#0B1E33", marker_line_width=0,
        texttemplate="%{x:,}", textposition="outside",
        textfont={"family": "Inter, system-ui, sans-serif", "size": 11, "color": "#0B1E33"},
        cliponaxis=False,
    )
    fig.update_layout(
        autosize=False, paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        height=420, margin={"l": 140, "r": 80, "t": 48, "b": 40},
        font={"family": "Inter, system-ui, sans-serif", "color": "#0B1E33", "size": 12},
        title=None, showlegend=False, bargap=0.45,
    )
    fig.update_xaxes(
        tickfont={"color": "#5A6478", "size": 10}, title=None,
        gridcolor="#EEF2F8", zerolinecolor="#E3E8F0", showline=False, ticks="",
    )
    fig.update_yaxes(
        tickfont={"color": "#0B1E33", "size": 13}, title=None,
        gridcolor="rgba(0,0,0,0)", showline=False, ticks="",
    )
    return fig


def build_score_hist(ranking: pd.DataFrame) -> go.Figure | None:
    if ranking.empty or "priority_score" not in ranking:
        return None
    df = ranking[ranking["priority_score"].notna()].copy()
    if df.empty:
        return None
    df["band"] = pd.cut(
        df["priority_score"],
        bins=[0, 20, 40, 70, 85, 100],
        labels=["0-20", "21-40", "41-70", "71-85", "86-100"],
        include_lowest=True,
    )
    counts = df["band"].value_counts().sort_index()
    colors = ["#1F827C", "#103A5C", "#C28832", "#E35A4B", "#8B2020"]
    fig = go.Figure(go.Bar(
        x=counts.index.astype(str), y=counts.values,
        marker_color=colors[: len(counts)],
        text=counts.values, textposition="outside",
        textfont={"family": "Inter, system-ui, sans-serif", "size": 12, "color": "#0B1E33"},
    ))
    fig.update_layout(
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        height=320, margin={"l": 40, "r": 40, "t": 48, "b": 40},
        font={"family": "Inter, system-ui, sans-serif", "color": "#0B1E33", "size": 12},
        title=None, showlegend=False,
    )
    fig.update_xaxes(title=None, gridcolor="rgba(0,0,0,0)", showline=False)
    fig.update_yaxes(
        title=None, gridcolor="#EEF2F8", zerolinecolor="#E3E8F0",
        showline=False, ticks="",
    )
    return fig


def build_paa_pie(ranking: pd.DataFrame) -> go.Figure | None:
    if ranking.empty or "paa_match_status" not in ranking:
        return None
    counts = ranking["paa_match_status"].value_counts()
    labels = []
    values = []
    colors = []
    cmap = {"strong": ("#1F827C", "Fuerte"), "weak": ("#C28832", "Debil"), "none": ("#BFC3C9", "Sin match")}
    for k, v in counts.items():
        color, label = cmap.get(k, ("#BFC3C9", str(k)))
        labels.append(label)
        values.append(v)
        colors.append(color)
    fig = go.Figure(go.Pie(
        labels=labels, values=values, marker_colors=colors,
        textinfo="label+percent", textfont={"size": 13},
        hole=0.4,
    ))
    fig.update_layout(
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        height=320, margin={"l": 20, "r": 20, "t": 40, "b": 20},
        font={"family": "Inter, system-ui, sans-serif", "color": "#0B1E33", "size": 12},
        showlegend=False,
    )
    return fig


def build_entity_bar(ranking: pd.DataFrame) -> go.Figure | None:
    if ranking.empty:
        return None
    top = ranking.groupby("entity_name", dropna=False).agg(
        avg_score=("priority_score", "mean"),
        count=("process_key", "count"),
    ).reset_index().sort_values("avg_score", ascending=False).head(10)
    if top.empty:
        return None
    top = top.sort_values("avg_score", ascending=True)
    fig = go.Figure(go.Bar(
        y=top["entity_name"], x=top["avg_score"], orientation="h",
        marker_color="#103A5C",
        text=top["avg_score"].round(0).astype(int),
        textposition="outside",
        textfont={"family": "Inter, system-ui, sans-serif", "size": 11, "color": "#0B1E33"},
    ))
    fig.update_layout(
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        height=380, margin={"l": 240, "r": 60, "t": 20, "b": 20},
        font={"family": "Inter, system-ui, sans-serif", "color": "#0B1E33", "size": 12},
        title=None, showlegend=False,
    )
    fig.update_xaxes(
        title=None, gridcolor="#EEF2F8", zerolinecolor="#E3E8F0",
        showline=False, ticks="",
    )
    fig.update_yaxes(
        tickfont={"size": 11}, title=None,
        gridcolor="rgba(0,0,0,0)", showline=False, ticks="",
    )
    return fig


def load_agr_enrichment() -> dict:
    """Validation experiment: do AGR-audited entities score higher?"""
    try:
        return svc_json(ANALYTICS_URL, "/analytics/agr-enrichment")
    except Exception:
        return {}


def build_agr_chart(agr: dict) -> go.Figure | None:
    """Grouped bars: high-priority rate, flagged vs baseline."""
    flagged = agr.get("flagged") or {}
    baseline = agr.get("baseline") or {}
    if not flagged or not baseline:
        return None
    cats = ["% en alta prioridad", "Mediana del score"]
    base_vals = [baseline.get("pct_high_priority", 0), baseline.get("median_score", 0)]
    flag_vals = [flagged.get("pct_high_priority", 0), flagged.get("median_score", 0)]
    fig = go.Figure()
    fig.add_bar(
        name="Entidad sin vigilancia AGR", x=cats, y=base_vals,
        marker_color="#BFC3C9",
        text=[f"{v:.2f}" if i == 0 else f"{v:.0f}" for i, v in enumerate(base_vals)],
        textposition="outside",
        textfont={"family": "Inter, system-ui, sans-serif", "size": 12, "color": "#5A6478"},
    )
    fig.add_bar(
        name="Entidad vigilada por AGR", x=cats, y=flag_vals,
        marker_color="#E35A4B",
        text=[f"{v:.2f}" if i == 0 else f"{v:.0f}" for i, v in enumerate(flag_vals)],
        textposition="outside",
        textfont={"family": "Inter, system-ui, sans-serif", "size": 12, "color": "#0B1E33"},
    )
    fig.update_layout(
        barmode="group",
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        height=360, margin={"l": 40, "r": 40, "t": 56, "b": 40},
        font={"family": "Inter, system-ui, sans-serif", "color": "#0B1E33", "size": 12},
        legend={"orientation": "h", "y": 1.12, "x": 0, "font": {"size": 11}},
        title=None,
    )
    fig.update_xaxes(title=None, gridcolor="rgba(0,0,0,0)", showline=False, ticks="")
    fig.update_yaxes(
        title=None, gridcolor="#EEF2F8", zerolinecolor="#E3E8F0",
        showline=False, ticks="",
    )
    return fig


# ── App factory ───────────────────────────────────────────────


def create_app() -> Any:
    if Dash is None:
        return None

    app = Dash(__name__, title="ContratIA Abierta")

    overview = coerce(load_overview(), [
        "processes", "entities", "providers",
        "avg_priority_score", "avg_confidence_score",
    ])
    ranking = coerce(load_ranking(), ["priority_score", "confidence_score"])
    plan = coerce(load_plan(), ["confidence"])
    concentration = coerce(load_concentration(ranking), ["awarded_value"])

    total_proc = int(overview["processes"].sum()) if not overview.empty else 0
    total_ent = int(overview["entities"].sum()) if "entities" in overview else 0
    total_prov = int(overview["providers"].sum()) if "providers" in overview else 0
    # High-priority share over the FULL scored universe (not the truncated
    # top-N ranking, which would inflate it). Weighted by department size.
    if not overview.empty and "pct_high_priority" in overview.columns:
        _n = pd.to_numeric(overview["processes"], errors="coerce").fillna(0)
        _p = pd.to_numeric(overview["pct_high_priority"], errors="coerce").fillna(0)
        high_share = float((_p * _n).sum() / _n.sum() / 100.0) if _n.sum() else 0.0
    else:
        high_share = 0.0
    paa_share = float(plan["confidence"].fillna(0).ge(0.75).mean()) if not plan.empty else 0.0
    top_cand = top_candidate(ranking)
    top_score = top_cand.get("priority_score")
    top_conf = top_cand.get("confidence_score")

    dept_fig = build_dept_chart(overview)
    hist_fig = build_score_hist(ranking)
    paa_fig = build_paa_pie(ranking)
    entity_fig = build_entity_bar(ranking)

    agr = load_agr_enrichment()
    agr_fig = build_agr_chart(agr)
    agr_lift = agr.get("enrichment_lift")

    # Territorial filter options (national universe with territorial lens)
    dept_options = [{"label": "Toda la Orinoquía (Meta + Casanare)", "value": "ALL"}]
    if not ranking.empty and "department" in ranking.columns:
        for d in sorted(x for x in ranking["department"].dropna().unique()):
            dept_options.append({"label": str(d), "value": str(d)})

    if not concentration.empty:
        concentration = concentration.sort_values("awarded_value", ascending=False).head(12)

    # ── Tab 1: Cola semanal ───────────────────────────────
    tab_cola = dcc.Tab(
        label="Cola semanal", className="app-tab",
        selected_className="app-tab app-tab--selected",
        children=[
            html.Section(
                [
                    decision(
                        "Que revisar primero",
                        str(top_cand.get("process_key") or "Sin procesos"),
                        "Primer candidato por score y confianza.",
                    ),
                    decision(
                        "Por que esta priorizado",
                        "Score alto + soporte visible",
                        "La prioridad ordena revision; la confianza indica cobertura.",
                    ),
                    decision(
                        "Accion humana siguiente",
                        action_text(top_score, top_conf),
                        "Abrir SECOP, contrastar fuente, registrar criterio.",
                    ),
                    metric(
                        f"{float(top_score):.1f}" if top_score else "Sin dato",
                        "Score del primer candidato",
                    ),
                    metric(
                        f"{float(top_conf):.1f}" if top_conf else "Sin dato",
                        "Confianza del primer candidato",
                    ),
                ],
                className="decision-strip",
            ),
            html.Section(
                [
                    metric(f"{total_proc:,}", "Procesos"),
                    metric(f"{total_ent:,}", "Entidades"),
                    metric(f"{total_prov:,}", "Proveedores"),
                    metric(f"{high_share:.1%}", "Alerta prioritaria"),
                    metric(f"{paa_share:.1%}", "Match PAA fuerte"),
                ],
                className="metric-grid",
            ),
            html.Div(DISCLAIMER, className="inline-disclaimer"),
            html.Div(
                [
                    html.Span("Cola semanal de revision", className="section-eyebrow"),
                    html.H2("Top 10 procesos a revisar esta semana"),
                    html.P(
                        "Procesos con mayor score de prioridad. Cada uno incluye "
                        "razon principal y accion sugerida.",
                        className="section-desc",
                    ),
                ],
                className="section-header",
            ),
            (
                dash_table.DataTable(
                    id="cola-table",
                    columns=[{"name": c, "id": c} for c in cola_table(ranking).columns],
                    data=cola_table(ranking).to_dict("records"),
                    page_size=10,
                    sort_action="native",
                    style_as_list_view=True,
                    style_data_conditional=[
                        {
                            "if": {"filter_query": "{Score} >= 71"},
                            "backgroundColor": "#FCEAE5", "color": "#E35A4B", "fontWeight": "700",
                        },
                        {
                            "if": {"filter_query": "{Score} >= 41 && {Score} < 71"},
                            "backgroundColor": "#FBF1DC", "color": "#C28832", "fontWeight": "700",
                        },
                        {
                            "if": {"filter_query": "{Score} >= 21 && {Score} < 41"},
                            "backgroundColor": "#E8EFF7", "color": "#103A5C", "fontWeight": "700",
                        },
                        {
                            "if": {"filter_query": "{Score} < 21"},
                            "backgroundColor": "#DDF1EF", "color": "#1F827C", "fontWeight": "700",
                        },
                    ],
                    style_header={
                        "backgroundColor": "#F1F4F9", "color": "#0B1E33",
                        "fontWeight": "700", "textTransform": "uppercase",
                        "fontSize": "11px", "letterSpacing": "0.06em",
                        "borderBottom": "1px solid #CCD3DF",
                    },
                    style_cell={
                        "padding": "10px 14px", "fontSize": "13px",
                        "fontFamily": "Inter, system-ui, sans-serif",
                        "color": "#1F2C40", "border": "0",
                        "borderBottom": "1px solid #E3E8F0",
                    },
                )
                if not ranking.empty
                else empty_state("Sin procesos cargados")
            ),
            html.Div(
                [
                    html.Button("Descargar cola semanal CSV", id="dl-cola-btn"),
                    dcc.Download(id="dl-cola"),
                ],
                className="filter-row",
            ),
            plot_or(overview, dept_fig, "Panorama sin datos"),
        ],
    )

    # ── Tab 2: Ranking ────────────────────────────────────
    tab_ranking = dcc.Tab(
        label="Ranking", className="app-tab",
        selected_className="app-tab app-tab--selected",
        children=[
            html.Div(DISCLAIMER, className="inline-disclaimer"),
            html.Div(
                [
                    html.Label("Score minimo"),
                    dcc.Slider(0, 100, 5, value=20, id="score-filter"),
                    html.Button("Descargar CSV", id="dl-rank-btn"),
                    dcc.Download(id="dl-rank"),
                ],
                className="filter-row",
            ),
            (
                dash_table.DataTable(
                    id="ranking-table",
                    columns=[{"name": c, "id": c} for c in ranking_table(ranking).columns],
                    data=ranking_table(ranking).to_dict("records"),
                    page_size=15,
                    sort_action="native",
                    filter_action="native",
                    style_as_list_view=True,
                    style_data_conditional=[
                        {
                            "if": {"filter_query": "{Score} >= 71"},
                            "backgroundColor": "#FCEAE5", "color": "#E35A4B", "fontWeight": "700",
                        },
                        {
                            "if": {"filter_query": "{Score} >= 41 && {Score} < 71"},
                            "backgroundColor": "#FBF1DC", "color": "#C28832", "fontWeight": "700",
                        },
                        {
                            "if": {"filter_query": "{Score} >= 21 && {Score} < 41"},
                            "backgroundColor": "#E8EFF7", "color": "#103A5C", "fontWeight": "700",
                        },
                        {
                            "if": {"filter_query": "{Score} < 21"},
                            "backgroundColor": "#DDF1EF", "color": "#1F827C", "fontWeight": "700",
                        },
                    ],
                    style_header={
                        "backgroundColor": "#F1F4F9", "color": "#0B1E33",
                        "fontWeight": "700", "textTransform": "uppercase",
                        "fontSize": "11px", "letterSpacing": "0.06em",
                        "borderBottom": "1px solid #CCD3DF",
                    },
                    style_cell={
                        "padding": "10px 14px", "fontSize": "13px",
                        "fontFamily": "Inter, system-ui, sans-serif",
                        "color": "#1F2C40", "border": "0",
                        "borderBottom": "1px solid #E3E8F0",
                    },
                )
                if not ranking.empty
                else empty_state("Ranking sin procesos")
            ),
        ],
    )

    # ── Tab 3: Detalle ────────────────────────────────────
    tab_detail = dcc.Tab(
        label="Detalle", className="app-tab",
        selected_className="app-tab app-tab--selected",
        children=[
            html.Div(DISCLAIMER, className="inline-disclaimer"),
            html.Div(
                [
                    html.Label("Proceso"),
                    dcc.Dropdown(
                        id="detail-dropdown",
                        options=[
                            {
                                "label": f"{r['process_key']} - {r['entity_name']}",
                                "value": r["process_id"],
                            }
                            for r in ranking.head(100).to_dict("records")
                        ],
                        value=(int(ranking.iloc[0]["process_id"]) if not ranking.empty else None),
                    ),
                ],
                className="filter-row",
            ),
            html.Div(id="detail-panel"),
            html.Button("Descargar HTML", id="dl-detail-btn"),
            dcc.Download(id="dl-detail"),
        ],
    )

    # ── Tab 4: Distribucion ───────────────────────────────
    tab_dist = dcc.Tab(
        label="Distribucion", className="app-tab",
        selected_className="app-tab app-tab--selected",
        children=[
            html.Div(
                [
                    html.Span("Distribucion de scores", className="section-eyebrow"),
                    html.H2("Como se distribuyen los procesos por nivel de prioridad"),
                ],
                className="section-header",
            ),
            plot_or(ranking, hist_fig, "Sin datos de ranking"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Span("Cobertura PAA", className="section-eyebrow"),
                            html.H3("Match plan vs ejecucion"),
                            plot_or(ranking, paa_fig, "Sin datos PAA"),
                        ],
                        className="dist-col",
                    ),
                    html.Div(
                        [
                            html.Span("Entidades con mas alertas", className="section-eyebrow"),
                            html.H3("Top 10 por score promedio"),
                            plot_or(ranking, entity_fig, "Sin datos de entidades"),
                        ],
                        className="dist-col",
                    ),
                ],
                className="dist-grid",
            ),
        ],
    )

    # ── Tab 5: Concentracion ──────────────────────────────
    tab_conc = dcc.Tab(
        label="Concentracion", className="app-tab app-tab-secondary",
        selected_className="app-tab app-tab--selected",
        children=[
            html.Div(
                "Contexto secundario: no es ranking de entidades ni acusacion. "
                "Requiere revision humana para interpretar.",
                className="inline-disclaimer",
            ),
            dash_table.DataTable(
                columns=[{"name": c, "id": c} for c in conc_table(concentration).columns],
                data=conc_table(concentration).to_dict("records"),
                page_size=12,
                style_as_list_view=True,
                style_header={
                    "backgroundColor": "#F1F4F9", "color": "#0B1E33",
                    "fontWeight": "700", "textTransform": "uppercase",
                    "fontSize": "11px", "letterSpacing": "0.06em",
                    "borderBottom": "1px solid #CCD3DF",
                },
                style_cell={
                    "padding": "10px 14px", "fontSize": "13px",
                    "fontFamily": "Inter, system-ui, sans-serif",
                    "color": "#1F2C40", "border": "0",
                    "borderBottom": "1px solid #E3E8F0",
                },
            ) if not concentration.empty else empty_state("Sin datos de concentracion"),
        ],
    )

    # ── Tab 6: Metodologia ────────────────────────────────
    tab_method = dcc.Tab(
        label="Metodologia", className="app-tab",
        selected_className="app-tab app-tab--selected",
        children=[
            html.Article(
                [
                    html.H2("Metodologia"),
                    html.P(
                        "El sistema combina IsolationForest para anomalias, "
                        "desviacion frente a pares comparables, reglas explicables "
                        "y confianza de datos para ordenar revision humana."
                    ),
                    html.P(
                        "Score = 45% anomalia + 35% desviacion pares + 20% reglas. "
                        "Confianza mide soporte de datos, no certeza del score."
                    ),
                    html.P(
                        "La salida no acusa personas ni entidades. Solo ayuda a "
                        "decidir que procesos revisar primero."
                    ),
                ],
                className="methodology",
            ),
        ],
    )

    # ── Tab 7: Datos ──────────────────────────────────────
    tab_data = dcc.Tab(
        label="Datos", className="app-tab",
        selected_className="app-tab app-tab--selected",
        children=[
            html.Article(
                [
                    html.H2("Calidad de datos"),
                    html.P("Estado operativo de fuentes y servicios."),
                    dash_table.DataTable(
                        columns=[{"name": c, "id": c} for c in load_quality().columns],
                        data=load_quality().to_dict("records"),
                        page_size=10,
                        style_as_list_view=True,
                    ),
                ],
                className="methodology",
            ),
        ],
    )

    # ── Tab 8: Revision ───────────────────────────────────
    tab_review = dcc.Tab(
        label="Revision humana", className="app-tab",
        selected_className="app-tab app-tab--selected",
        children=[
            html.Article(
                [
                    html.H2("Revision humana"),
                    html.P(
                        "Flujo para mantener, subir o bajar prioridad con notas "
                        "trazables. En presentacion publica opera en modo lectura."
                    ),
                    html.Ul([
                        html.Li("Contrastar SECOP y PAA."),
                        html.Li("Registrar criterio humano."),
                        html.Li("Exportar evidencia para seguimiento."),
                    ]),
                ],
                className="methodology",
            ),
        ],
    )

    # ── Load project context ─────────────────────────────
    project_ctx = load_project_context()

    # ── Tab: Proyecto ────────────────────────────────────
    tab_project = dcc.Tab(
        label="Proyecto", className="app-tab",
        selected_className="app-tab app-tab--selected",
        children=[
            html.Article(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Span("SOBRE EL PROYECTO", className="section-eyebrow"),
                                    html.H2("ContratIA Abierta"),
                                    html.P(
                                        "IA explicable que prioriza revision humana de la "
                                        "contratacion publica colombiana. Convierte miles de "
                                        "procesos SECOP en una cola priorizada y auditable.",
                                        className="project-tagline",
                                    ),
                                ],
                                className="project-header-text",
                            ),
                            html.Div(
                                [
                                    html.Span("DATOS", className="section-eyebrow"),
                                    html.Div(
                                        [
                                            html.Div([
                                                html.Strong(f"{total_proc:,}"),
                                                html.Span("Procesos analizados"),
                                            ], className="project-stat"),
                                            html.Div([
                                                html.Strong("4"),
                                                html.Span("Datasets oficiales"),
                                            ], className="project-stat"),
                                            html.Div([
                                                html.Strong(f"{high_share:.1%}"),
                                                html.Span("Alerta prioritaria"),
                                            ], className="project-stat"),
                                        ],
                                        className="project-stats",
                                    ),
                                ],
                                className="project-header-stats",
                            ),
                        ],
                        className="project-hero",
                    ),
                    *[
                        html.Section(
                            [
                                html.H3(doc.get("title", "")),
                                html.P(doc.get("content", "")),
                            ],
                            className="project-section",
                        )
                        for doc in project_ctx
                    ],
                ],
                className="project-page",
            ),
        ],
    )

    # ── Zona CONFIAR: validacion AGR (titular) ────────────
    lift_text = f"{agr_lift:.1f}x" if agr_lift else "—"
    agr_section = html.Section(
        [
            html.Span("Validación independiente", className="section-eyebrow"),
            html.H2("¿El score se concentra donde el control fiscal ya miró?"),
            html.P(
                "Cruzamos las entidades que la Auditoría General (AGR, dataset "
                "wasc-xi4h) puso bajo vigilancia fiscal contra nuestro score. "
                "El modelo no se entrena con esa etiqueta: es una prueba ciega.",
                className="section-desc",
            ),
            html.Div(
                [
                    metric(lift_text, "Enriquecimiento en tasa de alta prioridad"),
                    metric(
                        f"{(agr.get('flagged') or {}).get('median_score', 0):.0f}",
                        "Mediana score — entidad vigilada",
                    ),
                    metric(
                        f"{(agr.get('baseline') or {}).get('median_score', 0):.0f}",
                        "Mediana score — resto",
                    ),
                    metric(
                        f"{(agr.get('flagged') or {}).get('n_processes', 0):,}",
                        "Procesos en entidades vigiladas",
                    ),
                ],
                className="metric-grid",
            ),
            plot_or(
                pd.DataFrame([1]) if agr_fig else pd.DataFrame(),
                agr_fig, "Sin datos AGR disponibles",
            ),
            html.Div(
                "Auditoría AGR no prueba conducta indebida: mide selección para "
                "revisión fiscal. Que el score enriquezca ese grupo es señal de "
                "que el triage prioriza donde el control humano ya encontró "
                "motivo de revisión, no una etiqueta de culpabilidad.",
                className="inline-disclaimer",
            ),
        ],
        className="confiar-hero",
    )

    zona_decidir = dcc.Tab(
        label="1 · DECIDIR", className="app-tab",
        selected_className="app-tab app-tab--selected",
        children=[
            html.Div(
                [
                    html.Label("Lente territorial"),
                    dcc.Dropdown(
                        id="dept-filter", options=dept_options, value="ALL",
                        clearable=False, className="dept-dropdown",
                    ),
                ],
                className="filter-row filter-row--territorial",
            ),
            *tab_cola.children,
            html.Div(
                [
                    html.Span("Ranking completo", className="section-eyebrow"),
                    html.H2("Explorar toda la cola priorizada"),
                ],
                className="section-header",
            ),
            *tab_ranking.children,
        ],
    )
    zona_entender = dcc.Tab(
        label="2 · ENTENDER", className="app-tab",
        selected_className="app-tab app-tab--selected",
        children=[*tab_detail.children, *tab_review.children],
    )
    zona_confiar = dcc.Tab(
        label="3 · CONFIAR", className="app-tab",
        selected_className="app-tab app-tab--selected",
        children=[
            agr_section,
            *tab_dist.children,
            *tab_method.children,
            *tab_conc.children,
            *tab_data.children,
        ],
    )

    # ── Layout ────────────────────────────────────────────
    app.layout = html.Div([
        html.Header(
            [
                html.Div(
                    "Concurso Datos al Ecosistema 2026  \u00b7  "
                    "Gobernanza y Transparencia",
                    className="app-eyebrow",
                ),
                html.H1("ContratIA Abierta"),
                html.P(
                    "Sistema de priorizacion de revision contractual. "
                    "Ordena procesos SECOP por nivel de riesgo estadistico "
                    "para decidir que revisar primero. No acusa ni prueba "
                    "corrupcion."
                ),
                html.P(DISCLAIMER, className="ethics-note"),
            ],
            className="app-header",
        ),
        dcc.Tabs(
            [tab_project, zona_decidir, zona_entender, zona_confiar],
            parent_className="app-tabs",
            className="app-tabs-container",
        ),
    ])

    # ── Callbacks ─────────────────────────────────────────

    def _by_dept(frame: pd.DataFrame, dept: str | None) -> pd.DataFrame:
        if frame.empty or not dept or dept == "ALL" or "department" not in frame:
            return frame
        return frame[frame["department"] == dept]

    @app.callback(
        Output("ranking-table", "data"),
        Input("score-filter", "value"),
        Input("dept-filter", "value"),
    )
    def filter_ranking(min_s: int, dept: str | None) -> list[dict]:
        return ranking_table(
            pd.DataFrame(filtered_records(_by_dept(ranking, dept), min_s)),
        ).to_dict("records")

    @app.callback(
        Output("cola-table", "data"),
        Input("dept-filter", "value"),
    )
    def filter_cola(dept: str | None) -> list[dict]:
        return cola_table(_by_dept(ranking, dept)).to_dict("records")

    @app.callback(
        Output("dl-rank", "data"),
        Input("dl-rank-btn", "n_clicks"),
        State("score-filter", "value"),
        prevent_initial_call=True,
    )
    def dl_rank(_n: int | None, min_s: int) -> dict | None:
        return {"content": ranking_csv(ranking, min_s), "filename": "contratia-ranking.csv", "type": "text/csv"}

    @app.callback(
        Output("dl-cola", "data"),
        Input("dl-cola-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def dl_cola(_n: int | None) -> dict | None:
        return {"content": cola_table(ranking).to_csv(index=False), "filename": "contratia-cola-semanal.csv", "type": "text/csv"}

    @app.callback(
        Output("detail-panel", "children"),
        Input("detail-dropdown", "value"),
    )
    def render_detail(pid: int | None) -> list[Any]:
        if pid is None or ranking.empty:
            return [empty_state("Sin proceso seleccionado")]
        det = _detail_payload(ranking, pid)
        comps = load_comparables(int(pid))
        return detail_panel(det, comps)

    @app.callback(
        Output("dl-detail", "data"),
        Input("dl-detail-btn", "n_clicks"),
        State("detail-dropdown", "value"),
        prevent_initial_call=True,
    )
    def dl_detail(_n: int | None, pid: int | None) -> dict | None:
        det = _detail_payload(ranking, pid)
        if det is None:
            return None
        pk = str(det.get("process_key", pid))
        return {"content": _report_html(ranking, pid), "filename": f"contratia-{pk}.html", "type": "text/html"}

    return app


def _detail_payload(ranking: pd.DataFrame, pid: int | None) -> dict | None:
    if pid is None or ranking.empty:
        return None
    row = ranking[ranking["process_id"] == pid]
    if row.empty:
        return None
    d = row.iloc[0].to_dict()
    svc = svc_frame(CONTRACTS_URL, f"/processes/{pid}")
    if not svc.empty:
        d = {**d, **svc.iloc[0].to_dict()}
    # Fetch score components from risk service
    try:
        risk = svc_json(RISK_URL, f"/risk/process/{pid}")
        if risk:
            d["anomaly_score"] = risk.get("anomaly_score", 0)
            d["peer_deviation_score"] = risk.get("peer_deviation_score", 0)
            d["rule_score"] = risk.get("rule_score", 0)
            d["paa_match_status"] = risk.get("paa_match_status", d.get("paa_match_status"))
    except Exception:
        pass
    return d


def _report_html(ranking: pd.DataFrame, pid: int | None) -> str:
    det = _detail_payload(ranking, pid)
    if det is None:
        return build_process_report_html(
            {"process_key": "Sin proceso", "reasons": EMPTY_MSG}, [],
        )
    comps = load_comparables(int(pid))
    return build_process_report_html(det, comps.to_dict("records") if not comps.empty else [])


# Backward-compatible alias for tests
process_report_html = _report_html


app = create_app()
server = app.server if app is not None else None

if __name__ == "__main__":
    port = int(os.getenv("DASH_PORT", "8050"))
    debug = os.getenv("DASH_DEBUG", "0").lower() in {"1", "true", "yes"}
    if app is None:
        raise SystemExit("Dash no esta instalado.")
    app.run(debug=debug, host="0.0.0.0", port=port)
