from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

from src.extract.state import load_manifest
from src.utils.config import get_settings
from src.utils.io import read_parquet_flexible
from src.utils.logging import configure_logging, logger
from src.utils.normalization import (
    normalize_duration_to_days,
    normalize_reference,
    normalize_text,
    only_digits,
    parse_date,
    safe_float,
    text_is_sufficient,
)


@dataclass
class JoinAudit:
    p6dx_entity_code_fill_rate: float
    rpmr_entity_code_fill_rate: float
    paa_entity_code_fill_rate: float
    p6dx_entity_cardinality: int
    rpmr_entity_cardinality: int
    paa_entity_cardinality: int
    rpmr_high_confidence_link_rate: float
    paa_related_process_coverage: float
    process_text_sufficiency_rate: float
    comparable_ready_rate: float


def load_parquet(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo requerido: {path}")
    return read_parquet_flexible(path)


def paa_raw_path(raw_dir: Path) -> Path:
    chunked = raw_dir / "paa_detail"
    single_file = raw_dir / "paa_detail.parquet"
    if chunked.exists():
        return chunked
    return single_file


def validate_paa_source() -> None:
    settings = get_settings()
    path = paa_raw_path(settings.raw_dir)
    if not path.exists():
        raise FileNotFoundError("No existe fuente PAA activa en data/raw.")
    if path.is_file():
        return

    manifest = load_manifest(settings.manifest_path, scope={})
    paa_state = manifest.get("datasets", {}).get("paa_detail")
    if not paa_state:
        raise ValueError("Falta estado de `paa_detail` en manifest para fuente chunked.")
    if not paa_state.get("completed"):
        raise ValueError("`paa_detail` está incompleto; termina la extracción antes de construir.")
    if settings.extract_scope == "demo" and paa_state.get("mode") != "demo":
        raise ValueError("La fuente PAA activa no corresponde al scope demo esperado.")


def modality_family(value: str | None) -> str:
    text = normalize_text(value)
    if "licitacion" in text:
        return "licitacion"
    if "seleccion abreviada" in text:
        return "seleccion_abreviada"
    if "concurso" in text:
        return "concurso"
    if "directa" in text:
        return "contratacion_directa"
    if "minima" in text:
        return "minima_cuantia"
    return "otros"


def build_entity_key(code: object, nit: object, name: object) -> str:
    entity_code = only_digits(code)
    if entity_code:
        return f"code::{entity_code}"
    entity_nit = only_digits(nit)
    if entity_nit:
        return f"nit::{entity_nit}"
    return f"name::{normalize_text(name)}"


def normalize_secop_ii(frame: pd.DataFrame) -> pd.DataFrame:
    df = frame.copy()
    df["process_key"] = df["id_del_proceso"].astype(str).str.strip()
    df["entity_code"] = df["codigo_entidad"].map(only_digits)
    df["entity_nit"] = df["nit_entidad"].map(only_digits)
    df["entity_name"] = df["entidad"].fillna("").astype(str).str.strip()
    df["entity_key"] = df.apply(
        lambda row: build_entity_key(
            row.get("codigo_entidad"),
            row.get("nit_entidad"),
            row.get("entidad"),
        ),
        axis=1,
    )
    df["process_reference"] = df["referencia_del_proceso"].fillna("").astype(str).str.strip()
    df["process_reference_norm"] = df["process_reference"].map(normalize_reference)
    df["process_title"] = df["nombre_del_procedimiento"].fillna("").astype(str).str.strip()
    df["process_description"] = (
        df["descripci_n_del_procedimiento"].fillna("").astype(str).str.strip()
    )
    df["process_text"] = (
        df["process_title"].where(df["process_title"].ne(""), other="")
        + " "
        + df["process_description"].where(df["process_description"].ne(""), other="")
    ).str.strip()
    df["publication_date"] = df["fecha_de_publicacion_del"].map(parse_date)
    df["last_publication_date"] = df["fecha_de_ultima_publicaci"].map(parse_date)
    df["award_date"] = df["fecha_adjudicacion"].map(parse_date)
    df["process_year"] = df["publication_date"].dt.year.fillna(0).astype(int)
    df["base_price"] = df["precio_base"].map(safe_float)
    df["awarded_total"] = df["valor_total_adjudicacion"].map(safe_float)
    df["duration_days"] = df.apply(
        lambda row: normalize_duration_to_days(
            row.get("duracion"),
            row.get("unidad_de_duracion"),
        ),
        axis=1,
    )
    df["modality"] = df["modalidad_de_contratacion"].fillna("").astype(str).str.strip()
    df["modality_family"] = df["modality"].map(modality_family)
    df["contract_type"] = df["tipo_de_contrato"].fillna("").astype(str).str.strip()
    df["category_code"] = df["codigo_principal_de_categoria"].fillna("").astype(str).str.strip()
    df["response_count"] = df["conteo_de_respuestas_a_ofertas"].map(safe_float).fillna(0.0)
    df["invited_suppliers"] = df["proveedores_invitados"].map(safe_float).fillna(0.0)
    df["unique_suppliers"] = df["proveedores_unicos_con"].map(safe_float).fillna(0.0)
    df["provider_name"] = df["nombre_del_proveedor"].fillna("").astype(str).str.strip()
    df["provider_nit"] = df["nit_del_proveedor_adjudicado"].map(only_digits)
    df["adjudicado_flag"] = (
        df["adjudicado"].fillna("").astype(str).str.strip().str.lower().eq("si")
    )
    df["department"] = df["departamento_entidad"].fillna("").astype(str).str.strip()
    df["city"] = df["ciudad_entidad"].fillna("").astype(str).str.strip()
    df["text_sufficient"] = df["process_text"].map(text_is_sufficient)
    settings = get_settings()
    df["demo_scope"] = df["department"].isin(settings.scope_departments)

    columns = [
        "process_key",
        "entity_key",
        "entity_code",
        "entity_nit",
        "entity_name",
        "department",
        "city",
        "ordenentidad",
        "process_reference",
        "process_reference_norm",
        "ppi",
        "id_del_portafolio",
        "process_title",
        "process_description",
        "process_text",
        "publication_date",
        "last_publication_date",
        "award_date",
        "process_year",
        "base_price",
        "awarded_total",
        "duration_days",
        "modality",
        "modality_family",
        "contract_type",
        "category_code",
        "estado_del_procedimiento",
        "estado_resumen",
        "adjudicado_flag",
        "response_count",
        "invited_suppliers",
        "unique_suppliers",
        "provider_name",
        "provider_nit",
        "urlproceso",
        "text_sufficient",
        "demo_scope",
    ]
    return df[columns].rename(
        columns={
            "ordenentidad": "entity_order",
            "estado_del_procedimiento": "procedure_state",
            "estado_resumen": "state_summary",
            "urlproceso": "process_url",
        }
    )


def normalize_rpmr(frame: pd.DataFrame) -> pd.DataFrame:
    df = frame.copy()
    df["entity_code"] = df["codigo_entidad_en_secop"].map(only_digits)
    df["entity_nit"] = df["nit_de_la_entidad"].map(only_digits)
    df["entity_name"] = df["nombre_de_la_entidad"].fillna("").astype(str).str.strip()
    df["entity_key"] = df.apply(
        lambda row: build_entity_key(
            row.get("codigo_entidad_en_secop"),
            row.get("nit_de_la_entidad"),
            row.get("nombre_de_la_entidad"),
        ),
        axis=1,
    )
    df["process_reference_norm"] = df["numero_de_proceso"].map(normalize_reference)
    df["contract_date"] = df["fecha_de_firma_del_contrato"].map(parse_date)
    df["contract_value"] = df["valor_contrato"].map(safe_float)
    df["process_text"] = (
        df["objeto_del_proceso"].fillna("").astype(str).str.strip()
        + " "
        + df["objeto_a_contratar"].fillna("").astype(str).str.strip()
    ).str.strip()
    return df[
        [
            "entity_key",
            "entity_code",
            "entity_nit",
            "entity_name",
            "departamento_entidad",
            "municipio_entidad",
            "modalidad_de_contrataci_n",
            "tipo_de_contrato",
            "numero_del_contrato",
            "numero_de_proceso",
            "process_reference_norm",
            "contract_date",
            "contract_value",
            "nom_raz_social_contratista",
            "documento_proveedor",
            "url_contrato",
            "process_text",
        ]
    ].rename(
        columns={
            "departamento_entidad": "department",
            "municipio_entidad": "city",
            "modalidad_de_contrataci_n": "modality",
            "tipo_de_contrato": "contract_type",
            "nom_raz_social_contratista": "provider_name",
            "documento_proveedor": "provider_document",
            "url_contrato": "contract_url",
        }
    )


def normalize_paa(frame: pd.DataFrame) -> pd.DataFrame:
    df = frame.copy()
    df["entity_code"] = df["codigo_entidad"].map(only_digits)
    df["entity_nit"] = df["nit_entidad"].map(only_digits)
    df["entity_name"] = df["nombre_entidad"].fillna("").astype(str).str.strip()
    df["entity_key"] = df.apply(
        lambda row: build_entity_key(
            row.get("codigo_entidad"),
            row.get("nit_entidad"),
            row.get("nombre_entidad"),
        ),
        axis=1,
    )
    df["paa_item_id"] = df["id"].astype(str).str.strip()
    df["paa_year"] = pd.to_numeric(df["annio"], errors="coerce").fillna(0).astype(int)
    df["planned_start_date"] = df["fecha_esperada_de_inicio"].map(parse_date)
    df["planned_value"] = df["valor_total_esperado"].map(safe_float)
    df["planned_duration_days"] = df.apply(
        lambda row: normalize_duration_to_days(
            row.get("duracion_esperada"),
            row.get("unidad_de_duracion_esperada"),
        ),
        axis=1,
    )
    df["modality"] = df["modalidad"].fillna("").astype(str).str.strip()
    df["modality_family"] = df["modality"].map(modality_family)
    df["paa_text"] = df["descripcion"].fillna("").astype(str).str.strip()
    df["paa_text_sufficient"] = df["paa_text"].map(text_is_sufficient)
    df["related_process_reference_norm"] = df["procesos_relacionados"].map(normalize_reference)
    return df[
        [
            "paa_item_id",
            "entity_key",
            "entity_code",
            "entity_nit",
            "entity_name",
            "paa_year",
            "planned_start_date",
            "planned_value",
            "planned_duration_days",
            "modality",
            "modality_family",
            "categorias_unspsc",
            "paa_text",
            "paa_text_sufficient",
            "related_process_reference_norm",
            "procesos_relacionados",
            "url_proceso",
            "id_plan_anual_de_adquisiciones",
        ]
    ].rename(
        columns={
            "categorias_unspsc": "category_codes",
            "procesos_relacionados": "related_process_raw",
            "url_proceso": "process_url",
            "id_plan_anual_de_adquisiciones": "paa_plan_id",
        }
    )


def normalize_control_context(frame: pd.DataFrame) -> pd.DataFrame:
    df = frame.copy()
    df["subject_key"] = df["sujeto_auditado"].fillna("").astype(str).map(normalize_text)
    df["vigencia"] = pd.to_numeric(df["vigencia"], errors="coerce").fillna(0).astype(int)
    for column in (
        "hallazgos_administrativos",
        "hallazgos_disciplinarios",
        "hallazgos_penales",
        "hallazgos_fiscales",
        "cuant_a",
    ):
        df[column] = df[column].map(safe_float).fillna(0.0)
    return df[
        [
            "subject_key",
            "sujeto_auditado",
            "modalidad_de_auditor_a",
            "hallazgos_administrativos",
            "hallazgos_disciplinarios",
            "hallazgos_penales",
            "hallazgos_fiscales",
            "cuant_a",
            "vigencia",
        ]
    ].rename(
        columns={
            "sujeto_auditado": "subject_name",
            "modalidad_de_auditor_a": "audit_modality",
            "cuant_a": "amount",
        }
    )


def link_rpmr(processes: pd.DataFrame, rpmr: pd.DataFrame) -> pd.DataFrame:
    merged = processes.merge(
        rpmr,
        on=["entity_key", "process_reference_norm"],
        how="left",
        suffixes=("", "_rpmr"),
    )
    publication_date = pd.to_datetime(merged["publication_date"], errors="coerce")
    contract_date = pd.to_datetime(merged["contract_date"], errors="coerce")
    delta_days = (contract_date - publication_date).dt.days.abs()
    same_contract_type = (
        normalize_text_series(merged["contract_type"])
        == normalize_text_series(merged["contract_type_rpmr"])
    )
    merged["rpmr_match_confidence"] = 0.0
    has_reference = merged["process_reference_norm"].fillna("").ne("")
    has_contract = merged["numero_del_contrato"].fillna("").astype(str).str.strip().ne("")
    merged.loc[has_reference & has_contract, "rpmr_match_confidence"] = 0.7
    merged.loc[delta_days.notna() & delta_days.le(365), "rpmr_match_confidence"] += 0.2
    merged.loc[same_contract_type.fillna(False), "rpmr_match_confidence"] += 0.1
    merged["rpmr_match_confidence"] = merged["rpmr_match_confidence"].clip(0.0, 1.0)
    return merged[
        [
            "process_key",
            "entity_key",
            "process_reference_norm",
            "numero_del_contrato",
            "numero_de_proceso",
            "contract_date",
            "contract_value",
            "provider_name_rpmr",
            "provider_document",
            "contract_url",
            "rpmr_match_confidence",
        ]
    ].rename(columns={"provider_name_rpmr": "rpmr_provider_name"})


def normalize_text_series(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).map(normalize_text)


def validate_process_master(processes: pd.DataFrame) -> None:
    if processes["process_key"].isna().any():
        raise ValueError("La tabla process_master contiene process_key nulo.")
    if processes["process_key"].duplicated().any():
        raise ValueError("La tabla process_master no es única por process_key.")


def write_join_audit(path: Path, audit: JoinAudit) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = f"""# Join Audit

## Cobertura estructural

- Fill rate `codigo_entidad` en `p6dx-8zbt`: {audit.p6dx_entity_code_fill_rate:.2%}
- Fill rate `codigo_entidad` en `rpmr-utcd`: {audit.rpmr_entity_code_fill_rate:.2%}
- Fill rate `codigo_entidad` en `9sue-ezhx`: {audit.paa_entity_code_fill_rate:.2%}
- Cardinalidad `codigo_entidad` en `p6dx-8zbt`: {audit.p6dx_entity_cardinality:,}
- Cardinalidad `codigo_entidad` en `rpmr-utcd`: {audit.rpmr_entity_cardinality:,}
- Cardinalidad `codigo_entidad` en `9sue-ezhx`: {audit.paa_entity_cardinality:,}

## Join y preparación de señal

- Tasa de enlace de alta confianza `p6dx ↔ rpmr`: {audit.rpmr_high_confidence_link_rate:.2%}
- Cobertura útil de `procesos_relacionados` en PAA: {audit.paa_related_process_coverage:.2%}
- Procesos con texto suficiente para embeddings: {audit.process_text_sufficiency_rate:.2%}
- Procesos listos para comparables: {audit.comparable_ready_rate:.2%}

## Notas

- `p6dx-8zbt` es la tabla canónica del MVP.
- `rpmr-utcd` se usa solo como enriquecimiento cuando el enlace es de alta confianza.
- `9sue-ezhx` queda visible desde el inicio,
  pero su entrada al score depende de compuerta posterior.
- `wasc-xi4h` se mantiene como contexto visible y no entra al score base.
"""
    path.write_text(content)


def build_process_master() -> dict[str, pd.DataFrame]:
    settings = get_settings()
    raw_dir = settings.raw_dir
    validate_paa_source()
    processes = normalize_secop_ii(load_parquet(raw_dir / "secop_ii_processes.parquet"))
    rpmr = normalize_rpmr(load_parquet(raw_dir / "secop_integrado.parquet"))
    paa = normalize_paa(load_parquet(paa_raw_path(raw_dir)))
    control = normalize_control_context(load_parquet(raw_dir / "control_fiscal_context.parquet"))

    validate_process_master(processes)
    rpmr_linkage = link_rpmr(processes, rpmr)

    process_master = processes.merge(
        rpmr_linkage.sort_values("rpmr_match_confidence", ascending=False)
        .drop_duplicates("process_key"),
        on=["process_key", "entity_key", "process_reference_norm"],
        how="left",
    )
    process_master["rpmr_linked"] = process_master["rpmr_match_confidence"].fillna(0.0) >= 0.8

    audit = JoinAudit(
        p6dx_entity_code_fill_rate=process_master["entity_code"].fillna("").ne("").mean(),
        rpmr_entity_code_fill_rate=rpmr["entity_code"].fillna("").ne("").mean(),
        paa_entity_code_fill_rate=paa["entity_code"].fillna("").ne("").mean(),
        p6dx_entity_cardinality=process_master["entity_code"].replace("", pd.NA).nunique(),
        rpmr_entity_cardinality=rpmr["entity_code"].replace("", pd.NA).nunique(),
        paa_entity_cardinality=paa["entity_code"].replace("", pd.NA).nunique(),
        rpmr_high_confidence_link_rate=process_master["rpmr_linked"].mean(),
        paa_related_process_coverage=paa["related_process_reference_norm"].fillna("").ne("").mean(),
        process_text_sufficiency_rate=process_master["text_sufficient"].mean(),
        comparable_ready_rate=(
            process_master["text_sufficient"] & process_master["demo_scope"]
        ).mean(),
    )

    output = {
        "process_master": process_master,
        "paa_items": paa,
        "control_context": control,
        "rpmr_linkage": rpmr_linkage,
        "join_audit": pd.DataFrame([asdict(audit)]),
    }
    return output


def main() -> None:
    configure_logging()
    settings = get_settings()
    assets = build_process_master()
    settings.interim_dir.mkdir(parents=True, exist_ok=True)
    settings.validation_dir.mkdir(parents=True, exist_ok=True)

    for name, frame in assets.items():
        if name == "join_audit":
            continue
        output_path = settings.interim_dir / f"{name}.parquet"
        frame.to_parquet(output_path, index=False)
        logger.info("Guardado {} con {} filas.", output_path.name, len(frame))

    rpmr_sample = (
        assets["rpmr_linkage"]
        .sort_values("rpmr_match_confidence", ascending=False)
        .head(80)
        .copy()
    )
    rpmr_sample.to_csv(settings.validation_dir / "rpmr_linkage_sample.csv", index=False)

    audit = JoinAudit(**assets["join_audit"].iloc[0].to_dict())
    write_join_audit(settings.docs_dir / "join-audit.md", audit)
    logger.info("Join audit inicial escrito en docs/join-audit.md.")


if __name__ == "__main__":
    main()
