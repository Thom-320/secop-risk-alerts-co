---
title: "Transparencia360 / ContratIA Abierta"
subtitle: "Sistema de Priorizacion Explicable de Revision Contractual en Colombia"
format: 16:9
---

# 1. ContratIA Abierta

Ordenar miles de procesos SECOP para decidir que revisar primero.

**Prioriza revision humana; no prueba conductas indebidas.**

Ingenieria de Datos, Universidad del Rosario.

---

# 2. Problema

No faltan datos de contratacion.

Falta capacidad humana para revisarlos con prioridad, evidencia y trazabilidad.

Muchos procesos -> ranking -> revision humana.

---

# 3. Stakeholder y decision

Veeduria ciudadana

Control interno

Periodista de datos

**Decision semanal:** que procesos revisar primero y por que.

---

# 4. Requisitos cubiertos

PostgreSQL + MongoDB como persistencia oficial

Polars para ETL

Scoring explicable (3 componentes)

Dash para sustentación

FastAPI x3 para microservicios

66 tests pasan

---

# 5. Fuentes y volumen

SECOP II Procesos

SECOP Integrado

Plan Anual de Adquisiciones

Contexto fiscal abierto

Demo validada: 17.229 procesos.

---

# 6. Arquitectura

Socrata -> ETL Python -> PostgreSQL + MongoDB -> Microservicios FastAPI -> Dash

---

# 7. process_master como tabla canonica

id_del_proceso como PK

entity_key para joins

4 fuentes con compuertas:

- p6dx-8zbt: fuente principal
- rpmr-utcd: enriquecimiento
- 9sue-ezhx: entra si pasa compuerta
- wasc-xi4h: solo contexto, no entra al score

---

# 8. Score explicable

6 señales interpretables con pesos:

- Competencia (0.24): ofertas recibidas
- Valor relativo (0.24): percentil frente a pares
- Modalidad (0.16): tipo de contratacion
- Planeacion (0.14): presencia de match PAA
- Concentracion de proveedor (0.12)
- Calidad de descripcion (0.10)

PAA entra solo si pasa compuerta.
Confianza mide soporte de datos disponible.

---

# 9. Confianza y bandas

Confidence score: base 45 + bonuses

Bandas de prioridad:

- Alerta prioritaria: 85+
- Alerta alta: 70+
- Observacion: 40+
- Baja prioridad: <40

Bandas de confianza:

- Alta: 75+
- Media: 55+
- Baja: <55

---

# 10. Score explicable

Competencia + valor relativo como senales principales.

Modalidad, planeacion y concentracion como contexto.

Descripcion como soporte visible.

Confianza de datos.

Razones auditables.

---

# 11. Demo

Panel principal -> Ranking de alertas -> Detalle de proceso -> Comparables

Dash en localhost:8050

---

# 12. Validacion y cierre

Limites: datos ruidosos, joins imperfectos, requiere revision humana.

Siguiente: extender a mas departamentos, mas procesos, ajustar pesos con evidencia.
