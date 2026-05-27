# Product Route — ContratIA Abierta

## Propósito

ContratIA Abierta es la ruta lean para concurso, demo pública y portafolio de
producto. Está optimizada para explicar una decisión concreta: qué procesos
SECOP conviene revisar primero y con qué evidencia trazable.

## Arquitectura

```text
src/extract -> src/transform -> src/scoring -> data/marts
data/marts -> src/api/main.py
data/marts -> src/app/streamlit_app.py
```

## Storage

La ruta usa Parquet como formato reproducible y DuckDB/Pandas para consulta
local. No requiere PostgreSQL, MongoDB ni Docker.

## Por qué es mejor para concurso

- Arranca rápido en una máquina nueva.
- Reduce dependencias operativas durante la presentación.
- Muestra el flujo de producto sin explicar infraestructura académica.
- Permite desplegar una demo read-only con Streamlit y FastAPI simple.

## Cómo correr

```bash
uv sync --python 3.11 --extra dev
make product-pipeline
make product-ui
make product-api
```

Por defecto `make product-pipeline` usa fixtures versionables de muestra. Para
descargar datos abiertos actuales, ejecutar con una fuente explícita:

```bash
make product-pipeline PRODUCT_SOURCE_MODE=download
```

## Evidencia que produce

- `data/marts/overview.parquet`
- `data/marts/ranking.parquet`
- `data/marts/process_detail.parquet`
- `data/marts/comparables.parquet`
- `validation/ranking_meta_casanare.csv`
- `validation/paa_match_sample.csv`
- `docs/join-audit.md`
- `validation/product_validation.json`

## Interpretación

El producto produce una alerta explicable para revisión humana. El score no es
una conclusión jurídica, fiscal o disciplinaria. La salida correcta es una cola
priorizada y auditable.
