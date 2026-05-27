from __future__ import annotations

import json
import subprocess
import unicodedata
from pathlib import Path
from typing import Any

import pandas as pd

from etl.common import ROOT

REQUIRED_DOCS = [
    "README.md",
    "docs/product_route.md",
    "docs/contest_submission_checklist.md",
    "docs/demo-guide.md",
    "docs/demo-casebook.md",
    "docs/model-card.md",
    "docs/ethics-note.md",
    "docs/validation-summary.md",
    "docs/human_validation_protocol.md",
    "docs/human_validation_results.md",
    "docs/usability_results.md",
    "docs/data-cards/secop-ii-procesos.md",
    "docs/data-cards/secop-integrado.md",
    "docs/data-cards/paa-detalle.md",
    "docs/data-cards/control-fiscal.md",
    "docs/fairness_territorial.md",
    "docs/deployment.md",
]

REQUIRED_MARTS = [
    "overview.parquet",
    "ranking.parquet",
    "process_detail.parquet",
    "comparables.parquet",
]

FORBIDDEN_CLAIMS = [
    "detecta corrupcion",
    "detecta corrupción",
    "prueba fraude",
    "culpable",
    "irregularidad confirmada",
    "fraude probado",
    "proveedor corrupto",
    "corrupcion confirmada",
    "corrupción confirmada",
]

SCAN_PATHS = ["README.md", "PRODUCT.md", "SECURITY.md", "src", "dashboard", "docs", "slides"]
SCAN_EXCLUDES = (
    "docs/agent_handoffs/",
    "docs/audit/",
    "docs/legacy/",
)


def normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def run_command(command: list[str]) -> dict[str, Any]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    output = (result.stdout + "\n" + result.stderr).strip()
    return {"ok": result.returncode == 0, "output_tail": output[-4000:]}


def tracked_text_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", *SCAN_PATHS],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    paths: list[Path] = []
    for line in result.stdout.splitlines():
        if line.startswith(SCAN_EXCLUDES):
            continue
        if line.endswith((".png", ".jpg", ".jpeg", ".pdf", ".pptx")):
            continue
        path = ROOT / line
        if path.is_file():
            paths.append(path)
    return paths


def check_docs(blockers: list[str], evidence: dict[str, Any]) -> None:
    missing = []
    empty = []
    for relative in REQUIRED_DOCS:
        path = ROOT / relative
        if not path.exists():
            missing.append(relative)
        elif not path.read_text(errors="ignore").strip():
            empty.append(relative)
    evidence["required_docs"] = {
        "expected": len(REQUIRED_DOCS),
        "missing": missing,
        "empty": empty,
    }
    if missing:
        blockers.append("Faltan documentos de producto: " + ", ".join(missing))
    if empty:
        blockers.append("Documentos de producto vacios: " + ", ".join(empty))


def check_marts(blockers: list[str], evidence: dict[str, Any]) -> None:
    marts_dir = ROOT / "data" / "marts"
    missing = [name for name in REQUIRED_MARTS if not (marts_dir / name).exists()]
    evidence["required_marts"] = {"missing": missing}
    if missing:
        blockers.append(
            "Faltan marts del producto: "
            + ", ".join(missing)
            + ". Ejecute make product-pipeline."
        )
        return
    ranking = pd.read_parquet(marts_dir / "ranking.parquet")
    evidence["ranking_rows"] = int(len(ranking))
    if ranking.empty:
        blockers.append("ranking.parquet no contiene filas. Ejecute make product-pipeline.")


def check_language(blockers: list[str], evidence: dict[str, Any]) -> None:
    violations: list[dict[str, str]] = []
    normalized_patterns = [normalize(pattern) for pattern in FORBIDDEN_CLAIMS]
    for path in tracked_text_files():
        lines = normalize(path.read_text(errors="ignore")).splitlines()
        for original, pattern in zip(FORBIDDEN_CLAIMS, normalized_patterns, strict=False):
            for line in lines:
                if pattern in line and f"no {pattern}" not in line:
                    violations.append({"path": str(path.relative_to(ROOT)), "claim": original})
                    break
    evidence["forbidden_language_violations"] = violations
    if violations:
        blockers.append(
            "Lenguaje publico prohibido encontrado: "
            + "; ".join(f"{item['path']} -> {item['claim']}" for item in violations[:10])
        )


def main() -> None:
    blockers: list[str] = []
    evidence: dict[str, Any] = {"mode": "product-lean"}

    for name, command in {
        "lint": ["uv", "run", "--python", "3.11", "--extra", "dev", "ruff", "check", "."],
        "test": [
            "uv",
            "run",
            "--python",
            "3.11",
            "--extra",
            "dev",
            "python",
            "-m",
            "pytest",
            "-q",
            "-m",
            "not integration",
        ],
    }.items():
        result = run_command(command)
        evidence[name] = result
        if not result["ok"]:
            blockers.append(f"Fallo `{name}`: {result['output_tail']}")

    check_docs(blockers, evidence)
    check_marts(blockers, evidence)
    check_language(blockers, evidence)

    report = {
        "mode": "product-lean",
        "ok": not blockers,
        "blockers": blockers,
        "evidence": evidence,
    }
    validation_dir = ROOT / "validation"
    validation_dir.mkdir(exist_ok=True)
    (validation_dir / "product_validation.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False)
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    raise SystemExit(0 if not blockers else 1)


if __name__ == "__main__":
    main()
