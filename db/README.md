# Base relacional PostgreSQL

Esta carpeta empaqueta, con nombres academicos, la misma implementacion SQL que usa la
validacion del proyecto en `sql/`.

- `migrations/001_schema.sql`: tablas, llaves, restricciones y tipos.
- `migrations/002_indexes.sql`: indices B-tree y de consulta frecuente.
- `triggers/001_auditoria.sql`: auditoria, historial de estado y `updated_at`.
- `views/001_analytics.sql`: vistas analiticas, CTE recursiva y window functions.
- `procedures/001_scoring.sql`: procedimientos de recalculo y registro atomico.
- `seeds/001_demo.sql`: fuentes oficiales y reglas explicables.

PostgreSQL es la fuente de verdad relacional. Parquet queda como cache de ingesta y
MongoDB como soporte documental/eventos.
