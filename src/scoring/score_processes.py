from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.features.process_features import (
    build_reason_snippets,
    comparable_label,
    compute_anomaly_component,
    compute_confidence_score,
    compute_peer_deviation_component,
    confidence_band,
    priority_band,
    rule_score_from_row,
)
from src.scoring.semantic_similarity import semantic_similarity_matrix
from src.utils.config import get_settings
from src.utils.logging import configure_logging, logger
from src.utils.normalization import normalize_text


def load_assets() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    settings = get_settings()
    process_master = pd.read_parquet(settings.interim_dir / "process_master.parquet")
    paa_items = pd.read_parquet(settings.interim_dir / "paa_items.parquet")
    control = pd.read_parquet(settings.interim_dir / "control_context.parquet")
    rpmr_linkage = pd.read_parquet(settings.interim_dir / "rpmr_linkage.parquet")
    return process_master, paa_items, control, rpmr_linkage


def attach_control_context(processes: pd.DataFrame, control: pd.DataFrame) -> pd.DataFrame:
    if control.empty:
        enriched = processes.copy()
        enriched["control_badge"] = "sin contexto"
        return enriched

    process_subject = processes["entity_name"].fillna("").map(normalize_text)
    control_summary = (
        control.groupby("subject_key", dropna=False)
        .agg(
            hallazgos_fiscales_total=("hallazgos_fiscales", "sum"),
            hallazgos_administrativos_total=("hallazgos_administrativos", "sum"),
            amount_total=("amount", "sum"),
        )
        .reset_index()
    )
    enriched = processes.copy()
    enriched["subject_key"] = process_subject
    enriched = enriched.merge(control_summary, on="subject_key", how="left")
    enriched["control_badge"] = np.where(
        enriched["hallazgos_fiscales_total"].fillna(0.0) > 0,
        "contexto fiscal",
        "sin contexto",
    )
    return enriched.drop(columns=["subject_key"])


