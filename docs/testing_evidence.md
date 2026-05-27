# Testing evidence

Fecha: 2026-05-27 (tercera ronda de cierre — auditoría final Codex).

## Comandos de cierre ejecutados

```bash
make lint
make test
make product-pipeline
make validate-product
make demo-full
make validate-final
```

## Resultado

- `make lint`: pasa con `ruff check .`. All checks passed.
- `make test`: pasa con 66 pruebas no integrales (0 fallos) y 2 advertencias de
  deprecación de Dash `dash_table.DataTable`.
- `make product-pipeline`: pasa con `PRODUCT_SOURCE_MODE=sample`, 19.625 procesos
  generados, 420 filas en ranking, 2080 comparables, 34 departamentos en overview.
- `make validate-product`: pasa con `validation/product_validation.json`
  `ok=true`. Ranking: 420 filas. Sin violaciones de lenguaje prohibido.
- `make demo-full`: pasa con Docker, 33 objetos públicos en PostgreSQL (27 tablas
  + vistas y otros), 13.999 filas en procurement_process, MongoDB con 5/5 colecciones
  con documentos, APIs respondiendo HTTP 200.
- `make validate-final`: pasa con ambas validaciones `ok=true`.

## Evidencia de `validate-final` (2026-05-27 final)

- PostgreSQL: 33 objetos públicos en schema public.
- `procurement_process`: 13.999 filas (supera el mínimo de 10.000+).
- MongoDB:
  - `raw_process_snapshots=100`
  - `etl_run_logs=14`
  - `risk_event_logs=14`
  - `report_snapshots=14`
  - `user_action_logs=14`
- APIs `/health`:
  - contracts=200
  - risk=200
  - analytics=200
- Documentos requeridos presentes: 36/36.
- Lint: All checks passed.
- Tests: 66 passed, 0 failed, 2 deprecation warnings (dash_table).

## Mejoras acumuladas

- `write_sample_product_sources()` prefiere `data/sample/generated/processes.parquet`
  (19.625 filas) sobre fixture CSV de 3 filas. Ranking demo: 420 filas con
  variedad real de departamentos, modalidades y scores.
- Corregido fallo por duplicados `id_del_proceso` en el parquet generado.
- Columna `fecha_de_publicacion_del` inferida desde `fecha_de_apertura_efectiva`.
- `services/risk_service/main.py`: ranking incluye department, modality, base_price,
  priority_score, confidence_score, explanation, has_comparables.
- `PUBLIC_READ_ONLY` bloquea POST mutables en demo pública.
- Documentación completa: model card, data cards, product/academic routes,
  contest/class checklists, demo guide, demo casebook, human validation protocol,
  fairness territorial, deployment guide.
- `etl/validate_product.py`: validación lean que no requiere PostgreSQL ni MongoDB.
- `etl/validate_final.py`: acepta `CONTRACTS_SERVICE_URL`, `RISK_SERVICE_URL`,
  `ANALYTICS_SERVICE_URL` por variable de entorno.
- `etl/apply_schema.py`: aplica schema incluyendo `007_security_roles.sql`.
- `services/analytics_service/main.py`: `/analytics/hierarchy/{entity_id}` usa
  CTE recursiva correcta.
- Presentación slides: corregida para reflejar 6 señales de scoring reales
  (no 3 componentes genéricos).

## Pendientes humanos

- Encuesta UX con 5 usuarios reales.
- Validación manual de 40 a 100 procesos por revisores reales.
- Nombres, roles, director/docente y fecha exacta de entrega.
- URL pública de despliegue.
- Registro en "Usos" si aplica al concurso.
