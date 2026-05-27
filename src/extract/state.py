from __future__ import annotations

import json
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

MANIFEST_VERSION = 2


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def fresh_manifest(scope: dict[str, Any]) -> dict[str, Any]:
    return {
        "version": MANIFEST_VERSION,
        "scope": scope,
        "datasets": {},
    }


def load_manifest(path: Path, scope: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return fresh_manifest(scope)
    data = json.loads(path.read_text())
    if data.get("version") != MANIFEST_VERSION or "datasets" not in data:
        return fresh_manifest(scope)
    return data


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


def dataset_scope(
    mode: str,
    years: list[str],
    departments: list[str],
    entity_codes: list[str],
) -> dict[str, Any]:
    return {
        "mode": mode,
        "years": years,
        "departments": departments,
        "entity_codes": entity_codes,
    }


def ensure_dataset_state(
    manifest: dict[str, Any],
    *,
    dataset_key: str,
    dataset_id: str,
    page_size: int,
    mode: str,
    scope: dict[str, Any],
    layout: str,
) -> dict[str, Any]:
    existing = manifest["datasets"].get(dataset_key)
    if existing:
        return deepcopy(existing)
    state = {
        "dataset_key": dataset_key,
        "dataset_id": dataset_id,
        "page_size": page_size,
        "mode": mode,
        "scope": scope,
        "layout": layout,
        "next_offset": 0,
        "rows_written": 0,
        "part_count": 0,
        "started_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
        "completed": False,
    }
    manifest["datasets"][dataset_key] = deepcopy(state)
    return state


def update_dataset_state(
    manifest: dict[str, Any],
    dataset_key: str,
    state: dict[str, Any],
) -> None:
    state["updated_at"] = utc_now_iso()
    manifest["datasets"][dataset_key] = deepcopy(state)


def validate_chunked_state(dataset_dir: Path, state: dict[str, Any]) -> None:
    parts = sorted(dataset_dir.glob("part-*.parquet")) if dataset_dir.exists() else []
    if len(parts) != int(state.get("part_count", 0)):
        raise ValueError(
            f"Inconsistencia entre manifest y chunks de {dataset_dir.name}: "
            f"manifest={state.get('part_count', 0)}, disco={len(parts)}"
        )
    expected = [f"part-{idx:06d}.parquet" for idx in range(1, len(parts) + 1)]
    current = [part.name for part in parts]
    if expected != current:
        raise ValueError(f"Chunks no contiguos o renombrados en {dataset_dir.name}.")
