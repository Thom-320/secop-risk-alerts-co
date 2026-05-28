# Guion técnico de sustentación — ContratIA Abierta

> Audiencia: evaluador con perfil CTO / VP de Ingeniería / científico de la
> computación con años de experiencia en bases de datos. Asume que va a
> cuestionar el modelo de datos, los índices, la concurrencia, la normalización,
> la complejidad de las consultas y la honestidad de la validación. Este guion
> prioriza el **porqué** de cada decisión técnica, no solo el **qué**.

## Antes de empezar (60 segundos de preparación)

- Abre el deck en Chrome: `slides/html/contratia_abierta.html`. Navega con `←/→`.
- Ten el dashboard vivo en otra pestaña: `http://localhost:8050` (stack con `make demo-full`).
- Ten una terminal lista con el repo para responder con SQL en vivo si lo piden.
- Frase de apertura, memorizada: *"Esto es un sistema de ingeniería de datos que
  prioriza revisión humana de contratación pública. No es un detector de
  corrupción; es triage explicable y auditable."*
- Tiempo objetivo: 15 minutos de exposición + Q&A. ~45–50 s por slide.

---

## SLIDE 1 — Portada

**Narración:** "ContratIA Abierta. Es un sistema de ingeniería de datos que toma
los datos abiertos de contratación pública de Colombia — SECOP — y los convierte
en una cola priorizada de qué revisar primero. La tesis de una frase: **no
emitimos juicios de corrupción; ordenamos qué revisar primero, con evidencia
trazable.**"

**Por qué importa decir esto primero:** delimita el problema y blinda contra la
objeción ética que un evaluador serio plantea de entrada. Si arrancas vendiendo
"detector de corrupción", te desmontan en treinta segundos.

---

## SLIDE 2 — Tesis (qué hace / qué no hace)

**Narración:** "Antes de la arquitectura, definamos el contrato del producto. **Sí
hace**: ranking 0–100 auditable, comparables semánticos, alineación plan-PAA vs
ejecución, razones legibles y trazabilidad con hash de modelo. **No hace**: no
declara responsabilidad, no reemplaza auditoría jurídica ni fiscal, y — clave
para el modelo de datos — **el contexto fiscal nunca entra como etiqueta del
modelo**."

**Punto técnico para el DB expert:** "Esa última línea es una decisión de diseño
de datos, no solo ética: el dataset de control fiscal (AGR) vive en tablas
separadas y solo se usa para *validación retrospectiva*, nunca como feature ni
como target. Evitamos label leakage por construcción."

---

## SLIDE 3 — Problema (triage, no detección)

**Narración:** "El problema es de escala vs capacidad. SECOP publica más de 2
millones de procesos al año. Una oficina de control interno tiene decenas de
revisores. La pregunta operativa no es '¿hay corrupción?', es '¿cuáles 20
procesos reviso primero esta semana?'. Eso es un problema de **ranking y
priorización**, que es exactamente lo que un sistema de datos puede resolver bien
y de forma defendible."

**Si preguntan por el número:** "Los 2M+ son orden de magnitud del universo
nacional SECOP; nuestro universo scoreado en el demo es 88.148 procesos reales de
Meta y Casanare."

---

## SLIDE 4 — Arquitectura (5 capas)

**Narración:** "Cinco capas. Extracción desde la API Socrata de datos.gov.co.
Transformación con Polars a una tabla maestra. Persistencia poliglota:
**PostgreSQL como fuente de verdad relacional y MongoDB para evidencia
documental y eventos**. Servicio con tres microservicios FastAPI. Presentación en
Dash. La pieza que más pesa es el Score Engine, entre transformación y
persistencia."

**Por qué poliglota (anticipa la pregunta del DB expert):** "PostgreSQL lleva lo
que tiene esquema estable y necesita integridad transaccional: procesos, scores,
matches, auditoría. MongoDB lleva lo que es semiestructurado y de forma variable:
snapshots crudos de la API (que cambian de esquema), logs de ejecución de ETL,
eventos de la UI. Forzar los snapshots crudos a columnas relacionales sería
deuda; forzar el ranking a documentos perdería integridad referencial y
constraints. Cada motor donde rinde."

