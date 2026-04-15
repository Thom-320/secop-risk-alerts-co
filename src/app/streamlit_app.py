from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.utils.config import get_settings

st.set_page_config(page_title="Alertas Priorizadas SECOP II", layout="wide")


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    settings = get_settings()
    contracts_path = settings.marts_dir / "contracts_scored.parquet"
    providers_path = settings.marts_dir / "providers_scored.parquet"
    return pd.read_parquet(contracts_path), pd.read_parquet(providers_path)


def show_missing_data(paths: list[Path]) -> None:
    st.error("Faltan artefactos del pipeline.")
    for path in paths:
        st.write(f"- {path}")
    st.code(
        "uv run --python 3.11 python -m src.extract.secop_api\n"
        "uv run --python 3.11 python -m src.transform.build_base_contracts\n"
        "uv run --python 3.11 python -m src.scoring.score_contracts"
    )


def home_page(contracts: pd.DataFrame, providers: pd.DataFrame) -> None:
    st.title("Sistema de Alertas Priorizadas de Riesgo Contractual")
    st.caption("Demo MVP para priorizar revisión humana de contratación pública.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Contratos evaluados", f"{len(contracts):,}".replace(",", "."))
    c2.metric("Proveedores evaluados", f"{len(providers):,}".replace(",", "."))
    c3.metric("Score promedio", round(float(contracts['score_final'].mean()), 1))
    c4.metric("Contratos alto/crítico", int((contracts["score_final"] >= 50).sum()))

    top_contracts = contracts.nlargest(10, "score_final")[
        ["id_contrato", "nombre_entidad", "proveedor_adjudicado", "score_final", "risk_level"]
    ]
    top_providers = providers.nlargest(10, "score_final")[
        ["proveedor_adjudicado", "nombre_entidad", "score_final", "risk_level"]
    ]

    chart = px.histogram(
        contracts,
        x="score_final",
        nbins=20,
        title="Distribución del score final de contratos",
    )
    chart.update_layout(height=320)
    st.plotly_chart(chart, use_container_width=True)

    left, right = st.columns(2)
    left.subheader("Top contratos priorizados")
    left.dataframe(top_contracts, use_container_width=True, hide_index=True)
    right.subheader("Top proveedores priorizados")
    right.dataframe(top_providers, use_container_width=True, hide_index=True)

    st.warning(
        "La app muestra alertas de riesgo para priorización de revisión. "
        "No constituye prueba de corrupción ni reemplaza auditoría."
    )


