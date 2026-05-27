# Speaker notes

## 1. Title

Presentar el proyecto como una solucion de ingenieria de datos, no como una idea de IA generica. La frase central es que el sistema ayuda a decidir que revisar primero.

## 2. Problem

Explicar que el cliente tiene capacidad limitada y muchos procesos. El problema es de priorizacion operativa.

## 3. Requirements mapping

Conectar cada requisito de la guia con un artefacto del repositorio: PostgreSQL, MongoDB, microservicios, Dash, ETL, pruebas y documentacion.

## 4. Data sources and volume

Nombrar los datasets oficiales y mostrar la evidencia de volumen desde `validation/table_counts.csv`.

## 5. Architecture

Recorrer el flujo completo: fuentes, ETL, bases de datos, servicios y dashboard.

## 6. Relational design

Enfatizar llaves, restricciones, normalizacion, indices y uso de `NUMERIC` para dinero.

## 7. NoSQL design

Explicar que Mongo se usa para documentos y eventos porque ese formato cambia con mas frecuencia.

## 8. SQL engineering

Mostrar los elementos vistos en clase: triggers, CTE recursiva, window functions y transacciones.

## 9. Risk scoring

Repetir la advertencia etica: no detecta corrupcion. El score es una herramienta de triage.

## 10. Dashboard flow

Hacer una demo breve desde panorama hacia ranking y detalle.

## 11. Tests

Mostrar comandos y resultado de validacion. Si hay bloqueadores de infraestructura, explicarlos.

## 12. Impact and limitations

Cerrar con impacto realista, limites y trabajo pendiente de encuesta con usuarios reales.
