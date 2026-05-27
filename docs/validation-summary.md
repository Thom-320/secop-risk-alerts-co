# Validation Summary

## Validado automáticamente

- `make lint`: Ruff sobre el repositorio.
- `make test`: pruebas no integración.
- `make product-pipeline`: genera marts lean cuando hay fixtures o fuentes.
- `make validate-product`: valida ruta ContratIA Abierta sin PostgreSQL, MongoDB
  ni Docker. En esta ronda quedó `ok=true`.
- `make validate-academic`: valida ruta Transparencia360 cuando PostgreSQL,
  MongoDB y microservicios están activos. En la verificación final quedó
  `ok=true`.
- Pruebas SQL: tablas, llaves, constraints, triggers, CTE recursiva y window
  functions.
- Pruebas de lenguaje: evitan afirmaciones acusatorias en superficies públicas.

## Validado manualmente

Pendiente. No hay revisiones humanas reales incorporadas al repositorio.

## Pendiente

- Validación manual de 40 y 100 procesos según capacidad de revisión.
- Encuesta UX con 5 usuarios reales.
- URL pública de despliegue.
- Registro en “Usos” si aplica al concurso.
- Revisión final de diapositivas contra la evidencia real disponible.

## Bloqueadores conocidos

- `validate-academic` requiere PostgreSQL, MongoDB y servicios vivos.
- Docker/OrbStack o puertos ocupados pueden bloquear la ruta académica.
- En una ejecución intermedia del 2026-05-27, `etl.load_to_postgres --limit 20000`
  terminó con `Error 143`; después se recuperó Docker/OrbStack y
  `make validate-final` quedó `ok=true`.
- La ruta lean usa fixtures por defecto para CI; las métricas de concurso deben
  reconstruirse con datos abiertos reales antes de publicarse.

## Comandos para reproducir evidencia

```bash
make lint
make test
make product-pipeline
make validate-product
make demo-full
make validate-final
```

## Archivos de evidencia

- `validation/product_validation.json`
- `validation/final_validation.json`
- `validation/table_counts.csv`
- `validation/mongo_summary.json`
- `validation/load_summary.json`
- `docs/testing_evidence.md`

## Lo que no se valida aquí

No se validan conclusiones jurídicas o fiscales. Tampoco se fabrican resultados
de UX, etiquetas humanas, métricas de precisión manual ni URL pública.
