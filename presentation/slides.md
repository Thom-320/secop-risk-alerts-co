---
marp: true
title: Transparencia360 / ContratIA Abierta
paginate: true
---

# Transparencia360 / ContratIA Abierta

Sistema poliglota de priorizacion de revision contractual en Colombia.

**Tesis:** ordenar miles de procesos SECOP para decidir que revisar primero.

---

# Problema

- Usuario: veeduria, oficina de transparencia, periodista de datos.
- Dolor: demasiados procesos y poca capacidad humana.
- Decision: que procesos revisar primero.

---

# Mapa de requisitos

- PostgreSQL: 20+ tablas, constraints, triggers, vistas.
- MongoDB: snapshots, logs y eventos.
- FastAPI: tres microservicios.
- Dash: interfaz oficial.
- ETL: 10.000+ procesos demo.
- Pruebas: lint, pytest, validacion final.

---

# Fuentes y volumen

- SECOP II procesos.
- SECOP Integrado.
- PAA detalle.
- Contexto de control fiscal.

Usar `validation/table_counts.csv` como evidencia final.

---

# Arquitectura

![bg right fit](../docs/diagrams/architecture.mmd)

Socrata o Parquet local -> ETL -> PostgreSQL + MongoDB -> FastAPI -> Dash.

---

# Diseno relacional

- PostgreSQL es la fuente de verdad.
- 20+ tablas normalizadas.
- PK/FK, UNIQUE, CHECK, NOT NULL.
- Dinero en `NUMERIC`.

---

# Diseno NoSQL

- `raw_process_snapshots`
- `etl_run_logs`
- `risk_event_logs`
- `report_snapshots`
- `user_action_logs`

Mongo guarda documentos y eventos, no reemplaza PostgreSQL.

---

# SQL engineering

- Trigger de auditoria OLD/NEW JSONB.
- Historial de estado.
- Validacion de risk assessment.
- Window functions para concentracion/outliers.
- CTE recursiva para jerarquia administrativa.

---

# Scoring explicable

- Anomalia.
- Desviacion frente a pares.
- Reglas explicitas.
- Confianza.
- Razones visibles.

No detecta corrupcion; prioriza revision humana.

---

# Dashboard

Flujo:

1. Panorama.
2. Ranking.
3. Detalle y comparables.

Insertar screenshots reales despues de ejecutar la demo.

---

# Pruebas y validacion

- `make lint`
- `make test`
- `make validate-final`

Evidencia: `validation/final_validation.json`.

---

# Impacto y limites

- Impacto: usa mejor la capacidad humana de revision.
- Limites: calidad de datos, joins imperfectos, no acusacion.
- Siguientes pasos: encuesta real, despliegue, mejor resolucion de entidades.
