from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from src.utils.config import get_settings
from src.utils.logging import configure_logging, logger


def parquet_path(path: Path) -> str:
    return path.as_posix()


def build_base_contracts() -> pd.DataFrame:
    settings = get_settings()
    con = duckdb.connect()
    raw_dir = settings.raw_dir

    contracts_path = parquet_path(raw_dir / "contracts.parquet")
    processes_path = parquet_path(raw_dir / "processes.parquet")
    additions_path = parquet_path(raw_dir / "additions.parquet")
    locations_path = parquet_path(raw_dir / "locations.parquet")

    query = f"""
    with contracts as (
      select
        trim(id_contrato) as id_contrato,
        trim(nombre_entidad) as nombre_entidad,
        try_cast(codigo_entidad as bigint) as codigo_entidad,
        trim(nit_entidad) as nit_entidad,
        trim(sector) as sector,
        trim(proceso_de_compra) as proceso_de_compra,
        trim(referencia_del_contrato) as referencia_del_contrato,
        trim(estado_contrato) as estado_contrato,
        trim(tipo_de_contrato) as tipo_de_contrato,
        trim(modalidad_de_contratacion) as modalidad_de_contratacion,
        trim(codigo_de_categoria_principal) as codigo_categoria_principal,
        try_cast(fecha_de_firma as timestamp) as fecha_de_firma,
        try_cast(fecha_de_inicio_del_contrato as timestamp) as fecha_inicio_contrato,
        try_cast(fecha_de_fin_del_contrato as timestamp) as fecha_fin_contrato,
        trim(documento_proveedor) as documento_proveedor,
        trim(codigo_proveedor) as codigo_proveedor,
        trim(proveedor_adjudicado) as proveedor_adjudicado,
        try_cast(valor_del_contrato as double) as valor_del_contrato,
        try_cast(dias_adicionados as double) as dias_adicionados,
        trim(urlproceso) as url_proceso,
        trim(objeto_del_contrato) as objeto_del_contrato
      from parquet_scan('{contracts_path}')
    ),
    ranked_processes as (
      select
        *,
        case
          when lower(coalesce(adjudicado, '')) = 'si' then 2
          when lower(coalesce(estado_del_procedimiento, '')) = 'seleccionado' then 1
          else 0
        end as process_priority,
        row_number() over (
          partition by id_del_portafolio
          order by
            case
              when lower(coalesce(adjudicado, '')) = 'si' then 2
              when lower(coalesce(estado_del_procedimiento, '')) = 'seleccionado' then 1
              else 0
            end desc,
            try_cast(fecha_de_ultima_publicaci as timestamp) desc nulls last,
            try_cast(fecha_de_publicacion_del as timestamp) desc nulls last
        ) as row_priority
      from parquet_scan('{processes_path}')
    ),
    selected_processes as (
      select
        trim(id_del_portafolio) as id_del_portafolio,
        trim(id_del_proceso) as id_del_proceso,
        try_cast(precio_base as double) as precio_base,
        try_cast(valor_total_adjudicacion as double) as valor_total_adjudicacion,
        try_cast(duracion as double) as duracion_proceso,
        trim(unidad_de_duracion) as unidad_duracion_proceso,
        trim(estado_del_procedimiento) as estado_del_procedimiento,
        trim(adjudicado) as adjudicado,
        trim(modalidad_de_contratacion) as modalidad_proceso,
        try_cast(proveedores_unicos_con as double) as proveedores_unicos_con_respuesta,
        try_cast(fecha_de_publicacion_del as timestamp) as fecha_publicacion_proceso,
        try_cast(fecha_de_ultima_publicaci as timestamp) as fecha_ultima_publicacion_proceso
      from ranked_processes
      where row_priority = 1
    ),
    additions as (
      select
        trim(id_contrato) as id_contrato,
        count(*) as n_modificaciones,
        sum(case when upper(coalesce(tipo, '')) like '%ADICION%' then 1 else 0 end) as n_adiciones,
        string_agg(distinct coalesce(tipo, ''), ' | ') as tipos_modificacion,
        min(coalesce(descripcion, '')) as descripcion_modificacion_ejemplo,
        max(try_cast(fecharegistro as timestamp)) as fecha_ultima_modificacion
      from parquet_scan('{additions_path}')
      group by 1
    ),
    locations as (
      select
        trim(id_contrato) as id_contrato,
        count(distinct nullif(trim(ubicacion), '')) as n_ubicaciones,
        count(
          distinct case
            when trim(coalesce(ubicacion, '')) not in ('', 'No definido') then trim(ubicacion)
          end
        ) as n_ubicaciones_validas,
        string_agg(
          distinct case
            when trim(coalesce(ubicacion, '')) not in ('', 'No definido') then trim(ubicacion)
          end,
          ' | '
        ) as ubicacion_ejecucion
      from parquet_scan('{locations_path}')
      group by 1
    )
    select
      c.id_contrato,
      c.nombre_entidad,
      c.codigo_entidad,
      c.nit_entidad,
      c.sector,
      c.proceso_de_compra,
      c.referencia_del_contrato,
      c.estado_contrato,
      c.tipo_de_contrato,
      c.modalidad_de_contratacion,
      c.codigo_categoria_principal,
      c.fecha_de_firma,
      c.fecha_inicio_contrato,
      c.fecha_fin_contrato,
      c.documento_proveedor,
      c.codigo_proveedor,
      c.proveedor_adjudicado,
      c.valor_del_contrato,
      c.dias_adicionados,
      c.url_proceso,
      c.objeto_del_contrato,
      p.id_del_proceso,
      p.id_del_portafolio,
      p.precio_base,
      p.valor_total_adjudicacion,
      p.duracion_proceso,
      p.unidad_duracion_proceso,
      p.estado_del_procedimiento,
      p.adjudicado,
      p.modalidad_proceso,
      p.proveedores_unicos_con_respuesta,
      p.fecha_publicacion_proceso,
      p.fecha_ultima_publicacion_proceso,
      a.n_modificaciones,
      a.n_adiciones,
      a.tipos_modificacion,
      a.descripcion_modificacion_ejemplo,
      a.fecha_ultima_modificacion,
      coalesce(l.n_ubicaciones, 0) as n_ubicaciones,
      coalesce(l.n_ubicaciones_validas, 0) as n_ubicaciones_validas,
      l.ubicacion_ejecucion,
      case when p.id_del_proceso is not null then true else false end as flag_match_proceso,
      case
        when coalesce(l.n_ubicaciones_validas, 0) > 1 then true
        else false
      end as flag_multiple_ubicaciones
    from contracts c
    left join selected_processes p
      on c.proceso_de_compra = p.id_del_portafolio
    left join additions a
      on c.id_contrato = a.id_contrato
    left join locations l
      on c.id_contrato = l.id_contrato
    """
    base_df = con.execute(query).df()
    con.close()

    base_df["n_modificaciones"] = base_df["n_modificaciones"].fillna(0).astype(int)
    base_df["n_adiciones"] = base_df["n_adiciones"].fillna(0).astype(int)
    base_df["supplier_key"] = (
        base_df["documento_proveedor"]
        .fillna("")
        .astype(str)
        .str.strip()
        .where(
            lambda s: s.ne(""),
            other=base_df["codigo_proveedor"].fillna("").astype(str).str.strip(),
        )
    )
    base_df["supplier_key"] = base_df["supplier_key"].where(
        base_df["supplier_key"].str.strip().ne(""),
        other=base_df["proveedor_adjudicado"].fillna("").astype(str).str.upper().str.strip(),
    )
    return base_df


def validate_base_contracts(base_df: pd.DataFrame) -> None:
    if base_df["id_contrato"].isna().any():
        raise ValueError("La tabla base contiene id_contrato nulo.")
    if base_df["id_contrato"].duplicated().any():
        raise ValueError("La tabla base no es única por id_contrato.")


def main() -> None:
    configure_logging()
    settings = get_settings()
    base_df = build_base_contracts()
    validate_base_contracts(base_df)
    output_path = settings.interim_dir / "base_contracts.parquet"
    base_df.to_parquet(output_path, index=False)
    logger.info(
        "Tabla base guardada con {} contratos y tasa de match con proceso de {:.2%}.",
        len(base_df),
        base_df["flag_match_proceso"].mean(),
    )


if __name__ == "__main__":
    main()
