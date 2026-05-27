from __future__ import annotations

import json

import pandas as pd
import pytest

from src.transform import build_process_master as bpm
from src.utils.config import Settings


def secop_row() -> dict[str, object]:
    return {
        "entidad": "Entidad Demo",
        "nit_entidad": "900123123",
        "departamento_entidad": "Meta",
        "ciudad_entidad": "Villavicencio",
        "ordenentidad": "Territorial",
        "codigo_pci": "PCI-1",
        "id_del_proceso": "PROC-1",
        "referencia_del_proceso": "REF-1",
        "ppi": "PPI-1",
        "id_del_portafolio": "PORT-1",
        "nombre_del_procedimiento": "Compra de equipos",
        "descripci_n_del_procedimiento": "Compra de equipos médicos para hospital público",
        "fase": "Planeación",
        "fecha_de_publicacion_del": "2025-01-10T00:00:00.000",
        "fecha_de_ultima_publicaci": "2025-01-12T00:00:00.000",
        "precio_base": "1000000",
        "modalidad_de_contratacion": "Contratación directa",
        "justificaci_n_modalidad_de": "",
        "duracion": "30",
        "unidad_de_duracion": "Día(s)",
        "proveedores_invitados": "3",
        "proveedores_con_invitacion": "2",
        "proveedores_que_manifestaron": "1",
        "respuestas_al_procedimiento": "1",
        "conteo_de_respuestas_a_ofertas": "1",
        "proveedores_unicos_con": "1",
        "numero_de_lotes": "1",
        "estado_del_procedimiento": "Publicado",
        "adjudicado": "Si",
        "fecha_adjudicacion": "2025-02-10",
        "valor_total_adjudicacion": "950000",
        "nombre_del_proveedor": "Proveedor Demo",
        "nit_del_proveedor_adjudicado": "800111222",
        "codigo_principal_de_categoria": "42190000",
        "estado_de_apertura_del_proceso": "Abierto",
        "tipo_de_contrato": "Suministro",
        "subtipo_de_contrato": "Equipos",
        "urlproceso": "https://example.com/proc",
        "codigo_entidad": "7001",
        "estado_resumen": "Activo",
    }


def rpmr_row() -> dict[str, object]:
    return {
        "nivel_entidad": "Territorial",
        "codigo_entidad_en_secop": "7001",
        "nombre_de_la_entidad": "Entidad Demo",
        "nit_de_la_entidad": "900123123",
        "departamento_entidad": "Meta",
        "municipio_entidad": "Villavicencio",
        "estado_del_proceso": "Firmado",
        "modalidad_de_contrataci_n": "Contratación directa",
        "objeto_a_contratar": "Equipos médicos",
        "objeto_del_proceso": "Compra de equipos médicos para hospital público",
        "tipo_de_contrato": "Suministro",
        "fecha_de_firma_del_contrato": "2025-02-11",
        "fecha_inicio_ejecuci_n": "2025-02-12",
        "fecha_fin_ejecuci_n": "2025-03-12",
        "numero_del_contrato": "CONT-1",
        "numero_de_proceso": "REF-1",
        "valor_contrato": "950000",
        "nom_raz_social_contratista": "Proveedor Demo",
        "url_contrato": "https://example.com/contract",
        "origen": "SECOP II",
        "tipo_documento_proveedor": "NIT",
        "documento_proveedor": "800111222",
    }


def paa_row() -> dict[str, object]:
    return {
        "id": "PAA-1",
        "identificador_unico": "PAA-U-1",
        "descripcion": "Compra de equipos médicos para hospital público",
        "fecha_esperada_de_inicio": "2025-01-01",
        "fecha_esperada_de_recepcion": "2025-01-10",
        "duracion_esperada": "30",
        "unidad_de_duracion_esperada": "Día(s)",
        "origen_recursos": "Propios",
        "valor_total_esperado": "1000000",
        "valor_esperado_de_presupuesto": "1000000",
        "modalidad": "Contratación directa",
        "categorias_unspsc": "42190000",
        "id_plan_anual_de_adquisiciones": "PLAN-1",
        "procesos_relacionados": "REF-1",
        "url_proceso": "https://example.com/paa",
        "codigo_entidad": "7001",
        "nombre_entidad": "Entidad Demo",
        "nit_entidad": "900123123",
        "id_paa_encabezado": "H-1",
        "causal_de_contratacion": "",
        "grupo_de_procedimiento": "",
        "annio": "2025",
        "tipo": "Bien",
        "version_del_paa": "1",
        "fecha_version": "2025-01-01",
        "fecha_de_carga_del_paa": "2025-01-01",
    }


