# Diccionario de datos

El diccionario operativo esta en `docs/data_dictionary.md`. Esta version resume las
entidades principales para el informe.

| Tabla | Proposito |
| --- | --- |
| `source_dataset` | Catalogo de fuentes oficiales abiertas. |
| `extraction_run` | Lotes de extraccion y carga. |
| `public_entity` | Entidades contratantes normalizadas. |
| `provider` | Proveedores normalizados por NIT cuando existe. |
| `procurement_process` | Unidad canonica de analisis: proceso contractual. |
| `contract` | Contratos asociados a procesos. |
| `annual_procurement_plan`, `paa_item` | Plan anual de adquisiciones y detalle. |
| `risk_assessment`, `risk_reason` | Score de prioridad y explicaciones auditables. |
| `semantic_comparable` | Procesos comparables para contexto. |
| `audit_log`, `process_state_history` | Trazabilidad tecnica. |
| `human_review` | Revision humana demo y decision trazable. |
