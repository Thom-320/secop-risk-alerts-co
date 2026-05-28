from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from etl.common import database_url, mongo_url, require_psycopg  # noqa: E402


def to_decimal(value: Any) -> Decimal:
    if value is None or pd.isna(value) or value == "":
        return Decimal("0")
    try:
        return Decimal(str(value).replace(",", "."))
    except (InvalidOperation, ValueError):
        return Decimal("0")


def to_int(value: Any) -> int:
    if value is None or pd.isna(value) or value == "":
        return 0
    try:
        return int(float(str(value)))
    except ValueError:
        return 0


def clean_text(value: Any, default: str = "") -> str:
    if value is None or pd.isna(value):
        return default
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text or default


def one(conn: Any, sql: str, params: tuple[Any, ...]) -> Any:
    cur = conn.cursor()
    cur.execute(sql, params)
    row = cur.fetchone()
    cur.close()
    return row[0] if row else None


def load_processes(
    conn: Any, scores: pd.DataFrame,
) -> dict[str, int]:
    """Upsert all scored processes into PostgreSQL."""
    process_ids: dict[str, int] = {}
    batch_size = 500
    rows = list(scores.iterrows())
    total = len(rows)

    for batch_start in range(0, total, batch_size):
        batch = rows[batch_start:batch_start + batch_size]
        for _idx, row in batch:
            dept_name = clean_text(row.get("department"), "Sin departamento")
            department_id = int(one(
                conn,
                "INSERT INTO department(name) VALUES (%s) "
                "ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name "
                "RETURNING department_id",
                (dept_name,),
            ))
            entity_id = int(one(
                conn,
                """
                INSERT INTO public_entity(
                    entity_code, nit, name, department_id, entity_order
                )
                VALUES (
                    NULLIF(%s, ''), NULLIF(%s, ''), %s, %s, %s
                )
                ON CONFLICT (entity_code) DO UPDATE
                SET nit = COALESCE(EXCLUDED.nit, public_entity.nit),
                    name = EXCLUDED.name,
                    department_id = EXCLUDED.department_id,
                    entity_order = EXCLUDED.entity_order
                RETURNING entity_id
                """,
                (
                    clean_text(row.get("entity_code")),
                    clean_text(row.get("entity_nit")),
                    clean_text(row.get("entity_name"), "Entidad sin nombre"),
                    department_id,
                    clean_text(row.get("entity_order"), ""),
                ),
            ))
            mod_name = clean_text(row.get("modality"), "Sin modalidad")
            mod_family = clean_text(row.get("modality_family"), "otros")
            modality_id = int(one(
                conn,
                "INSERT INTO modality(name, family) VALUES (%s, %s) "
                "ON CONFLICT (name) DO UPDATE "
                "SET family = EXCLUDED.family RETURNING modality_id",
                (mod_name, mod_family),
            ))

            provider_id = None
            prov_name = clean_text(row.get("provider_name"))
            prov_nit = clean_text(row.get("provider_nit"))
            if prov_name or prov_nit:
                if not prov_name:
                    prov_name = f"Proveedor {prov_nit}"
                if not prov_nit:
                    import hashlib
                    digest = hashlib.sha256(
                        prov_name.lower().encode("utf-8"),
                    ).hexdigest()[:16]
                    prov_nit = f"sin-nit-{digest}"
                provider_id = int(one(
                    conn,
                    "INSERT INTO provider(nit, name) VALUES (%s, %s) "
                    "ON CONFLICT (nit) DO UPDATE SET name = EXCLUDED.name "
                    "RETURNING provider_id",
                    (prov_nit, prov_name),
                ))

            process_key = clean_text(row.get("process_key"))
            pub_date = row.get("publication_date")
            if pd.isna(pub_date):
                pub_date = None
            award_date = row.get("award_date")
            if pd.isna(award_date):
                award_date = None
            process_id = int(one(
                conn,
                """
                INSERT INTO procurement_process(
                    process_key, process_reference, entity_id, modality_id,
                    title, description, status, publication_date, award_date,
                    base_price, awarded_total, duration_days, response_count,
                    invited_suppliers, unique_suppliers, provider_id,
                    source_url, source_dataset_id
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, 'p6dx-8zbt'
                )
                ON CONFLICT (process_key) DO UPDATE
                SET title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    status = EXCLUDED.status,
                    base_price = EXCLUDED.base_price,
                    awarded_total = EXCLUDED.awarded_total,
                    provider_id = EXCLUDED.provider_id,
                    modality_id = EXCLUDED.modality_id
                RETURNING process_id
                """,
                (
                    process_key,
                    clean_text(row.get("process_reference")),
                    entity_id,
                    modality_id,
                    clean_text(
                        row.get("process_title"), "Proceso sin titulo",
                    ),
                    clean_text(row.get("process_description"), ""),
                    clean_text(row.get("procedure_state"), "sin_estado"),
                    pub_date,
                    award_date,
                    to_decimal(row.get("base_price")),
                    to_decimal(row.get("awarded_total")),
                    to_int(row.get("duration_days")),
                    to_int(row.get("response_count")),
                    to_int(row.get("invited_suppliers")),
                    to_int(row.get("unique_suppliers")),
                    provider_id,
                    clean_text(row.get("process_url")),
                ),
            ))
            process_ids[process_key] = process_id
        conn.commit()
        if batch_start % 5000 == 0 and batch_start > 0:
            print(f"    {batch_start}/{total} procesos...")

    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO administrative_hierarchy(
                parent_node_id, node_type, label
            )
            VALUES (NULL, 'country', 'Colombia')
            ON CONFLICT DO NOTHING;
            WITH country AS (
                SELECT node_id FROM administrative_hierarchy
                WHERE node_type = 'country' AND label = 'Colombia'
                LIMIT 1
            )
            INSERT INTO administrative_hierarchy(
                parent_node_id, node_type, label
            )
            SELECT country.node_id, 'department', d.name
            FROM department d CROSS JOIN country
            ON CONFLICT DO NOTHING;
        """)
    conn.commit()

    return process_ids


def load_risk_assessments(
    conn: Any,
    scores: pd.DataFrame,
    process_ids: dict[str, int],
) -> int:
    """Delete old assessments and load real IA scores."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM risk_reason")
        cur.execute("DELETE FROM risk_assessment")
    conn.commit()

    loaded = 0
    batch_size = 500
    rows = list(scores.iterrows())

    for batch_start in range(0, len(rows), batch_size):
        batch = rows[batch_start:batch_start + batch_size]
        for _idx, row in batch:
            process_key = clean_text(row.get("process_key"))
            process_id = process_ids.get(process_key)
            if not process_id:
                continue

            explanation = clean_text(
                row.get("reasons"), "Sin señales fuertes visibles",
            )
            ra_id = int(one(
                conn,
                """
                INSERT INTO risk_assessment(
                    process_id, priority_score, confidence_score,
                    anomaly_score, peer_deviation_score, rule_score,
                    explanation
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING risk_assessment_id
                """,
                (
                    process_id,
                    to_decimal(row.get("priority_score")),
                    to_decimal(row.get("confidence_score")),
                    to_decimal(row.get("anomaly_score")),
                    to_decimal(row.get("peer_deviation_score")),
                    to_decimal(row.get("rule_score")),
                    explanation,
                ),
            ))

            snippets = row.get("reason_snippets")
            if (
                snippets is not None
                and hasattr(snippets, '__iter__')
                and not isinstance(snippets, str)
            ):
                try:
                    for snippet in list(snippets):
                        if snippet:
                            one(
                                conn,
                                "INSERT INTO risk_reason("
                                "risk_assessment_id, reason_text, "
                                "contribution"
                                ") VALUES (%s, %s, 0) "
                                "RETURNING risk_reason_id",
                                (ra_id, clean_text(snippet)),
                            )
                except (TypeError, ValueError):
                    pass
            loaded += 1
        conn.commit()
        if batch_start % 5000 == 0 and batch_start > 0:
            print(f"    {batch_start}/{len(rows)} evaluaciones...")

    return loaded


