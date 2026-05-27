from __future__ import annotations

import os
from typing import Any

from fastapi import HTTPException

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://contratia:contratia@localhost:55432/contratia")


def require_psycopg():
    try:
        import psycopg
        from psycopg.rows import dict_row
    except ImportError as exc:
        raise HTTPException(status_code=503, detail="psycopg no esta instalado") from exc
    return psycopg, dict_row


def fetch_all(sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    psycopg, dict_row = require_psycopg()
    try:
        with (
            psycopg.connect(DATABASE_URL, row_factory=dict_row, connect_timeout=3) as conn,
            conn.cursor() as cur,
        ):
            cur.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Base de datos no disponible: {exc}") from exc


def fetch_one(sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any]:
    rows = fetch_all(sql, params)
    if not rows:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return rows[0]


def execute(sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any]:
    psycopg, dict_row = require_psycopg()
    try:
        with psycopg.connect(DATABASE_URL, row_factory=dict_row, connect_timeout=3) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                row = cur.fetchone()
            conn.commit()
            return dict(row) if row else {}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Base de datos no disponible: {exc}") from exc
