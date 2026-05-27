# Brief para Claude Design — Diapositivas técnicas ContratIA Abierta

> Pega este brief en una conversación nueva de claude.ai. Adjunta los archivos listados al final. Pide explícitamente "artifact" / "haz un slide deck como artifact HTML interactivo navegable con teclas ← → o clicks". Después exportas a PDF desde el navegador (Cmd+P → Guardar como PDF, dos páginas por hoja si se requiere).

---

## ROL

Eres director de diseño + arquitecto de presentaciones técnicas para audiencia ejecutiva senior. Tu cliente típico es CTO, VP Eng, jefe de plataforma de gobierno digital, o jurado técnico de un concurso nacional de IA. No diseñas para impresionar a estudiantes; diseñas para que un CTO escéptico, con poco tiempo y mucho criterio, asienta y haga preguntas duras.

## ENTREGABLE

Un **único artifact HTML** con:
- 14 diapositivas, 16:9, navegables con flechas `←/→` (JS vanilla) y barra de progreso superior.
- Sin dependencias pesadas; Tailwind CDN ok; iconografía lucide CDN ok; gráficos vectoriales inline SVG; diagramas con Mermaid CDN ok.
- Todo el texto en **español de Colombia**.
- Diseñado para verse perfecto en pantalla **y** al exportar a PDF (sin scroll interno, sin contenido cortado).
- Cada diapositiva ocupa exactamente una pantalla 16:9. Sin "scroll para ver más".

## PRODUCTO QUE ESTÁS PRESENTANDO

**ContratIA Abierta** — sistema de IA explicable que **prioriza revisión humana** de contratación pública en Colombia. No emite juicios de corrupción. Convierte miles de procesos SECOP en una cola priorizada y auditable. Datos abiertos oficiales del ecosistema Datos Abiertos Colombia. Demo en Meta + Casanare (Orinoquía). Concurso: Datos al Ecosistema 2026.

## AUDIENCIA Y TONO

- Audiencia: jurado técnico del concurso + observadores tipo CTO de entidad pública.
- Tono: técnicamente preciso, sobrio, denso pero respirable. Sin lenguaje de marketing. Sin "revolucionario", "disruptivo", "potencia tu". Sin emojis decorativos.
- Cada slide gana o pierde por **substancia** (números reales, fórmulas, métricas), no por adornos.
- Honestidad explícita sobre límites es **parte del producto**: no oculta lo que falta validar.

## RESTRICCIONES ÉTICAS (no negociables)

- **Nunca** usar las palabras: "corrupción", "fraude", "irregularidad", "ilegal", "delito".
- Score = "prioridad de revisión", no "riesgo de corrupción".
- Toda diapositiva con alertas/ranking debe llevar la nota: *"Prioriza revisión humana; no prueba conductas indebidas."*
- Contexto fiscal (AGR) se muestra como evidencia contextual, **no** como etiqueta del modelo.

## SISTEMA DE DISEÑO (impleméntalo como design tokens en CSS variables)

```
--ink:          #0B1E33   /* texto primario y fondos hero */
--ink-2:        #1F2C40
--muted:        #5A6478
--faint:        #8893A8
--rule:         #E3E8F0
--canvas:       #F7F8FB
--surface:      #FFFFFF
--panel:        #F1F4F9
--navy:         #103A5C   /* color de marca primario */
--navy-strong:  #0B2A45
--coral:        #E35A4B   /* acento, llamadas a atención */
--coral-soft:   #FCEAE5
--teal:         #1F827C   /* positivos / validación */
--teal-soft:    #DDF1EF
--amber:        #C28832   /* advertencia */
--amber-soft:   #FBF1DC
```

- **Tipografía**: Inter (`@import` desde Google Fonts). Display 800 para titulares, 600-700 para subtítulos, 400-500 para cuerpo. `font-feature-settings: "cv11", "ss01"`. `tabular-nums` SIEMPRE en cifras.
- **Mono**: `SF Mono`, `ui-monospace`, `Consolas` para IDs SECOP, códigos de dataset (`p6dx-8zbt`), nombres de tabla, comandos shell, fórmulas.
- **Espaciado**: padding base de 48px en bordes; gap de 24-32px entre bloques mayores.
- **Sombras**: muy sutiles, solo `0 4px 14px rgba(11,30,51,.06)`. Nada de neón, glow, gradientes saturados.
- **Bordes**: 1px sólido `--rule`; radio 12-16px.
- **Patrón de slide estándar**:
  - Top band 6px navy + 3px coral overlay a la izquierda.
  - Eyebrow uppercase coral 11px, letter-spacing 0.12em.
  - Título 28-32px ink, peso 800.
  - Regla coral de 60px bajo el título.
  - Cuerpo en grid de 2 o 3 columnas.
  - Footer izquierda: disclaimer ético. Footer derecha: `X / 14`.

