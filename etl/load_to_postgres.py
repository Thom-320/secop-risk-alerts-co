from __future__ import annotations

import argparse
import csv
import json
from typing import Any

import pandas as pd

from etl.common import (
    ROOT,
    clean_key,
    clean_text,
    database_url,
    modality_family,
    only_digits,
    read_local_demo_sources,
    require_psycopg,
    stable_missing_identifier,
    to_date,
    to_decimal,
    to_int,
)

SQL_FILES = [
    "001_schema.sql",
    "002_indexes.sql",
    "003_triggers.sql",
    "004_views_analytics.sql",
    "005_seed_reference_data.sql",
    "007_security_roles.sql",
]


def apply_sql(conn: Any) -> None:
    sql_dir = ROOT / "sql"
    with conn.cursor() as cur:
        for name in SQL_FILES:
            cur.execute((sql_dir / name).read_text())
    conn.commit()


def reset_public_tables(conn: Any) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            DO $$
            DECLARE stmt TEXT;
            BEGIN
                SELECT 'TRUNCATE TABLE ' || string_agg(format('%I.%I', schemaname, tablename), ', ')
                       || ' RESTART IDENTITY CASCADE'
                INTO stmt
                FROM pg_tables
                WHERE schemaname = 'public';
                IF stmt IS NOT NULL THEN
                    EXECUTE stmt;
                END IF;
            END $$;
            """
        )
    conn.commit()


def one(conn: Any, sql: str, params: tuple[Any, ...]) -> Any:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        row = cur.fetchone()
    return row[0] if row else None


def upsert_department(conn: Any, name: str) -> int:
    name = clean_text(name, "Sin departamento")
    return int(
        one(
            conn,
            "INSERT INTO department(name) VALUES (%s) "
            "ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name RETURNING department_id",
            (name,),
        )
    )


def upsert_municipality(conn: Any, department_id: int, name: str) -> int:
    name = clean_text(name, "Sin municipio")
    return int(
        one(
            conn,
            "INSERT INTO municipality(department_id, name) VALUES (%s, %s) "
            "ON CONFLICT (department_id, name) DO UPDATE SET name = EXCLUDED.name "
            "RETURNING municipality_id",
            (department_id, name),
        )
    )


def upsert_modality(conn: Any, name: str) -> int:
    name = clean_text(name, "Sin modalidad")
    return int(
        one(
            conn,
            "INSERT INTO modality(name, family) VALUES (%s, %s) "
            "ON CONFLICT (name) DO UPDATE SET family = EXCLUDED.family RETURNING modality_id",
            (name, modality_family(name)),
        )
    )


def upsert_contract_type(conn: Any, name: str) -> int:
    name = clean_text(name, "Sin tipo")
    return int(
        one(
            conn,
            "INSERT INTO contract_type(name) VALUES (%s) "
            "ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name RETURNING contract_type_id",
            (name,),
        )
    )


def upsert_unspsc(conn: Any, code: str | None) -> int | None:
    if not code:
        return None
    return int(
        one(
            conn,
            "INSERT INTO unspsc_category(code) VALUES (%s) "
            "ON CONFLICT (code) DO UPDATE SET code = EXCLUDED.code RETURNING unspsc_category_id",
            (code,),
        )
    )


def upsert_entity(
    conn: Any,
    row: pd.Series,
    department_id: int,
    municipality_id: int,
) -> int:
    entity_code = only_digits(row.get("codigo_entidad"))
    nit = only_digits(row.get("nit_entidad"))
    name = clean_text(row.get("entidad") or row.get("nombre_entidad"), "Entidad sin nombre")
    entity_order = clean_text(row.get("ordenentidad"), "")
    if not entity_code:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT entity_id
                FROM public_entity
                WHERE entity_code IS NULL
                  AND lower(name) = lower(%s)
                  AND department_id IS NOT DISTINCT FROM %s
                  AND municipality_id IS NOT DISTINCT FROM %s
                LIMIT 1
                """,
                (name, department_id, municipality_id),
            )
            existing = cur.fetchone()
            if existing:
                cur.execute(
                    """
                    UPDATE public_entity
                    SET nit = COALESCE(%s, nit),
                        entity_order = %s,
                        updated_at = now()
                    WHERE entity_id = %s
                    RETURNING entity_id
                    """,
                    (nit, entity_order, existing[0]),
                )
                return int(cur.fetchone()[0])
    return int(
        one(
            conn,
            """
            INSERT INTO public_entity(
                entity_code, nit, name, department_id, municipality_id, entity_order
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (entity_code) DO UPDATE
            SET nit = EXCLUDED.nit,
                name = EXCLUDED.name,
                department_id = EXCLUDED.department_id,
                municipality_id = EXCLUDED.municipality_id,
                entity_order = EXCLUDED.entity_order
            RETURNING entity_id
            """,
            (
                entity_code,
                nit,
                name,
                department_id,
                municipality_id,
                entity_order,
            ),
        )
    )


