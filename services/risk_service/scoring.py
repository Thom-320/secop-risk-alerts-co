from __future__ import annotations

from typing import Any


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def score_process_context(context: dict[str, Any]) -> dict[str, Any]:
    response_count = int(context.get("response_count") or 0)
    value_percentile = float(context.get("value_percentile") or 0.5)
    modality = str(context.get("modality") or "").lower()
    has_paa_match = bool(context.get("has_paa_match"))
    provider_share = float(context.get("provider_share") or 0)
    description_length = int(context.get("description_length") or 0)

    competition_score = 90 if response_count <= 1 else 55 if response_count <= 2 else 25
    value_score = clamp(value_percentile * 100)
    modality_score = 70 if "directa" in modality else 45 if "minima" in modality else 30
    planning_score = 15 if has_paa_match else 55
    concentration_score = clamp(provider_share * 100)
    description_score = 70 if description_length < 40 else 35 if description_length < 120 else 15

    priority_score = clamp(
        0.24 * competition_score
        + 0.24 * value_score
        + 0.16 * modality_score
        + 0.14 * planning_score
        + 0.12 * concentration_score
        + 0.10 * description_score
    )
    confidence_score = clamp(
        35
        + (15 if description_length >= 40 else 0)
        + (15 if context.get("base_price") else 0)
        + (15 if context.get("modality") else 0)
        + (10 if response_count >= 0 else 0)
        + (10 if has_paa_match else 0)
    )
    components = {
        "competition": round(competition_score, 2),
        "value_percentile": round(value_score, 2),
        "modality": round(modality_score, 2),
        "planning": round(planning_score, 2),
        "provider_concentration": round(concentration_score, 2),
        "description_quality": round(description_score, 2),
    }
    top_components = sorted(components.items(), key=lambda item: item[1], reverse=True)[:3]
    reasons = ", ".join(name.replace("_", " ") for name, _score in top_components)
    explanation = (
        "Priorizacion de revision humana basada en "
        f"{reasons}. Requiere validacion humana y trazabilidad de fuentes."
    )
    return {
        "priority_score": round(priority_score, 2),
        "confidence_score": round(confidence_score, 2),
        "anomaly_score": round(value_score, 2),
        "peer_deviation_score": round((competition_score + value_score) / 2, 2),
        "rule_score": round((modality_score + planning_score + concentration_score) / 3, 2),
        "components": components,
        "explanation": explanation,
    }
