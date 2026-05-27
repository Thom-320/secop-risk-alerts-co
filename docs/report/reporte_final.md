# 1. Hoja de presentación

**Título:** Transparencia360 / ContratIA Abierta: sistema full-stack de priorización explicable de revisión contractual en Colombia.

**Integrantes y roles:** [COMPLETAR POR EL EQUIPO ANTES DE ENTREGA].

**Director/docente:** [COMPLETAR POR EL EQUIPO ANTES DE ENTREGA].

**Universidad:** Universidad del Rosario, Escuela de Ciencias e Ingeniería.

**Ciudad y fecha:** Bogotá, [COMPLETAR FECHA EXACTA POR EL EQUIPO ANTES DE ENTREGA].

> [COMPLETAR POR EL EQUIPO ANTES DE ENTREGA]
> Registrar nombres completos, roles reales, director/docente y fecha exacta según
> el registro oficial del curso antes de entregar.

# 2. Resumen ejecutivo

Transparencia360 es una solución de Ingeniería de Datos para priorizar revisión
humana de procesos de contratación pública en Colombia. Integra datos abiertos
de SECOP II, SECOP Integrado, Plan Anual de Adquisiciones y contexto de control
fiscal. La solución no emite acusaciones ni conclusiones jurídicas o fiscales:
entrega una cola explicable para decidir qué revisar primero, por qué y con qué
evidencia.

La ruta oficial de entrega es full-stack: PostgreSQL como base relacional
principal, MongoDB como soporte NoSQL, tres microservicios FastAPI, dashboard en
Plotly Dash, ETL reproducible y validación final con `make validate-final`. El
modo Streamlit/Parquet se conserva como respaldo offline y superficie ligera de
producto, pero no reemplaza la sustentación académica.

El scoring combina señales interpretables: anomalía, desviación frente a pares,
reglas explícitas, similitud textual TF-IDF/coseno y confianza de datos. Los
embeddings neuronales quedan como mejora opcional con bandera de entorno; no son
un requisito de la ruta validada.

# 3. Definición del problema

Las organizaciones de revisión pública tienen capacidad humana limitada frente a
miles de procesos contractuales. Necesitan priorizar revisión con criterios
transparentes, trazables y reproducibles, sin reemplazar el juicio jurídico,
fiscal o profesional.

Requerimientos funcionales:

- Cargar 10.000+ procesos desde fuentes oficiales abiertas.
- Modelar datos relacionales y NoSQL con responsabilidades claras.
- Consultar procesos, entidades, proveedores, ranking y detalle.
- Mostrar razones de prioridad, comparables y contexto PAA.
- Exportar evidencia desde el dashboard para revisión humana.

Requerimientos no funcionales:

- Reproducibilidad por comandos (`make demo-full`, `make validate-final`).
- Trazabilidad de fuentes, joins, cargas y validación.
- Pruebas automatizadas y validación operativa de servicios.
- Lenguaje ético: priorización de revisión humana, no acusación.

# 4. Objetivos

Objetivo general: implementar una plataforma full-stack de priorización
explicable de revisión contractual sobre datos abiertos oficiales.

Objetivos específicos:

- Extraer y normalizar fuentes SECOP II, SECOP Integrado, PAA y contexto fiscal.
- Diseñar una base PostgreSQL con 15+ tablas, llaves, constraints, índices,
  triggers, vistas, CTE recursiva, window functions y transacción demo.
- Integrar MongoDB para snapshots, logs, eventos, reportes y soporte documental.
- Exponer microservicios FastAPI de contratos, riesgo y analítica.
- Construir dashboard Dash para panorama, ranking, detalle, exportación y
  validación de calidad.
- Validar con pruebas automatizadas, documentación y tareas humanas explícitas.

# 5. Metodología

El trabajo siguió fases de diseño de Ingeniería de Datos:

- Exploración de fuentes Socrata y requisitos del curso.
- Evaluación de alternativas: producto lean Parquet/Streamlit, relacional puro y
  arquitectura poliglota PostgreSQL/MongoDB.
- Selección de arquitectura oficial: poliglota full-stack para cumplir la
  exigencia académica de bases, servicios, SQL avanzado y validación.
- Implementación de ETL, cargas PostgreSQL/MongoDB, microservicios y Dash.
- Scoring explicable con reglas, anomalía, pares comparables y confianza.
- Pruebas, documentación, demo y checklist de entrega.

# 6. Referencias y bibliografía consultada

