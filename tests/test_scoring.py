from __future__ import annotations

import pandas as pd

from src.scoring.score_contracts import aggregate_providers, score_contracts


def sample_contracts() -> pd.DataFrame:
    rows = []
    for idx in range(40):
        rows.append(
            {
                "id_contrato": f"C{idx}",
                "nombre_entidad": "Entidad A",
                "codigo_entidad": 1,
                "nit_entidad": "1",
                "sector": "Salud",
                "proceso_de_compra": f"P{idx}",
                "referencia_del_contrato": f"REF-{idx}",
                "estado_contrato": "Cerrado",
                "tipo_de_contrato": "Prestación de servicios",
                "modalidad_de_contratacion": "Contratación directa",
                "codigo_categoria_principal": "V1.1",
                "fecha_de_firma": "2025-01-01",
                "fecha_inicio_contrato": "2025-01-01",
                "fecha_fin_contrato": "2025-02-01",
                "documento_proveedor": "123" if idx < 10 else f"{idx}",
                "codigo_proveedor": f"K{idx}",
                "proveedor_adjudicado": "Proveedor 1" if idx < 10 else f"Proveedor {idx}",
                "valor_del_contrato": 1000 if idx < 39 else 100000,
                "dias_adicionados": 5 if idx < 10 else 0,
                "url_proceso": "https://example.com",
                "objeto_del_contrato": "Objeto",
                "id_del_proceso": f"REQ{idx}",
                "id_del_portafolio": f"P{idx}",
                "precio_base": 1000,
                "valor_total_adjudicacion": 1000,
                "duracion_proceso": 1,
                "unidad_duracion_proceso": "Mes(es)",
                "estado_del_procedimiento": "Seleccionado",
                "adjudicado": "Si",
                "modalidad_proceso": "Contratación directa",
                "proveedores_unicos_con_respuesta": 1,
                "fecha_publicacion_proceso": "2025-01-01",
                "fecha_ultima_publicacion_proceso": "2025-01-05",
                "n_modificaciones": 1 if idx < 10 else 0,
                "n_adiciones": 1 if idx < 10 else 0,
                "tipos_modificacion": "ADICION EN EL VALOR" if idx < 10 else None,
                "descripcion_modificacion_ejemplo": (
                    "Adición por valor de $33.935.616,00" if idx < 10 else None
                ),
                "fecha_ultima_modificacion": "2025-01-15",
                "n_ubicaciones": 1,
                "n_ubicaciones_validas": 1,
                "ubicacion_ejecucion": "Bogotá",
                "flag_match_proceso": True,
                "flag_multiple_ubicaciones": False,
                "supplier_key": "123" if idx < 10 else f"{idx}",
            }
        )
    return pd.DataFrame(rows)


def test_score_contracts_bounds_and_explanations() -> None:
    scored = score_contracts(sample_contracts())
    assert scored["score_final"].between(0, 100).all()
    top = scored.sort_values("score_final", ascending=False).iloc[0]
    assert top["score_explanation"]
    assert top["risk_level"] in {"bajo", "medio", "alto", "crítico"}


def test_provider_aggregation() -> None:
    scored = score_contracts(sample_contracts())
    providers = aggregate_providers(scored)
    assert not providers.empty
    assert providers["score_final"].between(0, 100).all()
