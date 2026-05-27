# CRISP-ML

## 1. Comprensión del problema

Priorizar revisión humana de procesos contractuales abiertos, sin emitir juicios automáticos.

## 2. Comprensión de datos

- SECOP II para universo de procesos
- SECOP Integrado para enriquecimiento opcional
- PAA para plan vs ejecución
- Control fiscal como contexto visible

## 3. Preparación

- Normalización de entidad, NIT y referencia de proceso
- Derivación de llaves y familias de modalidad
- Auditoría explícita de joins

## 4. Modelado

- `anomaly_score`
- `peer_deviation_score`
- `rule_score`
- `confidence_score`

## 5. Evaluación

- validación manual de matches y comparables
- compuertas para decidir el rol del PAA
- score visible y explicable

## 6. Despliegue

- PostgreSQL + MongoDB como columna vertebral de la entrega académica
- FastAPI como microservicios de contratos, riesgo y analítica
- Dash como interfaz oficial de sustentación
- Parquet/DuckDB + Streamlit quedan como respaldo offline y plus de producto