def load_paa_matches(
    conn: Any,
    scores: pd.DataFrame,
    process_ids: dict[str, int],
) -> int:
    """Load real PAA matches into paa_process_match."""
    matched = scores[
        scores["paa_match_status"] != "none"
    ].copy()
    if matched.empty:
        return 0

    loaded = 0
    with conn.cursor() as cur:
        cur.execute("DELETE FROM paa_process_match")
    conn.commit()

    one(
        conn,
        "INSERT INTO annual_procurement_plan("
        "plan_key, entity_id, year, version"
        ") VALUES ('sync-default-plan', 1, 2025, 'sync') "
        "ON CONFLICT (plan_key) DO NOTHING RETURNING plan_id",
        (),
    )
    conn.commit()

    for _idx, row in matched.iterrows():
        process_key = clean_text(row.get("process_key"))
        process_id = process_ids.get(process_key)
        if not process_id:
            continue

        paa_item_id_raw = clean_text(row.get("paa_item_id"))
        if not paa_item_id_raw:
            continue

        item_id = int(one(
            conn,
            """
            INSERT INTO paa_item(
                item_key, plan_id, description, planned_value
            )
            VALUES (
                %s,
                (SELECT plan_id FROM annual_procurement_plan
                 WHERE plan_key = 'sync-default-plan' LIMIT 1),
                %s, %s
            )
            ON CONFLICT (item_key) DO UPDATE
            SET description = EXCLUDED.description
            RETURNING paa_item_id
            """,
            (
                paa_item_id_raw,
                clean_text(row.get("paa_text"), "Item PAA"),
                to_decimal(row.get("planned_value")),
            ),
        ))

        method = clean_text(row.get("paa_match_method"), "semantic")
        confidence = to_decimal(row.get("paa_match_confidence"))
        status = clean_text(row.get("paa_match_status"), "none")

        one(
            conn,
            """
            INSERT INTO paa_process_match(
                paa_item_id, process_id, method, confidence, status
            )
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (paa_item_id, process_id) DO UPDATE
            SET confidence = EXCLUDED.confidence,
                status = EXCLUDED.status
            RETURNING paa_process_match_id
            """,
            (item_id, process_id, method, confidence, status),
        )
        loaded += 1
        if loaded % 5000 == 0:
            conn.commit()
            print(f"    {loaded} PAA matches...")
    conn.commit()
    return loaded


