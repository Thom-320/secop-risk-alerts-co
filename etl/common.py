from __future__ import annotations

import os
import re
import subprocess
import sys
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE_URL = "postgresql://contratia:contratia@localhost:55432/contratia"
DEFAULT_MONGO_URL = "mongodb://localhost:27018/contratia"


def database_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def mongo_url() -> str:
    return os.getenv("MONGO_URL", DEFAULT_MONGO_URL)


def only_digits(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    digits = re.sub(r"\D+", "", str(value))
    return digits or None


def clean_text(value: Any, default: str = "") -> str:
    if value is None or pd.isna(value):
        return default
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text or default


def clean_key(value: Any, default: str) -> str:
    text = clean_text(value)
    return text if text else default


def to_decimal(value: Any) -> Decimal:
    if value is None or pd.isna(value) or value == "":
        return Decimal("0")
    try:
        return Decimal(str(value).replace(",", "."))
    except (InvalidOperation, ValueError):
        return Decimal("0")


def to_int(value: Any) -> int:
    if value is None or pd.isna(value) or value == "":
        return 0
    try:
        return int(float(str(value).replace(",", ".")))
    except ValueError:
        return 0


def to_date(value: Any) -> date | None:
    if value is None or pd.isna(value) or value == "":
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date()


def modality_family(value: Any) -> str:
    text = clean_text(value).lower()
    if "licitaci" in text:
        return "licitacion"
    if "selecci" in text and "abreviada" in text:
        return "seleccion_abreviada"
    if "concurso" in text:
        return "concurso"
    if "directa" in text:
        return "contratacion_directa"
    if "minima" in text or "mínima" in text:
        return "minima_cuantia"
    return "otros"


def stable_missing_identifier(prefix: str, value: str) -> str:
    import hashlib

    normalized = clean_text(value, "sin_nombre").lower()
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}-{digest}"


def _read_sample_sources(limit: int | None = None) -> dict[str, pd.DataFrame] | None:
    sample_dir = ROOT / "data" / "sample" / "fixtures"
    processes_csv = sample_dir / "processes.csv"
    contracts_csv = sample_dir / "contracts.csv"
    paa_csv = sample_dir / "paa.csv"
    if not processes_csv.exists():
        return None
    processes = pd.read_csv(processes_csv)
    contracts = pd.read_csv(contracts_csv) if contracts_csv.exists() else pd.DataFrame()
    paa = pd.read_csv(paa_csv) if paa_csv.exists() else pd.DataFrame()
    if limit:
        processes = processes.head(limit)
    return {"processes": processes, "contracts": contracts, "paa": paa}


def _read_generated_sources(limit: int | None = None) -> dict[str, pd.DataFrame] | None:
    generated_dir = ROOT / "data" / "sample" / "generated"
    processes_path = generated_dir / "processes.parquet"
    if not processes_path.exists():
        return None
    processes = pd.read_parquet(processes_path)
    contracts_path = generated_dir / "contracts.parquet"
    paa_path = generated_dir / "paa.parquet"
    contracts = pd.read_parquet(contracts_path) if contracts_path.exists() else pd.DataFrame()
    paa = pd.read_parquet(paa_path) if paa_path.exists() else pd.DataFrame()
    if limit:
        processes = processes.head(limit)
    return {"processes": processes, "contracts": contracts, "paa": paa}


def _download_demo_sources_if_requested(limit: int | None) -> dict[str, pd.DataFrame] | None:
    if os.getenv("DEMO_SOURCE_MODE", "").lower() != "download" and os.getenv(
        "EXTRACT_SCOPE", ""
    ).lower() != "demo":
        return None
    command = [sys.executable, "-m", "etl.download_demo_sources"]
    if limit:
        command.extend(["--limit", str(limit)])
    subprocess.run(command, cwd=ROOT, check=True)
    return _read_generated_sources(limit=limit)


def read_local_demo_sources(limit: int | None = None) -> dict[str, pd.DataFrame]:
    processes_path = ROOT / "data" / "legacy_raw" / "processes.parquet"
    contracts_path = ROOT / "data" / "legacy_raw" / "contracts.parquet"
    paa_dir = ROOT / "data" / "raw" / "paa_detail"
    if processes_path.exists() and contracts_path.exists():
        processes = pd.read_parquet(processes_path)
        contracts = pd.read_parquet(contracts_path)
        paa_parts = sorted(paa_dir.glob("*.parquet")) if paa_dir.exists() else []
        paa = (
            pd.concat([pd.read_parquet(path) for path in paa_parts], ignore_index=True)
            if paa_parts
            else pd.DataFrame()
        )
        if limit:
            processes = processes.head(limit)
        return {"processes": processes, "contracts": contracts, "paa": paa}

    readers = (_read_generated_sources, _read_sample_sources, _download_demo_sources_if_requested)
    for reader in readers:
        sources = reader(limit)
        if sources is not None:
            return sources

    raise FileNotFoundError(
        "No se encontraron fuentes demo. Agrega Parquet locales en data/legacy_raw, "
        "usa fixtures en data/sample/fixtures o ejecuta "
        "`DEMO_SOURCE_MODE=download python -m etl.download_demo_sources --limit 10000`."
    )


def require_psycopg():
    try:
        import psycopg
        from psycopg.rows import dict_row
    except ImportError as exc:
        raise SystemExit(
            "Falta psycopg. Ejecuta `uv sync --python 3.11 --extra dev` antes de cargar PostgreSQL."
        ) from exc
    return psycopg, dict_row
