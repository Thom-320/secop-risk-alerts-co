# Data dictionary

| Table | Description |
| --- | --- |
| `source_dataset` | Official source datasets used by the project. |
| `extraction_run` | ETL run metadata and row counts. |
| `department`, `municipality` | Geographic dimensions. |
| `public_entity` | Contracting public entities. |
| `provider` | Awarded or visible providers. |
| `modality`, `contract_type`, `unspsc_category` | Procurement classification dimensions. |
| `procurement_process` | Main SECOP process fact table. |
| `process_state_history` | Status history maintained by trigger. |
| `contract` | Contract facts linked to procurement processes. |
| `annual_procurement_plan`, `paa_item`, `paa_process_match` | PAA planning and process matching. |
| `fiscal_control_subject`, `fiscal_finding` | Visible fiscal context. |
| `risk_rule`, `risk_assessment`, `risk_reason` | Explainable prioritization model. |
| `semantic_comparable` | Comparable processes for explanation. |
| `audit_log` | OLD/NEW JSONB audit records. |
| `app_user`, `usability_survey_response`, `user_action_event` | UX and application support tables. |

Money fields use `NUMERIC`; scores are constrained between 0 and 100; match confidence is constrained between 0 and 1.
