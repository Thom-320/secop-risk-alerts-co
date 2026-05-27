# Testing evidence

Fecha: 2026-05-27 (cierre final de contest readiness — 4ta ronda).

## Comandos de cierre ejecutados

```bash
make lint
make test
make product-pipeline PRODUCT_SOURCE_MODE=sample
make validate-product
make demo-full
make validate-final

# Ronda adicional con datos abiertos reales:
make product-pipeline PRODUCT_SOURCE_MODE=download
make validate-product
```

## Resultado

- `make lint`: pasa con `ruff check .`. All checks passed.
- `make test`: pasa con 71 pruebas no integrales (0 fallos) y 2 advertencias de
  deprecación de Dash `dash_table.DataTable`.
- `make product-pipeline PRODUCT_SOURCE_MODE=sample`: pasa con 19.625 procesos
  generados, 420 filas en ranking, 2.080 comparables, 34 departamentos en overview.
- `make validate-product`: pasa con `validation/product_validation.json`
  `ok=true`. Ranking: 420 filas (sample) o 3.527 filas (download). Sin violaciones de lenguaje prohibido.
- `make demo-full`: pasa con Docker, 33 objetos públicos en PostgreSQL (27 tablas
  + vistas y otros), 13.999 filas en procurement_process, MongoDB con 5/5 colecciones
  con documentos, APIs respondiendo HTTP 200.
- `make validate-final`: pasa con ambas validaciones `ok=true` (cuando Docker/OrbStack activo).

## Evidencia con datos abiertos reales (2026-05-27)

Ejecutado con `PRODUCT_SOURCE_MODE=download` (SECOP II, SECOP Integrado, PAA, control fiscal desde Socrata, scope Meta/Casanare):

- `make product-pipeline PRODUCT_SOURCE_MODE=download`: 13.999 SECOP II procesos (reales, no generados), 80.000 items PAA, 6.933 contratos SECOP Integrado, 527 registros de control fiscal.
- `make validate-product`: `ok=true`, **3.527 ranking rows** (datos reales), 17 docs, 0 forbidden claims.
- Score distribution (real): mean 8.4, max 53, 139 PAA strong matches, 3.521 processes with comparables.
- Top score: CO1.REQ.9381735 (Red Salud Casanare, score 53, conf 85), CO1.REQ.8496410 (Empresa Servicios Públicos Granada, score 53, conf 70).

Nota: los scores están limitados a Meta y Casanare (demo scope). Con el dataset
nacional completo (900K+ procesos) se espera una distribución más amplia de
scores de prioridad. La descarga completa de Socrata requiere manejar paginación
de alto offset, que la API de Socrata puede degradar con timeouts. El
procedimiento de descarga parcial con retry está documentado en el extractor.

## Evidencia de `validate-final` (2026-05-27 final, con OrbStack activo)

- PostgreSQL: 33 objetos públicos en schema public.
- `procurement_process`: 13.999 filas (supera el mínimo de 10.000+).
- MongoDB:
  - `raw_process_snapshots=100`
  - `etl_run_logs=14`
  - `risk_event_logs=14`
  - `report_snapshots=14`
  - `user_action_logs=14`
- APIs `/health`:
  - contracts=200
  - risk=200
  - analytics=200
- Documentos requeridos presentes: 36/36.
- Lint: All checks passed.
- Tests: 71 passed, 0 failed, 2 deprecation warnings (dash_table).

## Nota sobre infraestructura (OrbStack/Docker)

La ruta académica (`make demo-full && make validate-final`) exige PostgreSQL,
MongoDB y servicios FastAPI vivos. Cuando OrbStack/Docker están activos, la
validación es `ok=true`. Si OrbStack se detiene (comportamiento normal en macOS
al inactivar la sesión), `validate-final` reporta `ok=false` con bloqueadores de
integración exactos. La ruta lean (`make product-pipeline && make validate-product`)
funciona sin dependencias externas.

Si el jurado ejecuta en una máquina sin Docker, la ruta lean es la alternativa
documentada, no un fallo del proyecto. Ver `docs/demo-guide.md` para el protocolo
completo.

## Nota sobre descarga de datos Socrata

La API de Socrata (`datos.gov.co`) tiene limitaciones de offset pagination:
consultas con `$offset > 800.000` pueden devolver ReadTimeout. El extractor
implementa retry con backoff, pero para datasets muy grandes (>900K filas) la
descarga completa puede requerir múltiples intentos o reducir el scope
territorial con `EXTRACT_SCOPE=demo`. La evidencia con datos reales presentada
aquí usa scope Meta/Casanare (13.999 procesos) y pasa validación completa.

## Mejoras acumuladas (esta ronda final — contest readiness)

- `src/scoring/semantic_similarity.py`: SentenceTransformerProvider opcional con `CONTRATIA_USE_TRANSFORMER_EMBEDDINGS=1` y fallback automático a TF-IDF.
- Test coverage: +4 tests para provider transformer, +1 test para contest-critical docs non-emptiness.
- Demo casebook: 5 casos reales con process_key, entidad, score, confianza, razones y acción humana desde datos SECOP reales.
- Checklists (`class_submission_checklist.md`, `contest_submission_checklist.md`): marcados con [x] para todo lo cumplido, [ ] solo para pendientes humanos reales.
- README: clarificada la ruta de concurso (lean) vs evidencia de ingeniería (full-stack).
- `final_repo_audit.md`: corregida contradicción sobre estado Git.
- `reporte_final.md`, `project_report.md`: tildes corregidas, tablas actualizadas, test count 71.
- Slides: conteo de tests 71, disclaimer ético.

## Pendientes humanos

- Encuesta UX con 5 usuarios reales.
- Validación manual de 40 a 100 procesos por revisores reales.
- Nombres, roles, director/docente y fecha exacta de entrega.
- URL pública de despliegue.
- Registro en "Usos" si aplica al concurso.
