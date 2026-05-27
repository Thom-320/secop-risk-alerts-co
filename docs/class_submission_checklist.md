# Class Submission Checklist

## Datos y volumen

- [ ] 10.000+ registros cargados.
- [ ] Fuentes SECOP II, SECOP Integrado, PAA y contexto fiscal documentadas.
- [ ] Evidencia de conteos en `docs/testing_evidence.md` o `validation/final_validation.json`.

## PostgreSQL

- [ ] 15+ tablas relacionales.
- [ ] Esquema PostgreSQL aplicado.
- [ ] Llaves primarias y foráneas.
- [ ] Constraints de score/confianza.
- [ ] Índices relevantes.
- [ ] Triggers de auditoría o historial.
- [ ] Vistas analíticas.
- [ ] CTE recursiva.
- [ ] Window functions.
- [ ] Transacción demo.

## MongoDB

- [ ] Colecciones documentadas.
- [ ] Colecciones con documentos.
- [ ] Uso claro como soporte NoSQL, no duplicado decorativo.

## Aplicación

- [ ] Microservicios FastAPI: contracts, risk, analytics.
- [ ] Dashboard Dash académico.
- [ ] Endpoint `/risk/ranking` con columnas necesarias para la tabla.
- [ ] Endpoints mutables documentados y bloqueables en demo pública.

## Validación y entrega

- [ ] `make lint`.
- [ ] `make test`.
- [ ] `make demo-full`.
- [ ] `make validate-final`.
- [ ] Reporte final.
- [ ] Slides.
- [ ] Evidencia de pruebas.
- [ ] Encuesta UX con 5 personas reales.
- [ ] Validación humana real o estado pendiente explícito.
- [ ] Integrantes, roles, director y fecha exacta completados por el equipo.
