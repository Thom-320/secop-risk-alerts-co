# Academic Route — Transparencia360

## Propósito

Transparencia360 es la ruta académica y de portafolio para el proyecto final de
Ingeniería de Datos. Conserva la arquitectura full-stack necesaria para demostrar
modelado relacional, persistencia NoSQL, microservicios, ETL, SQL avanzado,
pruebas y validación operativa.

## Arquitectura

```text
etl/* -> PostgreSQL
etl/* -> MongoDB
PostgreSQL -> services/contracts_service
PostgreSQL -> services/risk_service
PostgreSQL -> services/analytics_service
services + PostgreSQL -> dashboard/dash_app.py
```

## Componentes

- PostgreSQL: esquema relacional principal con más de 20 tablas públicas.
- MongoDB: snapshots, logs de ETL, eventos de riesgo, reportes y acciones.
- FastAPI microservices: contratos, riesgo y analítica.
- Dash: dashboard full-stack académico.
- SQL avanzado: triggers, vistas, CTE recursiva, window functions y demo de
  transacciones.
- Pruebas: unitarias, estáticas e integración cuando hay servicios disponibles.

## Cómo correr

```bash
uv sync --python 3.11 --extra dev
make demo-full
make validate-final
```

Equivalente por etapas:

```bash
make academic-db-up
make academic-db-schema
make academic-etl
make academic-services-up
make validate-final
```

## Criterios de validación

`make validate-final` exige:

- PostgreSQL disponible.
- 20+ tablas públicas.
- `procurement_process` con 10.000+ filas.
- colecciones MongoDB existentes y con documentos.
- microservicios FastAPI vivos.
- documentación de entrega.
- lint y pruebas no integración.

Si Docker, OrbStack o los puertos fallan, la validación marca bloqueadores de
integración y no declara éxito.

## Uso en sustentación

Esta ruta es la evidencia de ingeniería de datos. Para pitch de concurso se debe
abrir con ContratIA Abierta; para sustentación académica se debe mostrar cómo
Transparencia360 implementa persistencia, servicios y validación.
