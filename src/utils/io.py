from __future__ import annotations

from pathlib import Path

import pandas as pd


def list_partition_parts(path: Path) -> list[Path]:
    if not path.exists():
        return []
    if path.is_file():
        return [path]
    return sorted(
        candidate
        for candidate in path.glob("part-*.parquet")
        if candidate.is_file()
    )


def read_parquet_flexible(path: Path) -> pd.DataFrame:
    if path.is_file():
        return pd.read_parquet(path)
    parts = list_partition_parts(path)
    if not parts:
        raise FileNotFoundError(f"No existen parquets válidos en {path}")
    frames = [pd.read_parquet(part) for part in parts]
    return pd.concat(frames, ignore_index=True)
