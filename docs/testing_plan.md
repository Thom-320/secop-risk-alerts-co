# Testing plan

## Automated checks

- `make lint`: estilo y errores estaticos con Ruff.
- `make test`: pruebas unitarias y smoke tests.
- `make validate-final`: validacion de base de datos, MongoDB, APIs, docs y README.

## Required scenarios

- El esquema tiene 20+ tablas.
- Las tablas principales tienen PK.
- Existen FK para procesos, contratos, PAA, riesgo y comparables.
- Constraints rechazan scores invalidos.
- Triggers registran auditoria e historial de estado.
- ETL demo carga 10.000+ procesos.
- Servicios FastAPI responden `/health`.
- Dashboard importa sin fallar.