def load_semantic_comparables(conn: Any) -> int:
    """Compute and load semantic comparables for top processes."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.neighbors import NearestNeighbors

    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.process_id,
                   COALESCE(p.title, '') || ' '
                   || COALESCE(p.description, '') AS text
            FROM procurement_process p
            ORDER BY p.process_id
            LIMIT 2000
        """)
        rows = cur.fetchall()

    if len(rows) < 2:
        return 0

    pids = [int(r[0]) for r in rows]
    texts = [r[1] for r in rows]

    vectors = TfidfVectorizer(
        max_features=4000, ngram_range=(1, 2),
    ).fit_transform(texts)
    k = min(4, len(texts))
    nn = NearestNeighbors(
        n_neighbors=k, metric="cosine", algorithm="brute",
    )
    nn.fit(vectors)
    distances, indices = nn.kneighbors(vectors)

    with conn.cursor() as cur:
        cur.execute("DELETE FROM semantic_comparable")
        loaded = 0
        for pid_idx, pid in enumerate(pids):
            for rank, neighbor_idx in enumerate(indices[pid_idx]):
                if neighbor_idx == pid_idx:
                    continue
                sim = round(
                    1.0 - float(distances[pid_idx][rank]), 4,
                )
                if sim <= 0:
                    continue
                cur.execute(
                    """
                    INSERT INTO semantic_comparable(
                        process_id, comparable_process_id,
                        similarity, rank
                    )
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (process_id, comparable_process_id)
                    DO UPDATE SET similarity = EXCLUDED.similarity,
                        rank = EXCLUDED.rank
                    """,
                    (pid, pids[neighbor_idx], sim, rank + 1),
                )
                loaded += 1
    conn.commit()
    return loaded


