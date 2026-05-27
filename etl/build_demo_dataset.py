from __future__ import annotations

import json

from etl.common import ROOT, read_local_demo_sources


def main() -> None:
    sources = read_local_demo_sources(limit=10000)
    output_dir = ROOT / "validation"
    output_dir.mkdir(exist_ok=True)
    summary = {
        "demo_process_rows": int(len(sources["processes"])),
        "available_contract_rows": int(len(sources["contracts"])),
        "available_paa_rows": int(len(sources["paa"])),
        "source": "local_parquet_fallback",
    }
    (output_dir / "demo_dataset_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False)
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
