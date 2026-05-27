# Arquitectura ContratIA Abierta

## Flujo

1. Extracción desde Socrata hacia `data/raw/`
   - `p6dx` y `rpmr` como parquets únicos
   - `PAA` como directorio chunked con manifest y resume
2. Normalización y construcción de `process_master` en `data/interim/`
3. Auditoría de joins y artefactos de validación en `docs/` y `validation/`
4. Scoring provisional en `data/marts/`
5. Consumo por FastAPI y Streamlit

## Decisiones clave

- `p6dx-8zbt` es la fuente canónica del proceso.
- `rpmr-utcd` solo enriquece con enlace de alta confianza.
- `9sue-ezhx` siempre es visible y entra al score solo si pasa compuerta.
- `wasc-xi4h` solo aporta contexto visible.
- `confidence_score` es una salida de primer nivel del MVP.
- La fuente PAA activa debe estar completa según manifest antes de construir `process_master`.

## Marts

- `overview.parquet`
- `ranking.parquet`
- `process_detail.parquet`
- `comparables.parquet`

## Endpoints

- `/health`
- `/overview`
- `/ranking`
- `/process/{process_key}`
- `/process/{process_key}/comparables`
- `/process/{process_key}/report`