def load_audit_log(
    conn: Any, summary: dict[str, Any],
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO audit_log(
                table_name, operation, row_pk, new_data
            )
            VALUES ('risk_assessment', 'MANUAL', 'sync', %s::jsonb)
            """,
            (json.dumps(summary, ensure_ascii=False),),
        )
    conn.commit()


def load_mongo_risk_events(summary: dict[str, Any]) -> None:
    try:
        import pymongo
    except ImportError:
        print("pymongo no instalado, saltando MongoDB")
        return

    try:
        client = pymongo.MongoClient(
            mongo_url(), serverSelectionTimeoutMS=3000,
        )
        db = client.get_default_database()
        now = datetime.now(UTC)

        db.risk_event_logs.insert_one({
            "event": "product_sync",
            "message": "Sync scoring real a PostgreSQL",
            "summary": summary,
            "created_at": now,
        })
        db.join_audits.insert_one({
            "audit_type": "product_to_academic_sync",
            "summary": summary,
            "created_at": now,
        })
        db.etl_run_logs.insert_one({
            "status": "completed",
            "source": "product_pipeline_sync",
            "processes_synced": summary.get("processes_loaded", 0),
            "created_at": now,
        })
        synced = summary.get("processes_loaded", 0)
        print(f"MongoDB: {synced} eventos de riesgo registrados")
    except Exception as exc:
        print(f"MongoDB no disponible: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--limit", type=int, default=0,
        help="Limitar procesos (0 = todos)",
    )
    args = parser.parse_args()

    marts_dir = ROOT / "data" / "marts"
    scores_path = marts_dir / "process_scores.parquet"
    if not scores_path.exists():
        print(
            "ERROR: Falta data/marts/process_scores.parquet. "
            "Ejecuta primero: make score"
        )
        sys.exit(1)

    print("Cargando process_scores.parquet...")
    scores = pd.read_parquet(scores_path)
    if args.limit > 0:
        scores = scores.head(args.limit)
    print(f"  {len(scores)} procesos a sincronizar")

    psycopg, _ = require_psycopg()
    conn_str = database_url()
    host_info = conn_str.split('@')[1] if '@' in conn_str else conn_str
    print(f"Conectando a PostgreSQL: {host_info}")

    with psycopg.connect(conn_str) as conn:
        print("\n[1/6] Cargando procesos...")
        process_ids = load_processes(conn, scores)
        print(f"  {len(process_ids)} procesos upserted")

        print("\n[2/6] Cargando evaluaciones de riesgo (IA real)...")
        ra_count = load_risk_assessments(conn, scores, process_ids)
        print(f"  {ra_count} evaluaciones de riesgo cargadas")

        print("\n[3/6] Cargando matches PAA...")
        paa_count = load_paa_matches(conn, scores, process_ids)
        print(f"  {paa_count} matches PAA cargados")

        print("\n[4/6] Computando comparables semánticos...")
        comp_count = load_semantic_comparables(conn)
        print(f"  {comp_count} comparables semánticos cargados")

        summary = {
            "processes_loaded": len(process_ids),
            "risk_assessments_loaded": ra_count,
            "paa_matches_loaded": paa_count,
            "comparables_loaded": comp_count,
            "synced_at": datetime.now(UTC).isoformat(),
        }

        print("\n[5/6] Registrando en audit_log...")
        load_audit_log(conn, summary)

        print("\n[6/6] Sincronizando MongoDB...")
        load_mongo_risk_events(summary)

    print("\n=== SYNC COMPLETADO ===")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
