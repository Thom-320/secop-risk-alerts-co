from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sql_text(name: str) -> str:
    return (ROOT / "sql" / name).read_text()


def test_schema_has_at_least_twenty_tables() -> None:
    schema = sql_text("001_schema.sql")
    tables = re.findall(r"CREATE TABLE IF NOT EXISTS\s+([a-z_]+)", schema)
    assert len(set(tables)) >= 20
    for table in [
        "procurement_process",
        "contract",
        "paa_item",
        "risk_assessment",
        "audit_log",
    ]:
        assert table in tables


def test_core_tables_have_primary_keys_and_foreign_keys() -> None:
    schema = sql_text("001_schema.sql")
    for key in [
        "process_id BIGSERIAL PRIMARY KEY",
        "contract_id BIGSERIAL PRIMARY KEY",
        "paa_item_id BIGSERIAL PRIMARY KEY",
        "risk_assessment_id BIGSERIAL PRIMARY KEY",
    ]:
        assert key in schema
    for fk in [
        "REFERENCES procurement_process(process_id)",
        "REFERENCES public_entity(entity_id)",
        "REFERENCES paa_item(paa_item_id)",
        "REFERENCES risk_assessment(risk_assessment_id)",
    ]:
        assert fk in schema


def test_score_and_confidence_constraints_are_declared() -> None:
    schema = sql_text("001_schema.sql")
    assert "priority_score >= 0 AND priority_score <= 100" in schema
    assert "confidence_score >= 0 AND confidence_score <= 100" in schema
    assert "confidence >= 0 AND confidence <= 1" in schema
    assert "NUMERIC(18,2)" in schema


def test_triggers_cover_audit_state_history_and_risk_validation() -> None:
    triggers = sql_text("003_triggers.sql")
    for trigger_name in [
        "trg_procurement_process_audit",
        "trg_contract_audit",
        "trg_paa_item_audit",
        "trg_risk_assessment_audit",
        "trg_procurement_process_state_history",
        "trg_risk_assessment_validate",
    ]:
        assert trigger_name in triggers
    assert "OLD" in triggers
    assert "NEW" in triggers


def test_views_include_window_functions_and_recursive_cte() -> None:
    views = sql_text("004_views_analytics.sql")
    assert "WITH RECURSIVE tree" in views
    assert "row_number() OVER" in views
    assert "dense_rank() OVER" in views
    assert "percent_rank() OVER" in views
    assert "ntile(10) OVER" in views


def test_required_docs_exist() -> None:
    for relative in [
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
        "docs/diagrams/microservices.mmd",
    ]:
        assert (ROOT / relative).exists()


def test_usability_results_are_not_fabricated() -> None:
    content = (ROOT / "docs" / "usability_results.md").read_text()
    assert "Pendiente de diligenciar con 5 usuarios reales" in content
    assert "No se incluyen resultados fabricados" in content


def test_local_demo_source_has_required_volume() -> None:
    import pandas as pd

    processes = pd.read_parquet(ROOT / "data" / "legacy_raw" / "processes.parquet")
    assert len(processes) >= 10000
