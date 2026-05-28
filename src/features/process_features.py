from __future__ import annotations

import math

import pandas as pd
from sklearn.ensemble import IsolationForest

from src.utils.normalization import normalize_text


def stable_missing_identifier(prefix: str, value: str) -> str:
    """Generate a stable, opaque identifier for rows with missing codes.

    Replaces the legacy ``etl.common.stable_missing_identifier`` with a
    src-native implementation that uses ``normalize_text`` instead of
    ``clean_text``.
    """
    import hashlib

    normalized = normalize_text(value) or "sin_nombre"
    digest = hashlib.sha256(normalized.lower().encode("utf-8")).hexdigest()[:16]
    return f"{prefix}-{digest}"


def normalize_to_100(series: pd.Series, *, robust: bool = False) -> pd.Series:
    clean = pd.to_numeric(series, errors="coerce").fillna(0.0)
    if clean.nunique(dropna=True) <= 1:
        return pd.Series([0.0] * len(clean), index=clean.index)
    if robust:
        p99 = clean.quantile(0.99)
        p1 = clean.quantile(0.01)
        if p99 == p1:
            return pd.Series([0.0] * len(clean), index=clean.index)
        clipped = clean.clip(lower=p1, upper=p99)
        return ((clipped - p1) / (p99 - p1) * 100).clip(0, 100)
    min_value = clean.min()
    max_value = clean.max()
    return ((clean - min_value) / (max_value - min_value) * 100).clip(0, 100)


def safe_log1p(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0.0).clip(lower=0.0).map(math.log1p)


def build_numeric_feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    frame = pd.DataFrame(index=df.index)
    frame["base_price_log"] = safe_log1p(df["base_price"])
    frame["awarded_total_log"] = safe_log1p(df["awarded_total"])
    frame["duration_days_log"] = safe_log1p(df["duration_days"])
    frame["response_count"] = pd.to_numeric(df["response_count"], errors="coerce").fillna(0.0)
    frame["invited_suppliers"] = pd.to_numeric(
        df["invited_suppliers"],
        errors="coerce",
    ).fillna(0.0)
    frame["unique_suppliers"] = pd.to_numeric(
        df["unique_suppliers"],
        errors="coerce",
    ).fillna(0.0)
    frame["adjudicado_flag"] = df["adjudicado_flag"].fillna(False).astype(int)
    frame["has_rpmr_link"] = df["rpmr_linked"].fillna(False).astype(int)
    return frame


def compute_anomaly_component(df: pd.DataFrame, random_state: int = 42) -> pd.Series:
    numeric = build_numeric_feature_frame(df)
    if len(numeric) < 30:
        return pd.Series([0.0] * len(df), index=df.index)
    model = IsolationForest(
        random_state=random_state,
        contamination=min(max(0.03, 20 / max(len(numeric), 1)), 0.15),
        n_estimators=200,
    )
    model.fit(numeric)
    raw_score = pd.Series(-model.decision_function(numeric), index=df.index)
    return normalize_to_100(raw_score, robust=True).round(2)


def compute_peer_statistics(df: pd.DataFrame) -> pd.DataFrame:
    category = df["category_code"].fillna("").astype(str)
    # Value band by order of magnitude: keeps peers value-homogeneous so the
    # median is meaningful. Without it, a $588M contract lands in the same group
    # as $2M ones and shows an absurd "289x la mediana". A $588M contract is
    # compared against other ~$100M-$1B contracts of its modality+category.
    import math
    price = pd.to_numeric(df.get("base_price"), errors="coerce").fillna(0.0)
    value_band = price.clip(lower=1.0).map(
        lambda v: str(int(math.log10(v)))
    )
    peer_group = (
        df["modality_family"].fillna("otros").astype(str)
        + "||"
        + category.where(category.ne(""), "sin_categoria")
        + "||"
        + df["process_year"].fillna(0).astype(int).astype(str)
        + "||v"
        + value_band
    )
    peer = df.copy()
    peer["peer_group_key"] = peer_group
    stats = (
        peer.groupby("peer_group_key", dropna=False)
        .agg(
            peer_group_size=("process_key", "count"),
            peer_price_median=("base_price", "median"),
            peer_duration_median=("duration_days", "median"),
            peer_response_median=("response_count", "median"),
        )
        .reset_index()
    )
    return peer.merge(stats, on="peer_group_key", how="left")


