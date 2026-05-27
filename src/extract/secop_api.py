from __future__ import annotations

import json
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
    validate_chunked_state,
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
    def __init__(self) -> None:
        self.settings = get_settings()
        headers = {"Accept": "application/json"}
        if self.settings.app_token_socrata:
            headers["X-App-Token"] = self.settings.app_token_socrata
        self.client = httpx.Client(
            base_url=self.settings.socrata_domain,
            headers=headers,
            timeout=self.settings.request_timeout_seconds,
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
                wait_seconds = 1.5 * attempt
                logger.warning(
                    "Error consultando {}. Reintento {}/{} en {}s.",
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
    validate_chunked_state(output_dir, state)
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


def main() -> None:
    configure_logging()
    settings = get_settings()
    move_legacy_assets()
    client = SocrataClient()
    manifest = load_manifest(settings.manifest_path, scope_payload(settings))
    manifest["scope"] = scope_payload(settings)

    try:
        metadata_dir = settings.raw_dir / "metadata"
        write_paa_status_json(manifest)
        for dataset_key, spec in DATASET_SPECS.items():
            if not should_extract(dataset_key):
                continue

            dataset_id = spec["id"]
            metadata = normalized_metadata(client.fetch_metadata(dataset_id))
            write_json(metadata, metadata_dir / f"{dataset_key}.json")

            if spec["layout"] == "chunked":
                stream_dataset_to_parquet(
                    dataset_key=dataset_key,
                    dataset_id=dataset_id,
                    params=build_params(dataset_key, spec),
                    output_dir=settings.raw_dir / dataset_key,
                    fetch_page=client.fetch_page,
                    manifest=manifest,
                )
            else:
                frame = client.fetch_all(dataset_id, build_params(dataset_key, spec))
                write_parquet(frame, settings.raw_dir / f"{dataset_key}.parquet")
                state = ensure_dataset_state(
                    manifest,
                    dataset_key=dataset_key,
                    dataset_id=dataset_id,
                    page_size=int(build_params(dataset_key, spec)["$limit"]),
                    mode=settings.extract_scope,
                    scope=dataset_scope(
                        settings.extract_scope,
                        settings.paa_years,
                        settings.scope_departments,
                        [],
                    ),
                    layout="single_file",
                )
                state["rows_written"] = frame.height
                state["completed"] = True
                update_dataset_state(manifest, dataset_key, state)

            manifest["datasets"][dataset_key]["metadata"] = metadata
            write_manifest(settings.manifest_path, manifest)
            if dataset_key == "paa_detail":
                write_paa_status_json(manifest)

        write_paa_status_json(manifest)
    finally:
        client.close()


if __name__ == "__main__":
    main()
