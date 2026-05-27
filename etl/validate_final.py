from __future__ import annotations

import json
import os
import subprocess
from urllib.error import URLError
from urllib.request import urlopen

from etl.common import ROOT, database_url, mongo_url
from etl.load_to_mongo import COLLECTIONS

REQUIRED_DOCS = [
    "docs/report/anteproyecto.md",
    "docs/report/reporte_final.md",
    "docs/data_dictionary.md",
    "docs/manual_usuario.md",
    "docs/testing_plan.md",
    "docs/testing_evidence.md",
    "docs/usability_survey_template.md",
    "docs/usability_results.md",
    "docs/ai_usage_disclosure.md",
    "docs/diagrams/architecture.mmd",
    "docs/diagrams/er_diagram.mmd",
    "docs/diagrams/er_model.mmd",
    "docs/diagrams/microservices.mmd",
    "docs/diagrams/pipeline.mmd",
    "docs/auditoria_estado_actual.md",
    "docs/project_report.md",
    "db/README.md",
    "db/migrations/001_schema.sql",
    "mongo/README.md",
    "slides/outline.md",
    "validation/README.md",
]


def run_command(command: list[str]) -> tuple[bool, str]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    output = (result.stdout + "\n" + result.stderr).strip()
    return result.returncode == 0, output[-4000:]


def check_postgres(blockers: list[str], evidence: dict[str, object]) -> None:
    try:
        import psycopg
    except ImportError:
        blockers.append("psycopg no esta instalado; ejecuta `uv sync --python 3.11 --extra dev`.")
        return
    try:
        with (
            psycopg.connect(database_url(), connect_timeout=3) as conn,
            conn.cursor() as cur,
        ):
            cur.execute(
                "SELECT count(*) FROM information_schema.tables "
                "WHERE table_schema='public'"
            )
            table_count = int(cur.fetchone()[0])
            cur.execute("SELECT count(*) FROM procurement_process")
            process_rows = int(cur.fetchone()[0])
        evidence["postgres_table_count"] = table_count
        evidence["procurement_process_rows"] = process_rows
        if table_count < 20:
            blockers.append(f"PostgreSQL tiene {table_count} tablas publicas; se requieren 20+.")
        if process_rows < 10000:
            blockers.append(
                f"procurement_process tiene {process_rows} filas; se requieren 10.000+."
            )
    except Exception as exc:
        blockers.append(f"No se pudo validar PostgreSQL en {database_url()}: {exc}")


def check_mongo(blockers: list[str], evidence: dict[str, object]) -> None:
    try:
        from pymongo import MongoClient
    except ImportError:
        blockers.append("pymongo no esta instalado; ejecuta `uv sync --python 3.11 --extra dev`.")
        return
    try:
        client = MongoClient(mongo_url(), serverSelectionTimeoutMS=3000)
        db = client.get_default_database()
        counts = {name: db[name].count_documents({}) for name in COLLECTIONS}
        evidence["mongo_counts"] = counts
        empty = [name for name, count in counts.items() if count <= 0]
        if empty:
            blockers.append(f"Colecciones Mongo sin documentos: {', '.join(empty)}.")
    except Exception as exc:
        blockers.append(f"No se pudo validar MongoDB en {mongo_url()}: {exc}")


def check_api_health(blockers: list[str], evidence: dict[str, object]) -> None:
    endpoints = {
        "contracts": os.getenv("CONTRACTS_SERVICE_URL", "http://localhost:8001").rstrip("/")
        + "/health",
        "risk": os.getenv("RISK_SERVICE_URL", "http://localhost:8002").rstrip("/") + "/health",
        "analytics": os.getenv("ANALYTICS_SERVICE_URL", "http://localhost:8003").rstrip("/")
        + "/health",
    }
    statuses: dict[str, str] = {}
    for name, url in endpoints.items():
        try:
            with urlopen(url, timeout=2) as response:
                statuses[name] = str(response.status)
        except (URLError, TimeoutError, OSError) as exc:
            statuses[name] = f"unavailable: {exc}"
    evidence["api_health"] = statuses
    unavailable = [name for name, status in statuses.items() if status != "200"]
    if unavailable:
        blockers.append(
            "Endpoints API no disponibles: "
            + ", ".join(f"{name}={statuses[name]}" for name in unavailable)
        )


def check_docs(blockers: list[str], evidence: dict[str, object]) -> None:
    missing = [path for path in REQUIRED_DOCS if not (ROOT / path).exists()]
    evidence["required_docs_present"] = len(REQUIRED_DOCS) - len(missing)
    if missing:
        blockers.append("Faltan documentos requeridos: " + ", ".join(missing))
    readme = (ROOT / "README.md").read_text() if (ROOT / "README.md").exists() else ""
    required_terms = ["make db-up", "make etl-demo", "make validate-final", "PostgreSQL", "MongoDB"]
    missing_terms = [term for term in required_terms if term not in readme]
    if missing_terms:
        blockers.append(
            "README no contiene comandos/terminos requeridos: " + ", ".join(missing_terms)
        )


def main() -> None:
    blockers: list[str] = []
    evidence: dict[str, object] = {}
    for command_name, command in {
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
        ok, output = run_command(command)
        evidence[command_name] = {"ok": ok, "output_tail": output}
        if not ok:
            blockers.append(f"Fallo `{command_name}`: {output}")
    check_postgres(blockers, evidence)
    check_mongo(blockers, evidence)
    check_api_health(blockers, evidence)
    check_docs(blockers, evidence)

    report = {"ok": not blockers, "blockers": blockers, "evidence": evidence}
    validation_dir = ROOT / "validation"
    validation_dir.mkdir(exist_ok=True)
    (validation_dir / "final_validation.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False)
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    raise SystemExit(0 if not blockers else 1)


if __name__ == "__main__":
    main()
