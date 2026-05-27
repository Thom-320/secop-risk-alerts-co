from __future__ import annotations

import argparse
import json
from typing import Any

from etl.common import ROOT, database_url, require_psycopg

SCHEMA_FILES = [
    "001_schema.sql",
    "002_indexes.sql",
    "003_triggers.sql",
    "004_views_analytics.sql",
    "005_seed_reference_data.sql",
    "007_security_roles.sql",
]


def reset_schema(conn: Any) -> None:
    with conn.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS public CASCADE")
        cur.execute("CREATE SCHEMA public")
        cur.execute("GRANT ALL ON SCHEMA public TO contratia")
        cur.execute("GRANT ALL ON SCHEMA public TO public")
    conn.commit()


def apply_schema(conn: Any) -> list[str]:
    sql_dir = ROOT / "sql"
    applied: list[str] = []
    with conn.cursor() as cur:
        for name in SCHEMA_FILES:
            path = sql_dir / name
            if path.exists():
                cur.execute(path.read_text())
                applied.append(name)
    conn.commit()
    return applied


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply PostgreSQL schema without loading data.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop and recreate public schema first.",
    )
    args = parser.parse_args()

    psycopg, _dict_row = require_psycopg()
    with psycopg.connect(database_url()) as conn:
        if args.reset:
            reset_schema(conn)
        applied = apply_schema(conn)
    print(json.dumps({"status": "completed", "reset": args.reset, "applied": applied}, indent=2))


if __name__ == "__main__":
    main()