def contracts_page(contracts: pd.DataFrame) -> None:
    st.title("Contratos")
    entity_options = sorted(contracts["nombre_entidad"].dropna().unique().tolist())
    supplier_query = st.text_input("Filtrar proveedor", value="")
    selected_entities = st.multiselect(
        "Entidad",
        options=entity_options,
        default=entity_options,
    )
    min_score, max_score = st.slider("Rango de score", 0, 100, (0, 100))

    filtered = contracts[
        contracts["nombre_entidad"].isin(selected_entities)
        & contracts["score_final"].between(min_score, max_score)
    ].copy()
    if supplier_query:
        filtered = filtered[
            filtered["proveedor_adjudicado"].fillna("").str.contains(supplier_query, case=False)
        ]

    bar = px.bar(
        filtered.nlargest(15, "score_final"),
        x="score_final",
        y="id_contrato",
        color="nombre_entidad",
        orientation="h",
        title="Top 15 contratos por score",
    )
    bar.update_layout(height=500, yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(bar, use_container_width=True)

    st.dataframe(
        filtered[
            [
                "id_contrato",
                "nombre_entidad",
                "proveedor_adjudicado",
                "valor_del_contrato",
                "score_final",
                "risk_level",
            ]
        ].sort_values("score_final", ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    if filtered.empty:
        st.info("No hay contratos en el filtro actual.")
        return

    detail_id = st.selectbox(
        "Ficha de detalle",
        options=filtered.sort_values("score_final", ascending=False)["id_contrato"].tolist(),
    )
    row = filtered.set_index("id_contrato").loc[detail_id]
    c1, c2, c3 = st.columns(3)
    c1.metric("Score final", int(row["score_final"]))
    c2.metric("Nivel", row["risk_level"])
    c3.metric("Valor", f"${row['valor_del_contrato']:,.0f}".replace(",", "."))

    st.markdown(f"**Entidad:** {row['nombre_entidad']}")
    st.markdown(f"**Proveedor:** {row['proveedor_adjudicado']}")
    st.markdown(f"**Objeto:** {row['objeto_del_contrato']}")
    st.markdown(f"**Explicación:** {row['score_explanation']}")
    st.markdown(
        f"**Señales:** adiciones={row['score_adiciones']}, "
        f"concentración={row['score_concentracion']}, "
        f"recurrencia={row['score_recurrencia']}, valor/plazo={row['score_valor_plazo']}"
    )
    if row.get("url_proceso"):
        st.markdown(f"[Abrir contrato en SECOP]({row['url_proceso']})")


def providers_page(providers: pd.DataFrame, contracts: pd.DataFrame) -> None:
    st.title("Proveedores")
    provider_query = st.text_input("Buscar proveedor", value="", key="provider_query")
    min_score, max_score = st.slider(
        "Rango de score proveedor",
        0,
        100,
        (0, 100),
        key="provider_score",
    )
    filtered = providers[providers["score_final"].between(min_score, max_score)].copy()
    if provider_query:
        filtered = filtered[
            filtered["proveedor_adjudicado"].fillna("").str.contains(provider_query, case=False)
        ]

    chart = px.bar(
        filtered.nlargest(15, "score_final"),
        x="score_final",
        y="proveedor_adjudicado",
        color="nombre_entidad",
        orientation="h",
        title="Top 15 proveedores por score",
    )
    chart.update_layout(height=500, yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(chart, use_container_width=True)

    st.dataframe(
        filtered[
            [
                "proveedor_adjudicado",
                "nombre_entidad",
                "total_contratos",
                "max_share_proveedor_en_entidad",
                "score_final",
                "risk_level",
            ]
        ].sort_values("score_final", ascending=False),
        use_container_width=True,
        hide_index=True,
    )
    if filtered.empty:
        st.info("No hay proveedores en el filtro actual.")
        return

    supplier_key = st.selectbox(
        "Detalle proveedor",
        options=filtered.sort_values("score_final", ascending=False)["supplier_key"].tolist(),
        format_func=lambda key: filtered.set_index("supplier_key").loc[key, "proveedor_adjudicado"],
    )
    provider = filtered.set_index("supplier_key").loc[supplier_key]
    related_contracts = contracts[contracts["supplier_key"] == supplier_key].sort_values(
        "score_final",
        ascending=False,
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Score proveedor", int(provider["score_final"]))
    c2.metric("Contratos", int(provider["total_contratos"]))
    c3.metric("Entidades", int(provider["entidades_distintas"]))
    st.markdown(f"**Explicación:** {provider['score_explanation']}")
    st.dataframe(
        related_contracts[
            [
                "id_contrato",
                "nombre_entidad",
                "valor_del_contrato",
                "score_final",
                "score_explanation",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


def methodology_page() -> None:
    st.title("Metodología")
    st.markdown(
        """
        ### Alcance
        - Contratos 2025-2026
        - Tres subredes de salud en Bogotá
        - Priorización de revisión humana

        ### Datasets
        - SECOP II contratos electrónicos (`jbjy-vk9h`)
        - SECOP II procesos (`p6dx-8zbt`)
        - SECOP II adiciones (`cb9c-h8sn`)
        - SECOP II ubicaciones (`gra4-pcp2`)

        ### Score
        - Reglas explícitas para adiciones, concentración, recurrencia y valor/plazo
        - IsolationForest como señal complementaria de anomalía
        - Score final de 0 a 100

        ### Limitaciones
        - `cb9c-h8sn` no trae monto estructurado de adición
        - Los joins SECOP II no son perfectos
        - El score no demuestra irregularidad
        """
    )


def main() -> None:
    settings = get_settings()
    contracts_path = settings.marts_dir / "contracts_scored.parquet"
    providers_path = settings.marts_dir / "providers_scored.parquet"
    if not contracts_path.exists() or not providers_path.exists():
        show_missing_data([contracts_path, providers_path])
        return

    contracts, providers = load_data()
    page = st.sidebar.radio("Sección", ["Home", "Contratos", "Proveedores", "Metodología"])
    if page == "Home":
        home_page(contracts, providers)
    elif page == "Contratos":
        contracts_page(contracts)
    elif page == "Proveedores":
        providers_page(providers, contracts)
    else:
        methodology_page()


if __name__ == "__main__":
    main()
