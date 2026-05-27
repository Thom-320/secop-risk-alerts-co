# ContratIA Abierta: reporte de proyecto

## Hoja de presentación

Título: ContratIA Abierta: Sistema full-stack de priorización explicable para
revisión de contratación pública colombiana usando datos abiertos SECOP.

Programa: Ingeniería de Datos, Universidad del Rosario.

Cliente objetivo: veedurías ciudadanas, periodistas de datos y oficinas de control
interno con requerimientos reales de priorización.

Roles técnicos del equipo: [COMPLETAR POR EL EQUIPO ANTES DE ENTREGA].
Registrar nombres completos, roles reales, director/docente y fecha exacta según el
registro oficial del grupo.

## Resumen ejecutivo de 500 palabras

ContratIA Abierta es una solución de ingeniería de datos para ordenar grandes volúmenes
de procesos de contratación pública y ayudar a decidir qué revisar primero. El sistema
usa fuentes abiertas oficiales de Colombia, incluyendo SECOP II Procesos de
Contratación, SECOP Integrado, Plan Anual de Adquisiciones y contexto público de control
fiscal. La unidad de análisis es el proceso contractual, no una persona ni una
acusación. La salida es un score de prioridad con razones auditables, confianza de datos,
comparables y trazabilidad hacia las fuentes.

El proyecto implementa un pipeline reproducible en Python. En modo online puede consultar
Socrata; en modo demo usa artefactos Parquet locales ya verificados para cargar más de
10.000 procesos sin depender de una descarga pesada. PostgreSQL funciona como base
relacional principal, con 27 tablas y 33 objetos públicos, llaves primarias, foráneas, restricciones,
índices, triggers, vistas, CTE recursiva, window functions y transacciones. MongoDB se
usa como soporte NoSQL para snapshots crudos, logs de ingesta, auditorías de joins,
eventos de uso y reportes generados. Esta separación permite demostrar persistencia
políglota con responsabilidades claras.

La integración se expone mediante microservicios FastAPI: contratos, prioridad y
analítica. El dashboard oficial está construido en Plotly Dash y presenta panorama,
ranking, detalle de proceso, comparables, concentración entidad-proveedor, calidad de
datos, metodología y flujo demo de revisión humana. La interfaz mantiene el lenguaje
ético del proyecto: priorización de revisión humana, explicación auditable y
trazabilidad de datos.

El enfoque de scoring es rules-first. Combina componente de anomalía, desviación frente
a pares, reglas interpretables y confianza. Esta decisión evita depender de modelos
opacos o de descargas pesadas para la demo. Los comparables pueden calcularse con
TF-IDF/coseno por defecto y usar embeddings neuronales como mejora opcional
(`CONTRATIA_USE_TRANSFORMER_EMBEDDINGS=1`), con fallback automático a TF-IDF. Las explicaciones son
plantillas auditables basadas en features, no juicios.

La validación incluye pruebas unitarias, pruebas estáticas del esquema SQL, pruebas de
constraints y triggers, endpoints API, import del dashboard y validación final de
PostgreSQL, MongoDB, APIs, documentación y comandos de reproducción. El proyecto queda
preparado para repositorio público y sustentación académica, con la única tarea humana
pendiente de aplicar la encuesta UX a cinco personas reales.

## Definición del problema

Las organizaciones que revisan contratación pública enfrentan volumen, heterogeneidad y
capacidad humana limitada. Necesitan priorizar revisión con evidencia, no reemplazar la
revisión jurídica o fiscal.

## Requerimientos funcionales y no funcionales

Funcionales: ingesta, normalización, carga relacional, soporte NoSQL, ranking, detalle,
comparables, revisión humana demo, APIs y dashboard.

No funcionales: reproducibilidad, trazabilidad, lenguaje ético, datos reales, pruebas,
documentación y ejecución local.

## Objetivo general y objetivos específicos

Objetivo general: implementar una plataforma full-stack para priorizar revisión humana de
procesos contractuales con datos abiertos.

Objetivos específicos: extraer fuentes oficiales, normalizar entidades, diseñar una base
relacional, integrar MongoDB, exponer microservicios, construir dashboard, documentar y
validar.

## Metodología

El trabajo sigue fases de diseño de ingeniería: definición del problema, alternativas,
selección, diseño, implementación, pruebas y documentación.

## Cronograma tipo Gantt

Ver `docs/metodología_gantt.md`.

## Referencias

- Datos Abiertos Colombia. (2026). *SECOP II - Procesos de Contratación* (`p6dx-8zbt`). Consultado el 27 de mayo de 2026, en https://www.datos.gov.co/
- Datos Abiertos Colombia. (2026). *SECOP Integrado* (`rpmr-utcd`). Consultado el 27 de mayo de 2026, en https://www.datos.gov.co/
- Datos Abiertos Colombia. (2026). *SECOP II Plan Anual de Adquisiciones Detalle* (`9sue-ezhx`). Consultado el 27 de mayo de 2026, en https://www.datos.gov.co/
- PostgreSQL Global Development Group. (2026). *PostgreSQL 16 Documentation*. Consultado el 27 de mayo de 2026, en https://www.postgresql.org/docs/16/
- MongoDB Inc. (2026). *MongoDB Manual*. Consultado el 27 de mayo de 2026, en https://www.mongodb.com/docs/
- FastAPI. (2026). *FastAPI Documentation*. Consultado el 27 de mayo de 2026, en https://fastapi.tiangolo.com/
- Plotly. (2026). *Dash Documentation*. Consultado el 27 de mayo de 2026, en https://dash.plotly.com/

## Evaluación de alternativas

Ver `docs/evaluacion_alternativas.md`.

## Evidencias de gerencia

El repositorio contiene auditoría de estado actual, README, Makefile, CI y documentos de
planificación.

## Evidencias de diseño

Ver `docs/modelo_relacional.md`, `docs/modelo_nosql.md`,
`docs/diagrams/architecture.mmd` y `docs/diagrams/er_model.mmd`.

## Evidencias de documentación

Manual de usuario, diccionario de datos, reproducibilidad, modelo, ética y pruebas están
en `docs/`.

## Evidencias de pruebas

Ver `docs/testing_evidence.md` y `docs/pruebas.md`.

## Evidencias UX/interfaz

Dash es la interfaz oficial. La encuesta real queda pendiente en
`docs/ux_usability_survey.md`.

## Conclusiones y mejoras futuras

El proyecto demuestra una solución reproducible con datos reales, persistencia poliglota,
microservicios y dashboard. Mejoras futuras: entidad-resolución más robusta, más fuentes,
despliegue y encuesta UX diligenciada por cinco usuarios reales.