def control_row() -> dict[str, object]:
    return {
        "sujeto_auditado": "Entidad Demo",
        "modalidad_de_auditor_a": "Regular",
        "hallazgos_administrativos": "1",
        "hallazgos_disciplinarios": "0",
        "hallazgos_penales": "0",
        "hallazgos_fiscales": "0",
        "cuant_a": "0",
        "vigencia": "2025",
    }


def build_settings(tmp_path) -> Settings:
    settings = Settings(
        root_dir=tmp_path,
        raw_dir=tmp_path / "data" / "raw",
        legacy_raw_dir=tmp_path / "data" / "legacy_raw",
        interim_dir=tmp_path / "data" / "interim",
        marts_dir=tmp_path / "data" / "marts",
        docs_dir=tmp_path / "docs",
        docs_legacy_dir=tmp_path / "docs" / "legacy",
        validation_dir=tmp_path / "validation",
        report_dir=tmp_path / "data" / "reports",
        manifest_path=tmp_path / "data" / "raw" / "manifest.json",
        extract_scope="demo",
        paa_signal_mode="pending",
    )
    settings.ensure_directories()
    return settings


def write_chunked_paa(settings: Settings, completed: bool) -> None:
    paa_dir = settings.raw_dir / "paa_detail"
    paa_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([paa_row()]).to_parquet(paa_dir / "part-000001.parquet", index=False)
    manifest = {
        "version": 2,
        "scope": {"extract_scope": "demo"},
        "datasets": {
            "paa_detail": {
                "dataset_key": "paa_detail",
                "dataset_id": "9sue-ezhx",
                "page_size": 20000,
                "mode": "demo",
                "scope": {"mode": "demo"},
                "layout": "chunked",
                "next_offset": 1,
                "rows_written": 1,
                "part_count": 1,
                "started_at": "2026-01-01T00:00:00+00:00",
                "updated_at": "2026-01-01T00:00:01+00:00",
                "completed": completed,
            }
        },
    }
    settings.manifest_path.write_text(json.dumps(manifest))


def test_build_process_master_reads_chunked_paa(tmp_path, monkeypatch) -> None:
    settings = build_settings(tmp_path)
    pd.DataFrame([secop_row()]).to_parquet(
        settings.raw_dir / "secop_ii_processes.parquet",
        index=False,
    )
    pd.DataFrame([rpmr_row()]).to_parquet(
        settings.raw_dir / "secop_integrado.parquet",
        index=False,
    )
    pd.DataFrame([control_row()]).to_parquet(
        settings.raw_dir / "control_fiscal_context.parquet",
        index=False,
    )
    write_chunked_paa(settings, completed=True)

    monkeypatch.setattr(bpm, "get_settings", lambda: settings)
    assets = bpm.build_process_master()
    assert not assets["process_master"].empty
    assert not assets["paa_items"].empty


def test_build_process_master_rejects_incomplete_chunked_paa(tmp_path, monkeypatch) -> None:
    settings = build_settings(tmp_path)
    pd.DataFrame([secop_row()]).to_parquet(
        settings.raw_dir / "secop_ii_processes.parquet",
        index=False,
    )
    pd.DataFrame([rpmr_row()]).to_parquet(
        settings.raw_dir / "secop_integrado.parquet",
        index=False,
    )
    pd.DataFrame([control_row()]).to_parquet(
        settings.raw_dir / "control_fiscal_context.parquet",
        index=False,
    )
    write_chunked_paa(settings, completed=False)

    monkeypatch.setattr(bpm, "get_settings", lambda: settings)
    with pytest.raises(ValueError):
        bpm.build_process_master()
