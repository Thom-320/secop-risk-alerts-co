# ContratIA Abierta - speaker notes

Tiempo total objetivo: 15 minutos. Las notas estan escritas para una exposicion tecnica en espanol, con enfasis en evidencia y alcance etico.

## Slide 1 - Titulo (45s)

Presentamos Transparencia360 / ContratIA Abierta, un sistema full-stack para priorizar revision humana de procesos de contratacion publica colombiana. La tesis es simple: los datos abiertos ya existen, pero revisarlos todos manualmente no es viable. El sistema ordena procesos para decidir que revisar primero y mantiene trazabilidad hacia las fuentes. Desde el inicio dejamos claro el limite: no prueba conductas indebidas, no reemplaza auditoria juridica o fiscal y no acusa a ninguna entidad o proveedor.

## Slide 2 - Problema (90s)

El problema no es la ausencia de datos. En Colombia existen fuentes abiertas como SECOP, PAA y otros datasets institucionales. El problema practico es que una veeduria, una oficina de control interno o un periodista de datos no puede revisar miles de procesos con el mismo nivel de detalle. La decision operativa es semanal y concreta: en que procesos invertir tiempo humano primero. Por eso el proyecto no intenta emitir veredictos; intenta transformar volumen y ruido en una cola explicable de revision.

## Slide 3 - Stakeholder y decision (75s)

El stakeholder esta definido como una organizacion con requerimientos reales: veeduria ciudadana, oficina de transparencia, control interno o periodismo de datos. Todos comparten una restriccion: tienen capacidad limitada y necesitan justificar por que revisan un caso antes que otro. La salida del sistema es un ranking con razones, comparables y confianza. Eso permite discutir una decision de priorizacion, no una acusacion automatica.

## Slide 4 - Requisitos cubiertos (90s)

La guia de clase pedia una solucion de ingenieria de datos, no solo un dashboard. Por eso el proyecto se cerro con PostgreSQL como base relacional principal, MongoDB como soporte documental y de eventos, tres microservicios FastAPI, una interfaz oficial en Dash, ETL reproducible y SQL avanzado. La validacion final reporta 27 tablas relacionales y 33 objetos publicos, 17.229 procesos en la carga demo, colecciones Mongo con documentos, health checks en 200 y la suite automatizada no integral pasando.

## Slide 5 - Fuentes y volumen (90s)

Las fuentes son datasets oficiales abiertos. SECOP II Procesos aporta la unidad analitica principal: el proceso contractual. SECOP Integrado y PAA permiten contexto de ejecucion y planeacion. El dataset de vigilancia o control fiscal se usa como contexto visible, no como determinante de responsabilidad. La demo carga mas de 10.000 registros, concretamente 17.229 procesos, y deja conteos en `validation/table_counts.csv` para que el profesor pueda verificar el volumen.

## Slide 6 - Arquitectura (90s)

La arquitectura separa ingestion, persistencia, servicios y presentacion. Socrata alimenta el ETL. Parquet queda como cache o fallback local. PostgreSQL conserva el modelo normalizado y es la fuente de verdad. MongoDB almacena snapshots, logs y eventos que encajan mejor como documentos. Encima hay servicios FastAPI separados para contratos, prioridad y analitica. Dash consume esos datos y presenta el flujo de demo. Esta separacion permite probar cada capa.

## Slide 7 - Modelo relacional (90s)

El modelo relacional supera el minimo de 15 tablas y llega a 27 tablas relacionales y 33 objetos publicos en la validacion local. Agrupa ingesta, geografia, entidades, proveedores, procesos, PAA, contexto fiscal, score, razones, comparables, auditoria y revision humana. La parte importante no es solo contar tablas: hay llaves primarias, foraneas, restricciones de score y confianza, indices utiles y vistas analiticas. PostgreSQL se usa para garantizar integridad, no solo como deposito.

## Slide 8 - NoSQL y auditoria (75s)

MongoDB no reemplaza a PostgreSQL. Se usa para datos con forma documental o historica: snapshots crudos, logs de ETL, eventos de prioridad, reportes generados y acciones de dashboard. Esto permite conservar evidencia flexible sin deformar el modelo relacional. En la validacion, las colecciones requeridas existen y tienen documentos. La idea es que un auditor pueda reconstruir de donde salio una vista o un reporte sin depender solamente de tablas normalizadas.

## Slide 9 - SQL engineering (90s)

La solucion incluye piezas concretas del temario. Hay triggers de auditoria que escriben cambios en `audit_log`, historial de estado para procesos, validacion de score y mantenimiento de `updated_at`. Las vistas usan window functions para ranking, concentracion proveedor-entidad y outliers por grupo par. Tambien hay CTE recursiva para jerarquia territorial. El archivo de transacciones muestra como registrar score y evento asociado de forma atomica.

## Slide 10 - Score explicable (90s)

El score sigue una filosofia rules-first. Combina reglas claras, desviacion frente a procesos pares, componente de anomalia como apoyo y una medida de confianza. Cada evaluacion genera razones auditables. Si la calidad de datos es baja, la confianza baja. Si hay comparables cercanos, se muestran como referencia. Lo clave es que el score ordena revision humana; no determina responsabilidad, no sanciona y no sustituye criterio experto.

## Slide 11 - Demo (120s)

La demo empieza en Panorama con conteos, cobertura y distribucion por departamento. Luego pasa a Ranking, donde se filtra por score y se revisan procesos priorizados. Despues entra a Detalle de proceso, que muestra explicacion, entidad, modalidad, score, confianza y comparables. El flujo esperado para el usuario es: primero entender el universo, segundo escoger un candidato, tercero revisar evidencia y cuarto decidir si abre una revision humana.

## Slide 12 - Validacion y cierre (75s)

La validacion final cruza los criterios academicos: tablas, filas, Mongo, APIs, tests, docs y README. Quedan limites honestos: los datos abiertos pueden ser ruidosos, los joins entre fuentes no son perfectos y la herramienta requiere revision humana. El siguiente paso humano es aplicar la encuesta real con 5 usuarios, incorporar retroalimentacion y, si hay stakeholder disponible, ejecutar un piloto controlado. El aporte del proyecto es convertir datos masivos en una cola trazable de revision.