## ESTRUCTURA DE LAS 14 DIAPOSITIVAS

> Sigue el orden exactamente. Cada slide tiene un propósito de defensa técnica.

### 1. Portada
- Fondo `--ink`. Banda izquierda coral 4px.
- Eyebrow: "CONCURSO DATOS AL ECOSISTEMA 2026 · IA PARA COLOMBIA".
- Titular: **ContratIA Abierta**, 72px, peso 800, blanco.
- Subtítulo: "IA explicable para priorizar revisión humana de la contratación pública en Colombia."
- Línea italic sand: "No emitimos juicios de corrupción. Ordenamos qué revisar primero, con evidencia trazable."
- 4 chips navy con texto blanco: "Datos abiertos SECOP", "Score 0–100 explicable", "Revisión humana trazable", "Orinoquía → Colombia".
- Pie: "Gobernanza y Transparencia · Meta y Casanare · Universidad del Rosario".

### 2. Tesis del producto (qué hace / qué NO hace)
- Dos columnas verticales. Izquierda con barra teal 4px y header "SÍ HACE"; derecha con barra coral 4px y header "NO HACE".
- SÍ HACE: (a) Ranking 0–100 explicable; (b) Comparables semánticos; (c) Alineación plan (PAA) vs ejecución; (d) Razones legibles + confianza visible; (e) Trazabilidad: fuente, fecha, snapshot, hash.
- NO HACE: (a) No declara corrupción/fraude/responsabilidad; (b) No reemplaza auditoría jurídica ni fiscal; (c) No deanonimiza más allá del dato público; (d) No usa contexto fiscal como etiqueta del modelo; (e) No reemplaza decisión humana — la informa.
- Footer strip cloud: "Un score alto significa 'revísalo primero con evidencia', no 'es corrupción'."

### 3. Problema operativo cuantificado
- Headline: "Triage, no detección. Capacidad humana < volumen de procesos."
- Tres tarjetas con barra de color a la izquierda (navy, coral, teal):
  - **Volumen**: cientos de miles de procesos/año en SECOP.
  - **Capacidad**: decenas de revisores con tiempo limitado por entidad.
  - **Decisión real**: una pregunta semanal — *¿qué revisamos primero esta semana?*
- Pie sand: "Triage de contratación = océano de procesos → cola priorizada y auditable."

### 4. Arquitectura técnica end-to-end
- Diagrama Mermaid `flowchart LR` con 5 capas — pídeselo a la audiencia como diagrama, no como bullets:
  ```
  flowchart LR
    A[Socrata API · SECOP II/Integrado/PAA/AGR] --> B[Extract · Polars + Parquet]
    B --> C[Transform · build_process_master · join audit]
    C --> D[Score · rules + peer dev + IsolationForest + confidence]
    D --> E[Postgres relacional · 33 objetos]
    D --> F[Mongo evidencia · 5 colecciones]
    E --> G[FastAPI · contracts · risk · analytics]
    F --> G
    G --> H[Dash UI · panorama → ranking → detalle]
  ```
- Lateral derecho: stack table con label + valor, en mono donde aplica.

### 5. Modelo de datos relacional
- Diagrama ERD reducido — usa los 6 tableros centrales con sus claves:
  - `procurement_process` (PK `process_key`) — núcleo SECOP II
  - `provider`, `public_entity`, `paa_item` con FKs
  - `paa_process_match` (matching plan↔ejecución)
  - `risk_assessment` (score + confidence con CHECK 0–100, 0–1)
  - `semantic_comparable` (pares comparables con similarity)
  - `audit_log` (triggers de cambios)
- Footer: "33 objetos públicos en PostgreSQL · constraints + índices + vistas analíticas."

