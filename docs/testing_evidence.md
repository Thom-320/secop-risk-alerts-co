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

Fecha: 2026-05-27.

- `make lint`: pasa con `ruff check .`.
- `make test`: 46 pruebas no integrales pasan, con 2 advertencias de deprecacion de Dash.
- `make db-reset`: aplica `sql/001_schema.sql` a `sql/005_seed_reference_data.sql` y
  `sql/007_security_roles.sql` sin leer datos.
- `make etl-demo`: carga 17.229 procesos unicos en PostgreSQL desde fallback Parquet local.
- `make mongo-load`: carga snapshots, logs, eventos y reportes demo en MongoDB.
- `make validate-final`: pasa con `ok=true` usando bases y APIs locales.

Evidencia reportada por `validation/final_validation.json`:

- Objetos PostgreSQL publicos: 33.
- Filas en `procurement_process`: 17.229.
- Colecciones Mongo con documentos: 5/5.
- APIs `/health`: 200 para contracts, risk y analytics.
- Pytest: 46 pruebas pasan.

Nota de entorno: durante esta corrida, OrbStack/Docker quedo con forwards de
puerto `8001`-`8003` ocupados pero sin respuesta despues de recrear servicios.
Para no fabricar exito de Docker, la validacion final se ejecuto con PostgreSQL,
MongoDB y FastAPI en host usando puertos alternos:

```bash
DATABASE_URL=postgresql://contratia@127.0.0.1:15532/contratia \
MONGO_URL=mongodb://127.0.0.1:17018/contratia \
CONTRACTS_SERVICE_URL=http://127.0.0.1:18001 \
RISK_SERVICE_URL=http://127.0.0.1:18002 \
ANALYTICS_SERVICE_URL=http://127.0.0.1:18003 \
make validate-final
```

La ruta oficial sigue siendo `make demo-full && make validate-final` con Docker
cuando OrbStack responde normalmente.