- Datos Abiertos Colombia. (2026). *SECOP II - Procesos de Contratación* (`p6dx-8zbt`). Consultado el 27 de mayo de 2026, en https://www.datos.gov.co/
- Datos Abiertos Colombia. (2026). *SECOP Integrado* (`rpmr-utcd`). Consultado el 27 de mayo de 2026, en https://www.datos.gov.co/
- Datos Abiertos Colombia. (2026). *SECOP II Plan Anual de Adquisiciones Detalle* (`9sue-ezhx`). Consultado el 27 de mayo de 2026, en https://www.datos.gov.co/
- PostgreSQL Global Development Group. (2026). *PostgreSQL 16 Documentation*. Consultado el 27 de mayo de 2026, en https://www.postgresql.org/docs/16/
- MongoDB Inc. (2026). *MongoDB Manual*. Consultado el 27 de mayo de 2026, en https://www.mongodb.com/docs/
- FastAPI. (2026). *FastAPI Documentation*. Consultado el 27 de mayo de 2026, en https://fastapi.tiangolo.com/
- Plotly. (2026). *Dash Documentation*. Consultado el 27 de mayo de 2026, en https://dash.plotly.com/
- Scikit-learn. (2026). *IsolationForest*. Consultado el 27 de mayo de 2026, en https://scikit-learn.org/
- Guía del proyecto de clase de Ingeniería de Datos, Universidad del Rosario.

# 7. Evaluación de la solución propuesta

Se evaluaron tres alternativas. El MVP Parquet/Streamlit ofrece reproducción
rápida; el sistema relacional puro demuestra SQL, pero pierde soporte documental
flexible; la arquitectura poliglota PostgreSQL/MongoDB permite demostrar
modelado relacional, NoSQL, microservicios, trazabilidad y dashboard operativo.

Por eso se selecciona la arquitectura poliglota full-stack como entrega oficial
del curso. Streamlit/Parquet queda documentado como modo plus offline.

# 8. Evidencias de gerencia

- README con ruta oficial `make demo-full && make validate-final`.
- `docs/academic_route.md`, `docs/product_route.md` y
  `docs/class_submission_checklist.md`.
- Auditorías en `docs/audit/` y reportes de handoff en `docs/agent_handoffs/`.
- Bitácora Git y comandos reproducibles en Makefile.

# 9. Evidencias de diseño

- PostgreSQL: `sql/001_schema.sql`, `sql/002_indexes.sql`,
  `sql/003_triggers.sql`, `sql/004_views_analytics.sql` y
  `sql/006_transactions_demo.sql`.
- MongoDB: `mongo/collections.md`, `mongo/init_mongo.py` y
  `etl/load_to_mongo.py`.
- Microservicios: `services/contracts_service`, `services/risk_service` y
  `services/analytics_service`.
- Dashboard oficial: `dashboard/dash_app.py`.
- Diagramas: `docs/diagrams/architecture.mmd`, `er_model.mmd` y
  `microservices.mmd`.

# 10. Evidencias de documentación

- `README.md`.
- `docs/model-card.md`.
- `docs/data-cards/`.
- `docs/manual_usuario.md`.
- `docs/ethics-note.md`.
- `docs/demo-guide.md`.
- `docs/validation-summary.md`.
- `docs/human_validation_protocol.md`.
- `docs/usability_results.md`.

# 11. Evidencias de pruebas

La evidencia viva se registra en `docs/testing_evidence.md`,
`validation/product_validation.json` y `validation/final_validation.json`.

Comandos esperados:

```bash
make lint
make test
make demo-full
make validate-final
```

La última evidencia documentada reporta 66 pruebas no integrales pasando y la
validación final de la ruta académica cuando las bases y servicios están vivos.

# 12. Evidencias de experiencia de usuario e interfaz gráfica

Dash es la interfaz oficial de sustentación. Incluye panorama, ranking filtrable,
detalle de proceso, comparables, concentración secundaria, calidad de datos,
metodología, flujo de revisión humana y exportación CSV/HTML para evidencia.

La encuesta de usabilidad debe diligenciarse con 5 personas reales. El archivo
`docs/usability_results.md` queda explícitamente pendiente y no contiene
resultados fabricados.

# 13. Conclusiones

Transparencia360 demuestra una solución de Ingeniería de Datos reproducible con
datos reales, persistencia poliglota, microservicios, SQL avanzado, dashboard,
pruebas y documentación. El sistema prioriza revisión humana con evidencia
trazable y no emite acusaciones. Los pendientes humanos antes de entregar son:
encuesta UX con 5 usuarios reales, validación manual de casos, nombres/roles,
director/docente y fecha exacta.
