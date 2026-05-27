from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.utils.config import get_settings
from src.utils.reporting import build_process_report_html

PLOTLY_CANVAS = "#f8fafc"
PLOTLY_SURFACE = "#ffffff"
PLOTLY_GRID = "#e2e8f0"
PLOTLY_ZERO = "#cbd5e1"
PLOTLY_ACCENT = "#2f6fbb"
PLOTLY_ACCENT_SOFT = "#dce8f4"
PLOTLY_WARNING = "#d9911f"
PLOTLY_DANGER = "#be3d35"
PLOTLY_SUCCESS = "#2f8f66"

st.set_page_config(page_title="ContratIA Abierta", layout="wide")

APP_DISCLAIMER = "Prioriza revisión humana. No prueba corrupción."
FINAL_DASHBOARD_URL = os.getenv("FINAL_DASHBOARD_URL", "http://localhost:8050")

DESIGN_CSS = """
<style>
:root {
  --ca-canvas: oklch(0.985 0.004 250);
  --ca-surface: oklch(0.998 0.003 250);
  --ca-panel: oklch(0.965 0.006 250);
  --ca-ink: oklch(0.22 0.012 250);
  --ca-muted: oklch(0.48 0.012 250);
  --ca-rule: oklch(0.88 0.008 250);
  --ca-accent: oklch(0.46 0.115 245);
  --ca-accent-soft: oklch(0.95 0.025 245);
  --ca-warning: oklch(0.76 0.105 80);
  --ca-warning-soft: oklch(0.96 0.036 82);
  --ca-success: oklch(0.58 0.08 155);
  --ca-success-soft: oklch(0.95 0.025 155);
  --ca-danger: oklch(0.58 0.13 28);
  --ca-danger-soft: oklch(0.96 0.03 28);
}

.stApp {
  background: var(--ca-canvas);
  color: var(--ca-ink);
}

section[data-testid="stSidebar"] {
  background: oklch(0.955 0.006 250);
  border-right: 1px solid var(--ca-rule);
}

section[data-testid="stSidebar"],
section[data-testid="stSidebar"] *,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span {
  color: var(--ca-ink) !important;
}

section[data-testid="stSidebar"] [role="radiogroup"] label {
  background: transparent;
  opacity: 1;
}

.main .block-container {
  max-width: 1280px;
  padding-top: 2rem;
  padding-bottom: 3rem;
}

h1, h2, h3 {
  letter-spacing: 0;
}

h1 {
  font-size: 2rem;
  line-height: 1.15;
}

h2 {
  font-size: 1.28rem;
}

h3 {
  font-size: 1.06rem;
}

.ca-shell {
  border: 1px solid var(--ca-rule);
  border-radius: 8px;
  background: var(--ca-surface);
  padding: 22px 24px;
  margin-bottom: 18px;
}

.ca-eyebrow {
  color: var(--ca-accent);
  font-size: 0.76rem;
  font-weight: 760;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.ca-title {
  color: var(--ca-ink);
  font-size: 2rem;
  font-weight: 780;
  line-height: 1.14;
  margin: 0;
}

.ca-subtitle {
  color: var(--ca-muted);
  max-width: 72ch;
  margin: 8px 0 0;
}

.ca-disclaimer,
.ca-callout,
.ca-empty,
.ca-decision,
.ca-fact {
  border: 1px solid var(--ca-rule);
  border-radius: 8px;
}

.ca-disclaimer {
  background: var(--ca-accent-soft);
  color: var(--ca-ink);
  display: inline-flex;
  gap: 8px;
  align-items: center;
  padding: 8px 11px;
  margin-top: 14px;
  font-size: 0.92rem;
  font-weight: 650;
}

.ca-empty {
  background: var(--ca-surface);
  padding: 24px;
}

.ca-empty h2 {
  margin: 0 0 8px;
}

.ca-empty p {
  color: var(--ca-muted);
  margin: 0 0 16px;
  max-width: 72ch;
}

.ca-empty-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 8px;
  margin: 16px 0;
}

.ca-missing-file {
  background: var(--ca-panel);
  border: 1px solid var(--ca-rule);
  border-radius: 8px;
  padding: 9px 11px;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.76rem;
  color: var(--ca-ink);
  overflow-wrap: anywhere;
}

.ca-decision-grid {
  display: grid;
  grid-template-columns: minmax(220px, 1.1fr) minmax(260px, 1.35fr) minmax(260px, 1.4fr);
  gap: 12px;
  margin: 18px 0;
}

.ca-decision,
.ca-fact {
  background: var(--ca-surface);
  padding: 15px 16px;
}

.ca-label {
  color: var(--ca-muted);
  display: block;
  font-size: 0.78rem;
  font-weight: 720;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  margin-bottom: 7px;
}

.ca-value {
  color: var(--ca-ink);
  font-size: 1.2rem;
  font-weight: 760;
  line-height: 1.25;
}

.ca-note {
  color: var(--ca-muted);
  display: block;
  font-size: 0.92rem;
  line-height: 1.3;
  margin-top: 4px;
}

.ca-metric-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(150px, 1fr));
  gap: 12px;
  margin: 12px 0 20px;
}

.ca-fact strong {
  display: block;
  font-size: 1.35rem;
  line-height: 1.2;
}

.ca-section-title {
  margin: 24px 0 10px;
}

.ca-section-title p {
  color: var(--ca-muted);
  margin: 4px 0 0;
}

.ca-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 10px 0 14px;
}

.ca-badge {
  border: 1px solid var(--ca-rule);
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 9px;
  font-size: 0.78rem;
  font-weight: 700;
}

.ca-badge-high {
  background: var(--ca-danger-soft);
  color: var(--ca-danger);
}

.ca-badge-medium {
  background: var(--ca-warning-soft);
  color: oklch(0.43 0.085 75);
}

.ca-badge-low {
  background: var(--ca-success-soft);
  color: var(--ca-success);
}

.ca-checklist {
  background: var(--ca-panel);
  border: 1px solid var(--ca-rule);
  border-radius: 8px;
  padding: 14px 16px;
}

.ca-checklist li {
  margin-bottom: 6px;
}

div[data-testid="stMetric"] {
  background: var(--ca-surface);
  border: 1px solid var(--ca-rule);
  border-radius: 8px;
  padding: 13px 14px;
}

div[data-testid="stMetricLabel"] p {
  color: var(--ca-muted);
  font-size: 0.8rem;
  font-weight: 700;
}

div[data-testid="stMetricLabel"],
div[data-testid="stMetricLabel"] *,
div[data-testid="stMetricValue"],
div[data-testid="stMetricValue"] * {
  color: var(--ca-ink) !important;
  opacity: 1 !important;
}

div[data-testid="stMetricValue"] {
  color: var(--ca-ink);
}

.stDataFrame {
  border: 1px solid var(--ca-rule);
  border-radius: 8px;
  overflow: hidden;
}

.stDownloadButton button,
.stButton button {
  border-radius: 8px;
  border: 1px solid var(--ca-accent);
  background: var(--ca-accent);
  color: oklch(0.985 0.004 250);
  font-weight: 700;
}

@media (max-width: 900px) {
  .main .block-container {
    padding-left: 1rem;
    padding-right: 1rem;
  }

  .ca-decision-grid,
  .ca-metric-row {
    grid-template-columns: 1fr;
  }
}
</style>
"""


