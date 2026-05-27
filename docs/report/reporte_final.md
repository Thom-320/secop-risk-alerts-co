# 1. Hoja de presentación

**Titulo:** Transparencia360 / ContratIA Abierta: Sistema Poliglota de Priorizacion de Revision Contractual en Colombia.

**Integrantes y roles:** pendiente de completar por el grupo.

**Director:** docente de Ingenieria de Datos.

**Universidad:** Universidad del Rosario, Escuela de Ciencias e Ingenieria.

**Ciudad y fecha:** Bogota, 2026.

# 2. Resumen ejecutivo

Transparencia360 es una solucion de ingenieria de datos para priorizar revision humana de procesos de contratacion publica en Colombia. Integra datos abiertos de SECOP II, SECOP Integrado, Plan Anual de Adquisiciones y contexto de control fiscal. La solucion no detecta corrupcion ni emite acusaciones; entrega un ranking explicable para apoyar a veedurias, oficinas de transparencia y periodistas de datos.

La arquitectura usa PostgreSQL como fuente relacional principal, MongoDB como soporte para documentos y eventos, ETL en Python, microservicios FastAPI y dashboard Plotly Dash. El diseno incluye mas de 20 tablas normalizadas, llaves primarias y foraneas, restricciones, indices, triggers de auditoria, historial de estados, vistas con funciones de ventana, CTE recursiva y una transaccion demostrativa.

# 3. Definición del problema

Las organizaciones de revision publica tienen capacidad humana limitada frente a miles de procesos contractuales. Necesitan decidir que revisar primero usando criterios transparentes, trazables y reproducibles.

Requerimientos funcionales:

- Cargar 10.000+ procesos.
- Consultar procesos, entidades, proveedores, ranking y detalle.
- Mostrar razones de prioridad y comparables.
- Registrar auditoria y cambios de estado.

Requerimientos no funcionales:

- Persistencia relacional con PostgreSQL.
- Soporte NoSQL con MongoDB.
- Integracion por microservicios.
- Pruebas automatizadas.
- Lenguaje etico y no acusatorio.

# 4. Objetivos

Objetivo general: implementar una plataforma de priorizacion explicable de revision contractual sobre datos abiertos oficiales.

Objetivos especificos:

- Normalizar datos SECOP en un modelo relacional.
- Registrar snapshots y eventos en MongoDB.
- Exponer servicios de contratos, riesgo y analitica.
- Construir una interfaz Dash para consulta y sustentacion.
- Validar el sistema con pruebas y evidencia reproducible.

# 5. Metodología

Fases:

- Exploracion de datos y requerimientos.
- Diseno conceptual y seleccion de arquitectura.
- Implementacion de PostgreSQL, MongoDB, ETL y servicios.
- Implementacion de dashboard.
- Pruebas, documentacion y preparacion de presentacion.

Cronograma sugerido: ver bitacora de gerencia y commits del repositorio.

# 6. Referencias y bibliografía consultada

- Datos Abiertos Colombia, datasets SECOP en `datos.gov.co`.
- Documentacion PostgreSQL 16.
- Documentacion MongoDB 7.
- Documentacion FastAPI.
- Documentacion Plotly Dash.
- Guia del proyecto de clase de Ingenieria de Datos, Universidad del Rosario.

# 7. Evaluación de la solución propuesta

Se evaluaron tres alternativas: MVP analitico Parquet/Streamlit, sistema relacional puro y arquitectura poliglota. Se selecciono la arquitectura poliglota porque cumple mejor los criterios del curso: base relacional fuerte, soporte NoSQL, microservicios, interfaz grafica, pruebas y trazabilidad.

# 8. Evidencias de gerencia

La gerencia del proyecto se evidencia con:

- `docs/audit/current_state_audit.md`.
- README reproducible.
- Makefile con comandos de validacion.
- Bitacora de cambios en Git.
- Discusion de alternativas en este reporte.

# 9. Evidencias de diseño

El diseno incluye:

- Modelo relacional en `sql/001_schema.sql`.
- Indices en `sql/002_indexes.sql`.
- Triggers en `sql/003_triggers.sql`.
- Vistas analiticas en `sql/004_views_analytics.sql`.
- Diagramas Mermaid en `docs/diagrams/`.

# 10. Evidencias de documentación

Documentacion principal:

- `README.md`.
- `docs/data_dictionary.md`.
- `docs/manual_usuario.md`.
- `docs/testing_plan.md`.
- `docs/ai_usage_disclosure.md`.

# 11. Evidencias de pruebas

El plan de pruebas esta en `docs/testing_plan.md`. La evidencia se registra en `docs/testing_evidence.md` y `validation/final_validation.json`.

Comandos:

```bash
make lint
make test
make validate-final
```

# 12. Evidencias de experiencia de usuario e interfaz gráfica

La interfaz oficial es `dashboard/dash_app.py`, con vistas de panorama, ranking, concentracion y metodologia. El mapa de navegacion esta en `docs/manual_usuario.md`.

La encuesta de usabilidad debe diligenciarse con 5 personas reales. El archivo `docs/usability_results.md` esta marcado como pendiente y no contiene resultados fabricados.

# 13. Conclusiones

Transparencia360 convierte un MVP de ciencia de datos en una solucion de ingenieria reproducible, con persistencia poliglota, microservicios, SQL avanzado, pruebas y documentacion. Las mejoras futuras incluyen despliegue cloud, resolucion de entidades mas robusta, mayor cobertura de datasets y encuesta real de usuarios.