**Si cuestionan 'por qué no todo en Postgres con JSONB':** "Válido para escala
pequeña. Separamos por responsabilidad operativa: los snapshots crudos son
append-only de alto volumen y esquema volátil; mantenerlos fuera del motor
transaccional evita inflar el WAL y los vacuum de las tablas que sí sirven
consultas analíticas calientes."

---

## SLIDE 5 — Modelo relacional (ERD)

**Este es el slide donde el DB expert se va a quedar. Dale tiempo.**

**Narración:** "8 tablas centrales, 33 objetos públicos en total contando vistas y
triggers. `procurement_process` es el núcleo, con `process_key` como PK estable
derivada de entidad + referencia, y un `unique(entity, reference)` para
idempotencia de carga. Dos piezas marcadas con estrella son las distintivas:
`risk_assessment` y `paa_process_match`."

**Detalles que un experto valora (menciónalos explícitamente):**
- "`risk_assessment` tiene `PK·FK process_key` — relación 1:1 con el proceso,
  con `CHECK priority_score BETWEEN 0 AND 100` y `CHECK confidence_score BETWEEN
  0 AND 1`. Las invariantes del dominio viven en el esquema, no solo en el código."
- "`model_hash` y `computed_at` en `risk_assessment`: cada score es trazable a la
  versión del modelo que lo produjo. Reproducibilidad y auditoría."
- "FK `ON DELETE RESTRICT`: no se borra un proceso si tiene evaluación; la
  integridad referencial es estricta, no en cascada silenciosa."
- "`paa_process_match.match_method` ∈ {tfidf, embeddings}: el método de matching
  queda registrado por fila, así que la procedencia del enlace es auditable."
- "Vistas: `v_ranking_priority`, `v_provider_concentration`,
  `v_paa_execution_gap` — la lógica analítica vive en vistas versionadas en
  `sql/001_schema.sql`, no en strings dispersos en la app."

**Si preguntan por normalización:** "Está en 3FN. Las dimensiones
(`public_entity`, `provider`, `paa_item`) están separadas de los hechos
(`procurement_process`, `risk_assessment`, `paa_process_match`). Desnormalizamos
solo en las vistas de servicio para lectura."

**Si preguntan por índices:** "Índices en las FKs usadas en joins calientes
(`entity_code`, `process_key`), y en `priority_score` para el ranking ordenado.
El `unique(entity, reference)` es además un índice que sirve el upsert idempotente
del ETL."

---

## SLIDE 6 — Fuentes (4 datasets, un pipeline)

**Narración:** "Cuatro datasets oficiales: `p6dx-8zbt` SECOP II procesos
(canónico), `rpmr-utcd` SECOP Integrado (baseline histórico de valor),
`9sue-ezhx` Plan Anual de Adquisiciones (ancla de planeación), y `wasc-xi4h`
resultados de control fiscal AGR (contexto, no etiqueta). Un solo pipeline los
ingiere a todos."

**Punto técnico:** "El cruce no trivial es proceso ↔ contrato histórico, porque
no hay FK natural confiable entre SECOP II e Integrado. Lo resolvemos con un
`entity_crosswalk` y fallback por entidad + categoría UNSPSC + ventana temporal.
Lo cubro en detalle en el slide de matching."

---

## SLIDE 7 — Pipeline (5 pasos, artefacto auditable)

**Narración:** "Cinco pasos, cada uno deja un artefacto auditable en
`data/marts/`. Extracción con paginación Socrata (`$limit`/`$offset`) y manifest
versionado; si la API falla, fallback a Parquet local — el demo nunca depende de
la red. Limpieza y normalización con dedup por `process_key`. Matching. Scoring.
Y materialización de evidencia."

**Por qué le gusta a un ingeniero de datos:** "Es reproducible de extremo a
extremo: `make demo-full && make validate-final`. Cada etapa es idempotente — re-
correrla no duplica filas por el `unique(entity, reference)` y los upserts. El
`manifest` permite extracción incremental por offset."

---

