# Arquitectura

## Flujo

1. `src/extract/secop_api.py`
   - Consulta Socrata
   - Guarda snapshots crudos en Parquet
2. `src/transform/build_base_contracts.py`
   - Arma tabla base canónica por contrato
3. `src/features/risk_features.py`
   - Calcula features analíticas
4. `src/scoring/score_contracts.py`
   - Calcula score, explicaciones y agregado de proveedores
5. `src/app/streamlit_app.py`
   - Presenta rankings y fichas de detalle

## Contratos de datos

- `data/raw/contracts.parquet`
- `data/raw/processes.parquet`
- `data/raw/additions.parquet`
- `data/raw/locations.parquet`
- `data/raw/pida_context.parquet`
- `data/raw/secop_integrado_qc.parquet`
- `data/interim/base_contracts.parquet`
- `data/interim/contracts_features.parquet`
- `data/marts/contracts_scored.parquet`
- `data/marts/providers_scored.parquet`

## Joins principales

- Contratos -> Procesos:
  - `proceso_de_compra = id_del_portafolio`
- Contratos -> Adiciones:
  - `id_contrato = id_contrato`
- Contratos -> Ubicaciones:
  - `id_contrato = id_contrato`

## DuckDB

DuckDB se usa como columna vertebral para leer Parquet, hacer joins reproducibles y materializar tablas intermedias sin depender de base de datos externa.

## Limitaciones

- Match parcial con procesos
- Ubicaciones múltiples por contrato
- `cb9c-h8sn` sin monto estructurado
- `rpmr-utcd` solo para QA, no como verdad principal

