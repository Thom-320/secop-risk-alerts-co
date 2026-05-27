from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_pipeline_public_packaging_exists() -> None:
    for relative in [
        "db/README.md",
        "db/migrations/001_schema.sql",
        "db/triggers/001_auditoria.sql",
        "db/views/001_analytics.sql",
        "db/procedures/001_scoring.sql",
        "mongo/README.md",
        "mongo/seed_demo.py",
        "data/sample/README.md",
        "validation/README.md",
        "slides/outline.md",
    ]:
        assert (ROOT / relative).exists()
