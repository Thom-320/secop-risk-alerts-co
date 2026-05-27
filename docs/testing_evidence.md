# Testing evidence

La evidencia se actualiza ejecutando:

```bash
make lint
make test
make validate-final
```

`make validate-final` escribe `validation/final_validation.json`.

Si Docker, PostgreSQL, MongoDB o Socrata no estan disponibles, el validador reporta el bloqueador exacto sin fabricar resultados.

## Ultima ejecucion local

- `uv run --python 3.11 ruff check .`: pasa.
- `uv run --python 3.11 pytest -q`: 39 pruebas pasan.
- `make db-up`: si Docker/OrbStack esta activo, levanta PostgreSQL y MongoDB por
  Compose en puertos host `55432` y `27018` para evitar conflicto con servicios locales.
- `make etl-demo`: carga 17.229 procesos unicos en PostgreSQL desde fallback Parquet local.
- `make mongo-load`: carga snapshots, logs, eventos y reportes demo en MongoDB.
- `make api`: levanta contracts, risk y analytics contra PostgreSQL.
- `make validate-final`: validacion completa con OrbStack/Docker para bases y FastAPI local:
  - `validate-final`: pasa.
  - Tablas PostgreSQL publicas: 33.
  - Filas en `procurement_process`: 17.229.
  - Colecciones Mongo con documentos: 5/5.
  - APIs `/health`: 200 para contracts, risk y analytics.
  - Pytest: 39 pruebas pasan.