## SLIDE 8 — Score explicable (4 componentes → 0–100)

**Narración:** "El score combina cuatro componentes auditables:
**anomalía 45%** (IsolationForest sobre el vector de features numéricas),
**desviación contra pares 35%** (cuán atípico es vs procesos comparables del
mismo segmento UNSPSC), **reglas 20%** (thresholds verificables: valor, plazo,
plan-vs-valor), y **confianza** aparte (0–1, cobertura de datos). La fórmula es
`score = round(100 · σ(Σ wᵢ·sᵢ))`."

**El punto que separa esto de 'humo de IA' (dilo):** "El score se normaliza por
**cuantiles robustos del dataset**, así que es relativo, no absoluto. Un score de
91 significa 'top 0.02% más atípico de los 88.148', no '91% corrupto'. Por eso la
UI muestra percentil. La distribución es de cola: mediana 7, p95 ≈ 45, solo 0.5%
supera 70. Eso es triage real: recorta el océano a un puñado."

**Si cuestionan los pesos 45/35/20:** "Son provisionales y documentados en la
model card. No los presento como óptimos; los presento como interpretables. El
siguiente paso de validación es calibrarlos contra un goldset humano."

---

## SLIDE 9 — SQL engineering

**Otro slide para el DB expert. Aquí te luces.**

**Narración:** "No es solo almacenamiento. Cuatro técnicas:
**Triggers** que escriben `audit_log` e historial de estados en cada cambio, y
mantienen `updated_at`. **Window functions** para la concentración proveedor por
entidad (`SUM() OVER (PARTITION BY entity)`, `RANK()`) y para el `percent_rank()`
global que da el percentil del score. **CTE recursiva** para la jerarquía
territorial departamento → municipio. **Transacciones** que escriben el score y
su evento de auditoría de forma atómica."

**Demo en vivo si lo piden (ten la query lista):** el `percent_rank()` del
ranking, o la window de concentración. Muéstrala corriendo contra los 88.148.

**Si preguntan por concurrencia/aislamiento:** "Las escrituras de score + evento
van en una transacción; el nivel por defecto de Postgres (READ COMMITTED) es
suficiente porque no hay read-modify-write sobre la misma fila desde dos
procesos; el scoring es batch single-writer. Si escaláramos a recompute
concurrente, subiríamos a SERIALIZABLE o usaríamos `SELECT ... FOR UPDATE` sobre
la fila de `risk_assessment`."

---

## SLIDE 10 — Microservicios (3 servicios)

**Narración:** "Tres servicios FastAPI por dominio: `contracts_service` (8001,
procesos y revisión humana), `risk_service` (8002, scoring y ranking),
`analytics_service` (8003, agregados, concentración, validación AGR). Cada uno con
`/health`. `validate-final` exige los tres healthchecks vivos antes de declarar
éxito — no hay 'éxito falso'."

**Por qué separados:** "Separación por dominio y por carga: el ranking
(`risk_service`) es lectura pesada con window functions; los agregados
(`analytics_service`) son otra clase de query. Comparten la capa de acceso a
datos pero escalan independiente. En `PUBLIC_READ_ONLY=true` los endpoints
mutables (recompute, POST /reviews) se bloquean con 403 — hardening para demo
pública."

---

## SLIDE 11 — Polyglot: PostgreSQL + MongoDB

**Narración:** "PostgreSQL para estructura: lo que tiene esquema y necesita
integridad. MongoDB para flexibilidad: snapshots crudos de la API (esquema
volátil), logs de ETL, eventos de la UI, reportes generados. Cinco colecciones."

**La pregunta que SIEMPRE hace un DB expert — '¿por qué no solo Postgres?' — ya
respondida arriba; aquí refuérzala con el caso de los snapshots:** "El snapshot
crudo de Socrata cambia de columnas entre versiones de la API. En relacional eso
es un ALTER TABLE recurrente o un mar de NULLs. En Mongo es un documento. Pero el
dato que sirve decisiones vive en Postgres con constraints. Es separación por
naturaleza del dato, no por moda."

---

## SLIDE 12 — Evidencia (números duros)

