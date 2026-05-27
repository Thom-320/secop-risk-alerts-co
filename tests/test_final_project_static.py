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
        "docs/validation-summary.md",
        "docs/human_validation_protocol.md",
        "docs/human_validation_results.md",
        "docs/demo-casebook.md",
        "docs/usability_survey_template.md",
        "docs/usability_results.md",
        "docs/ai_usage_disclosure.md",
        "docs/product_route.md",
        "docs/academic_route.md",
        "docs/contest_submission_checklist.md",
        "docs/class_submission_checklist.md",
        "docs/model-card.md",
        "docs/ethics-note.md",
        "docs/reproducibility.md",
        "docs/data-cards/secop-ii-procesos.md",
        "docs/data-cards/secop-integrado.md",
        "docs/data-cards/paa-detalle.md",
        "docs/data-cards/control-fiscal.md",
        "docs/fairness_territorial.md",
        "docs/deployment.md",
        "docs/product_route.md",
        "docs/academic_route.md",
        "docs/contest_submission_checklist.md",
        "docs/class_submission_checklist.md",
        "docs/diagrams/architecture.mmd",
        "docs/diagrams/er_diagram.mmd",
        "docs/diagrams/microservices.mmd",
    ]:
        assert (ROOT / relative).exists()


def test_usability_results_are_not_fabricated() -> None:
    content = (ROOT / "docs" / "usability_results.md").read_text()
    assert "Estado: pendiente de 5 usuarios reales" in content
    assert "No se incluyen resultados fabricados" in content
    assert "is_real_response" in content


def test_human_validation_results_are_not_fabricated() -> None:
    content = (ROOT / "docs" / "human_validation_results.md").read_text()
    assert "Estado: pendiente" in content
    assert "No se fabrican etiquetas humanas" in content
    assert "is_real_review" in content


def test_model_card_has_required_sections() -> None:
    content = (ROOT / "docs" / "model-card.md").read_text()
    for section in [
        "## 1. Nombre del sistema",
        "## 2. Propósito",
        "## 3. Usuarios previstos",
        "## 4. Decisión que apoya",
        "## 5. Decisiones que NO debe tomar",
        "## 6. Fuentes de datos",
        "## 7. Unidad de análisis",
        "## 8. Features principales",
        "## 9. Método de scoring",
        "## 10. Componentes del score",
        "## 11. Métrica de confianza",
        "## 12. Validación automática existente",
        "## 13. Validación humana pendiente",
        "## 14. Sesgos y riesgos",
        "## 15. Limitaciones técnicas",
        "## 16. Uso permitido",
        "## 17. Uso no permitido",
        "## 18. Monitoreo recomendado",
        "## 19. Cambios futuros",
    ]:
        assert section in content


def test_data_cards_have_required_fields() -> None:
    required = [
        "## 1. Dataset",
        "## 2. ID en datos.gov.co",
        "## 3. Entidad fuente",
        "## 4. Uso dentro del sistema",
        "## 5. Granularidad",
        "## 6. Campos usados",
        "## 7. Llaves de enlace",
        "## 8. Problemas de calidad esperados",
        "## 9. Transformaciones aplicadas",
        "## 10. Riesgos de sesgo",
        "## 11. Qué NO se infiere desde este dataset",
        "## 12. Estado en el MVP",
    ]
    cards = {
        "docs/data-cards/secop-ii-procesos.md": "p6dx-8zbt",
        "docs/data-cards/secop-integrado.md": "rpmr-utcd",
        "docs/data-cards/paa-detalle.md": "9sue-ezhx",
        "docs/data-cards/control-fiscal.md": "wasc-xi4h",
    }
    for relative, dataset_id in cards.items():
        content = (ROOT / relative).read_text()
        assert dataset_id in content
        for heading in required:
            assert heading in content


