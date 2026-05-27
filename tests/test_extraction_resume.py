from __future__ import annotations

from collections import defaultdict

import polars as pl

from src.extract.secop_api import stream_dataset_to_parquet
from src.extract.state import fresh_manifest
from src.utils.config import Settings


def test_stream_dataset_to_parquet_resume_without_duplicates(tmp_path, monkeypatch) -> None:
    settings = Settings(
        root_dir=tmp_path,
        raw_dir=tmp_path / "data" / "raw",
        legacy_raw_dir=tmp_path / "data" / "legacy_raw",
        interim_dir=tmp_path / "data" / "interim",
        marts_dir=tmp_path / "data" / "marts",
        docs_dir=tmp_path / "docs",
        docs_legacy_dir=tmp_path / "docs" / "legacy",
        validation_dir=tmp_path / "validation",
        report_dir=tmp_path / "data" / "reports",
        manifest_path=tmp_path / "data" / "raw" / "manifest.json",
        extract_scope="demo",
        paa_years=["2025", "2026"],
        scope_departments=["Meta", "Casanare"],
        paa_page_size=2,
    )
    settings.ensure_directories()
    monkeypatch.setattr("src.extract.secop_api.get_settings", lambda: settings)
    monkeypatch.setattr("src.extract.secop_api.build_demo_entity_codes", lambda: ["7001"])

    pages = {
        0: [{"id": "1"}, {"id": "2"}],
        2: [{"id": "3"}, {"id": "4"}],
        4: [{"id": "5"}],
        5: [],
    }
    calls = defaultdict(int)

    def fake_fetch_page(_dataset_id: str, params: dict[str, object]) -> pl.DataFrame:
        offset = int(params["$offset"])
        calls[offset] += 1
        return pl.DataFrame(pages[offset])

    manifest = fresh_manifest({"extract_scope": "demo"})
    dataset_dir = settings.raw_dir / "paa_detail"

    state = stream_dataset_to_parquet(
        dataset_key="paa_detail",
        dataset_id="9sue-ezhx",
        params={"$limit": 2},
        output_dir=dataset_dir,
        fetch_page=fake_fetch_page,
        manifest=manifest,
        max_pages=1,
    )
    assert state["completed"] is False
    assert state["next_offset"] == 2
    assert len(list(dataset_dir.glob("part-*.parquet"))) == 1

    state = stream_dataset_to_parquet(
        dataset_key="paa_detail",
        dataset_id="9sue-ezhx",
        params={"$limit": 2},
        output_dir=dataset_dir,
        fetch_page=fake_fetch_page,
        manifest=manifest,
    )
    assert state["completed"] is True
    assert state["rows_written"] == 5
    assert len(list(dataset_dir.glob("part-*.parquet"))) == 3
    assert calls[0] == 1