**Narración:** "Números reproducibles de `make validate-final`: 88.148 procesos
scoreados, 33 objetos PostgreSQL, 5 colecciones MongoDB con documentos, 3 APIs
con health 200, 71 tests pytest. Validaciones cubiertas: integridad de esquema,
auditoría de joins con fill rates, compuerta PAA, y bounds del scoring."

**Postura:** "Cada cifra se regenera desde el repo en menos de cinco minutos. No
es una captura; es un comando."

---

## SLIDE 13 — Dashboard (DECIDIR / ENTENDER / CONFIAR)

**Narración:** "El producto son tres zonas por el trabajo del usuario, no por
features. **DECIDIR**: la cola priorizada con filtro territorial y KPIs reales.
**ENTENDER**: la ficha del caso — score desglosado en sus componentes, razones,
comparables, alineación PAA, contexto fiscal. **CONFIAR**: la validación."
(Cambia a la pestaña del dashboard vivo aquí si el evaluador quiere verlo.)

---

## SLIDE 14 — Caso real: Puerto Gaitán (EL MOMENTO FUERTE)

**Narración pausada, este es el clímax:** "Prueba retrospectiva ciega. La
Contraloría documentó irregularidades **vigentes** en Puerto Gaitán: contratos de
agua/acueducto con hallazgo de más de $14.700 millones, sistemas fotovoltaicos
por $8.901 millones. Nuestro sistema, **sin haber visto esa información**, marca
Puerto Gaitán 2.5× sobre la tasa nacional, y su proceso top priorizado es una
construcción de acueducto de $42.408 millones — misma entidad, misma categoría
que señaló la Contraloría."

**El contraejemplo que demuestra rigor (no lo omitas):** "Y aquí está lo que da
credibilidad: la Gobernación de Casanare, emblema de corrupción con
exgobernadores condenados, puntúa en el **promedio (1.0×)**. ¿Por qué? Porque esos
escándalos son de hace 10+ años y la contratación *actual* no es estructuralmente
anómala. El sistema detecta **estructura del proceso vigente, no reputación
histórica**. No es una lista negra. Eso es exactamente lo que debe hacer un
detector serio."

**Si preguntan si es causalidad:** "No. Es corroboración retrospectiva a nivel
entidad + categoría. Auditoría AGR no prueba conducta indebida; mide selección
para revisión fiscal. Lo presento como validación del triage, no como acusación."

---

## SLIDE 15 — Matching (plan ↔ ejecución ↔ baseline)

**Narración:** "Tres cruces. Plan-PAA ↔ proceso por similitud semántica
(embeddings MiniLM multilingüe, cosine ≥ 0.55, con fallback TF-IDF). Proceso ↔
contrato histórico por `id_del_proceso` ↔ `numero_de_proceso`, con fallback a
entidad + UNSPSC + ventana. Proceso ↔ AGR por `sujeto_auditado = entidad`,
visible pero nunca como etiqueta. **Cuando no hay match fuerte, el sistema lo dice
en lugar de inventarlo** — reportamos cobertura, no forzamos enlaces."

**Sobre embeddings (si profundizan):** "El proveedor es configurable. Por defecto
`paraphrase-multilingual-MiniLM-L12-v2`, 384 dimensiones, corre local sin API key.
Lo probamos: `sim(acueducto, alcantarillado)=0.61` vs `sim(acueducto,
papelería)=0.14` — discrimina por significado. El fallback TF-IDF garantiza que
el demo no dependa de descargar el modelo."

---

## SLIDE 16 — Validación y límites

**Narración:** "Honesto, sin teatro. Validado: 71 tests, distribución de triage
real, enriquecimiento AGR 2.65×, caso Puerto Gaitán 2.5×, embeddings funcionando.
Pendiente declarado: validación humana de 100 casos con dos revisores, benchmark
formal embeddings vs TF-IDF, despliegue público, encuesta de usabilidad."

**Postura ante el evaluador:** "Prefiero declarar un pendiente a inventar un
resultado. La validación humana con precision@k es el siguiente paso, y el
protocolo ya está escrito."

---

## SLIDE 17 — Roadmap (Orinoquía → nacional)

