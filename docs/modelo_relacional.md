# Modelo relacional

PostgreSQL es la base principal. El diseno usa mas de 20 tablas publicas con:

- Llaves primarias y foraneas.
- `NUMERIC` para valores monetarios.
- Restricciones `CHECK` para scores, confianza, fechas y estados.
- Indices para filtros frecuentes por entidad, modalidad, fecha, score y proveedor.
- Triggers de auditoria, historial de estado, validacion de score y `updated_at`.

La implementacion SQL vive en `sql/` y se empaqueta tambien bajo `db/` para lectura
academica.
