from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RESULTS_PATH = ROOT / "validation" / "manual_review_results.csv"
OUTPUT_PATH = ROOT / "validation" / "human_validation_summary.json"


def require_real_reviews(frame: pd.DataFrame) -> pd.DataFrame:
    required = {
        "sample_flag",
        "review_id",
        "process_id",
        "useful_alert",
        "clear_reason",
        "is_real_review",
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise SystemExit("Faltan columnas de validación humana: " + ", ".join(missing))

    sample_rows = frame["sample_flag"].astype(str).str.upper().eq("SAMPLE")
    if sample_rows.any():
        raise SystemExit("manual_review_results.csv contiene filas SAMPLE; no se resumen.")

    real_rows = frame["is_real_review"].astype(str).str.upper().eq("TRUE")
    if not real_rows.any():
        raise SystemExit("No hay filas con is_real_review=TRUE; no se fabrican resultados.")
    return frame[real_rows].copy()


def yes_rate(series: pd.Series) -> float:
    normalized = series.astype(str).str.strip().str.lower()
    return float(normalized.isin({"yes", "si", "sí", "true", "1", "util", "útil"}).mean())


def main() -> None:
    if not RESULTS_PATH.exists():
        raise SystemExit(
            "No existe validation/manual_review_results.csv. "
            "Ejecute primero el protocolo con revisores reales."
        )

    real = require_real_reviews(pd.read_csv(RESULTS_PATH))
    top20 = real.head(20)
    summary = {
        "review_count": int(len(real)),
        "precision_at_20": yes_rate(top20["useful_alert"]) if not top20.empty else None,
        "useful_explanation_rate": yes_rate(real["clear_reason"]),
        "paa_match_correct_rate": yes_rate(real["paa_match_correct"])
        if "paa_match_correct" in real.columns
        else None,
        "comparable_useful_rate": yes_rate(real["comparable_useful"])
        if "comparable_useful" in real.columns
        else None,
    }
    OUTPUT_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