def build_paa_matches(processes: pd.DataFrame, paa: pd.DataFrame) -> pd.DataFrame:
    demo = processes[processes["demo_scope"]].copy()
    if demo.empty or paa.empty:
        return pd.DataFrame(columns=[
            "process_key",
            "paa_item_id",
            "paa_match_method",
            "paa_match_similarity",
            "paa_match_confidence",
            "paa_match_status",
            "paa_text",
            "planned_value",
            "planned_start_date",
        ])

    exact = demo.merge(
        paa,
        left_on=["entity_key", "process_reference_norm"],
        right_on=["entity_key", "related_process_reference_norm"],
        how="left",
        suffixes=("", "_paa"),
    )
    exact["paa_match_method"] = np.where(
        exact["paa_item_id"].notna(),
        "related_process",
        "",
    )
    exact["paa_match_similarity"] = np.where(exact["paa_item_id"].notna(), 1.0, 0.0)
    exact["paa_match_confidence"] = np.where(exact["paa_item_id"].notna(), 1.0, 0.0)

    unmatched = exact[exact["paa_item_id"].isna()][processes.columns].copy()

    # Phase 1.5: reference-pattern matching for unmatched processes
    # Matches PAA items from same entity where reference shares a structural pattern
    # (e.g., both contain "CACOM2GRUTE" even with different prefixes/suffixes)
    pattern_rows: list[dict[str, object]] = []
    if not unmatched.empty:
        paa_valid = paa[
            (paa["related_process_reference_norm"].fillna("").ne(""))
            & (paa["related_process_reference_norm"].fillna("").str.upper() != "NODEFINIDO")
        ].copy()
        paa_valid = paa_valid[paa_valid["related_process_reference_norm"].str.len() >= 8]

        grouped_pattern = unmatched.groupby("entity_key", dropna=False)
        for entity_key, group in grouped_pattern:
            entity_paa = paa_valid[paa_valid["entity_key"] == entity_key]
            if entity_paa.empty:
                continue
            for _, proc_row in group.iterrows():
                ref_norm = str(proc_row.get("process_reference_norm", ""))
                if len(ref_norm) < 8:
                    continue
                # Extract core pattern: remove year suffix and leading digits
                # e.g., "01500ECACOM2GRUTE2026" -> "CACOM2GRUTE"
                import re
                core = re.sub(r"^\d+", "", ref_norm)
                core = re.sub(r"\d{4}$", "", core)
                if len(core) < 4:
                    continue
                # Find PAA items whose reference contains the same core pattern
                matches = entity_paa[
                    entity_paa["related_process_reference_norm"].str.contains(
                        core, na=False, regex=False,
                    )
                ]
                if matches.empty:
                    continue
                # Take the best match (prefer same year)
                proc_year = int(proc_row.get("process_year", 0))
                same_year = matches[matches["paa_year"] == proc_year]
                if not same_year.empty:
                    best_match = same_year.iloc[0]
                    confidence = 0.80
                else:
                    best_match = matches.iloc[0]
                    confidence = 0.65
                status = (
                    "strong" if confidence >= 0.75
                    else "weak" if confidence >= 0.65
                    else "none"
                )
                pattern_rows.append({
                    "process_key": proc_row["process_key"],
                    "paa_item_id": best_match["paa_item_id"],
                    "paa_match_method": "reference_pattern",
                    "paa_match_similarity": confidence,
                    "paa_match_confidence": confidence,
                    "paa_match_status": status,
                    "paa_text": best_match["paa_text"],
                    "planned_value": best_match["planned_value"],
                    "planned_start_date": best_match["planned_start_date"],
                })

    # Remove processes that got a pattern match from the semantic pool
    pattern_keys = {r["process_key"] for r in pattern_rows}
    unmatched = unmatched[~unmatched["process_key"].isin(pattern_keys)]

    # Filter PAA: exclude NODEFINIDO/empty references for semantic matching
    paa_valid = paa[
        (paa["related_process_reference_norm"].fillna("").ne(""))
        & (paa["related_process_reference_norm"].fillna("").str.upper() != "NODEFINIDO")
    ].copy()
    # Also keep all PAA items for entity-key-based fallback (even NODEFINIDO)
    paa_all = paa.copy()

    semantic_rows: list[dict[str, object]] = []
    grouped = unmatched.groupby(["entity_key", "process_year"], dropna=False)
    for (entity_key, year), group in grouped:
        # First try: match against PAA items with valid references (same entity + year)
        candidates = paa_valid[
            (paa_valid["entity_key"] == entity_key) & (paa_valid["paa_year"] == year)
        ].copy()
        # Fallback: use all PAA items including NODEFINIDO if no valid-reference candidates
        if candidates.empty:
            candidates = paa_all[
                (paa_all["entity_key"] == entity_key) & (paa_all["paa_year"] == year)
            ].copy()
        if candidates.empty:
            continue

        process_texts = group["process_text"].fillna("").astype(str).tolist()
        paa_texts = candidates["paa_text"].fillna("").astype(str).tolist()

        # Skip if all PAA texts are empty
        if not any(t.strip() for t in paa_texts):
            continue

        similarity = semantic_similarity_matrix(process_texts, paa_texts)
        for idx, (_, process_row) in enumerate(group.iterrows()):
            best_idx = int(similarity[idx].argmax())
            best_score = float(similarity[idx, best_idx])

            # Skip very low similarity matches (noise)
            if best_score < 0.15:
                continue

            candidate = candidates.iloc[best_idx]
            confidence = best_score
            if process_row["modality_family"] == candidate["modality_family"]:
                confidence = min(1.0, best_score + 0.15)
            status = "strong" if confidence >= 0.75 else "weak" if confidence >= 0.65 else "none"
            semantic_rows.append(
                {
                    "process_key": process_row["process_key"],
                    "paa_item_id": candidate["paa_item_id"],
                    "paa_match_method": "semantic",
                    "paa_match_similarity": best_score,
                    "paa_match_confidence": confidence,
                    "paa_match_status": status,
                    "paa_text": candidate["paa_text"],
                    "planned_value": candidate["planned_value"],
                    "planned_start_date": candidate["planned_start_date"],
                }
            )

    semantic = pd.DataFrame(semantic_rows)
    pattern = pd.DataFrame(pattern_rows)
    exact_matches = exact[exact["paa_item_id"].notna()][
        [
            "process_key",
            "paa_item_id",
            "paa_match_method",
            "paa_match_similarity",
            "paa_match_confidence",
            "paa_text",
            "planned_value",
            "planned_start_date",
        ]
    ].copy()
    exact_matches["paa_match_status"] = "strong"

    combined = pd.concat([exact_matches, pattern, semantic], ignore_index=True, sort=False)
    if combined.empty:
        return pd.DataFrame(columns=[
            "process_key",
            "paa_item_id",
            "paa_match_method",
            "paa_match_similarity",
            "paa_match_confidence",
            "paa_match_status",
            "paa_text",
            "planned_value",
            "planned_start_date",
        ])
    return combined.sort_values(
        ["process_key", "paa_match_confidence", "paa_match_similarity"],
        ascending=[True, False, False],
    ).drop_duplicates("process_key")