**Narración:** "Escalar es particionar, no reescribir. El stack es horizontal:
añadir un departamento es más ingestión y más particiones Parquet, no rehacer
arquitectura. El costo marginal por departamento es un Postgres pequeño + storage."

---

## SLIDE 18 — Riesgos

**Narración:** "Lo que puede salir mal y cómo lo amortiguamos: volumen Socrata
(scope + nightly + Parquet), joins imperfectos (crosswalk + fallback +
reportamos cobertura), malinterpretación como detector de fraude (disclaimer
persistente + lenguaje de triage, con un test que falla si aparece lenguaje
acusatorio), sesgo a entidades pequeñas (mínimo de pares, 'evidencia
insuficiente' en lugar de forzar score)."

**Punto que impresiona:** "Tenemos un test automatizado, `test_language_guardrails`,
que escanea docs y UI y **falla el build** si aparece lenguaje acusatorio. La
ética es parte del CI."

---

## SLIDE 19 — Cierre

**Narración:** "Cierro con la frase que resume todo: sin entrenar contra ninguna
etiqueta de corrupción, el sistema prioriza 2.5× los contratos de Puerto Gaitán,
donde la Contraloría halló irregularidades vigentes. Detecta estructura, no
reputación. Prioriza revisión humana con evidencia trazable."

---

## Banco de preguntas difíciles (perfil base de datos)

**P: ¿Por qué PostgreSQL y MongoDB y no uno solo?**
R: Separación por naturaleza del dato. Postgres para lo transaccional con
constraints (procesos, scores, matches, auditoría); Mongo para lo append-only de
esquema volátil (snapshots crudos, logs, eventos). Forzar uno al otro genera
deuda: ALTER TABLE recurrentes o pérdida de integridad referencial.

**P: ¿Cómo garantizan idempotencia en la carga?**
R: `unique(entity, reference)` + upserts. Re-correr el ETL no duplica. El
`process_key` es determinista a partir de entidad + referencia.

**P: ¿El score es un modelo de caja negra?**
R: No. Es una agregación determinista de cuatro componentes con pesos
documentados, pasada por sigmoide y normalizada por cuantiles. Cada componente es
inspeccionable y cada score guarda su `model_hash`.

**P: ¿No están reentrenando contra la Contraloría (leakage)?**
R: No. El control fiscal AGR vive en tablas separadas y solo se usa para
validación retrospectiva. Nunca es feature ni target. El 2.65× es una prueba
ciega precisamente por eso.

**P: ¿Qué pasa con concurrencia en el recompute?**
R: El scoring es batch single-writer; score + evento van en una transacción. Para
recompute concurrente subiríamos a SERIALIZABLE o `SELECT FOR UPDATE` sobre la
fila de `risk_assessment`.

**P: ¿Por qué el percentil y no la nota absoluta?**
R: Porque la normalización es por cuantiles del dataset; el score es relativo. El
percentil es honesto: "top 0.5%", no "85/100 = malo".

**P: ¿Cobertura de los joins?**
R: Process ↔ Contract ~62%, Process ↔ PAA ~47%. Lo reportamos, no lo escondemos.
Cuando no hay match fuerte, el sistema lo declara.

**P: Vi el mismo proceso con dos scores distintos. ¿El score es aleatorio?**
R: No. El score es una función determinista de las features (IsolationForest con
`random_state=42` fijo; mismo vector de entrada → mismo score). Lo que se ve son
DOS FASES del mismo proceso que SECOP publica por separado: la fase "Evaluación"
(sin adjudicar: `awarded_total=0`, 0 oferentes) y la fase "Seleccionado"
(adjudicado: $544M, 5 oferentes). Tienen features distintas, así que scores
distintos (47 vs 96). Es correcto. La decisión de producto es mostrar UNA fila
por proceso (la fase más avanzada), y por eso deduplicamos por referencia
normalizada en la cola, el detalle y los comparables.

**P: ¿Por qué la mediana de pares es $2M si el proceso es de $588M?**
R: El grupo de pares es `modalidad · categoría UNSPSC · año`. En subasta inversa
de suministros aeronáuticos del año, la mayoría son contratos pequeños, así que la
mediana baja es real y el $588M es un outlier legítimo (289x). No es un artefacto:
es exactamente la señal que queremos que el revisor vea. Si el grupo tuviera menos
de N pares, el sistema reporta "evidencia insuficiente" en lugar de forzar el ratio.

**P: ¿Cómo sé que esto corre y no es un screenshot?**
R: `make demo-full && make validate-final`. 71 tests, 3 healthchecks, 33 objetos.
Cinco minutos desde un clone limpio. Lo puedo correr ahora.

---

## División entre dos expositores

19 slides, ~15 minutos, un solo punto de relevo limpio al terminar la slide 8.
Cada quien dueño de un bloque coherente.

### Expositor A — "El problema y la arquitectura" (slides 1–8, ~7 min)

| Slide | Foco | Frase de transición al siguiente |
| --- | --- | --- |
| 1 Portada | Abre con la tesis de una frase | "Empecemos por el problema." |
| 2 Tesis | Qué hace / qué no hace | "¿Por qué importa? Por la escala." |
| 3 Problema | Triage, no detección | "Así lo resolvemos, capa por capa." |
| 4 Arquitectura | 5 capas, Score Engine, polyglot | "Veamos la fuente de verdad: el modelo relacional." |
| 5 Modelo de datos | ERD, constraints, las 2 piezas ★ | "Cuatro fuentes alimentan esto." |
| 6 Fuentes | 4 datasets, AGR como contexto | "Y se procesan en un pipeline reproducible." |
| 7 Pipeline | 5 pasos, artefacto auditable | "El paso de scoring merece detalle." |
| 8 Score | 4 componentes, fórmula, percentil | **Relevo:** "Mi compañero/a les muestra ahora cómo está construido por dentro y la evidencia de que funciona." |

A es quien más cómodo debe estar con **modelo de datos y normalización** (slides 4–5),
porque ahí es donde el evaluador DB va a hacer las primeras preguntas duras.

### Expositor B — "La ingeniería profunda y la evidencia" (slides 9–19, ~8 min)

| Slide | Foco | Nota |
| --- | --- | --- |
| 9 SQL | Triggers, window, CTE, transacciones | Bloque donde B se luce; ten lista la query en vivo |
| 10 Microservicios | 3 servicios, healthchecks, read-only | |
| 11 MongoDB | Polyglot, por qué Mongo | Responde aquí la pregunta "¿por qué no todo Postgres?" |
| 12 Evidencia | Números duros reproducibles | |
| 13 Dashboard | DECIDIR/ENTENDER/CONFIAR | **Cambia al dashboard vivo aquí** |
| 14 Caso real | Puerto Gaitán 2.5× + Casanare | El clímax; pausa y dale peso |
| 15 Matching | Cruces + embeddings funcionando | |
| 16 Validación | Validado vs pendiente, AGR 2.65× | |
| 17 Roadmap | Orinoquía → nacional | |
| 18 Riesgos | Qué puede salir mal + CI ético | |
| 19 Cierre | Frase final | B cierra |

B es quien debe dominar **SQL, concurrencia y el caso Puerto Gaitán**. Es quien
recibe casi todas las preguntas técnicas profundas y de validación.

### Reparto del Q&A
- Preguntas de **modelo de datos, normalización, índices, persistencia poliglota** → A (y B apoya en Mongo).
- Preguntas de **SQL, concurrencia, scoring, validación, leakage, embeddings** → B.
- Si una pregunta se traba, el otro complementa en una frase. Nunca se pisan.

---

## Errores a evitar en la sustentación

- No uses lenguaje acusatorio (la palabra con C, "fraude", "irregularidad") como
  claim del sistema. Di "prioriza revisión".
- No vendas embeddings como SOTA; di "embeddings multilingües funcionando, con
  fallback robusto y benchmark formal pendiente".
- No prometas el clasificador supervisado: explica por qué NO lo haces (leakage,
  riesgo legal).
- Si algo falla en el demo, ten el PDF y los números a mano; no improvises datos.
