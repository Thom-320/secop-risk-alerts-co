# Class Submission Checklist

## Datos y volumen

- [x] 10.000+ registros cargados (13,999 procurement_process en PG).
- [x] Fuentes SECOP II, SECOP Integrado, PAA y contexto fiscal documentadas.
- [x] Evidencia de conteos en `docs/testing_evidence.md` y `validation/final_validation.json`.

## PostgreSQL

- [x] 15+ tablas relacionales (33 objetos públicos).
- [x] Esquema PostgreSQL aplicado.
- [x] Llaves primarias y foráneas.
- [x] Constraints de score/confianza.
- [x] Índices relevantes.
- [x] Triggers de auditoría o historial.
- [x] Vistas analíticas.
- [x] CTE recursiva.
- [x] Window functions.
- [x] Transacción demo.

## MongoDB

- [x] Colecciones documentadas.
- [x] Colecciones con documentos.
- [x] Uso claro como soporte NoSQL, no duplicado decorativo.

## Aplicación

- [x] Microservicios FastAPI: contracts, risk, analytics.
- [x] Dashboard Dash académico.
- [x] Endpoint `/risk/ranking` con columnas necesarias para la tabla.
- [x] Endpoints mutables documentados y bloqueables en demo pública.

## Validación y entrega

- [x] `make lint`.
- [x] `make test` (71 passed).
- [x] `make demo-full` (con Docker/OrbStack activo).
- [x] `make validate-final` (con Docker/OrbStack activo).
- [x] Reporte final.
- [x] Slides.
- [x] Evidencia de pruebas.
- [ ] Encuesta UX con 5 personas reales (tabla lista, sin respuestas reales).
- [ ] Validación humana real (protocolo listo, resultados pendientes).
- [ ] Integrantes, roles, director y fecha exacta completados por el equipo.