def build_semantic_comparables(processes: pd.DataFrame) -> pd.DataFrame:
    from src.scoring.semantic_similarity import semantic_similarity_matrix

    demo = processes[processes["demo_scope"] & processes["text_sufficient"]].copy()
    if demo.empty:
        return pd.DataFrame(
            columns=[
                "process_key",
                "comparable_process_key",
                "similarity",
                "rank",
                "comparable_label",
                "comparable_value",
                "comparable_duration_days",
            ]
        )

    settings = get_settings()
    top_k = settings.demo_top_k_comparables
    rows: list[dict[str, object]] = []

    grouped = demo.groupby(["department", "modality_family"], dropna=False)
    for (_, _modality_family), group in grouped:
        if len(group) < 2:
            continue
        texts = group["process_text"].fillna("").astype(str).tolist()
        group_rows = list(group.iterrows())

        similarity_matrix = semantic_similarity_matrix(texts)

        for row_idx, (_idx, row) in enumerate(group_rows):
            similarities = similarity_matrix[row_idx]
            similarities[row_idx] = -1.0
            top_indices = similarities.argsort()[::-1][:top_k]

            for rank, neighbor_idx in enumerate(top_indices, start=1):
                if similarities[neighbor_idx] <= 0:
                    break
                candidate = group.iloc[neighbor_idx]
                rows.append(
                    {
                        "process_key": row["process_key"],
                        "comparable_process_key": candidate["process_key"],
                        "similarity": float(similarities[neighbor_idx]),
                        "rank": rank,
                        "comparable_label": comparable_label(candidate),
                        "comparable_value": candidate["base_price"],
                        "comparable_duration_days": candidate["duration_days"],
                    }
                )
    return pd.DataFrame(rows)


def attach_peer_reason_metrics(df: pd.DataFrame) -> pd.DataFrame:
    scored = compute_peer_deviation_component(df)
    scored["value_deviation_ratio"] = (
        scored["base_price"] / scored["peer_price_median"].where(scored["peer_price_median"] > 0)
    ).replace([np.inf, -np.inf], np.nan)
    scored["duration_deviation_ratio"] = (
        scored["duration_days"]
        / scored["peer_duration_median"].where(scored["peer_duration_median"] > 0)
    ).replace([np.inf, -np.inf], np.nan)
    scored["response_gap"] = (
        scored["peer_response_median"].fillna(0.0) - scored["response_count"].fillna(0.0)
    ).clip(lower=0.0)
    return scored


def apply_gate_recommendation(
    paa_matches: pd.DataFrame,
    processes: pd.DataFrame,
) -> tuple[str, float, float]:
    settings = get_settings()
    if paa_matches.empty:
        return "visible_only", 0.0, 0.0
    top1_acceptable = paa_matches["paa_match_confidence"].fillna(0.0).ge(0.75).mean()
    coverage = processes["process_key"].isin(paa_matches["process_key"]).mean()
    if settings.paa_signal_mode != "pending":
        return settings.paa_signal_mode, top1_acceptable, coverage
    if top1_acceptable >= 0.75 and coverage >= 0.60:
        return "full", top1_acceptable, coverage
    if top1_acceptable >= 0.65:
        return "secondary", top1_acceptable, coverage
    return "visible_only", top1_acceptable, coverage