### 6. Datos abiertos: fuentes oficiales
- Cuatro tarjetas con código mono navy: `p6dx-8zbt` (SECOP II Procesos), `rpmr-utcd` (SECOP Integrado), `9sue-ezhx` (PAA), `wasc-xi4h` (AGR · contexto, no etiqueta).
- Cada una con barra de color a la izquierda y descripción de 1 línea.
- Fila inferior con 4 métricas en cards CLOUD: **17.229** procesos · **4.494** PAA items · **68.916** razones explicables · **100%** datos abiertos.

### 7. Pipeline reproducible (5 pasos numerados)
- Cinco bloques con círculo navy numerado encima de cada uno:
  1. **Extracción** — Socrata SODA + snapshots Parquet versionados.
  2. **Limpieza** — normalización, dedup, IDs estables (`process_key`).
  3. **Matching** — PAA ↔ proceso (TF-IDF actual; embeddings activables vía `MODEL_BACKEND`).
  4. **Scoring** — reglas + desviación contra pares + IsolationForest + confianza.
  5. **Evidencia** — ranking + razones + comparables + reporte HTML descargable.
- Flecha coral entre pasos.
- Strip inferior con bloque de código mono:
  ```bash
  make product-pipeline && make validate-product
  ```
  + "Reproducible end-to-end desde clone limpio; cada paso deja artefacto auditable."

### 8. Score explicable — fórmula visible
- Headline: "Cuatro componentes auditables → un número entre 0 y 100."
- Cuatro tarjetas con barra navy/teal/coral/muted:
  - **Reglas** (heurísticas: modalidad, unicidad, plazos, plan-vs-valor).
  - **Pares** (desviación contra procesos comparables del mismo segmento UNSPSC).
  - **Anomalía** (componente estadístico — IsolationForest sobre vector de features).
  - **Confianza** (0–1 según cobertura y calidad de datos cargados).
- Caja con fórmula explícita en mono, peso 700:
  ```
  score = round(100 · σ( Σ wᵢ · sᵢ ))
  pesos actuales: w_rules=0.45 · w_peer=0.35 · w_anomaly=0.20  · confidence visible aparte
  ```
- Tira inferior con 4 rangos de interpretación (0-20 típico · 21-40 leve · 41-70 notable · 71-100 alta prioridad).

### 9. SQL engineering (lo que un CTO espera ver)
- Dos columnas. Izquierda 4 cards: Triggers · Window functions · CTE recursiva · Transacciones. Cada una con descripción técnica de 1 línea.
- Derecha: bloque de código mono con un snippet real corto, p.ej. la window function de concentración o la CTE recursiva de jerarquía territorial. Sintaxis SQL resaltada (a mano con `<span>`).
- Footer: "No es solo almacenamiento. Integridad, trazabilidad y consultas analíticas reproducibles."

### 10. Microservicios + observabilidad
- Tres tarjetas (puerto · responsabilidad · health):
  - `contracts_service :8001` — procesos, ranking, revisión humana (POST `/reviews`).
  - `risk_service :8002` — scoring, recomputes, evidencia de comparables.
  - `analytics_service :8003` — concentración, plan-vs-execution, agregados.
- Bloque inferior: gráfico SVG simple con 3 indicadores de health 200 verdes.
- Stack lateral: Docker Compose · `make academic-services-up` · `validate-final` exige PG + Mongo + 3 healthchecks.

### 11. Evidencia de ingeniería (métricas duras)
- Grid 3×2 de métricas grandes en navy/coral/teal:
  - **17.229** procesos cargados
  - **33** objetos PostgreSQL
  - **5/5** colecciones MongoDB
  - **3** APIs FastAPI · health 200
  - **71** tests pytest
  - **21** documentos técnicos
- Lateral derecho: lista de validaciones cubiertas — schema integrity · join audit · PAA gate · process_key unique · scoring bounds · reporte HTML reproducible.

### 12. Validación y límites honestos
- Izquierda: gráfico `validation_summary.png` (lo trae como imagen adjunta) o reproduce métricas:
  - Compuerta PAA top-1: confianza ≥ 0.75 → reportada por entidad y modalidad.
  - Cobertura PAA: % procesos con match.
  - Fill rates `codigo_entidad`: % join válido `p6dx ↔ rpmr`.
- Derecha: checklist con ✓ (validado) y ○ (pendiente):
  - ✓ Software: 71 tests · lint estable · `validate-final` ok
  - ✓ Datos: 17.229 procesos · joins auditados
  - ○ Validación humana de 100 casos (protocolo definido, faltan revisores)
  - ○ Embeddings activables (`MODEL_BACKEND=embeddings`, falta benchmark vs TF-IDF)
  - ○ Despliegue público read-only
