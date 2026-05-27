from __future__ import annotations

import json
from datetime import UTC, datetime

from etl.common import ROOT, mongo_url, read_local_demo_sources

COLLECTIONS = [
    "raw_process_snapshots",
    "etl_run_logs",
    "risk_event_logs",
    "report_snapshots",
    "user_action_logs",
]

ACADEMIC_COLLECTION_ALIASES = {
    "raw_snapshots": "raw_process_snapshots",
    "ingestion_logs": "etl_run_logs",
    "join_audits": "risk_event_logs",
    "generated_reports": "report_snapshots",
    "dashboard_events": "user_action_logs",
}


def require_pymongo():
    try:
        import pymongo
    except ImportError as exc:
        raise SystemExit(
            "Falta pymongo. Ejecuta `uv sync --python 3.11 --extra dev` antes de cargar MongoDB."
        ) from exc
    return pymongo.MongoClient


def main() -> None:
    mongo_client = require_pymongo()
    sources = read_local_demo_sources(limit=250)
    client = mongo_client(mongo_url(), serverSelectionTimeoutMS=3000)
    db = client.get_default_database()
    now = datetime.now(UTC)

    for name in [*COLLECTIONS, *ACADEMIC_COLLECTION_ALIASES]:
        db.create_collection(name) if name not in db.list_collection_names() else None

    process_docs = []
    for row in sources["processes"].head(100).fillna("").to_dict(orient="records"):
        process_docs.append(
            {
                "process_key": str(row.get("id_del_proceso", "")),
                "source_dataset": "p6dx-8zbt",
                "snapshot": row,
                "loaded_at": now,
            }
        )
    if process_docs:
        db.raw_process_snapshots.delete_many({})
        db.raw_process_snapshots.insert_many(process_docs)
        db.raw_snapshots.delete_many({})
        db.raw_snapshots.insert_many(process_docs)

    ingestion_log = {
        "status": "completed",
        "source": "local_parquet_fallback",
        "process_snapshots": len(process_docs),
        "created_at": now,
    }
    risk_log = {
        "event": "demo_risk_scoring_ready",
        "message": "Priorizacion de revision humana; no acusacion.",
        "created_at": now,
    }
    report_snapshot = {
        "report": "reporte_final",
        "status": "draft",
        "created_at": now,
    }
    user_action = {
        "action": "mongo_demo_load",
        "created_at": now,
    }
    db.etl_run_logs.insert_one(ingestion_log)
    db.ingestion_logs.insert_one(ingestion_log)
    db.risk_event_logs.insert_one(risk_log)
    db.join_audits.insert_one({**risk_log, "audit_type": "scoring_join_ready"})
    db.report_snapshots.insert_one(report_snapshot)
    db.generated_reports.insert_one(report_snapshot)
    db.user_action_logs.insert_one(user_action)
    db.dashboard_events.insert_one(user_action)

    summary = {name: db[name].count_documents({}) for name in COLLECTIONS}
    validation_dir = ROOT / "validation"
    validation_dir.mkdir(exist_ok=True)
    (validation_dir / "mongo_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False)
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
