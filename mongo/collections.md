# MongoDB collections

MongoDB is used as a support store for document-shaped and event-shaped data. PostgreSQL remains the source of truth for relational queries.

| Collection | Purpose |
| --- | --- |
| `raw_process_snapshots` | Small raw SECOP process snapshots used for traceability. |
| `etl_run_logs` | ETL execution metadata and fallback mode notes. |
| `risk_event_logs` | Risk scoring events and recalculation notes. |
| `report_snapshots` | Report/export status snapshots. |
| `user_action_logs` | Dashboard or demo user action events. |

Academic aliases written by `etl.load_to_mongo` for the course wording:

| Alias | Mirrors |
| --- | --- |
| `raw_snapshots` | `raw_process_snapshots` |
| `ingestion_logs` | `etl_run_logs` |
| `join_audits` | `risk_event_logs` |
| `generated_reports` | `report_snapshots` |
| `dashboard_events` | `user_action_logs` |
