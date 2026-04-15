from __future__ import annotations

import math
import re
import unicodedata

import pandas as pd


def normalize_unit(value: str | None) -> str:
    if value is None:
        return ""
    normalized = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode("ascii")
    return normalized.strip().lower()


def unit_to_days_factor(unit_value: str | None) -> float | None:
    unit = normalize_unit(unit_value)
    if unit.startswith("dia"):
        return 1.0
    if unit.startswith("semana"):
        return 7.0
    if unit.startswith("mes"):
        return 30.0
    if unit.startswith("ano") or unit.startswith("año"):
        return 365.0
    if unit.startswith("hora"):
        return 1.0 / 24.0
    return None


def parse_currency_candidates(text: str | None) -> int | None:
    if not isinstance(text, str) or not text:
        return None
    matches = re.findall(r"\$?\s*([\d\.\,\';]{5,})", text)
    values: list[int] = []
    for match in matches:
        normalized = match.strip()
        if re.search(r"[,;]\d{2}$", normalized):
            normalized = re.sub(r"[,;]\d{2}$", "", normalized)
        digits = re.sub(r"\D", "", normalized)
        if len(digits) >= 5:
            values.append(int(digits))
    if not values:
        return None
    return max(values)


def build_duration_columns(df: pd.DataFrame) -> pd.DataFrame:
    feature_df = df.copy()
    for column in ["fecha_inicio_contrato", "fecha_fin_contrato"]:
        feature_df[column] = pd.to_datetime(feature_df[column], errors="coerce")

    contract_duration = (
        feature_df["fecha_fin_contrato"] - feature_df["fecha_inicio_contrato"]
    ).dt.days.astype("float64")
    contract_duration = contract_duration.where(contract_duration > 0)

    factors = feature_df["unidad_duracion_proceso"].map(unit_to_days_factor)
    process_duration = pd.to_numeric(feature_df["duracion_proceso"], errors="coerce") * factors
    process_duration = process_duration.where(process_duration > 0)

    feature_df["contract_duration_days"] = contract_duration
    feature_df["process_duration_days"] = process_duration
    feature_df["base_duration_days"] = contract_duration.fillna(process_duration)
    return feature_df


def assign_peer_group(df: pd.DataFrame, min_group_size: int = 20) -> pd.Series:
    counts = (
        df.assign(tipo_group=df["tipo_de_contrato"].fillna("Sin tipo"))
        .groupby(["nombre_entidad", "tipo_group"])
        .size()
        .rename("group_size")
        .reset_index()
    )
    merged = df.assign(tipo_group=df["tipo_de_contrato"].fillna("Sin tipo")).merge(
        counts,
        on=["nombre_entidad", "tipo_group"],
        how="left",
    )
    return merged.apply(
        lambda row: f"{row['nombre_entidad']}||{row['tipo_group']}"
        if row["group_size"] >= min_group_size
        else f"{row['nombre_entidad']}||ALL",
        axis=1,
    )


def build_data_quality_flags(df: pd.DataFrame) -> pd.DataFrame:
    feature_df = df.copy()
    feature_df["flag_missing_contract_dates"] = (
        feature_df["fecha_inicio_contrato"].isna() | feature_df["fecha_fin_contrato"].isna()
    )
    feature_df["flag_invalid_duration"] = (
        feature_df["base_duration_days"].isna() | (feature_df["base_duration_days"] <= 0)
    )
    feature_df["flag_missing_process_match"] = ~feature_df["flag_match_proceso"].fillna(False)
    feature_df["flag_missing_supplier_id"] = (
        feature_df["documento_proveedor"].fillna("").astype(str).str.strip().eq("")
        & feature_df["codigo_proveedor"].fillna("").astype(str).str.strip().eq("")
    )
    label_map = {
        "flag_missing_contract_dates": "fechas incompletas",
        "flag_invalid_duration": "duración inválida",
        "flag_missing_process_match": "sin match de proceso",
        "flag_multiple_ubicaciones": "múltiples ubicaciones",
        "flag_missing_supplier_id": "proveedor sin identificador estructurado",
    }

    def summarize_flags(row: pd.Series) -> str:
        active = [label for field, label in label_map.items() if bool(row.get(field, False))]
        return " | ".join(active)

    feature_df["data_quality_flags"] = feature_df.apply(summarize_flags, axis=1)
    return feature_df


def compute_risk_features(df: pd.DataFrame) -> pd.DataFrame:
    feature_df = build_duration_columns(df)
    feature_df["valor_del_contrato"] = pd.to_numeric(
        feature_df["valor_del_contrato"], errors="coerce"
    ).fillna(0.0)
    feature_df["dias_adicionados"] = pd.to_numeric(
        feature_df["dias_adicionados"], errors="coerce"
    ).fillna(0.0)
    feature_df["n_adiciones"] = (
        pd.to_numeric(feature_df["n_adiciones"], errors="coerce").fillna(0).astype(int)
    )
    feature_df["monto_adiciones_parseado"] = feature_df["descripcion_modificacion_ejemplo"].map(
        parse_currency_candidates
    )
    feature_df["ratio_adiciones"] = feature_df["dias_adicionados"] / feature_df[
        "base_duration_days"
    ].clip(lower=1)
    feature_df["ratio_adiciones"] = feature_df["ratio_adiciones"].replace(
        [math.inf, -math.inf],
        pd.NA,
    )

    entity_total = feature_df.groupby("nombre_entidad")["valor_del_contrato"].transform("sum")
    pair_total = feature_df.groupby(["nombre_entidad", "supplier_key"])[
        "valor_del_contrato"
    ].transform("sum")
    feature_df["share_proveedor_en_entidad"] = pair_total / entity_total.where(entity_total > 0)
    feature_df["share_proveedor_en_entidad"] = feature_df["share_proveedor_en_entidad"].fillna(0.0)
    feature_df["recurrencia_entidad_proveedor"] = feature_df.groupby(
        ["nombre_entidad", "supplier_key"]
    )["id_contrato"].transform("count")

    feature_df["metrica_valor_plazo"] = feature_df["valor_del_contrato"] / feature_df[
        "base_duration_days"
    ].clip(lower=1)
    feature_df["peer_group_key"] = assign_peer_group(feature_df)

    peer_stats = (
        feature_df.groupby("peer_group_key")["metrica_valor_plazo"]
        .agg(
            peer_median="median",
            peer_q25=lambda s: s.quantile(0.25),
            peer_q75=lambda s: s.quantile(0.75),
        )
        .reset_index()
    )
    feature_df = feature_df.merge(peer_stats, on="peer_group_key", how="left")
    feature_df["peer_iqr"] = feature_df["peer_q75"] - feature_df["peer_q25"]
    feature_df["ratio_valor_plazo_vs_peer"] = feature_df["metrica_valor_plazo"] / feature_df[
        "peer_median"
    ].where(feature_df["peer_median"] > 0)
    feature_df["ratio_valor_plazo_vs_peer"] = feature_df["ratio_valor_plazo_vs_peer"].replace(
        [math.inf, -math.inf],
        pd.NA,
    )
    feature_df["robust_z_valor_plazo"] = (
        feature_df["metrica_valor_plazo"] - feature_df["peer_median"]
    ) / feature_df["peer_iqr"].where(feature_df["peer_iqr"] > 0)
    feature_df["robust_z_valor_plazo"] = feature_df["robust_z_valor_plazo"].replace(
        [math.inf, -math.inf],
        pd.NA,
    )
    feature_df = build_data_quality_flags(feature_df)
    return feature_df
