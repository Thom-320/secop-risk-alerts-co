# Extraction Findings

Fecha de actualización: 2026-04-16

## Hallazgos de volumen

- `p6dx-8zbt` cerró completo con 2.639.419 filas.
- `rpmr-utcd` cerró completo con 2.541.148 filas.
- `9sue-ezhx` superó 4,5 millones de filas en una corrida monolítica previa.

## Decisión técnica

- `p6dx` y `rpmr` permanecen como parquets únicos.
- `PAA` migra a extracción incremental por chunks con resume.
- El foco de la primera iteración es `demo scope`, no full nacional.

## Estrategia nueva

- chunks `part-*.parquet` en `data/raw/paa_detail/`
- `manifest.json` con estado persistente por dataset
- `validation/paa_extraction_status.json` con filas, parts y offsets
- soporte de reanudación sin duplicados

## Estado de GitHub

- El remoto existe, pero el hardening de ingesta debe cerrarse antes de sincronizar el repo público.
