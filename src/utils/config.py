from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


class Settings(BaseModel):
    root_dir: Path = Field(default_factory=project_root)
    raw_dir: Path = Field(default_factory=lambda: project_root() / "data" / "raw")
    legacy_raw_dir: Path = Field(default_factory=lambda: project_root() / "data" / "legacy_raw")
    interim_dir: Path = Field(default_factory=lambda: project_root() / "data" / "interim")
    marts_dir: Path = Field(default_factory=lambda: project_root() / "data" / "marts")
    docs_dir: Path = Field(default_factory=lambda: project_root() / "docs")
    docs_legacy_dir: Path = Field(default_factory=lambda: project_root() / "docs" / "legacy")
    validation_dir: Path = Field(default_factory=lambda: project_root() / "validation")
    socrata_domain: str = "https://www.datos.gov.co"
    app_token_socrata: str | None = None
    request_timeout_seconds: float = 30.0
    request_retries: int = 3
    page_size: int = 50000
    paa_page_size: int = 20000
    random_state: int = 42
    start_date: str = "2025-01-01T00:00:00"
    end_date: str = "2026-12-31T23:59:59"
    scope_departments: list[str] = Field(default_factory=lambda: ["Meta", "Casanare"])
    extract_scope: str = "demo"
    extract_only: list[str] = Field(default_factory=list)
    paa_entity_codes: list[str] = Field(default_factory=list)
    paa_years: list[str] = Field(default_factory=lambda: ["2025", "2026"])
    paa_signal_mode: str = "pending"
    provisional_weights: dict[str, float] = Field(
        default_factory=lambda: {
            "anomaly": 0.45,
            "peer_deviation": 0.35,
            "rule": 0.20,
        }
    )
    min_text_chars: int = 40
    min_text_words: int = 6
    demo_top_k_comparables: int = 5
    report_dir: Path = Field(default_factory=lambda: project_root() / "data" / "reports")
    manifest_path: Path = Field(
        default_factory=lambda: project_root() / "data" / "raw" / "manifest.json"
    )

    def ensure_directories(self) -> None:
        for path in (
            self.raw_dir,
            self.legacy_raw_dir,
            self.interim_dir,
            self.marts_dir,
            self.docs_dir,
            self.docs_legacy_dir,
            self.validation_dir,
            self.report_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    token = os.getenv("APP_TOKEN_SOCRATA") or None
    product_source_mode = (os.getenv("PRODUCT_SOURCE_MODE") or "").strip().lower()
    extract_scope = os.getenv("EXTRACT_SCOPE") or "demo"
    extract_only = [
        item.strip()
        for item in (os.getenv("EXTRACT_ONLY") or "").split(",")
        if item.strip()
    ]
    paa_entity_codes = [
        item.strip()
        for item in (os.getenv("PAA_ENTITY_CODES") or "").split(",")
        if item.strip()
    ]
    paa_years = [
        item.strip()
        for item in (os.getenv("PAA_YEARS") or "2025,2026").split(",")
        if item.strip()
    ]
    paa_signal_mode = os.getenv("PAA_SIGNAL_MODE") or "pending"
    page_size = int(os.getenv("SOCRATA_PAGE_SIZE") or "50000")
    paa_page_size = int(os.getenv("PAA_PAGE_SIZE") or "20000")
    kwargs: dict[str, object] = {
        "app_token_socrata": token,
        "extract_scope": extract_scope,
        "extract_only": extract_only,
        "paa_entity_codes": paa_entity_codes,
        "paa_years": paa_years,
        "paa_signal_mode": paa_signal_mode,
        "page_size": page_size,
        "paa_page_size": paa_page_size,
    }
    if product_source_mode == "sample":
        sample_base = project_root() / "data" / "sample"
        kwargs.update(
            {
                "raw_dir": sample_base / "product_raw",
                "interim_dir": sample_base / "product_interim",
                "manifest_path": sample_base / "product_raw" / "manifest.json",
            }
        )
    settings = Settings(**kwargs)
    settings.ensure_directories()
    return settings
