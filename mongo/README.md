# MongoDB

MongoDB es una capa de soporte NoSQL para documentos y eventos. PostgreSQL sigue siendo
la fuente de verdad relacional.

Colecciones validadas por el sistema:

- `raw_process_snapshots`
- `etl_run_logs`
- `risk_event_logs`
- `report_snapshots`
- `user_action_logs`

Aliases academicos escritos por compatibilidad con la guia:

- `raw_snapshots`
- `ingestion_logs`
- `join_audits`
- `generated_reports`
- `dashboard_events`

Carga demo:

```bash
make mongo-load
```