def upsert_provider(
    conn: Any,
    name_value: Any,
    nit_value: Any,
    department_id: int | None = None,
    municipality_id: int | None = None,
) -> int | None:
    name = clean_text(name_value)
    nit = only_digits(nit_value)
    if not name and not nit:
        return None
    if not name:
        name = f"Proveedor {nit}"
    if not nit:
        nit = stable_missing_identifier("sin-nit", name)
    return int(
        one(
            conn,
            """
            INSERT INTO provider(nit, name, department_id, municipality_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (nit) DO UPDATE
            SET name = EXCLUDED.name,
                department_id = COALESCE(EXCLUDED.department_id, provider.department_id),
                municipality_id = COALESCE(EXCLUDED.municipality_id, provider.municipality_id)
            RETURNING provider_id
            """,
            (nit, name, department_id, municipality_id),
        )
    )


def create_extraction_run(conn: Any, rows_loaded: int) -> int:
    return int(
        one(
            conn,
            """
            INSERT INTO extraction_run(dataset_id, scope, finished_at, status, rows_loaded, message)
            VALUES ('p6dx-8zbt', 'demo', now(), 'completed', %s, 'Carga demo desde Parquet local')
            RETURNING extraction_run_id
            """,
            (rows_loaded,),
        )
    )


def seed_hierarchy(conn: Any) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO administrative_hierarchy(parent_node_id, node_type, label)
            VALUES (NULL, 'country', 'Colombia')
            ON CONFLICT DO NOTHING;

            WITH country AS (
                SELECT node_id FROM administrative_hierarchy
                WHERE node_type = 'country' AND label = 'Colombia'
                LIMIT 1
            )
            INSERT INTO administrative_hierarchy(parent_node_id, node_type, label)
            SELECT country.node_id, 'department', d.name
            FROM department d CROSS JOIN country
            ON CONFLICT DO NOTHING;

            WITH dept_nodes AS (
                SELECT ah.node_id, d.department_id
                FROM administrative_hierarchy ah
                JOIN department d ON d.name = ah.label
                WHERE ah.node_type = 'department'
            )
            INSERT INTO administrative_hierarchy(parent_node_id, node_type, label)
            SELECT dept_nodes.node_id, 'municipality', m.name
            FROM municipality m
            JOIN dept_nodes ON dept_nodes.department_id = m.department_id
            ON CONFLICT DO NOTHING;

            WITH muni_nodes AS (
                SELECT ah.node_id, m.municipality_id
                FROM administrative_hierarchy ah
                JOIN municipality m ON m.name = ah.label
                WHERE ah.node_type = 'municipality'
            )
            INSERT INTO administrative_hierarchy(parent_node_id, node_type, label, entity_id)
            SELECT muni_nodes.node_id, 'entity', e.name, e.entity_id
            FROM public_entity e
            JOIN muni_nodes ON muni_nodes.municipality_id = e.municipality_id
            ON CONFLICT DO NOTHING;
            """
        )


def dedupe_process_phases(processes: pd.DataFrame) -> pd.DataFrame:
    """Collapse duplicate SECOP phase-rows (same procurement appears once per
    phase, e.g. 'Evaluación' and 'Fase de Selección') into one canonical row.

    SECOP publishes the same procurement multiple times across phases with
    distinct id_del_proceso but the same referencia_del_proceso. Without this,
    a process appears twice in the ranking and shows up as a similarity-1.0
    "self" comparable of its own twin. We keep the most-advanced phase: the one
    with the highest adjudicated value (falls back to the latest one).
    """
    if processes.empty or "referencia_del_proceso" not in processes.columns:
        return processes
    d = processes.copy()
    d["_nref"] = (
        d["referencia_del_proceso"].fillna("").astype(str)
        .str.upper().str.strip().str.replace(r"\s*\(.*$", "", regex=True)
    )
    ent_col = "nit_entidad" if "nit_entidad" in d.columns else (
        "codigo_entidad" if "codigo_entidad" in d.columns else None
    )
    d["_ent"] = d[ent_col].fillna("").astype(str) if ent_col else ""
    d["_adj"] = pd.to_numeric(
        d.get("valor_total_adjudicacion"), errors="coerce"
    ).fillna(0)
    has_ref = d["_nref"].ne("")
    keep = (
        d[has_ref]
        .sort_values("_adj", ascending=False)
        .drop_duplicates(subset=["_ent", "_nref"], keep="first")
    )
    out = pd.concat([keep, d[~has_ref]], ignore_index=True)
    return out.drop(columns=["_nref", "_ent", "_adj"])


def load_processes(conn: Any, processes: pd.DataFrame, limit: int) -> dict[str, int]:
    processes = dedupe_process_phases(processes).head(limit).copy()
    extraction_run_id = create_extraction_run(conn, len(processes))
    process_ids: dict[str, int] = {}
    for idx, row in processes.iterrows():
        department_id = upsert_department(conn, row.get("departamento_entidad"))
        municipality_id = upsert_municipality(conn, department_id, row.get("ciudad_entidad"))
        entity_id = upsert_entity(conn, row, department_id, municipality_id)
        modality_id = upsert_modality(conn, row.get("modalidad_de_contratacion"))
        contract_type_id = upsert_contract_type(conn, row.get("tipo_de_contrato"))
        unspsc_id = upsert_unspsc(conn, clean_text(row.get("codigo_principal_de_categoria")))
        provider_id = upsert_provider(
            conn,
            row.get("nombre_del_proveedor"),
            row.get("nit_del_proveedor_adjudicado"),
            department_id,
            municipality_id,
        )
        process_key = clean_key(row.get("id_del_proceso"), f"demo-process-{idx}")
        title = clean_text(row.get("nombre_del_procedimiento"), "Proceso sin titulo")
        description = clean_text(row.get("descripci_n_del_procedimiento"), "")
        process_id = int(
            one(
                conn,
                """
                INSERT INTO procurement_process(
                    process_key, process_reference, entity_id, modality_id, contract_type_id,
                    unspsc_category_id, title, description, status, publication_date, award_date,
                    base_price, awarded_total, duration_days, response_count, invited_suppliers,
                    unique_suppliers, provider_id, source_url, source_dataset_id, extraction_run_id
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, 'p6dx-8zbt', %s
                )
                ON CONFLICT (process_key) DO UPDATE
                SET title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    status = EXCLUDED.status,
                    base_price = EXCLUDED.base_price,
                    awarded_total = EXCLUDED.awarded_total,
                    provider_id = EXCLUDED.provider_id
                RETURNING process_id
                """,
                (
                    process_key,
                    clean_text(row.get("referencia_del_proceso"), ""),
                    entity_id,
                    modality_id,
                    contract_type_id,
                    unspsc_id,
                    title,
                    description,
                    clean_text(row.get("estado_del_procedimiento"), "sin_estado"),
                    to_date(row.get("fecha_de_publicacion_del")),
                    to_date(row.get("fecha_adjudicacion")),
                    to_decimal(row.get("precio_base")),
                    to_decimal(row.get("valor_total_adjudicacion")),
                    to_int(row.get("duracion")),
                    to_int(row.get("conteo_de_respuestas_a_ofertas")),
                    to_int(row.get("proveedores_invitados")),
                    to_int(row.get("proveedores_unicos_con")),
                    provider_id,
                    clean_text(row.get("urlproceso"), ""),
                    extraction_run_id,
                ),
            )
        )
        process_ids[process_key] = process_id
        process_reference = clean_text(row.get("referencia_del_proceso"), "")
        if process_reference:
            process_ids[process_reference] = process_id
        if idx and idx % 1000 == 0:
            conn.commit()
    conn.commit()
    seed_hierarchy(conn)
    conn.commit()
    return process_ids


def load_contracts(
    conn: Any,
    contracts: pd.DataFrame,
    process_ids: dict[str, int],
    limit: int = 12000,
) -> int:
    loaded = 0
    for idx, row in contracts.head(limit).iterrows():
        process_key = clean_text(
            row.get("proceso_de_compra")
            or row.get("numero_de_proceso")
            or row.get("referencia_del_proceso")
        )
        process_id = process_ids.get(process_key)
        if not process_id:
            continue
        provider_id = upsert_provider(
            conn,
            row.get("proveedor_adjudicado") or row.get("nom_raz_social_contratista"),
            row.get("documento_proveedor"),
        )
        contract_key = clean_key(
            row.get("id_contrato") or row.get("numero_del_contrato"),
            f"demo-contract-{idx}",
        )
        status = clean_text(
            row.get("estado_contrato") or row.get("estado_del_proceso"),
            "sin_estado",
        )
        signed_date = to_date(
            row.get("fecha_de_firma") or row.get("fecha_de_firma_del_contrato")
        )
        start_date = to_date(
            row.get("fecha_de_inicio_del_contrato") or row.get("fecha_inicio_ejecuci_n")
        )
        end_date = to_date(
            row.get("fecha_de_fin_del_contrato") or row.get("fecha_fin_ejecuci_n")
        )
        one(
            conn,
            """
            INSERT INTO contract(
                contract_key, process_id, provider_id, status, signed_date,
                start_date, end_date, value, paid_value, source_url
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (contract_key) DO UPDATE
            SET status = EXCLUDED.status,
                value = EXCLUDED.value,
                paid_value = EXCLUDED.paid_value
            RETURNING contract_id
            """,
            (
                contract_key,
                process_id,
                provider_id,
                status,
                signed_date,
                start_date,
                end_date,
                to_decimal(row.get("valor_del_contrato") or row.get("valor_contrato")),
                to_decimal(row.get("valor_pagado")),
                clean_text(row.get("urlproceso") or row.get("url_contrato"), ""),
            ),
        )
        loaded += 1
    conn.commit()
    return loaded


def load_paa(
    conn: Any,
    paa: pd.DataFrame,
    process_ids: dict[str, int],
    max_rows: int = 5000,
) -> int:
    loaded = 0
    for idx, row in paa.head(max_rows).iterrows():
        department_id = upsert_department(conn, "Sin departamento PAA")
        municipality_id = upsert_municipality(conn, department_id, "Sin municipio PAA")
        entity_id = upsert_entity(conn, row, department_id, municipality_id)
        modality_id = upsert_modality(conn, row.get("modalidad"))
        unspsc_id = None
        plan_key = clean_key(
            row.get("id_plan_anual_de_adquisiciones"),
            f"plan-{entity_id}-{row.get('annio')}",
        )
        plan_id = int(
            one(
                conn,
                """
                INSERT INTO annual_procurement_plan(plan_key, entity_id, year, version)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (plan_key) DO UPDATE SET version = EXCLUDED.version
                RETURNING plan_id
                """,
                (
                    plan_key,
                    entity_id,
                    to_int(row.get("annio")) or 2025,
                    clean_text(row.get("version_del_paa"), ""),
                ),
            )
        )
        item_key = clean_key(row.get("id"), f"paa-item-{idx}")
        item_id = int(
            one(
                conn,
                """
                INSERT INTO paa_item(
                    item_key, plan_id, description, expected_start_date,
                    expected_reception_date, expected_duration_days, planned_value,
                    modality_id, unspsc_category_id, related_process_reference, source_url
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (item_key) DO UPDATE
                SET description = EXCLUDED.description,
                    planned_value = EXCLUDED.planned_value
                RETURNING paa_item_id
                """,
                (
                    item_key,
                    plan_id,
                    clean_text(row.get("descripcion"), "Item PAA sin descripcion"),
                    to_date(row.get("fecha_esperada_de_inicio")),
                    to_date(row.get("fecha_esperada_de_recepcion")),
                    to_int(row.get("duracion_esperada")),
                    to_decimal(row.get("valor_total_esperado")),
                    modality_id,
                    unspsc_id,
                    clean_text(row.get("procesos_relacionados"), ""),
                    clean_text(row.get("url_proceso"), ""),
                ),
            )
        )
        related_reference = clean_text(row.get("procesos_relacionados"), "")
        process_id = process_ids.get(related_reference)
        if process_id:
            one(
                conn,
                """
                INSERT INTO paa_process_match(paa_item_id, process_id, method, confidence, status)
                VALUES (%s, %s, 'related_process', 1.0, 'strong')
                ON CONFLICT (paa_item_id, process_id) DO UPDATE
                SET confidence = EXCLUDED.confidence,
                    status = EXCLUDED.status
                RETURNING paa_process_match_id
                """,
                (item_id, process_id),
            )
        loaded += 1
    conn.commit()
    return loaded


def load_fiscal_context(conn: Any) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO fiscal_control_subject(entity_id, subject_name)
            SELECT entity_id, name
            FROM public_entity
            ON CONFLICT (subject_name) DO NOTHING;

            INSERT INTO fiscal_finding(fiscal_subject_id, year, finding_type, amount, description)
            SELECT fiscal_subject_id, 2025, 'contexto_visible', 0,
                   'Contexto fiscal visible; no etiqueta de conducta indebida.'
            FROM fiscal_control_subject
            WHERE NOT EXISTS (
                SELECT 1 FROM fiscal_finding
                WHERE fiscal_finding.fiscal_subject_id = fiscal_control_subject.fiscal_subject_id
            )
            LIMIT 100;
            """
        )
    conn.commit()


def load_risk_outputs(conn: Any) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            WITH threshold AS (
                SELECT percentile_cont(0.75) WITHIN GROUP (ORDER BY base_price) AS p75
                FROM procurement_process
            )
            INSERT INTO risk_assessment(
                process_id, priority_score, confidence_score, anomaly_score,
                peer_deviation_score, rule_score, explanation
            )
            SELECT
                p.process_id,
                LEAST(100, GREATEST(0,
                    CASE WHEN p.response_count <= 1 THEN 30 ELSE 10 END
                    + CASE WHEN p.base_price > threshold.p75 THEN 35 ELSE 15 END
                    + CASE WHEN lower(COALESCE(m.name, '')) LIKE '%directa%' THEN 20 ELSE 10 END
                )) AS priority_score,
                CASE WHEN length(p.description) > 40 THEN 80 ELSE 55 END AS confidence_score,
                CASE WHEN p.base_price > threshold.p75 THEN 75 ELSE 35 END,
                CASE WHEN p.response_count <= 1 THEN 70 ELSE 30 END,
                CASE WHEN lower(COALESCE(m.name, '')) LIKE '%directa%' THEN 70 ELSE 35 END,
                'Priorizacion explicable para revision humana; no prueba conductas indebidas.'
            FROM procurement_process p
            CROSS JOIN threshold
            LEFT JOIN modality m ON m.modality_id = p.modality_id
            WHERE NOT EXISTS (
                SELECT 1 FROM risk_assessment existing
                WHERE existing.process_id = p.process_id
            );

            INSERT INTO risk_reason(risk_assessment_id, risk_rule_id, reason_text, contribution)
            SELECT ra.risk_assessment_id, rr.risk_rule_id, rr.description, rr.weight * 100
            FROM risk_assessment ra
            CROSS JOIN risk_rule rr
            WHERE rr.active
            ON CONFLICT DO NOTHING;

            """
        )
    conn.commit()


def load_semantic_comparables(conn: Any, max_processes: int = 500) -> None:
    from src.scoring.semantic_similarity import semantic_similarity_matrix

    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT p.process_id,
                   COALESCE(p.title, ''),
                   COALESCE(p.description, ''),
                   COALESCE(m.name, '')
            FROM procurement_process p
            LEFT JOIN modality m ON m.modality_id = p.modality_id
            ORDER BY p.process_id
            LIMIT %s
            """,
            (max_processes,),
        )
        rows = cur.fetchall()
    if len(rows) < 2:
        return

    process_ids = [int(row[0]) for row in rows]
    texts = [f"{row[1]} {row[2]} {row[3]}" for row in rows]
    similarity_matrix = semantic_similarity_matrix(texts)

    with conn.cursor() as cur:
        for idx, process_id in enumerate(process_ids):
            similarities = similarity_matrix[idx]
            similarities[idx] = -1.0
            candidates = [
                (process_ids[j], float(score))
                for j, score in enumerate(similarities)
                if score > 0
            ]
            candidates.sort(key=lambda item: item[1], reverse=True)
            for rank, (comparable_process_id, similarity) in enumerate(candidates[:3], start=1):
                cur.execute(
                    """
                    INSERT INTO semantic_comparable(
                        process_id, comparable_process_id, similarity, rank
                    )
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (process_id, comparable_process_id) DO UPDATE
                    SET similarity = EXCLUDED.similarity,
                        rank = EXCLUDED.rank
                    """,
                    (process_id, comparable_process_id, round(similarity, 4), rank),
                )
    conn.commit()


