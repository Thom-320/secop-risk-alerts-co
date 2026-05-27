# Auditoria de estado actual

Fecha de auditoria: 2026-05-27

## Estado verificado

- Rama inicial observada: `main`, con cambios locales sin confirmar.
- Rama de implementacion creada: `final-data-engineering-project`.
- `pytest` actual antes de la ampliacion: 13 pruebas pasan.
- `ruff check .` actual antes de la ampliacion: pasa.
- Los marts activos requeridos por la API/Streamlit anterior no existen en este workspace:
  - `data/interim/process_master.parquet`
  - `data/interim/paa_items.parquet`
  - `data/marts/ranking.parquet`
  - `data/marts/process_detail.parquet`
- Datos locales disponibles para fallback demo:
  - `data/legacy_raw/processes.parquet`: 19.767 filas.
  - `data/legacy_raw/contracts.parquet`: 32.646 filas.
  - `data/legacy_raw/additions.parquet`: 119.362 filas.
  - `data/raw/paa_detail/part-*.parquet`: 80.000 filas PAA en cuatro partes; manifest marcado como incompleto.

## Brecha frente a la materia

- Falta PostgreSQL como fuente relacional principal.
- Falta MongoDB como soporte NoSQL document/event.
- Falta esquema normalizado con 15+ tablas, constraints, triggers, vistas y SQL avanzado visible.
- Falta separacion real de microservicios.
- Falta Dash como interfaz oficial.
- Falta evidencia automatizada de carga de 10.000+ registros.
- Falta reporte final alineado con las 13 secciones de la guia.
- Falta evidencia de UX con 5 usuarios reales; no debe fabricarse.

## Archivos principales a crear o modificar

- `sql/*.sql`: esquema, indices, triggers, vistas, seed y transacciones demo.
- `etl/*.py`: validacion de fuentes y cargas a PostgreSQL/MongoDB.
- `services/*`: microservicios FastAPI.
- `dashboard/dash_app.py`: interfaz oficial en Dash.
- `mongo/*`: inicializacion y documentacion NoSQL.
- `docs/report/*`, `docs/*.md`, `docs/diagrams/*`: reporte, manuales, evidencia y diagramas.
- `Makefile`, `docker-compose.yml`, `.env.example`, `.gitignore`, `README.md`, `pyproject.toml`.
- `tests/test_*`: pruebas de requisitos academicos y smoke tests.

## Criterios de aceptacion

- `make lint` ejecuta `ruff check .`.
- `make test` ejecuta pruebas unitarias y smoke tests.
- `make validate-final` verifica o reporta bloqueadores precisos para:
  - 20+ tablas publicas en PostgreSQL.
  - 10.000+ procesos cargados.
  - colecciones MongoDB con documentos.
  - endpoints `/health` de los tres servicios.
  - docs requeridos presentes.
  - README con comandos de reproduccion.

## Politica etica

El sistema no detecta corrupcion, fraude ni responsabilidad individual. Produce priorizacion explicable para revision humana sobre datos abiertos oficiales y debe presentar sus limitaciones.
