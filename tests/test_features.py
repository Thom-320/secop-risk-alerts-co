from __future__ import annotations

import pandas as pd

from src.features.risk_features import (
    compute_risk_features,
    parse_currency_candidates,
    unit_to_days_factor,
)


def sample_base_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "id_contrato": "C1",
                "nombre_entidad": "Entidad A",
                "tipo_de_contrato": "Prestación de servicios",
                "fecha_inicio_contrato": "2025-01-01",
                "fecha_fin_contrato": "2025-03-02",
                "duracion_proceso": 2,
                "unidad_duracion_proceso": "Mes(es)",
                "documento_proveedor": "123",
                "codigo_proveedor": "X1",
                "supplier_key": "123",
                "proveedor_adjudicado": "Proveedor 1",
                "valor_del_contrato": 1000,
                "dias_adicionados": 15,
                "n_adiciones": 1,
                "flag_match_proceso": True,
                "flag_multiple_ubicaciones": False,
                "descripcion_modificacion_ejemplo": "Adición por valor de $33.935.616,00",
            },
            {
                "id_contrato": "C2",
                "nombre_entidad": "Entidad A",
                "tipo_de_contrato": "Prestación de servicios",
                "fecha_inicio_contrato": "2025-01-01",
                "fecha_fin_contrato": "2025-02-01",
                "duracion_proceso": 31,
                "unidad_duracion_proceso": "día(s)",
                "documento_proveedor": "123",
                "codigo_proveedor": "X1",
                "supplier_key": "123",
                "proveedor_adjudicado": "Proveedor 1",
                "valor_del_contrato": 900,
                "dias_adicionados": 0,
                "n_adiciones": 0,
                "flag_match_proceso": True,
                "flag_multiple_ubicaciones": True,
                "descripcion_modificacion_ejemplo": None,
            },
            {
                "id_contrato": "C3",
                "nombre_entidad": "Entidad A",
                "tipo_de_contrato": "Prestación de servicios",
                "fecha_inicio_contrato": None,
                "fecha_fin_contrato": None,
                "duracion_proceso": 4,
                "unidad_duracion_proceso": "Mes(es)",
                "documento_proveedor": "",
                "codigo_proveedor": "",
                "supplier_key": "PROVEEDOR 2",
                "proveedor_adjudicado": "Proveedor 2",
                "valor_del_contrato": 8000,
                "dias_adicionados": 0,
                "n_adiciones": 0,
                "flag_match_proceso": False,
                "flag_multiple_ubicaciones": False,
                "descripcion_modificacion_ejemplo": None,
            },
        ]
    )


def test_unit_to_days_factor() -> None:
    assert unit_to_days_factor("Mes(es)") == 30.0
    assert unit_to_days_factor("día(s)") == 1.0


def test_parse_currency_candidates() -> None:
    assert parse_currency_candidates("Adición por valor de $33.935.616,00") == 33935616


def test_compute_risk_features_expected_columns() -> None:
    features = compute_risk_features(sample_base_df())
    row = features.set_index("id_contrato").loc["C1"]
    assert row["base_duration_days"] > 0
    assert row["ratio_adiciones"] > 0
    assert row["share_proveedor_en_entidad"] > 0
    assert row["recurrencia_entidad_proveedor"] == 2
    flags = features.set_index("id_contrato")["data_quality_flags"]
    assert "múltiples ubicaciones" in flags.loc["C2"]
    assert "sin match de proceso" in flags.loc["C3"]