def compute_peer_deviation_component(df: pd.DataFrame) -> pd.DataFrame:
    peer = compute_peer_statistics(df)
    price_ratio = peer["base_price"] / peer["peer_price_median"].where(
        peer["peer_price_median"] > 0
    )
    duration_ratio = peer["duration_days"] / peer["peer_duration_median"].where(
        peer["peer_duration_median"] > 0
    )
    response_gap = (
        peer["peer_response_median"].fillna(0.0) - peer["response_count"].fillna(0.0)
    ).clip(lower=0.0)
    raw = (
        price_ratio.fillna(1.0).clip(lower=0.0)
        + duration_ratio.fillna(1.0).clip(lower=0.0)
        + response_gap.fillna(0.0)
    )
    peer["peer_deviation_score"] = normalize_to_100(raw, robust=True).round(2)
    return peer


def build_reason_snippets(row: pd.Series, paa_signal_mode: str) -> list[str]:
    reasons: list[str] = []
    if float(row.get("value_deviation_ratio") or 0.0) >= 1.8:
        reasons.append(
            "monto atípico frente a pares comparables "
            f"({row['value_deviation_ratio']:.2f}x la mediana)"
        )
    if float(row.get("duration_deviation_ratio") or 0.0) >= 1.8:
        reasons.append(
            "duración atípica frente a pares comparables "
            f"({row['duration_deviation_ratio']:.2f}x la mediana)"
        )
    if float(row.get("response_gap") or 0.0) >= 2:
        reasons.append(
            f"menor competencia observada que el grupo comparable ({row['response_gap']:.0f} menos)"
        )
    if (
        paa_signal_mode in {"full", "secondary"}
        and str(row.get("paa_match_status") or "") in {"weak", "none"}
    ):
        reasons.append("señal débil de alineación plan vs ejecución")
    if bool(row.get("rpmr_linked")):
        reasons.append("enriquecido con contrato consolidado de SECOP Integrado")
    return reasons[:3]


def rule_score_from_row(row: pd.Series, paa_signal_mode: str) -> float:
    score = 0.0
    if float(row.get("value_deviation_ratio") or 0.0) >= 2.5:
        score += 35
    elif float(row.get("value_deviation_ratio") or 0.0) >= 1.8:
        score += 20
    if float(row.get("duration_deviation_ratio") or 0.0) >= 2.5:
        score += 25
    elif float(row.get("duration_deviation_ratio") or 0.0) >= 1.8:
        score += 15
    if float(row.get("response_gap") or 0.0) >= 3:
        score += 20
    elif float(row.get("response_gap") or 0.0) >= 1:
        score += 10

    if paa_signal_mode == "full":
        if row.get("paa_match_status") == "none":
            score += 20
        elif row.get("paa_match_status") == "weak":
            score += 10
    elif paa_signal_mode == "secondary":
        if row.get("paa_match_status") == "none":
            score += 10
        elif row.get("paa_match_status") == "weak":
            score += 5
    return min(score, 100.0)


def compute_confidence_score(df: pd.DataFrame) -> pd.Series:
    base = pd.Series([45.0] * len(df), index=df.index)
    base += df["text_sufficient"].fillna(False).astype(int) * 15
    base += df["peer_group_size"].fillna(0).ge(8).astype(int) * 15
    base += df["semantic_comparable_count"].fillna(0).ge(3).astype(int) * 10
    base += df["rpmr_linked"].fillna(False).astype(int) * 5
    base += df["paa_match_confidence"].fillna(0.0).clip(0.0, 1.0) * 10
    return base.clip(0, 100).round(0)


def confidence_band(value: float) -> str:
    if value >= 75:
        return "alta"
    if value >= 55:
        return "media"
    return "baja"


def priority_band(value: float) -> str:
    if value >= 85:
        return "alerta prioritaria"
    if value >= 70:
        return "alerta alta"
    if value >= 40:
        return "observacion"
    return "baja prioridad"


def comparable_label(row: pd.Series) -> str:
    return (
        f"{row.get('process_reference', '')} | "
        f"{row.get('entity_name', '')} | "
        f"{normalize_text(row.get('process_title', ''))[:120]}"
    )
