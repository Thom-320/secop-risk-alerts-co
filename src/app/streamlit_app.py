from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.utils.config import get_settings
from src.utils.reporting import build_process_report_html

st.set_page_config(page_title="ContratIA Abierta", layout="wide")


@st.cache_data
def load_assets() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    settings = get_settings()
    return (
        pd.read_parquet(settings.marts_dir / "overview.parquet"),
        pd.read_parquet(settings.marts_dir / "ranking.parquet"),
        pd.read_parquet(settings.marts_dir / "process_detail.parquet"),
        pd.read_parquet(settings.marts_dir / "comparables.parquet"),
    )


def show_missing_data(paths: list[Path]) -> None:
    st.error("Faltan artefactos del MVP.")
    for path in paths:
        st.write(f"- {path}")
    st.code(
        "uv run --python 3.11 python -m src.extract.secop_api\n"
        "uv run --python 3.11 python -m src.transform.build_process_master\n"
        "uv run --python 3.11 python -m src.scoring.score_processes"
    )


def format_currency(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "No disponible"
    return "$" + f"{float(value):,.0f}".replace(",", ".")


def filter_ranking(frame: pd.DataFrame) -> pd.DataFrame:
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
    st.title("ContratIA Abierta")
    st.caption("Alertas explicables para priorizar revisión contractual.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Procesos analizados", f"{len(ranking):,}".replace(",", "."))
    c2.metric("% alta prioridad", f"{(ranking['priority_score'] >= 70).mean():.1%}")
    c3.metric("Entidades con alertas", f"{ranking['entity_name'].nunique():,}".replace(",", "."))
    c4.metric("% match PAA fuerte", f"{(ranking['paa_match_confidence'] >= 0.75).mean():.1%}")

    left, right = st.columns([1.2, 1])
    department_chart = px.bar(
        overview,
        x="department",
        y="avg_priority_score",
        color="high_priority_share",
        hover_data=["processes_analyzed", "paa_match_share"],
        title="Panorama agregado por departamento",
    )
    left.plotly_chart(department_chart, use_container_width=True)

    hist = px.histogram(
        ranking,
        x="priority_score",
        nbins=20,
        color="priority_band",
        title="Distribución del score de prioridad",
    )
    right.plotly_chart(hist, use_container_width=True)

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
    st.subheader("Top 10 entidades con mayor prioridad promedio")
    st.dataframe(top_entities, use_container_width=True, hide_index=True)
    st.warning(
        "La plataforma prioriza revisión humana. No prueba corrupción ni reemplaza auditoría."
    )


def detail_block(detail: pd.Series, comparables: pd.DataFrame) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Score", int(detail["priority_score"]))
    c2.metric("Banda", detail["priority_band"])
    c3.metric("Confianza", f"{int(detail['confidence_score'])} ({detail['confidence_band']})")
    c4.metric("Valor base", format_currency(detail["base_price"]))

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
    st.markdown(f"**Badge contextual:** {detail['control_badge']}")
    if detail.get("process_url"):
        st.markdown(f"[Abrir proceso en SECOP]({detail['process_url']})")

    st.subheader("Comparables semánticos")
    if comparables.empty:
        st.info("Sin comparables disponibles para este proceso.")
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
    st.title("Ranking de alertas")
    filtered = filter_ranking(ranking)
    st.dataframe(
        filtered[
            [
                "process_key",
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
        ],
        use_container_width=True,
        hide_index=True,
    )
    if filtered.empty:
        st.info("No hay procesos en el filtro actual.")
        return

    process_key = st.selectbox(
        "Abrir detalle",
        options=filtered["process_key"].tolist(),
        format_func=lambda key: filtered.set_index("process_key").loc[key, "process_reference"],
    )
    detail = detail_frame.set_index("process_key").loc[process_key]
    process_comparables = comparables[comparables["process_key"] == process_key].copy()
    detail_block(detail, process_comparables)


def detalle_page(detail_frame: pd.DataFrame, comparables: pd.DataFrame) -> None:
    st.title("Detalle de proceso")
    process_key = st.selectbox(
        "Proceso",
        options=detail_frame.sort_values("priority_score", ascending=False)["process_key"].tolist(),
        format_func=lambda key: detail_frame.set_index("process_key").loc[key, "process_reference"],
    )
    detail = detail_frame.set_index("process_key").loc[process_key]
    process_comparables = comparables[comparables["process_key"] == process_key].copy()
    detail_block(detail, process_comparables)


def methodology_page() -> None:
    st.title("Metodología del MVP")
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