def write_counts(conn: Any) -> dict[str, int]:
    tables = [
        "source_dataset", "extraction_run", "department", "municipality", "public_entity",
        "provider", "modality", "contract_type", "unspsc_category", "administrative_hierarchy",
        "procurement_process", "process_state_history", "contract", "annual_procurement_plan",
        "paa_item", "paa_process_match", "fiscal_control_subject", "fiscal_finding",
        "risk_rule", "risk_assessment", "risk_reason", "semantic_comparable", "audit_log",
        "app_user", "usability_survey_response", "human_review", "user_action_event",
    ]
    counts: dict[str, int] = {}
    with conn.cursor() as cur:
        for table in tables:
            cur.execute(f"SELECT count(*) FROM {table}")
            counts[table] = int(cur.fetchone()[0])
    validation_dir = ROOT / "validation"
    validation_dir.mkdir(exist_ok=True)
    with (validation_dir / "table_counts.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["table", "rows"])
        writer.writerows(counts.items())
    (validation_dir / "load_summary.json").write_text(
        json.dumps(
            {
                "status": "completed",
                "source": "local_parquet_fallback",
                "procurement_process_rows": counts["procurement_process"],
                "table_count": len(counts),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10000)
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()

    psycopg, _dict_row = require_psycopg()
    sources = read_local_demo_sources(limit=args.limit)
    with psycopg.connect(database_url()) as conn:
        if args.reset:
            reset_public_tables(conn)
        apply_sql(conn)
        process_ids = load_processes(conn, sources["processes"], args.limit)
        contracts_loaded = load_contracts(conn, sources["contracts"], process_ids)
        paa_loaded = load_paa(conn, sources["paa"], process_ids)
        load_fiscal_context(conn)
        load_risk_outputs(conn)
        load_semantic_comparables(conn)
        counts = write_counts(conn)
    print(
        json.dumps(
            {
                "status": "completed",
                "processes_loaded": counts["procurement_process"],
                "contracts_loaded": contracts_loaded,
                "paa_items_loaded": paa_loaded,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
