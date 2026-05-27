# Deployment

## Estado

No hay despliegue público activo ni URL pública. Este documento describe cómo ejecutar
localmente y qué faltaría para publicar de forma segura.

## Modo local oficial académico

```bash
uv sync --python 3.11 --extra dev
make demo-full
make validate-final
```

Servicios esperados:

- PostgreSQL: `localhost:55432`.
- MongoDB: `localhost:27018`.
- Contracts service: `http://localhost:8001`.
- Risk service: `http://localhost:8002`.
- Analytics service: `http://localhost:8003`.
- Dash dashboard: `http://localhost:8050`.

## Modo producto offline

```bash
uv sync --python 3.11 --extra dev
make product-pipeline
make validate-product
make product-ui
make product-api
```

Puertos:

- Streamlit producto: `localhost:8501`.
- FastAPI producto: `localhost:8000`.

## Variables de entorno

- `DATABASE_URL`: conexión PostgreSQL.
- `MONGO_URL`: conexión MongoDB.
- `CONTRACTS_SERVICE_URL`: URL del microservicio de contratos.
- `RISK_SERVICE_URL`: URL del microservicio de prioridad.
- `ANALYTICS_SERVICE_URL`: URL del microservicio analítico.
- `DASH_ALLOW_DB_FALLBACK`: permite fallback directo a DB solo en entorno local.
- `PUBLIC_READ_ONLY`: bloquea endpoints mutables cuando está en `true`.

## Modo demo

El modo demo carga datos locales/generados/fixtures si no hay descarga Socrata
disponible. Debe seguir la ruta `make demo-full && make validate-final` cuando Docker
funcione.

## Modo read-only para público

Para demos públicas:

```bash
PUBLIC_READ_ONLY=true
```

Con esa variable activa:

- GETs siguen disponibles.
- `POST /reviews` devuelve HTTP 403.
- `POST /risk/recompute/{process_id}` devuelve HTTP 403.

## Riesgos de endpoints mutables

- `POST /reviews` escribe revisión humana en base de datos.
- `POST /risk/recompute/{process_id}` recalcula e inserta assessment.
- En un despliegue público requieren autenticación, rate limiting, auditoría y roles.
- Sin esos controles, deben permanecer bloqueados con `PUBLIC_READ_ONLY=true`.

## Recomendaciones por plataforma

- Render/Railway/Fly.io: separar PostgreSQL, MongoDB y servicios FastAPI; configurar
  variables de entorno y health checks.
- Hugging Face Spaces: viable solo para demo de dashboard si se empaquetan datos de
  muestra y se mantiene lectura.
- Streamlit Community Cloud: útil para demo legado/offline, no para stack completo.

## Qué falta para desplegar realmente

- Credenciales gestionadas fuera del repo.
- Dominio/URL pública.
- Autenticación para POSTs.
- Backups y política de retención.
- Monitoreo de health checks y logs.
- Validación final en infraestructura destino.