def test_demo_and_validation_docs_have_expected_markers() -> None:
    expectations = {
        "docs/demo-guide.md": ["Flujo de 2 minutos", "Abrir dashboard"],
        "docs/demo-casebook.md": ["SAMPLE", "CASE-005"],
        "docs/human_validation_protocol.md": ["40 y 100 procesos", "controles aleatorios"],
        "docs/fairness_territorial.md": ["Proporción de alertas altas", "Pendientes"],
        "docs/deployment.md": ["PUBLIC_READ_ONLY", "POST /reviews"],
    }
    for relative, markers in expectations.items():
        content = (ROOT / relative).read_text()
        for marker in markers:
            assert marker in content


def test_route_docs_and_checklists_are_non_empty() -> None:
    for relative in [
        "docs/product_route.md",
        "docs/academic_route.md",
        "docs/contest_submission_checklist.md",
        "docs/class_submission_checklist.md",
        "docs/ethics-note.md",
        "docs/reproducibility.md",
    ]:
        content = (ROOT / relative).read_text()
        assert len(content.strip()) > 250


def test_contest_critical_docs_are_non_empty() -> None:
    for relative in [
        "docs/demo-casebook.md",
        "docs/model-card.md",
        "docs/validation-summary.md",
        "docs/deployment.md",
        "docs/fairness_territorial.md",
        "docs/human_validation_protocol.md",
        "docs/human_validation_results.md",
    ]:
        content = (ROOT / relative).read_text()
        assert len(content.strip()) > 100, f"{relative} esta vacio o es muy corto"


def test_validators_declare_expected_modes() -> None:
    product_validator = (ROOT / "etl" / "validate_product.py").read_text()
    academic_validator = (ROOT / "etl" / "validate_final.py").read_text()

    assert "product_validation.json" in product_validator
    assert '"mode": "product-lean"' in product_validator
    assert "final_validation.json" in academic_validator
    assert '"mode": "academic-fullstack"' in academic_validator


def test_dash_has_downloadable_evidence_exports() -> None:
    content = (ROOT / "dashboard" / "dash_app.py").read_text()
    assert "Descargar CSV" in content
    assert "Descargar HTML" in content
    assert "dcc.Download" in content


def test_sample_csvs_are_marked_sample() -> None:
    demo_cases = (ROOT / "validation" / "demo_cases_sample.csv").read_text().splitlines()
    manual_review = (ROOT / "validation" / "manual_review_sample.csv").read_text().splitlines()

    assert demo_cases[0].startswith("case_id,sample_flag,process_id")
    assert all(",SAMPLE," in line for line in demo_cases[1:])
    assert manual_review[0].startswith("sample_flag,review_id,process_id")
    assert all(line.startswith("SAMPLE,") for line in manual_review[1:])


def test_slide_sources_do_not_keep_stale_39_test_claim() -> None:
    forbidden_claims = (
        "39 pruebas",
        "39 pasan",
        "39 pytest",
        "39 passed",
        "50 tests",
        "50 passed",
    )
    for relative in [
        "slides/README.md",
        "slides/contratia_abierta_deck.md",
        "slides/contratia_abierta_speaker_notes.md",
        "presentation/slides.md",
        "presentation/speaker_notes.md",
        "slides/scripts/build_deck.mjs",
        "slides/scripts/generate_assets.py",
        "slides/latex/contratia_abierta_beamer.tex",
        "slides/html/contratia_abierta_interactive.html",
        "presentation/html/contratia_abierta_interactive.html",
    ]:
        text = (ROOT / relative).read_text()
        for forbidden in forbidden_claims:
            assert forbidden not in text
    assert "71 tests pasan" in (ROOT / "presentation/slides.md").read_text()


def test_sample_demo_source_exists_for_clean_clone() -> None:
    from etl.common import read_local_demo_sources

    sources = read_local_demo_sources(limit=2)
    assert not sources["processes"].empty
    assert "id_del_proceso" in sources["processes"].columns
