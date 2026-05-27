from __future__ import annotations

import pytest

from src.extract.state import (
    dataset_scope,
    ensure_dataset_state,
    fresh_manifest,
    load_manifest,
    update_dataset_state,
    validate_chunked_state,
    write_manifest,
)


def test_manifest_roundtrip(tmp_path) -> None:
    manifest_path = tmp_path / "manifest.json"
    manifest = fresh_manifest({"extract_scope": "demo"})
    state = ensure_dataset_state(
        manifest,
        dataset_key="paa_detail",
        dataset_id="9sue-ezhx",
        page_size=20000,
        mode="demo",
        scope=dataset_scope("demo", ["2025"], ["Meta"], ["7001"]),
        layout="chunked",
    )
    state["rows_written"] = 10
    update_dataset_state(manifest, "paa_detail", state)
    write_manifest(manifest_path, manifest)

    loaded = load_manifest(manifest_path, scope={})
    assert loaded["datasets"]["paa_detail"]["rows_written"] == 10


def test_validate_chunked_state_detects_mismatch(tmp_path) -> None:
    dataset_dir = tmp_path / "paa_detail"
    dataset_dir.mkdir()
    (dataset_dir / "part-000001.parquet").write_text("fake")
    state = {
        "part_count": 2,
    }
    with pytest.raises(ValueError):
        validate_chunked_state(dataset_dir, state)
