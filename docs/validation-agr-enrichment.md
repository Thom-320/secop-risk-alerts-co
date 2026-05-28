# Validación: ¿el score sirve? Experimento de enriquecimiento AGR

> Pregunta que responde este documento: *no hay etiqueta de "corrupción" para
> entrenar ni evaluar. ¿Cómo sabemos entonces que el ranking no ordena humo?*

## Tesis del experimento

No entrenamos contra ninguna etiqueta de control fiscal. Tomamos las entidades
que la **Auditoría General de la República (AGR)** efectivamente puso bajo
vigilancia fiscal (dataset abierto `wasc-xi4h`) y preguntamos, como **prueba
ciega**: ¿los procesos de esas entidades obtienen scores más altos que el resto?

Si el triage es útil, debería concentrar prioridad donde el control humano ya
encontró motivo de revisión — sin que el modelo "supiera" cuáles eran.

## Resultado (universo: 88.148 procesos scoreados, Meta + Casanare)

| Grupo | Procesos | Score medio | Mediana | % en alta prioridad (≥70) |
| --- | ---: | ---: | ---: | ---: |
| Entidad **sin** vigilancia AGR | 89.620 | 13.25 | 7.0 | 0.50% |
| Entidad **con** vigilancia AGR | 811 | 21.80 | 19.0 | **1.23%** |

- **Enriquecimiento en tasa de alta prioridad: 2.65×.**
- **Mediana del score: 19 vs 7 (2.7×).**

El modelo, sin ver la etiqueta AGR, empuja hacia arriba a las entidades que el
control fiscal ya vigilaba. Esa es la evidencia de que el ranking prioriza señal,
no ruido.

## Honestidad obligatoria (límites)

1. **Auditoría AGR ≠ conducta indebida probada.** Mide *selección para revisión
   fiscal*. Una entidad vigilada puede resultar sin hallazgos; el experimento
   valida el triage, no acusa.
2. **Señal a nivel entidad, no proceso.** Medimos "procesos de entidades
   vigiladas", no "este proceso específico fue objetado". Es una validación de
   correlación útil, no de causalidad.
3. **Universo Orinoquía.** El scope scoreado es Meta + Casanare (88.148 procesos
   reales de SECOP II). El pipeline es nacional-capaz; el demo se concentra en
   Orinoquía para mantener una historia limpia.
4. **No reemplaza validación humana.** El siguiente paso sigue siendo etiquetar
   manualmente ~100 casos del top del ranking con dos revisores (precision@k,
   acuerdo entre revisores, ejemplos de falso positivo).

## Distribución del score (forma de triage)

El score no está inflado: es una distribución de cola, exactamente lo que se
espera de una herramienta de priorización.

| Rango | Procesos |
| --- | ---: |
| 0–10 | 51.547 |
| 10–20 | 16.417 |
| 20–30 | 10.354 |
| 30–40 | 5.253 |
| 40–50 | 4.044 |
| 50–60 | 1.643 |
| 60–70 | 715 |
| 70–80 | 261 |
| 80–90 | 176 |
| 90–100 | 21 |

Mediana 7 · p95 ≈ 45 · solo **458 procesos (0.5%)** superan 70. Una oficina con
capacidad limitada revisa primero ese 0.5%, no el océano completo.

## Interpretación del score: percentil, no nota absoluta

El score se normaliza por cuantiles robustos sobre el dataset, así que es
**relativo al universo**, no una nota absoluta de 0 a 100. Por eso la UI muestra
*"top 0.5%"* (percentil) en vez de *"85/100 = malo"*. Un score de 91 significa
"está en el 0.02% más atípico de los 88.148", no "es 91% corrupto".

Fórmula: `score = round(100 · σ(Σ wᵢ · sᵢ))`, con
`w_anomalía = 0.45 · w_pares = 0.35 · w_reglas = 0.20`. La confianza (0–1) es
aparte y mide cobertura de datos, no certeza del score.

## Cómo reproducir

```bash
make demo-full                       # levanta Postgres con el universo real
curl localhost:8003/analytics/agr-enrichment    | python3 -m json.tool
curl localhost:8003/analytics/score-distribution | python3 -m json.tool
```

O en SQL directo:

```sql
WITH flagged AS (
  SELECT DISTINCT fcs.entity_id
  FROM fiscal_finding ff
  JOIN fiscal_control_subject fcs ON fcs.fiscal_subject_id = ff.fiscal_subject_id
  WHERE fcs.entity_id IS NOT NULL
)
SELECT (f.entity_id IS NOT NULL) AS vigilada,
       count(*) AS procesos,
       round(percentile_cont(0.5) WITHIN GROUP (ORDER BY ra.priority_score)::numeric,1) AS mediana,
       round((100.0*sum((ra.priority_score>=70)::int)/count(*))::numeric,2) AS pct_alta
FROM procurement_process p
JOIN risk_assessment ra ON ra.process_id = p.process_id
LEFT JOIN flagged f ON f.entity_id = p.entity_id
GROUP BY 1;
```
