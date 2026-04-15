from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field

DEFAULT_ENTITIES = [
    "SUBRED INTEGRADA DE SERVICIOS DE SALUD NORTE E.S.E. (OFICIAL)",
    "SUBRED INTEGRADA DE SERVICIOS DE SALUD SUR E.S.E.**",
    "SUBRED INTEGRADA DE SERVICIOS DE SALUD SUR OCCIDENTE ESE.",
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


class Settings(BaseModel):
    root_dir: Path = Field(default_factory=project_root)
    raw_dir: Path = Field(default_factory=lambda: project_root() / "data" / "raw")
    interim_dir: Path = Field(default_factory=lambda: project_root() / "data" / "interim")
    marts_dir: Path = Field(default_factory=lambda: project_root() / "data" / "marts")
    docs_dir: Path = Field(default_factory=lambda: project_root() / "docs")
    socrata_domain: str = "https://www.datos.gov.co"
    app_token_socrata: str | None = None
    request_timeout_seconds: float = 30.0
    request_retries: int = 3
    page_size: int = 50000
    random_state: int = 42
    start_date: str = "2025-01-01T00:00:00"
    end_date: str = "2026-12-31T23:59:59"
    scope_entities: list[str] = Field(default_factory=lambda: list(DEFAULT_ENTITIES))

    def ensure_directories(self) -> None:
        for path in (self.raw_dir, self.interim_dir, self.marts_dir, self.docs_dir):
            path.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    token = os.getenv("APP_TOKEN_SOCRATA") or None
    settings = Settings(app_token_socrata=token)
    settings.ensure_directories()
    return settings

