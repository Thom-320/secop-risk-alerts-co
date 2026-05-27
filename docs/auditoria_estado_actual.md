# Auditoria de estado actual

## Que existe

- Pipeline canonico por proceso contractual con extractor Socrata, transformacion a
  `process_master` y scoring explicable.
- El manifest local conserva la extraccion PAA como parcial, por eso el modo demo usa
  fallback Parquet documentado y no fabrica datos.
- Artefactos legacy preservados: metadata anterior en `docs/legacy/raw_metadata/` y
  notebooks exploratorios en `docs/legacy/notebooks/`.
- Carga demo a PostgreSQL con 20+ tablas, llaves, restricciones, indices, triggers,
  vistas analiticas, CTE recursiva, window functions y transaccion de ejemplo.
- Carga MongoDB para snapshots, logs, eventos y reportes.
- Tres microservicios FastAPI: contratos, prioridad y analitica.
- Dashboard oficial en Plotly Dash; Streamlit queda como interfaz legacy.
- Documentacion academica base, reporte final, notas eticas, model card y reproducibilidad.

## Que faltaba para cierre publico

- Empaque academico adicional bajo `db/`.
- Alias de Makefile pedidos por la guia.
- README de carpetas `data/sample`, `validation` y `mongo`.
- Endpoints de revision humana.
- Documentos puente en espanol para profesor y repositorio publico.
- Carpeta `slides/` con outline y notas base.

## Comandos que pasan

- `uv run --python 3.11 pytest -q`
- `uv run --python 3.11 ruff check .`
- `make db-up`
- `make etl-demo`
- `make mongo-load`
- `make validate-final`, con PostgreSQL/MongoDB levantados y APIs vivas.

La validacion final requiere PostgreSQL, MongoDB y los tres servicios API vivos. Si
Docker no esta disponible, se puede usar la ruta local documentada en
`docs/testing_evidence.md`.

## Plan de recuperacion

1. Levantar PostgreSQL y MongoDB con `make db-up`.
2. Ejecutar `make etl-demo`.
3. Ejecutar `make mongo-load`.
4. Levantar APIs con `make api`.
5. Ejecutar `make validate-final`.

Si Socrata no responde, el modo demo usa Parquet local preexistente. Si tampoco existen
las fuentes locales, el pipeline falla de forma explicita.
