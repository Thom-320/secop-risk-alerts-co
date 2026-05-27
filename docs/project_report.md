# ContratIA Abierta: reporte de proyecto

## Hoja de presentacion

Titulo: ContratIA Abierta: Sistema full-stack de priorizacion explicable para
revision de contratacion publica colombiana usando datos abiertos SECOP.

Programa: Ingenieria de Datos, Universidad del Rosario.

Cliente objetivo: veedurias ciudadanas, periodistas de datos y oficinas de control
interno con requerimientos reales de priorizacion.

## Resumen ejecutivo de 500 palabras

ContratIA Abierta es una solucion de ingenieria de datos para ordenar grandes volumenes
de procesos de contratacion publica y ayudar a decidir que revisar primero. El sistema
usa fuentes abiertas oficiales de Colombia, incluyendo SECOP II Procesos de
Contratacion, SECOP Integrado, Plan Anual de Adquisiciones y contexto publico de control
fiscal. La unidad de analisis es el proceso contractual, no una persona ni una
acusacion. La salida es un score de prioridad con razones auditables, confianza de datos,
comparables y trazabilidad hacia las fuentes.

El proyecto implementa un pipeline reproducible en Python. En modo online puede consultar
Socrata; en modo demo usa artefactos Parquet locales ya verificados para cargar mas de
10.000 procesos sin depender de una descarga pesada. PostgreSQL funciona como base
relacional principal, con mas de veinte tablas, llaves primarias, foraneas, restricciones,
indices, triggers, vistas, CTE recursiva, window functions y transacciones. MongoDB se
usa como soporte NoSQL para snapshots crudos, logs de ingesta, auditorias de joins,
eventos de uso y reportes generados. Esta separacion permite demostrar persistencia
poliglota con responsabilidades claras.

La integracion se expone mediante microservicios FastAPI: contratos, prioridad y
analitica. El dashboard oficial esta construido en Plotly Dash y presenta panorama,
ranking, detalle de proceso, comparables, concentracion entidad-proveedor, calidad de
datos, metodologia y flujo demo de revision humana. La interfaz mantiene el lenguaje
etico del proyecto: priorizacion de revision humana, explicacion auditable y
trazabilidad de datos.

El enfoque de scoring es rules-first. Combina componente de anomalia, desviacion frente
a pares, reglas interpretables y confianza. Esta decision evita depender de modelos
opacos o de descargas pesadas para la demo. Los comparables pueden calcularse con
TF-IDF/coseno por defecto y dejar embeddings como mejora opcional. Las explicaciones son
plantillas auditables basadas en features, no juicios.

La validacion incluye pruebas unitarias, pruebas estaticas del esquema SQL, pruebas de
constraints y triggers, endpoints API, import del dashboard y validacion final de
PostgreSQL, MongoDB, APIs, documentacion y comandos de reproduccion. El proyecto queda
preparado para repositorio publico y sustentacion academica, con la unica tarea humana
pendiente de aplicar la encuesta UX a cinco personas reales.

## Definicion del problema

Las organizaciones que revisan contratacion publica enfrentan volumen, heterogeneidad y
capacidad humana limitada. Necesitan priorizar revision con evidencia, no reemplazar la
revision juridica o fiscal.

## Requerimientos funcionales y no funcionales

Funcionales: ingesta, normalizacion, carga relacional, soporte NoSQL, ranking, detalle,
comparables, revision humana demo, APIs y dashboard.

No funcionales: reproducibilidad, trazabilidad, lenguaje etico, datos reales, pruebas,
documentacion y ejecucion local.

## Objetivo general y objetivos especificos

Objetivo general: implementar una plataforma full-stack para priorizar revision humana de
procesos contractuales con datos abiertos.

Objetivos especificos: extraer fuentes oficiales, normalizar entidades, disenar una base
relacional, integrar MongoDB, exponer microservicios, construir dashboard, documentar y
validar.

## Metodologia

El trabajo sigue fases de diseno de ingenieria: definicion del problema, alternativas,
seleccion, diseno, implementacion, pruebas y documentacion.

## Cronograma tipo Gantt

Ver `docs/metodologia_gantt.md`.

## Referencias

- Datos abiertos Colombia, datasets SECOP/PAA/contexto fiscal.
- Documentacion PostgreSQL.
- Documentacion MongoDB.
- Documentacion FastAPI.
- Documentacion Plotly Dash.

## Evaluacion de alternativas

Ver `docs/evaluacion_alternativas.md`.

## Evidencias de gerencia

El repositorio contiene auditoria de estado actual, README, Makefile, CI y documentos de
planificacion.

## Evidencias de diseno

Ver `docs/modelo_relacional.md`, `docs/modelo_nosql.md`,
`docs/diagrams/architecture.mmd` y `docs/diagrams/er_model.mmd`.

## Evidencias de documentacion

Manual de usuario, diccionario de datos, reproducibilidad, modelo, etica y pruebas estan
en `docs/`.

## Evidencias de pruebas

Ver `docs/testing_evidence.md` y `docs/pruebas.md`.

## Evidencias UX/interfaz

Dash es la interfaz oficial. La encuesta real queda pendiente en
`docs/ux_usability_survey.md`.

## Conclusiones y mejoras futuras

El proyecto demuestra una solucion reproducible con datos reales, persistencia poliglota,
microservicios y dashboard. Mejoras futuras: entidad-resolucion mas robusta, mas fuentes,
despliegue y encuesta UX diligenciada por cinco usuarios reales.