def build_process_scores() -> dict[str, pd.DataFrame]:
    settings = get_settings()
    processes, paa_items, control, _rpmr_linkage = load_assets()

    # Phase 1: compute peer statistics on ALL processes (for good peer groups)
    all_with_peers = attach_peer_reason_metrics(processes)
    all_with_peers = attach_control_context(all_with_peers, control)

    # Phase 2: filter to demo scope for expensive operations (anomaly, PAA, comparables)
    demo = all_with_peers[all_with_peers["demo_scope"]].copy()
    logger.info("Demo scope: {} procesos de {} totales.", len(demo), len(all_with_peers))

    demo["anomaly_score"] = compute_anomaly_component(demo, random_state=settings.random_state)

    paa_matches = build_paa_matches(demo, paa_items)
    semantic_comparables = build_semantic_comparables(demo)
    comparable_counts = (
        semantic_comparables.groupby("process_key")
        .size()
        .rename("semantic_comparable_count")
    )

    demo = demo.merge(paa_matches, on="process_key", how="left")
    demo = demo.merge(comparable_counts, on="process_key", how="left")
    demo["semantic_comparable_count"] = demo["semantic_comparable_count"].fillna(0).astype(int)
    demo["paa_match_status"] = demo["paa_match_status"].fillna("none")
    demo["paa_match_confidence"] = demo["paa_match_confidence"].fillna(0.0)
    demo["paa_match_method"] = demo["paa_match_method"].fillna("none")

    resolved_paa_mode, paa_precision, paa_coverage = apply_gate_recommendation(
        paa_matches,
        demo,
    )
    demo["rule_score"] = demo.apply(
        lambda row: rule_score_from_row(row, resolved_paa_mode),
        axis=1,
    )
    weights = settings.provisional_weights
    demo["priority_score"] = (
        demo["anomaly_score"] * weights["anomaly"]
        + demo["peer_deviation_score"] * weights["peer_deviation"]
        + demo["rule_score"] * weights["rule"]
    ).clip(0, 100).round(0)
    demo["confidence_score"] = compute_confidence_score(demo)
    demo["confidence_band"] = demo["confidence_score"].map(confidence_band)
    demo["priority_band"] = demo["priority_score"].map(priority_band)
    demo["reason_snippets"] = demo.apply(
        lambda row: build_reason_snippets(row, resolved_paa_mode),
        axis=1,
    )
    demo["reasons"] = demo["reason_snippets"].map(
        lambda values: " | ".join(values) if values else "sin señales fuertes visibles"
    )

    scored = demo
    ranking = scored.copy().sort_values(
        ["priority_score", "confidence_score"],
        ascending=[False, False],
    )
    detail = ranking.copy()
    overview = (
        scored.groupby("department", dropna=False)
        .agg(
            processes_analyzed=("process_key", "count"),
            entities=("entity_name", "nunique"),
            providers=("provider_name", "nunique"),
            avg_priority_score=("priority_score", "mean"),
            avg_confidence_score=("confidence_score", "mean"),
            high_priority_share=("priority_score", lambda s: (s >= 70).mean()),
            paa_match_share=("paa_match_confidence", lambda s: (s >= 0.75).mean()),
        )
        .reset_index()
        .sort_values("processes_analyzed", ascending=False)
    )

    ranking_export = ranking[
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
            "paa_match_method",
            "reasons",
        ]
    ].head(120)

    paa_sample = (
        paa_matches.sort_values(
            ["paa_match_confidence", "paa_match_similarity"],
            ascending=[False, False],
        )
        .head(60)
        .copy()
    )

    scored.attrs["resolved_paa_mode"] = resolved_paa_mode
    scored.attrs["paa_precision"] = paa_precision
    scored.attrs["paa_coverage"] = paa_coverage
    scored.attrs["comparable_ready_rate"] = (
        ranking["semantic_comparable_count"].ge(1).mean() if not ranking.empty else 0.0
    )
    return {
        "process_scores": scored,
        "overview": overview,
        "ranking": ranking,
        "process_detail": detail,
        "comparables": semantic_comparables,
        "ranking_export": ranking_export,
        "paa_sample": paa_sample,
    }


def update_join_audit(path: Path, process_scores: pd.DataFrame) -> None:
    resolved_paa_mode = process_scores.attrs.get("resolved_paa_mode", "pending")
    paa_precision = float(process_scores.attrs.get("paa_precision", 0.0))
    paa_coverage = float(process_scores.attrs.get("paa_coverage", 0.0))
    comparable_ready_rate = float(process_scores.attrs.get("comparable_ready_rate", 0.0))

    existing = path.read_text() if path.exists() else "# Join Audit\n"
    extra = f"""

## Señal y compuertas

- Top-1 aceptable PAA observado: {paa_precision:.2%}
- Cobertura de match PAA en alcance demo: {paa_coverage:.2%}
- Procesos con comparables semánticos válidos en alcance demo: {comparable_ready_rate:.2%}
- Modo PAA resuelto para el score provisional: `{resolved_paa_mode}`
"""
    path.write_text(existing.split("\n## Señal y compuertas")[0].rstrip() + extra + "\n")


def main() -> None:
    configure_logging()
    settings = get_settings()
    assets = build_process_scores()
    settings.marts_dir.mkdir(parents=True, exist_ok=True)
    settings.validation_dir.mkdir(parents=True, exist_ok=True)

    for name in ("process_scores", "overview", "ranking", "process_detail", "comparables"):
        frame = assets[name]
        output_path = settings.marts_dir / f"{name}.parquet"
        frame.to_parquet(output_path, index=False)
        logger.info("Guardado {} con {} filas.", output_path.name, len(frame))

    assets["ranking_export"].to_csv(
        settings.validation_dir / "ranking_meta_casanare.csv",
        index=False,
    )
    assets["paa_sample"].to_csv(
        settings.validation_dir / "paa_match_sample.csv",
        index=False,
    )
    update_join_audit(settings.docs_dir / "join-audit.md", assets["process_scores"])
    logger.info("Scoring provisional y artefactos de validación actualizados.")


if __name__ == "__main__":
    main()
