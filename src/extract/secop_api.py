from __future__ import annotations

import json
import os
import shutil
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
import pandas as pd
import polars as pl

from src.extract.state import (
    dataset_scope,
    ensure_dataset_state,
    load_manifest,
    update_dataset_state,
    write_manifest,
)
from src.utils.config import get_settings
from src.utils.io import list_partition_parts
from src.utils.logging import configure_logging, logger
from src.utils.normalization import only_digits

DATASET_SPECS: dict[str, dict[str, Any]] = {
    "secop_ii_processes": {
        "id": "p6dx-8zbt",
        "layout": "single_file",
        "where": (
            "fecha_de_publicacion_del between "
            "'{start_date}' and '{end_date}'"
        ),
        "select": [
            "entidad",
            "nit_entidad",
            "departamento_entidad",
            "ciudad_entidad",
            "ordenentidad",
            "codigo_pci",
            "id_del_proceso",
            "referencia_del_proceso",
            "ppi",
            "id_del_portafolio",
            "nombre_del_procedimiento",
            "descripci_n_del_procedimiento",
            "fase",
            "fecha_de_publicacion_del",
            "fecha_de_ultima_publicaci",
            "precio_base",
            "modalidad_de_contratacion",
            "justificaci_n_modalidad_de",
            "duracion",
            "unidad_de_duracion",
            "proveedores_invitados",
            "proveedores_con_invitacion",
            "proveedores_que_manifestaron",
            "respuestas_al_procedimiento",
            "conteo_de_respuestas_a_ofertas",
            "proveedores_unicos_con",
            "numero_de_lotes",
            "estado_del_procedimiento",
            "adjudicado",
            "fecha_adjudicacion",
            "valor_total_adjudicacion",
            "nombre_del_proveedor",
            "nit_del_proveedor_adjudicado",
            "codigo_principal_de_categoria",
            "estado_de_apertura_del_proceso",
            "tipo_de_contrato",
            "subtipo_de_contrato",
            "urlproceso",
            "codigo_entidad",
            "estado_resumen",
        ],
    },
    "secop_integrado": {
        "id": "rpmr-utcd",
        "layout": "single_file",
        "where": (
            "fecha_de_firma_del_contrato between "
            "'{start_date}' and '{end_date}'"
        ),
        "select": [
            "nivel_entidad",
            "codigo_entidad_en_secop",
            "nombre_de_la_entidad",
            "nit_de_la_entidad",
            "departamento_entidad",
            "municipio_entidad",
            "estado_del_proceso",
            "modalidad_de_contrataci_n",
            "objeto_a_contratar",
            "objeto_del_proceso",
            "tipo_de_contrato",
            "fecha_de_firma_del_contrato",
            "fecha_inicio_ejecuci_n",
            "fecha_fin_ejecuci_n",
            "numero_del_contrato",
            "numero_de_proceso",
            "valor_contrato",
            "nom_raz_social_contratista",
            "url_contrato",
            "origen",
            "tipo_documento_proveedor",
            "documento_proveedor",
        ],
    },
    "paa_detail": {
        "id": "9sue-ezhx",
        "layout": "chunked",
        "select": [
            "id",
            "identificador_unico",
            "descripcion",
            "fecha_esperada_de_inicio",
            "fecha_esperada_de_recepcion",
            "duracion_esperada",
            "unidad_de_duracion_esperada",
            "origen_recursos",
            "valor_total_esperado",
            "valor_esperado_de_presupuesto",
            "modalidad",
            "categorias_unspsc",
            "id_plan_anual_de_adquisiciones",
            "procesos_relacionados",
            "url_proceso",
            "codigo_entidad",
            "nombre_entidad",
            "nit_entidad",
            "id_paa_encabezado",
            "causal_de_contratacion",
            "grupo_de_procedimiento",
            "annio",
            "tipo",
            "version_del_paa",
            "fecha_version",
            "fecha_de_carga_del_paa",
        ],
    },
    "control_fiscal_context": {
        "id": "wasc-xi4h",
        "layout": "single_file",
        "select": [
            "sujeto_auditado",
            "modalidad_de_auditor_a",
            "hallazgos_administrativos",
            "hallazgos_disciplinarios",
            "hallazgos_penales",
            "hallazgos_fiscales",
            "cuant_a",
            "vigencia",
        ],
    },
}

