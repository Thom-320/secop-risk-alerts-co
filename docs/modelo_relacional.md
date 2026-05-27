# Modelo relacional

PostgreSQL es la base principal. El diseno usa 27 tablas relacionales y 33 objetos
publicos entre tablas y vistas con:

- Llaves primarias y foraneas.
- `NUMERIC` para valores monetarios.
- Restricciones `CHECK` para scores, confianza, fechas y estados.
- Indices para filtros frecuentes por entidad, modalidad, fecha, score y proveedor.
- Triggers de auditoria, historial de estado, validacion de score y `updated_at`.

La implementacion SQL vive en `sql/` y se empaqueta tambien bajo `db/` para lectura
academica.

## Roles de seguridad

`sql/007_security_roles.sql` define tres perfiles para sustentacion y despliegue:

- `contratia_analyst_readonly`: lectura de vistas analiticas.
- `contratia_reviewer`: lectura de vistas y escritura controlada en `human_review`.
- `contratia_admin`: administracion del esquema publico.

Estos roles separan consulta, revision humana y administracion sin cambiar el objetivo
del sistema: priorizacion de revision humana con trazabilidad.