- Footer sand: "Honesto > teatro. Los pendientes son parte del roadmap, no del pitch."

### 13. Roadmap de escalado y costo
- Línea de tiempo horizontal con 4 hitos (mes 1 → mes 6):
  - **Mes 1**: pilotos con 2 oficinas de control en Orinoquía + validación humana.
  - **Mes 2-3**: backend de embeddings activable; despliegue read-only en Render.
  - **Mes 4-5**: escalado por departamento, mismo pipeline; data cards completas.
  - **Mes 6**: cobertura nacional opcional con cuotas Socrata + ingestion programada.
- Caja navy lateral: "Costo marginal por departamento ≈ infra de 1 Postgres pequeño + storage Parquet partitioned. Stack es horizontal, no requiere reescritura."

### 14. Cierre
- Fondo `--ink`. Banda izquierda coral.
- Titular grande blanco: **ContratIA Abierta**.
- Subtítulo: "Prioriza revisión humana en la contratación pública colombiana."
- Tres bloques info: EQUIPO (Ingeniería de Datos · Universidad del Rosario) · REPO (`github.com/Thom-320/secop-risk-alerts-co`) · CATEGORÍA (Gobernanza y Transparencia · Meta y Casanare).
- Cita lateral en card navy: "Convierte una revisión imposible en una cola auditable."

## DATOS CONCRETOS QUE PUEDES USAR (números reales del repo, no los inventes diferentes)

- 17.229 procesos cargados en demo
- 33 objetos PostgreSQL (tablas + vistas)
- 5 colecciones MongoDB
- 71 tests pytest pasan
- 3 servicios FastAPI (puertos 8001/8002/8003) con `/health` 200
- 4.494 PAA items
- 68.916 razones explicables generadas
- Pesos actuales: `w_rules=0.45`, `w_peer=0.35`, `w_anomaly=0.20`
- Compuerta PAA: confianza top-1 ≥ 0.75
- `MODEL_BACKEND=tfidf` actualmente; `embeddings` disponible vía `.env`
- Scope demo: Meta y Casanare
- Fuentes: `p6dx-8zbt`, `rpmr-utcd`, `9sue-ezhx`, `wasc-xi4h`

## REGLAS QUE NO QUIERO QUE ROMPAS

- **Cero glassmorphism**, cero blur, cero "neumorphism", cero pie charts.
- **Cero íconos decorativos** (lupa gigante, persona, mundo). Iconos solo si aportan función — chevron, check, warning, copy, external-link.
- **Cero mapas decorativos** sin función analítica.
- **Cero gradientes saturados** (azul-rosa, naranja-amarillo). Si usas gradiente, navy → navy oscuro nada más.
- **Cero animaciones de scroll-parallax** o "fade-in al hacer scroll".
- **Cero emojis decorativos** salvo ⚠ específicamente en el disclaimer ético si ayuda.
- **No inventes números**. Si te falta uno, deja `—` y nota "dato por confirmar".

## EXPORTACIÓN

Cuando termines:
1. El artifact debe imprimirse bien con `@media print` — cada slide en su página A4 horizontal.
2. Verifica con vista previa de impresión que ningún elemento se corte.
3. Entrega también, en un bloque de código separado, el HTML completo listo para descargar.

## ARCHIVOS ADJUNTOS (los subo al chat)

1. `README.md` — tesis y arquitectura.
2. `docs/arquitectura.md` — detalle técnico.
3. `docs/model-card.md` — score y límites.
4. `docs/data-cards/*.md` — fichas por dataset.
5. `docs/testing_evidence.md` — métricas de validación.
6. `docs/ethics-note.md` — disclaimers.
7. `slides/assets/architecture.png` — diagrama existente (referencia).
8. `slides/assets/er_model.png` — ERD existente (referencia).
9. `slides/assets/screenshot_dashboard_home.png` / `screenshot_ranking.png` / `screenshot_process_detail.png` — screenshots reales del dashboard.
10. `slides/assets/validation_summary.png` — gráfico de validación.

Úsalos como **fuente de verdad técnica**. No inventes números diferentes.

---

Empieza por la portada (slide 1) y la slide 4 (arquitectura). Esas dos definen si el deck se siente serio o se siente decorativo. Cuando esas dos estén impecables, sigues con el resto.
