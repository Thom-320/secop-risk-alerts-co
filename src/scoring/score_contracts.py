from __future__ import annotations

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import StandardScaler

from src.features.risk_features import compute_risk_features
from src.utils.config import get_settings
from src.utils.logging import configure_logging, logger


def component_score_additions(row: pd.Series) -> int:
    score = 0
    ratio = float(row.get("ratio_adiciones") or 0)
    n_add = int(row.get("n_adiciones") or 0)
    if ratio >= 1.0:
        score += 20
    elif ratio >= 0.5:
        score += 15
    elif ratio >= 0.2:
        score += 10
    elif ratio > 0:
        score += 5
    if n_add >= 3:
        score += 10
    elif n_add == 2:
        score += 7
    elif n_add == 1 and ratio >= 0.2:
        score += 3
    return min(score, 30)


def component_score_concentration(row: pd.Series) -> int:
    share = float(row.get("share_proveedor_en_entidad") or 0)
    if share >= 0.20:
        return 25
    if share >= 0.10:
        return 18
    if share >= 0.05:
        return 10
    if share >= 0.03:
        return 5
    return 0


def component_score_recurrence(row: pd.Series) -> int:
    recurrence = int(row.get("recurrencia_entidad_proveedor") or 0)
    if recurrence >= 10:
        return 20
    if recurrence >= 5:
        return 12
    if recurrence >= 3:
        return 6
    return 0


def component_score_value_duration(row: pd.Series) -> int:
    ratio = float(row.get("ratio_valor_plazo_vs_peer") or 0)
    robust_z = float(row.get("robust_z_valor_plazo") or 0)
    if ratio >= 5 or robust_z >= 3:
        return 25
    if ratio >= 3 or robust_z >= 2:
        return 18
    if ratio >= 2:
        return 12
    if ratio >= 1.5:
        return 6
    return 0


def compute_rule_scores(df: pd.DataFrame) -> pd.DataFrame:
    scored = df.copy()
    scored["score_adiciones"] = scored.apply(component_score_additions, axis=1)
    scored["score_concentracion"] = scored.apply(component_score_concentration, axis=1)
    scored["score_recurrencia"] = scored.apply(component_score_recurrence, axis=1)
    scored["score_valor_plazo"] = scored.apply(component_score_value_duration, axis=1)
    scored["score_reglas"] = (
        scored["score_adiciones"]
        + scored["score_concentracion"]
        + scored["score_recurrencia"]
        + scored["score_valor_plazo"]
    ).clip(0, 100)
    return scored


def normalize_to_100(series: pd.Series) -> pd.Series:
    if series.nunique(dropna=True) <= 1:
        return pd.Series([0.0] * len(series), index=series.index)
    min_value = series.min()
    max_value = series.max()
    return ((series - min_value) / (max_value - min_value) * 100).clip(0, 100)


def anomaly_features(df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "ratio_adiciones",
        "n_adiciones",
        "share_proveedor_en_entidad",
        "recurrencia_entidad_proveedor",
        "metrica_valor_plazo",
        "valor_del_contrato",
    ]
    return df[cols].apply(pd.to_numeric, errors="coerce")


def compute_anomaly_scores(df: pd.DataFrame, random_state: int = 42) -> pd.DataFrame:
    scored = df.copy()
    feature_matrix = anomaly_features(scored)
    if len(scored) < 30 or feature_matrix.dropna(how="all").empty:
        scored["score_anomalia"] = 0.0
        scored["anomaly_available"] = False
        return scored

    feature_matrix = feature_matrix.fillna(feature_matrix.median()).fillna(0.0)
    scaled = StandardScaler().fit_transform(feature_matrix)
    contamination = 0.08 if len(scored) >= 100 else 0.10
    model = IsolationForest(
        n_estimators=300,
        contamination=contamination,
        random_state=random_state,
    )
    model.fit(scaled)
    raw_score = pd.Series(-model.decision_function(scaled), index=scored.index)
    scored["score_anomalia"] = normalize_to_100(raw_score).round(2)
    scored["anomaly_available"] = True
    return scored


def compute_lof_benchmark(df: pd.DataFrame, n_neighbors: int = 20) -> pd.Series:
    feature_matrix = anomaly_features(df).fillna(0.0)
    if len(feature_matrix) <= n_neighbors:
        return pd.Series([0.0] * len(df), index=df.index)
    scaled = StandardScaler().fit_transform(feature_matrix)
    lof = LocalOutlierFactor(n_neighbors=n_neighbors)
    prediction = lof.fit_predict(scaled)
    negative_factor = pd.Series(-lof.negative_outlier_factor_, index=df.index)
    normalized = normalize_to_100(negative_factor)
    return normalized.where(prediction == -1, other=0.0).round(2)


def risk_level(score: float) -> str:
    if score >= 75:
        return "crítico"
    if score >= 50:
        return "alto"
    if score >= 25:
        return "medio"
    return "bajo"


