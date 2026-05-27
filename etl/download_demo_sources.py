from __future__ import annotations

import argparse
import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

from etl.common import ROOT

SOCRATA_BASE = "https://www.datos.gov.co/resource/p6dx-8zbt.json"


def fetch_processes(limit: int, offset: int = 0) -> pd.DataFrame:
    params = {
        "$limit": str(limit),
        "$offset": str(offset),
        "$order": "fecha_de_publicacion_del DESC",
    }
    url = f"{SOCRATA_BASE}?{urlencode(params)}"
    headers = {}
    token = os.getenv("APP_TOKEN_SOCRATA")
    if token:
        headers["X-App-Token"] = token
    request = Request(url, headers=headers)
    with urlopen(request, timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return pd.DataFrame(payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download a reproducible SECOP II demo sample.")
    parser.add_argument("--limit", type=int, default=10000)
    parser.add_argument("--offset", type=int, default=0)
    args = parser.parse_args()

    out_dir = ROOT / "data" / "sample" / "generated"
    out_dir.mkdir(parents=True, exist_ok=True)
    processes = fetch_processes(args.limit, args.offset)
    if processes.empty:
        raise SystemExit("Socrata no retorno filas para la muestra demo.")
    processes.to_parquet(out_dir / "processes.parquet", index=False)
    print(
        json.dumps(
            {
                "status": "completed",
                "source": "p6dx-8zbt",
                "rows": len(processes),
                "path": str(out_dir / "processes.parquet"),
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
