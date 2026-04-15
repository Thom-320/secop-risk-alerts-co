from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import httpx
import pandas as pd

from src.utils.config import get_settings
from src.utils.logging import configure_logging, logger

DATASETS: dict[str, str] = {
    "contracts": "jbjy-vk9h",
    "processes": "p6dx-8zbt",
    "additions": "cb9c-h8sn",
    "locations": "gra4-pcp2",
    "pida_context": "wmwy-ixwz",
    "secop_integrado_qc": "rpmr-utcd",
}


class SocrataClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        headers = {"Accept": "application/json"}
        if self.settings.app_token_socrata:
            headers["X-App-Token"] = self.settings.app_token_socrata
        self.client = httpx.Client(
            base_url=self.settings.socrata_domain,
            timeout=self.settings.request_timeout_seconds,
            headers=headers,
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
                sleep_seconds = attempt * 1.5
                logger.warning(
                    "Error consultando {}. Reintento {}/{} en {}s.",
                    path,
                    attempt,
                    retries,
                    sleep_seconds,
                )
                time.sleep(sleep_seconds)
        return []

    def fetch_metadata(self, dataset_id: str) -> dict[str, Any]:
        return self._request(f"/api/views/{dataset_id}")

    def fetch_page(self, dataset_id: str, params: dict[str, Any] | None = None) -> pd.DataFrame:
        rows = self._request(f"/resource/{dataset_id}.json", params=params)
        return sanitize_dataframe(pd.DataFrame(rows))

    def fetch_all(self, dataset_id: str, params: dict[str, Any] | None = None) -> pd.DataFrame:
        base_params = dict(params or {})
        limit = int(base_params.pop("$limit", self.settings.page_size))
        offset = 0
        pages: list[pd.DataFrame] = []
        while True:
            page_params = {**base_params, "$limit": limit, "$offset": offset}
            rows = self._request(f"/resource/{dataset_id}.json", params=page_params)
            if not rows:
                break
            frame = sanitize_dataframe(pd.DataFrame(rows))
            pages.append(frame)
            logger.info(
                "Dataset {}: página offset={} con {} filas.",
                dataset_id,
                offset,
                len(frame),
            )
            if len(frame) < limit:
                break
            offset += limit
        if not pages:
            return pd.DataFrame()
        return pd.concat(pages, ignore_index=True)

    def close(self) -> None:
        self.client.close()


def escape_socrata_string(value: str) -> str:
    return value.replace("'", "''")


def build_in_clause(field: str, values: list[str]) -> str:
    escaped = ", ".join(f"'{escape_socrata_string(value)}'" for value in values)
    return f"{field} in ({escaped})"


def write_parquet(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    logger.info("Guardado {} con {} filas.", output_path.name, len(df))


def write_json(data: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def sanitize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    clean_df = df.copy()
    for column in clean_df.columns:
        clean_df[column] = clean_df[column].map(
            lambda value: json.dumps(value, ensure_ascii=False, sort_keys=True)
            if isinstance(value, (dict, list))
            else value
        )
    return clean_df


def fetch_contracts(client: SocrataClient) -> pd.DataFrame:
    settings = get_settings()
    entity_clause = build_in_clause("nombre_entidad", settings.scope_entities)
    where = (
        f"fecha_de_firma between '{settings.start_date}' and '{settings.end_date}' "
        f"and {entity_clause}"
    )
    params = {"$where": where}
    return client.fetch_all(DATASETS["contracts"], params=params)


def fetch_by_batches(
    client: SocrataClient,
    dataset_key: str,
    field_name: str,
    values: list[str],
    batch_size: int = 500,
) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    unique_values = [
        value
        for value in pd.Series(values).dropna().astype(str).unique().tolist()
        if value
    ]
    for index in range(0, len(unique_values), batch_size):
        batch = unique_values[index : index + batch_size]
        params = {"$where": build_in_clause(field_name, batch)}
        frame = client.fetch_all(DATASETS[dataset_key], params=params)
        frames.append(frame)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True).drop_duplicates()


def fetch_auxiliary_context(client: SocrataClient) -> tuple[pd.DataFrame, pd.DataFrame]:
    settings = get_settings()
    pida_df = client.fetch_page(DATASETS["pida_context"], params={"$limit": 5000})
    secop_where = (
        f"fecha_de_firma_del_contrato between '{settings.start_date}' and '{settings.end_date}' "
        "and (upper(nombre_de_la_entidad) like '%SUBRED%' "
        "or upper(nombre_de_la_entidad) like '%SALUD%')"
    )
    secop_integrado_df = client.fetch_page(
        DATASETS["secop_integrado_qc"],
        params={"$where": secop_where, "$limit": 20000},
    )
    return pida_df, secop_integrado_df


def build_manifest(
    row_counts: dict[str, int],
    metadata: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    return {
        "scope": {
            "start_date": get_settings().start_date,
            "end_date": get_settings().end_date,
            "entities": get_settings().scope_entities,
        },
        "row_counts": row_counts,
        "datasets": metadata,
    }


def main() -> None:
    configure_logging()
    settings = get_settings()
    client = SocrataClient()
    try:
        metadata = {key: client.fetch_metadata(dataset_id) for key, dataset_id in DATASETS.items()}

        contracts_df = fetch_contracts(client)
        write_parquet(contracts_df, settings.raw_dir / "contracts.parquet")

        processes_df = fetch_by_batches(
            client,
            dataset_key="processes",
            field_name="id_del_portafolio",
            values=contracts_df.get("proceso_de_compra", pd.Series(dtype=str)).astype(str).tolist(),
        )
        write_parquet(processes_df, settings.raw_dir / "processes.parquet")

        additions_df = fetch_by_batches(
            client,
            dataset_key="additions",
            field_name="id_contrato",
            values=contracts_df.get("id_contrato", pd.Series(dtype=str)).astype(str).tolist(),
        )
        write_parquet(additions_df, settings.raw_dir / "additions.parquet")

        locations_df = fetch_by_batches(
            client,
            dataset_key="locations",
            field_name="id_contrato",
            values=contracts_df.get("id_contrato", pd.Series(dtype=str)).astype(str).tolist(),
        )
        write_parquet(locations_df, settings.raw_dir / "locations.parquet")

        pida_df, secop_integrado_df = fetch_auxiliary_context(client)
        write_parquet(pida_df, settings.raw_dir / "pida_context.parquet")
        write_parquet(secop_integrado_df, settings.raw_dir / "secop_integrado_qc.parquet")

        metadata_output = settings.raw_dir / "metadata"
        metadata_output.mkdir(exist_ok=True)
        normalized_metadata: dict[str, dict[str, Any]] = {}
        for key, view in metadata.items():
            record = {
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
            normalized_metadata[key] = record
            write_json(record, metadata_output / f"{key}.json")

        manifest = build_manifest(
            {
                "contracts": len(contracts_df),
                "processes": len(processes_df),
                "additions": len(additions_df),
                "locations": len(locations_df),
                "pida_context": len(pida_df),
                "secop_integrado_qc": len(secop_integrado_df),
            },
            normalized_metadata,
        )
        write_json(manifest, settings.raw_dir / "manifest.json")
    finally:
        client.close()


if __name__ == "__main__":
    main()