def build_contract_explanation(row: pd.Series) -> str:
    reasons: list[str] = []
    if row["score_adiciones"] > 0:
        text = (
            f"adiciones relevantes: ratio temporal {row['ratio_adiciones']:.2f} "
            f"y {int(row['n_adiciones'])} evento(s) de adición"
        )
        if pd.notna(row.get("monto_adiciones_parseado")):
            amount_text = f"{int(row['monto_adiciones_parseado']):,}".replace(",", ".")
            text += f"; monto auxiliar parseado {amount_text}"
        reasons.append(text)
    if row["score_concentracion"] > 0:
        reasons.append(
            "concentración del proveedor en la entidad: "
            f"share {row['share_proveedor_en_entidad']:.1%}"
        )
    if row["score_recurrencia"] > 0:
        reasons.append(
            f"recurrencia entidad-proveedor: {int(row['recurrencia_entidad_proveedor'])} contratos"
        )
    if row["score_valor_plazo"] > 0:
        ratio_value = row["ratio_valor_plazo_vs_peer"]
        if pd.notna(ratio_value):
            reasons.append(
                f"valor/plazo desproporcionado frente al grupo par: {ratio_value:.2f}x la mediana"
            )
        else:
            reasons.append("valor/plazo atípico frente al grupo de referencia")

    explanation = (
        "Alerta priorizada por " + "; ".join(reasons)
        if reasons
        else "Sin alertas fuertes por reglas en el alcance actual."
    )
    if row.get("data_quality_flags"):
        explanation += f" Calidad de datos: {row['data_quality_flags']}."
    return explanation


def aggregate_providers(contracts_df: pd.DataFrame) -> pd.DataFrame:
    pair_summary = (
        contracts_df.groupby(
            ["supplier_key", "proveedor_adjudicado", "nombre_entidad"],
            dropna=False,
        )
        .agg(
            pair_contracts=("id_contrato", "count"),
            pair_share=("share_proveedor_en_entidad", "max"),
            pair_max_score=("score_final", "max"),
        )
        .reset_index()
    )
    top_pair = pair_summary.sort_values(
        ["pair_max_score", "pair_share", "pair_contracts"],
        ascending=False,
    ).drop_duplicates("supplier_key")

    providers = (
        contracts_df.groupby(
            ["supplier_key", "proveedor_adjudicado", "documento_proveedor"],
            dropna=False,
        )
        .agg(
            total_contratos=("id_contrato", "count"),
            total_valor=("valor_del_contrato", "sum"),
            entidades_distintas=("nombre_entidad", "nunique"),
            max_contract_score=("score_final", "max"),
            max_share_proveedor_en_entidad=("share_proveedor_en_entidad", "max"),
            max_recurrencia=("recurrencia_entidad_proveedor", "max"),
        )
        .reset_index()
        .merge(
            top_pair[
                [
                    "supplier_key",
                    "nombre_entidad",
                    "pair_contracts",
                    "pair_share",
                    "pair_max_score",
                ]
            ],
            on="supplier_key",
            how="left",
        )
    )
    providers["score_final"] = (
        providers["max_contract_score"] * 0.60
        + providers["max_share_proveedor_en_entidad"] * 100 * 0.25
        + providers["max_recurrencia"].clip(upper=20) * 5 * 0.15
    ).clip(0, 100).round(0)
    providers["risk_level"] = providers["score_final"].map(risk_level)
    providers["score_explanation"] = providers.apply(
        lambda row: (
            f"Proveedor priorizado por concentración en {row['nombre_entidad']} "
            f"({row['pair_share']:.1%} del valor observado), "
            f"{int(row['pair_contracts'])} contrato(s) con esa entidad y "
            f"contrato máximo con score {int(row['pair_max_score'])}."
        ),
        axis=1,
    )
    return providers.sort_values("score_final", ascending=False)


def score_contracts(df: pd.DataFrame) -> pd.DataFrame:
    featured = compute_risk_features(df)
    scored = compute_rule_scores(featured)
    scored = compute_anomaly_scores(scored, random_state=get_settings().random_state)
    scored["score_lof_benchmark"] = compute_lof_benchmark(scored)
    scored["score_final"] = scored["score_reglas"]
    mask = scored["anomaly_available"]
    scored.loc[mask, "score_final"] = (
        scored.loc[mask, "score_reglas"] * 0.7 + scored.loc[mask, "score_anomalia"] * 0.3
    ).round(0)
    scored["score_final"] = scored["score_final"].clip(0, 100)
    scored["risk_level"] = scored["score_final"].map(risk_level)
    scored["score_explanation"] = scored.apply(build_contract_explanation, axis=1)
    return scored.sort_values("score_final", ascending=False)


def main() -> None:
    configure_logging()
    settings = get_settings()
    base_path = settings.interim_dir / "base_contracts.parquet"
    base_df = pd.read_parquet(base_path)
    contracts_scored = score_contracts(base_df)
    providers_scored = aggregate_providers(contracts_scored)
    features_cols = [
        "id_contrato",
        "supplier_key",
        "base_duration_days",
        "contract_duration_days",
        "process_duration_days",
        "ratio_adiciones",
        "n_adiciones",
        "monto_adiciones_parseado",
        "share_proveedor_en_entidad",
        "recurrencia_entidad_proveedor",
        "metrica_valor_plazo",
        "peer_group_key",
        "ratio_valor_plazo_vs_peer",
        "robust_z_valor_plazo",
        "data_quality_flags",
    ]
    contracts_scored[features_cols].to_parquet(
        settings.interim_dir / "contracts_features.parquet",
        index=False,
    )
    contracts_scored.to_parquet(settings.marts_dir / "contracts_scored.parquet", index=False)
    providers_scored.to_parquet(settings.marts_dir / "providers_scored.parquet", index=False)
    logger.info(
        "Scores guardados: {} contratos y {} proveedores.",
        len(contracts_scored),
        len(providers_scored),
    )


if __name__ == "__main__":
    main()