@st.cache_data
def load_assets() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    settings = get_settings()
    return (
        pd.read_parquet(settings.marts_dir / "overview.parquet"),
        pd.read_parquet(settings.marts_dir / "ranking.parquet"),
        pd.read_parquet(settings.marts_dir / "process_detail.parquet"),
        pd.read_parquet(settings.marts_dir / "comparables.parquet"),
    )


def inject_design_system() -> None:
    st.markdown(DESIGN_CSS, unsafe_allow_html=True)


def relative_path(path: Path) -> str:
    settings = get_settings()
    try:
        return str(path.relative_to(settings.root_dir))
    except ValueError:
        return path.name


def app_header(title: str, subtitle: str, eyebrow: str = "ContratIA Abierta") -> None:
    st.markdown(
        f"""
        <section class="ca-shell">
          <div class="ca-eyebrow">{eyebrow}</div>
          <h1 class="ca-title">{title}</h1>
          <p class="ca-subtitle">{subtitle}</p>
          <div class="ca-disclaimer">{APP_DISCLAIMER}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def section_title(title: str, description: str) -> None:
    st.markdown(
        f"""
        <div class="ca-section-title">
          <h2>{title}</h2>
          <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def priority_badge(score: float | int | None, label: object | None = None) -> str:
    if score is None or pd.isna(score):
        return '<span class="ca-badge ca-badge-medium">Prioridad sin dato</span>'
    score_value = float(score)
    text = str(label or "Prioridad")
    if score_value >= 70:
        badge_class = "ca-badge-high"
    elif score_value >= 40:
        badge_class = "ca-badge-medium"
    else:
        badge_class = "ca-badge-low"
    return f'<span class="ca-badge {badge_class}">{text}: {score_value:.0f}</span>'


def confidence_badge(score: float | int | None, label: object | None = None) -> str:
    if score is None or pd.isna(score):
        return '<span class="ca-badge ca-badge-medium">Confianza sin dato</span>'
    score_value = float(score)
    text = str(label or "Confianza")
    if score_value >= 75:
        badge_class = "ca-badge-low"
    elif score_value >= 55:
        badge_class = "ca-badge-medium"
    else:
        badge_class = "ca-badge-high"
    return f'<span class="ca-badge {badge_class}">{text}: {score_value:.0f}</span>'


def decision_text(priority_score: float | int | None, confidence_score: float | int | None) -> str:
    if priority_score is None or pd.isna(priority_score):
        return "Validar datos antes de priorizar."
    priority = float(priority_score)
    confidence = (
        0
        if confidence_score is None or pd.isna(confidence_score)
        else float(confidence_score)
    )
    if priority >= 70 and confidence >= 60:
        return "Abrir revisión prioritaria y contrastar SECOP."
    if priority >= 70:
        return "Validar soporte de datos antes de escalar."
    if priority >= 40:
        return "Mantener en observación."
    return "Revisar solo por contexto externo."


def style_figure(fig):
    fig.update_layout(
        paper_bgcolor=PLOTLY_CANVAS,
        plot_bgcolor=PLOTLY_SURFACE,
        font={"family": "system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"},
        title={"font": {"size": 16}},
        margin={"l": 20, "r": 20, "t": 54, "b": 40},
        coloraxis_colorbar={"title": ""},
    )
    fig.update_xaxes(gridcolor=PLOTLY_GRID, zerolinecolor=PLOTLY_ZERO)
    fig.update_yaxes(gridcolor=PLOTLY_GRID, zerolinecolor=PLOTLY_ZERO)
    return fig


def show_missing_data(paths: list[Path]) -> None:
    missing = [path for path in paths if not path.exists()]
    app_header(
        "Preparar datos del producto",
        "La interfaz está lista, pero faltan tablas de salida para construir la cola de revisión.",
        eyebrow="Estado de datos",
    )
    files = "\n".join(
        f'<div class="ca-missing-file">{relative_path(path)}</div>' for path in missing
    )
    st.markdown(
        f"""
        <section class="ca-empty">
          <h2>Artefactos pendientes</h2>
          <p>
            La pantalla pública no debe mostrar rutas locales ni fallar de forma técnica.
            Estos archivos se generan al correr extracción, transformación y scoring.
          </p>
          <div class="ca-empty-list">{files}</div>
          <div class="ca-checklist">
            <strong>Después de prepararlos podrás revisar:</strong>
            <ul>
              <li>Ranking priorizado de procesos.</li>
              <li>Ficha ejecutiva con razones, PAA y comparables.</li>
              <li>Reporte HTML para revisión humana.</li>
            </ul>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Comandos de preparación local")
    st.code(
        "uv run --python 3.11 python -m src.extract.secop_api\n"
        "uv run --python 3.11 python -m src.transform.build_process_master\n"
        "uv run --python 3.11 python -m src.scoring.score_processes"
    )


def final_dashboard_notice() -> None:
    app_header(
        "Dashboard final de Ingeniería de Datos",
        "La sustentación oficial usa Dash, PostgreSQL, MongoDB y microservicios.",
        eyebrow="Transparencia360",
    )
    st.markdown(
        f"""
        <section class="ca-empty">
          <h2>Usa la ruta oficial full-stack</h2>
          <p>
            Esta pantalla Streamlit es el modo lean/offline legado. Para la presentación
            del proyecto de Ingeniería de Datos no debe usarse como dashboard principal.
          </p>
          <div class="ca-checklist">
            <strong>Dashboard final:</strong>
            <ul>
              <li>PostgreSQL con procesos SECOP cargados.</li>
              <li>MongoDB con colecciones de soporte.</li>
              <li>Microservicios FastAPI de contratos, riesgo y analítica.</li>
              <li>Dash con ranking, detalle, comparables y export HTML.</li>
            </ul>
          </div>
          <p>
            <a href="{FINAL_DASHBOARD_URL}" target="_self">Abrir dashboard final</a>
          </p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.link_button("Abrir dashboard final", FINAL_DASHBOARD_URL)
    st.caption(
        "Para usar el modo Streamlit legado, inicia con STREAMLIT_LEGACY_MODE=1. "
        "No es la ruta recomendada para la sustentación."
    )


def format_currency(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "No disponible"
    return "$" + f"{float(value):,.0f}".replace(",", ".")


def display_ranking(frame: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "process_reference",
        "entity_name",
        "department",
        "modality",
        "base_price",
        "priority_score",
        "priority_band",
        "confidence_score",
        "confidence_band",
        "paa_match_status",
        "reasons",
    ]
    available = [column for column in columns if column in frame.columns]
    display = frame[available].copy()
    if "base_price" in display:
        display["base_price"] = display["base_price"].apply(format_currency)
    if "priority_score" in display:
        display["priority_score"] = display["priority_score"].round(0).astype("Int64")
    if "confidence_score" in display:
        display["confidence_score"] = display["confidence_score"].round(0).astype("Int64")
    return display.rename(
        columns={
            "process_reference": "Referencia",
            "entity_name": "Entidad",
            "department": "Departamento",
            "modality": "Modalidad",
            "base_price": "Valor base",
            "priority_score": "Score",
            "priority_band": "Banda",
            "confidence_score": "Confianza",
            "confidence_band": "Soporte",
            "paa_match_status": "PAA",
            "reasons": "Razones",
        }
    )


def filter_ranking(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    if "process_year" not in frame.columns:
        if "year" in frame.columns:
            frame["process_year"] = frame["year"]
        else:
            frame["process_year"] = pd.Timestamp.today().year

    periods = sorted([int(year) for year in frame["process_year"].dropna().unique().tolist()])
    departments = sorted(frame["department"].dropna().unique().tolist())
    entities = sorted(frame["entity_name"].dropna().unique().tolist())
    modalities = sorted(frame["modality"].dropna().unique().tolist())
    bands = sorted(frame["priority_band"].dropna().unique().tolist())

    selected_years = st.sidebar.multiselect("Periodo", options=periods, default=periods)
    selected_departments = st.sidebar.multiselect(
        "Departamento",
        options=departments,
        default=[d for d in departments if d in get_settings().scope_departments] or departments,
    )
    selected_entities = st.sidebar.multiselect("Entidad", options=entities, default=entities)
    selected_modalities = st.sidebar.multiselect(
        "Modalidad",
        options=modalities,
        default=modalities,
    )
    selected_bands = st.sidebar.multiselect("Banda", options=bands, default=bands)
    min_confidence = st.sidebar.slider("Confianza mínima", min_value=0, max_value=100, value=40)

    filtered = frame[
        frame["process_year"].isin(selected_years)
        & frame["department"].isin(selected_departments)
        & frame["entity_name"].isin(selected_entities)
        & frame["modality"].isin(selected_modalities)
        & frame["priority_band"].isin(selected_bands)
        & frame["confidence_score"].fillna(0).ge(min_confidence)
    ].copy()
    return filtered.sort_values(["priority_score", "confidence_score"], ascending=[False, False])


def panorama_page(overview: pd.DataFrame, ranking: pd.DataFrame) -> None:
    app_header(
        "Cola de revisión contractual",
        "Convierte procesos SECOP en una lista ordenada para decidir qué revisar primero.",
    )
    top = (
        ranking.sort_values(["priority_score", "confidence_score"], ascending=[False, False])
        .head(1)
        .to_dict("records")
    )
    top_candidate = top[0] if top else {}
    top_reference = top_candidate.get("process_reference") or top_candidate.get("process_key")
    top_score = top_candidate.get("priority_score")
    top_confidence = top_candidate.get("confidence_score")
    st.markdown(
        f"""
        <section class="ca-decision-grid">
          <div class="ca-decision">
            <span class="ca-label">Qué revisar primero</span>
            <div class="ca-value">{top_reference or "Sin procesos cargados"}</div>
            <span class="ca-note">Primer candidato por score y soporte de datos.</span>
          </div>
          <div class="ca-decision">
            <span class="ca-label">Por qué está priorizado</span>
            <div class="ca-value">Score alto + confianza visible</div>
            <span class="ca-note">
              La prioridad ordena revisión; la confianza indica cobertura.
            </span>
          </div>
          <div class="ca-decision">
            <span class="ca-label">Acción humana siguiente</span>
            <div class="ca-value">{decision_text(top_score, top_confidence)}</div>
            <span class="ca-note">Abrir detalle, contrastar fuente y registrar criterio.</span>
          </div>
        </section>
        <div class="ca-badges">
          {priority_badge(top_score, top_candidate.get("priority_band"))}
          {confidence_badge(top_confidence, top_candidate.get("confidence_band"))}
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Procesos analizados", f"{len(ranking):,}".replace(",", "."))
    c2.metric("% alta prioridad", f"{(ranking['priority_score'] >= 70).mean():.1%}")
    c3.metric("Entidades revisables", f"{ranking['entity_name'].nunique():,}".replace(",", "."))
    c4.metric("% match PAA fuerte", f"{(ranking['paa_match_confidence'] >= 0.75).mean():.1%}")

    section_title(
        "Panorama territorial",
        "Usa volumen, prioridad y cobertura PAA para orientar una revisión acotada.",
    )
    left, right = st.columns([1.2, 1])
    department_chart = px.bar(
        overview,
        x="department",
        y="avg_priority_score",
        color="high_priority_share",
        hover_data=["processes_analyzed", "paa_match_share"],
        title="Panorama agregado por departamento",
        color_continuous_scale=[PLOTLY_ACCENT_SOFT, PLOTLY_ACCENT],
    )
    left.plotly_chart(style_figure(department_chart), use_container_width=True)

    hist = px.histogram(
        ranking,
        x="priority_score",
        nbins=20,
        color="priority_band",
        title="Distribución del score de prioridad",
        color_discrete_sequence=[
            PLOTLY_ACCENT,
            PLOTLY_WARNING,
            PLOTLY_DANGER,
            PLOTLY_SUCCESS,
        ],
    )
    right.plotly_chart(style_figure(hist), use_container_width=True)

    top_entities = (
        ranking.groupby("entity_name", dropna=False)
        .agg(
            avg_priority_score=("priority_score", "mean"),
            alerts=("process_key", "count"),
        )
        .reset_index()
        .sort_values(["avg_priority_score", "alerts"], ascending=[False, False])
        .head(10)
    )
    section_title(
        "Entidades para revisión inicial",
        "Promedio alto no acusa a una entidad; ayuda a ordenar capacidad humana limitada.",
    )
    st.dataframe(
        top_entities.rename(
            columns={
                "entity_name": "Entidad",
                "avg_priority_score": "Score promedio",
                "alerts": "Procesos",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


def detail_block(detail: pd.Series, comparables: pd.DataFrame) -> None:
    st.markdown(
        f"""
        <div class="ca-badges">
          {priority_badge(detail.get("priority_score"), detail.get("priority_band"))}
          {confidence_badge(detail.get("confidence_score"), detail.get("confidence_band"))}
          <span class="ca-badge ca-badge-medium">
            PAA: {detail.get("paa_match_status", "sin dato")}
          </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Score", int(detail["priority_score"]))
    c2.metric("Banda", detail["priority_band"])
    c3.metric("Confianza", f"{int(detail['confidence_score'])} ({detail['confidence_band']})")
    c4.metric("Valor base", format_currency(detail["base_price"]))

    left, right = st.columns([1.15, 1])
    with left:
        st.markdown("### Evidencia del proceso")
        st.markdown(f"**Entidad:** {detail['entity_name']}")
        st.markdown(f"**Referencia:** {detail['process_reference']}")
        st.markdown(f"**Modalidad:** {detail['modality']}")
        st.markdown(f"**Razones:** {detail['reasons']}")
        st.markdown(
            f"**Plan vs ejecución:** "
            f"{detail['paa_match_status']} ({detail['paa_match_method']})"
        )
        if pd.notna(detail.get("paa_text")) and detail.get("paa_text"):
            st.markdown(f"**Mejor match PAA:** {detail['paa_text']}")
        st.markdown(
            f"**Contexto visible:** {detail.get('control_badge', 'No disponible en esta carga')}"
        )
    with right:
        st.markdown(
            """
            <div class="ca-checklist">
              <strong>Qué revisar manualmente</strong>
              <ul>
                <li>Objeto, cuantía, modalidad y estado en SECOP.</li>
                <li>Coherencia entre proceso y PAA.</li>
                <li>Comparables disponibles y diferencias de valor.</li>
                <li>Soporte documental antes de escalar la revisión.</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
    if detail.get("process_url"):
        st.link_button("Abrir fuente SECOP", str(detail["process_url"]))

    section_title(
        "Comparables semánticos",
        "Procesos cercanos para contrastar valor, modalidad y objeto. No son prueba automática.",
    )
    if comparables.empty:
        st.markdown(
            """
            <section class="ca-empty">
              <h2>Sin comparables disponibles</h2>
              <p>
                La ficha sigue siendo revisable, pero este proceso no tiene pares
                suficientes en la carga actual.
              </p>
            </section>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.dataframe(comparables, use_container_width=True, hide_index=True)

    report_html = build_process_report_html(
        {**detail.to_dict(), "reasons_text": detail.get("reasons", "")},
        comparables.to_dict(orient="records"),
    )
    st.download_button(
        "Descargar reporte HTML",
        data=report_html,
        file_name=f"contratia-{detail['process_key']}.html",
        mime="text/html",
    )


def ranking_page(
    ranking: pd.DataFrame,
    detail_frame: pd.DataFrame,
    comparables: pd.DataFrame,
) -> None:
    app_header(
        "Ranking de revisión",
        "Filtra la cola, exporta candidatos y abre una ficha ejecutiva antes de decidir.",
    )
    filtered = filter_ranking(ranking)
    st.download_button(
        "Exportar ranking filtrado",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="contratia-ranking-filtrado.csv",
        mime="text/csv",
    )
    if filtered.empty:
        st.markdown(
            """
            <section class="ca-empty">
              <h2>Sin procesos para los filtros actuales</h2>
              <p>
                Ajusta periodo, departamento, modalidad o confianza mínima para
                reconstruir la cola.
              </p>
            </section>
            """,
            unsafe_allow_html=True,
        )
        return
    st.dataframe(display_ranking(filtered), use_container_width=True, hide_index=True)

    process_key = st.selectbox(
        "Abrir ficha ejecutiva",
        options=filtered["process_key"].tolist(),
        format_func=lambda key: filtered.set_index("process_key").loc[key, "process_reference"],
    )
    selected_row = filtered.set_index("process_key").loc[process_key]
    selected_action = decision_text(
        selected_row.get("priority_score"),
        selected_row.get("confidence_score"),
    )
    st.markdown(
        f"""
        <section class="ca-decision">
          <span class="ca-label">Proceso seleccionado</span>
          <div class="ca-value">{selected_row["process_reference"]}</div>
          <span class="ca-note">{selected_action}</span>
        </section>
        """,
        unsafe_allow_html=True,
    )
    detail = detail_frame.set_index("process_key").loc[process_key]
    process_comparables = comparables[comparables["process_key"] == process_key].copy()
    detail_block(detail, process_comparables)


def detalle_page(detail_frame: pd.DataFrame, comparables: pd.DataFrame) -> None:
    app_header(
        "Ficha ejecutiva",
        "Reúne score, confianza, PAA, razones y comparables para revisión manual.",
    )
    process_key = st.selectbox(
        "Proceso",
        options=detail_frame.sort_values("priority_score", ascending=False)["process_key"].tolist(),
        format_func=lambda key: detail_frame.set_index("process_key").loc[key, "process_reference"],
    )
    detail = detail_frame.set_index("process_key").loc[process_key]
    process_comparables = comparables[comparables["process_key"] == process_key].copy()
    detail_block(detail, process_comparables)


def methodology_page() -> None:
    app_header(
        "Metodología",
        "Cómo se construye la prioridad y qué límites debe respetar el revisor.",
    )
    st.markdown(
        """
- **Tabla canónica:** SECOP II (`p6dx-8zbt`)
- **Enriquecimiento opcional:** SECOP Integrado (`rpmr-utcd`)
  solo con enlace de alta confianza
- **Plan vs ejecución:** PAA (`9sue-ezhx`) visible siempre
  y sujeto a compuerta para entrar al score
- **Contexto visible:** `wasc-xi4h`
- **Score provisional:** anomalía estructurada,
  desviación frente a pares y reglas explícitas
- **Confianza:** visible en ranking y detalle
"""
    )


def main() -> None:
    inject_design_system()
    if os.getenv("STREAMLIT_LEGACY_MODE", "0").lower() not in {"1", "true", "yes"}:
        final_dashboard_notice()
        return
    settings = get_settings()
    required = [
        settings.marts_dir / "overview.parquet",
        settings.marts_dir / "ranking.parquet",
        settings.marts_dir / "process_detail.parquet",
        settings.marts_dir / "comparables.parquet",
    ]
    if any(not path.exists() for path in required):
        show_missing_data(required)
        return

    overview, ranking, detail_frame, comparables = load_assets()
    page = st.sidebar.radio("Sección", ["Panorama", "Ranking", "Detalle", "Metodología"])
    if page == "Panorama":
        panorama_page(overview, ranking)
    elif page == "Ranking":
        ranking_page(ranking, detail_frame, comparables)
    elif page == "Detalle":
        detalle_page(detail_frame, comparables)
    else:
        methodology_page()


if __name__ == "__main__":
    main()
