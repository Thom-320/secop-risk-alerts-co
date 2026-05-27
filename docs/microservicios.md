# Microservicios

La integracion se divide en tres servicios FastAPI:

- `contracts_service`: procesos, entidades, proveedores, historial y revision humana.
- `risk_service`: ranking, reglas, explicaciones, comparables y recalculo.
- `analytics_service`: panorama, concentracion, plan vs ejecucion, outliers y jerarquia.

Cada servicio expone `/health`, usa esquemas Pydantic y se conecta a PostgreSQL mediante
`DATABASE_URL`.
