from __future__ import annotations

import json

from etl.common import ROOT, read_local_demo_sources


def validate_sources() -> dict[str, object]:
    sources = read_local_demo_sources()
    summary = {
        "mode": "local_fallback",
        "available": True,
        "process_rows": int(len(sources["processes"])),
        "contract_rows": int(len(sources["contracts"])),
        "paa_rows": int(len(sources["paa"])),
        "meets_10000_process_requirement": bool(len(sources["processes"]) >= 10000),
        "notes": [
            "Fallback local usado para demo reproducible.",
            "La extraccion Socrata en vivo queda soportada por el extractor existente del MVP.",
        ],
    }
    validation_dir = ROOT / "validation"
    validation_dir.mkdir(exist_ok=True)
    (validation_dir / "source_validation.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False)
    )
    return summary


def main() -> None:
    summary = validate_sources()
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