LEGACY_RAW_FILES = [
    "additions.parquet",
    "contracts.parquet",
    "locations.parquet",
    "pida_context.parquet",
    "processes.parquet",
    "secop_integrado_qc.parquet",
]

LEGACY_METADATA_FILES = [
    "additions.json",
    "contracts.json",
    "locations.json",
    "pida_context.json",
    "processes.json",
    "secop_integrado_qc.json",
]


class SocrataClient:
    def __init__(self, timeout_seconds: float | None = None) -> None:
        self.settings = get_settings()
        headers = {"Accept": "application/json"}
        if self.settings.app_token_socrata:
            headers["X-App-Token"] = self.settings.app_token_socrata
        effective_timeout = timeout_seconds or self.settings.request_timeout_seconds
        self.client = httpx.Client(
            base_url=self.settings.socrata_domain,
            headers=headers,
            timeout=effective_timeout,
        )

    def _request(self, path: str, params: dict[str, Any] | None = None) -> Any:
        retries = self.settings.request_retries
        for attempt in range(1, retries + 1):
            try:
                response = self.client.get(path, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as exc:
                if attempt == retries:
                    raise RuntimeError(f"Fallo consultando {path}: {exc}") from exc
                wait_seconds = 2.5 * attempt
                logger.warning(
                    "Error consultando {}. Reintento {}/{} en {:.1f}s.",
                    path,
                    attempt,
                    retries,
                    wait_seconds,
                )
                time.sleep(wait_seconds)
        return []

    def fetch_metadata(self, dataset_id: str) -> dict[str, Any]:
        return self._request(f"/api/views/{dataset_id}.json")

    def fetch_page(self, dataset_id: str, params: dict[str, Any]) -> pl.DataFrame:
        rows = self._request(f"/resource/{dataset_id}.json", params=params)
        return sanitize_frame(rows)

    def fetch_all(self, dataset_id: str, params: dict[str, Any]) -> pl.DataFrame:
        limit = int(params.get("$limit", self.settings.page_size))
        offset = 0
        frames: list[pl.DataFrame] = []
        while True:
            page_params = dict(params)
            page_params["$limit"] = limit
            page_params["$offset"] = offset
            frame = self.fetch_page(dataset_id, page_params)
            if frame.height == 0:
                break
            frames.append(frame)
            logger.info(
                "Dataset {}: página offset={} con {} filas.",
                dataset_id,
                offset,
                frame.height,
            )
            offset += frame.height
            if frame.height < limit:
                break
        if not frames:
            return pl.DataFrame()
        return pl.concat(frames, how="diagonal_relaxed")

    def close(self) -> None:
        self.client.close()


def sanitize_value(value: Any) -> Any:
    if isinstance(value, dict):
        if "url" in value:
            return value["url"]
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    if isinstance(value, list):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return value


def sanitize_frame(rows: list[dict[str, Any]]) -> pl.DataFrame:
    clean_rows = [{key: sanitize_value(value) for key, value in row.items()} for row in rows]
    if not clean_rows:
        return pl.DataFrame()
    return pl.DataFrame(clean_rows)


def normalized_metadata(view: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": view.get("id"),
        "name": view.get("name"),
        "description": view.get("description"),
        "rowsUpdatedAt": view.get("rowsUpdatedAt"),
        "columns": [
            {
                "name": column.get("name"),
                "fieldName": column.get("fieldName"),
                "dataTypeName": column.get("dataTypeName"),
            }
            for column in view.get("columns", [])
        ],
    }


def write_parquet(frame: pl.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.write_parquet(path)
    logger.info("Guardado {} con {} filas.", path.name, frame.height)


def write_json(data: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def _column_frame(rows: list[dict[str, Any]], columns: list[str]) -> pd.DataFrame:
    frame = pd.DataFrame(rows)
    for column in columns:
        if column not in frame.columns:
            frame[column] = ""
    return frame[columns]


def write_sample_product_sources() -> None:
    """Prepare a versionable product dataset without calling Socrata.

    Prefers the larger generated Parquet (20k+ rows) when available so the
    demo shows a meaningful ranking.  Falls back to the tiny fixture CSV for
    CI / minimal smoke tests.
    """
    settings = get_settings()
    generated_proc = settings.root_dir / "data" / "sample" / "generated" / "processes.parquet"
    if generated_proc.exists():
        processes = pd.read_parquet(generated_proc).drop_duplicates(subset=["id_del_proceso"])
        logger.info("Usando datos generados ({:,} procesos).", len(processes))
    else:
        fixture_dir = settings.root_dir / "data" / "sample" / "fixtures"
        processes = pd.read_csv(fixture_dir / "processes.csv")
        logger.info("Usando fixtures CSV ({:,} procesos).", len(processes))
    fixture_dir = settings.root_dir / "data" / "sample" / "fixtures"
    contracts = pd.read_csv(fixture_dir / "contracts.csv")
    paa = pd.read_csv(fixture_dir / "paa.csv")

    process_rows = []
    reference_by_process = dict(
        zip(processes["id_del_proceso"], processes["referencia_del_proceso"], strict=False)
    )
    for row in processes.to_dict(orient="records"):
        publication_date = row.get(
            "fecha_de_publicacion_del"
        ) or row.get(
            "fecha_de_apertura_efectiva"
        ) or row.get(
            "fecha_de_apertura_de_respuesta"
        ) or row.get(
            "fecha_de_recepcion_de"
        ) or ""
        process_rows.append(
            {
                **row,
                "ppi": "",
                "id_del_portafolio": "",
                "fase": "",
                "fecha_de_publicacion_del": publication_date,
                "fecha_de_ultima_publicaci": publication_date,
                "unidad_de_duracion": "Dias",
                "justificaci_n_modalidad_de": "",
                "proveedores_con_invitacion": row.get("proveedores_invitados", ""),
                "proveedores_que_manifestaron": row.get("proveedores_unicos_con", ""),
                "numero_de_lotes": "1",
                "estado_de_apertura_del_proceso": "",
                "subtipo_de_contrato": "",
                "codigo_pci": "",
                "adjudicado": "Si" if row.get("fecha_adjudicacion") else "No",
                "estado_resumen": row.get("estado_del_procedimiento", ""),
            }
        )

    contract_rows = []
    process_lookup = processes.set_index("id_del_proceso").to_dict(orient="index")
    for row in contracts.to_dict(orient="records"):
        source = process_lookup.get(row.get("proceso_de_compra"), {})
        contract_rows.append(
            {
                "nivel_entidad": source.get("ordenentidad", "Territorial"),
                "codigo_entidad_en_secop": source.get("codigo_entidad", ""),
                "nombre_de_la_entidad": source.get("entidad", ""),
                "nit_de_la_entidad": source.get("nit_entidad", ""),
                "departamento_entidad": source.get("departamento_entidad", ""),
                "municipio_entidad": source.get("ciudad_entidad", ""),
                "estado_del_proceso": source.get("estado_del_procedimiento", ""),
                "modalidad_de_contrataci_n": source.get("modalidad_de_contratacion", ""),
                "objeto_a_contratar": source.get("nombre_del_procedimiento", ""),
                "objeto_del_proceso": source.get("descripci_n_del_procedimiento", ""),
                "tipo_de_contrato": source.get("tipo_de_contrato", ""),
                "fecha_de_firma_del_contrato": row.get("fecha_de_firma", ""),
                "fecha_inicio_ejecuci_n": row.get("fecha_de_inicio_del_contrato", ""),
                "fecha_fin_ejecuci_n": row.get("fecha_de_fin_del_contrato", ""),
                "numero_del_contrato": row.get("id_contrato", ""),
                "numero_de_proceso": reference_by_process.get(row.get("proceso_de_compra"), ""),
                "valor_contrato": row.get("valor_del_contrato", ""),
                "nom_raz_social_contratista": row.get("proveedor_adjudicado", ""),
                "url_contrato": row.get("urlproceso", ""),
                "origen": "sample",
                "tipo_documento_proveedor": "",
                "documento_proveedor": row.get("documento_proveedor", ""),
            }
        )

    paa_rows = []
    for row in paa.to_dict(orient="records"):
        paa_rows.append(
            {
                **row,
                "identificador_unico": row.get("id", ""),
                "unidad_de_duracion_esperada": "Dias",
                "origen_recursos": "",
                "valor_esperado_de_presupuesto": row.get("valor_total_esperado", ""),
                "categorias_unspsc": "",
                "id_paa_encabezado": row.get("id_plan_anual_de_adquisiciones", ""),
                "causal_de_contratacion": "",
                "grupo_de_procedimiento": "",
                "tipo": "",
                "fecha_version": "",
                "fecha_de_carga_del_paa": "",
            }
        )

    control_rows = [
        {
            "sujeto_auditado": "Alcaldia Demo Meta",
            "modalidad_de_auditor_a": "Contexto visible sample",
            "hallazgos_administrativos": 0,
            "hallazgos_disciplinarios": 0,
            "hallazgos_penales": 0,
            "hallazgos_fiscales": 0,
            "cuant_a": 0,
            "vigencia": 2025,
        },
        {
            "sujeto_auditado": "Gobernacion Demo Casanare",
            "modalidad_de_auditor_a": "Contexto visible sample",
            "hallazgos_administrativos": 0,
            "hallazgos_disciplinarios": 0,
            "hallazgos_penales": 0,
            "hallazgos_fiscales": 0,
            "cuant_a": 0,
            "vigencia": 2025,
        },
    ]

    settings.raw_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir = settings.raw_dir / "metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    _column_frame(process_rows, DATASET_SPECS["secop_ii_processes"]["select"]).to_parquet(
        settings.raw_dir / "secop_ii_processes.parquet",
        index=False,
    )
    _column_frame(contract_rows, DATASET_SPECS["secop_integrado"]["select"]).to_parquet(
        settings.raw_dir / "secop_integrado.parquet",
        index=False,
    )
    _column_frame(paa_rows, DATASET_SPECS["paa_detail"]["select"]).to_parquet(
        settings.raw_dir / "paa_detail.parquet",
        index=False,
    )
    _column_frame(control_rows, DATASET_SPECS["control_fiscal_context"]["select"]).to_parquet(
        settings.raw_dir / "control_fiscal_context.parquet",
        index=False,
    )
    manifest = {
        "version": 2,
        "scope": scope_payload(settings),
        "datasets": {
            key: {
                "dataset_key": key,
                "dataset_id": spec["id"],
                "mode": "sample",
                "layout": spec["layout"],
                "rows_written": (
                    len(process_rows)
                    if key == "secop_ii_processes"
                    else len(contract_rows)
                    if key == "secop_integrado"
                    else len(paa_rows)
                    if key == "paa_detail"
                    else len(control_rows)
                ),
                "completed": True,
                "metadata": {"id": spec["id"], "name": f"sample::{key}"},
            }
            for key, spec in DATASET_SPECS.items()
        },
    }
    write_manifest(settings.manifest_path, manifest)
    for key, spec in DATASET_SPECS.items():
        write_json({"id": spec["id"], "name": f"sample::{key}"}, metadata_dir / f"{key}.json")
    logger.info("Fuentes sample del producto escritas en {}.", settings.raw_dir)


def scope_payload(settings: Any) -> dict[str, Any]:
    return {
        "start_date": settings.start_date,
        "end_date": settings.end_date,
        "scope_departments": settings.scope_departments,
        "extract_scope": settings.extract_scope,
        "paa_years": settings.paa_years,
        "paa_entity_codes": settings.paa_entity_codes,
    }


def should_extract(dataset_key: str) -> bool:
    settings = get_settings()
    if not settings.extract_only:
        return True
    return dataset_key in settings.extract_only


def build_demo_entity_codes() -> list[str]:
    settings = get_settings()
    if settings.paa_entity_codes:
        return sorted(
            {
                only_digits(code)
                for code in settings.paa_entity_codes
                if only_digits(code)
            }
        )

    sources = [
        (
            settings.raw_dir / "secop_ii_processes.parquet",
            "codigo_entidad",
            "departamento_entidad",
        ),
        (
            settings.raw_dir / "secop_integrado.parquet",
            "codigo_entidad_en_secop",
            "departamento_entidad",
        ),
    ]
    codes: set[str] = set()
    for path, code_col, dep_col in sources:
        if not path.exists():
            continue
        frame = pd.read_parquet(path, columns=[code_col, dep_col])
        filtered = frame[frame[dep_col].isin(settings.scope_departments)][code_col]
        codes.update(
            only_digits(value)
            for value in filtered.dropna().tolist()
            if only_digits(value)
        )
    return sorted(codes)


def paa_where_clause() -> str:
    settings = get_settings()
    year_filter = ", ".join(f"'{year}'" for year in settings.paa_years)
    conditions = [f"annio in ({year_filter})"]
    if settings.extract_scope == "demo":
        entity_codes = build_demo_entity_codes()
        if not entity_codes:
            raise ValueError(
                "No se pudieron resolver `codigo_entidad` demo para PAA. "
                "Define `PAA_ENTITY_CODES` o extrae antes `p6dx/rpmr`."
            )
        code_filter = ", ".join(f"'{code}'" for code in entity_codes)
        conditions.append(f"codigo_entidad in ({code_filter})")
    return " and ".join(f"({condition})" for condition in conditions)


def build_params(dataset_key: str, spec: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    page_size = settings.paa_page_size if dataset_key == "paa_detail" else settings.page_size
    params: dict[str, Any] = {"$limit": page_size}
    if spec.get("select"):
        params["$select"] = ", ".join(spec["select"])
    if dataset_key == "paa_detail":
        params["$where"] = paa_where_clause()
    elif spec.get("where"):
        params["$where"] = spec["where"].format(
            start_date=settings.start_date,
            end_date=settings.end_date,
        )
    return params


def stream_dataset_to_parquet(
    *,
    dataset_key: str,
    dataset_id: str,
    params: dict[str, Any],
    output_dir: Path,
    fetch_page: Callable[[str, dict[str, Any]], pl.DataFrame],
    manifest: dict[str, Any],
    max_pages: int | None = None,
) -> dict[str, Any]:
    settings = get_settings()
    limit = int(params["$limit"])
    state = ensure_dataset_state(
        manifest,
        dataset_key=dataset_key,
        dataset_id=dataset_id,
        page_size=limit,
        mode=settings.extract_scope,
        scope=dataset_scope(
            settings.extract_scope,
            settings.paa_years,
            settings.scope_departments,
            build_demo_entity_codes() if dataset_key == "paa_detail" else [],
        ),
        layout="chunked",
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    parts_on_disk = sorted(output_dir.glob("part-*.parquet"))
    expected_parts = int(state.get("part_count", 0))
    if len(parts_on_disk) != expected_parts:
        logger.warning(
            "Inconsistencia entre manifest (%d partes) y disco (%d partes) para %s. "
            "Reiniciando extraccion desde offset 0.",
            expected_parts,
            len(parts_on_disk),
            dataset_key,
        )
        for part in parts_on_disk:
            part.unlink()
        state["next_offset"] = 0
        state["rows_written"] = 0
        state["part_count"] = 0
        state["completed"] = False
        update_dataset_state(manifest, dataset_key, state)
        write_manifest(settings.manifest_path, manifest)
        if dataset_key == "paa_detail":
            write_paa_status_json(manifest)

    if state.get("completed"):
        logger.info("Dataset {} ya estaba completo en modo {}.", dataset_key, state["mode"])
        if dataset_key == "paa_detail":
            write_paa_status_json(manifest)
        return state

    offset = int(state.get("next_offset", 0))
    rows_written = int(state.get("rows_written", 0))
    part_count = int(state.get("part_count", 0))
    pages_written = 0

    while True:
        if max_pages is not None and pages_written >= max_pages:
            break
        page_params = dict(params)
        page_params["$offset"] = offset
        frame = fetch_page(dataset_id, page_params)
        if frame.height == 0:
            state["completed"] = True
            update_dataset_state(manifest, dataset_key, state)
            write_manifest(settings.manifest_path, manifest)
            if dataset_key == "paa_detail":
                write_paa_status_json(manifest)
            break

        part_count += 1
        part_path = output_dir / f"part-{part_count:06d}.parquet"
        if part_path.exists():
            raise ValueError(f"El chunk ya existe y provocaría duplicados: {part_path.name}")
        frame.write_parquet(part_path)
        logger.info(
            "Dataset {}: chunk {} offset={} con {} filas.",
            dataset_id,
            part_path.name,
            offset,
            frame.height,
        )

        offset += frame.height
        rows_written += frame.height
        pages_written += 1

        state["next_offset"] = offset
        state["rows_written"] = rows_written
        state["part_count"] = part_count
        state["completed"] = frame.height < limit
        update_dataset_state(manifest, dataset_key, state)
        write_manifest(settings.manifest_path, manifest)
        if dataset_key == "paa_detail":
            write_paa_status_json(manifest)
        if frame.height < limit:
            break

    return state


def move_legacy_assets() -> None:
    settings = get_settings()
    settings.legacy_raw_dir.mkdir(parents=True, exist_ok=True)
    (settings.legacy_raw_dir / "metadata").mkdir(parents=True, exist_ok=True)

    for filename in LEGACY_RAW_FILES:
        source = settings.raw_dir / filename
        destination = settings.legacy_raw_dir / filename
        if source.exists() and not destination.exists():
            shutil.move(source.as_posix(), destination.as_posix())

    for filename in LEGACY_METADATA_FILES:
        source = settings.raw_dir / "metadata" / filename
        destination = settings.legacy_raw_dir / "metadata" / filename
        if source.exists() and not destination.exists():
            shutil.move(source.as_posix(), destination.as_posix())

    legacy_manifest = settings.raw_dir / "manifest.json"
    destination_manifest = settings.legacy_raw_dir / "manifest.legacy.json"
    if legacy_manifest.exists():
        try:
            current = json.loads(legacy_manifest.read_text())
        except json.JSONDecodeError:
            current = {}
        if current.get("version") != 2 and not destination_manifest.exists():
            shutil.move(legacy_manifest.as_posix(), destination_manifest.as_posix())


def write_paa_status_json(manifest: dict[str, Any]) -> None:
    settings = get_settings()
    paa_state = manifest.get("datasets", {}).get("paa_detail")
    if not paa_state:
        return
    started_at = paa_state.get("started_at")
    updated_at = paa_state.get("updated_at")
    duration_seconds = None
    if started_at and updated_at:
        try:
            start = datetime.fromisoformat(started_at)
            end = datetime.fromisoformat(updated_at)
            duration_seconds = max(0.0, (end - start).total_seconds())
        except ValueError:
            duration_seconds = None
    status = {
        "dataset_key": paa_state["dataset_key"],
        "dataset_id": paa_state["dataset_id"],
        "mode": paa_state["mode"],
        "scope": paa_state["scope"],
        "rows_written": paa_state["rows_written"],
        "part_count": paa_state["part_count"],
        "next_offset": paa_state["next_offset"],
        "completed": paa_state["completed"],
        "parts_present": len(list_partition_parts(settings.raw_dir / "paa_detail")),
        "started_at": started_at,
        "updated_at": updated_at,
        "duration_seconds": duration_seconds,
    }
    write_json(status, settings.validation_dir / "paa_extraction_status.json")


def finalize_single_file_dataset(
    *,
    dataset_key: str,
    output_dir: Path,
    manifest: dict[str, Any],
) -> Path:
    """Concatenate all part files into a single parquet and remove parts.
    
    The output file is written to the parent of output_dir (e.g.
    data/raw/secop_ii_processes.parquet, not data/raw/secop_ii_processes/secop_ii_processes.parquet).
    """
    state = manifest.get("datasets", {}).get(dataset_key, {})
    if not state.get("completed"):
        return output_dir.parent / f"{dataset_key}.parquet"

    part_files = sorted(output_dir.glob("part-*.parquet"))
    if not part_files:
        return output_dir.parent / f"{dataset_key}.parquet"

    frames = [pl.read_parquet(str(p)) for p in part_files]
    combined = pl.concat(frames, how="diagonal_relaxed")
    output_path = output_dir.parent / f"{dataset_key}.parquet"
    combined.write_parquet(output_path)
    logger.info(
        "Consolidado {} con {} filas desde {} partes.",
        dataset_key,
        combined.height,
        len(frames),
    )

    for part_file in part_files:
        part_file.unlink()
    return output_path


def _resolve_single_file_state(
    manifest: dict[str, Any],
    dataset_key: str,
    output_dir: Path,
) -> bool:
    """Return True if the single_file dataset should be re-extracted from scratch.
    
    Returns False if the dataset is already complete and the output file exists.
    Returns False if a partial extraction exists and should be resumed.
    """
    state = manifest.get("datasets", {}).get(dataset_key, {})
    output_file = output_dir / f"{dataset_key}.parquet"
    
    if state.get("completed"):
        if output_file.exists():
            return False
        part_files = sorted(output_dir.glob("part-*.parquet"))
        if part_files:
            return False
        manifest["datasets"].pop(dataset_key, None)
        return True
    
    return False


def main() -> None:
    configure_logging()
    if (os.getenv("PRODUCT_SOURCE_MODE") or "").strip().lower() == "sample":
        write_sample_product_sources()
        return
    settings = get_settings()
    move_legacy_assets()

    stream_client = SocrataClient(timeout_seconds=90.0)
    metadata_client = SocrataClient()

    manifest = load_manifest(settings.manifest_path, scope_payload(settings))
    manifest["scope"] = scope_payload(settings)

    try:
        metadata_dir = settings.raw_dir / "metadata"
        write_paa_status_json(manifest)
        for dataset_key, spec in DATASET_SPECS.items():
            if not should_extract(dataset_key):
                continue

            dataset_id = spec["id"]
            metadata = normalized_metadata(metadata_client.fetch_metadata(dataset_id))
            write_json(metadata, metadata_dir / f"{dataset_key}.json")

            output_dir = settings.raw_dir / dataset_key
            layout = spec.get("layout", "single_file")

            if layout == "single_file" and _resolve_single_file_state(
                manifest, dataset_key, output_dir
            ):
                for old_part in sorted(output_dir.glob("part-*.parquet")):
                    old_part.unlink()

            stream_dataset_to_parquet(
                dataset_key=dataset_key,
                dataset_id=dataset_id,
                params=build_params(dataset_key, spec),
                output_dir=output_dir,
                fetch_page=stream_client.fetch_page,
                manifest=manifest,
            )

            if layout == "single_file":
                _ = finalize_single_file_dataset(
                    dataset_key=dataset_key,
                    output_dir=output_dir,
                    manifest=manifest,
                )

            manifest["datasets"][dataset_key]["metadata"] = metadata
            write_manifest(settings.manifest_path, manifest)
            if dataset_key == "paa_detail":
                write_paa_status_json(manifest)

        write_paa_status_json(manifest)
    finally:
        stream_client.close()
        metadata_client.close()


if __name__ == "__main__":
    main()
