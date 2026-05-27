# Human Validation Protocol

## Objetivo

Validar con personas reales si la cola de ContratIA Abierta ayuda a decidir qué
procesos SECOP revisar primero, sin convertir el score en acusación.

## Muestra

- Revisar entre 40 y 100 procesos.
- Diseño mínimo: 20 high-priority, 10 medium y 10 controles aleatorios.
- Mezclar top score, score medio, score bajo y controles aleatorios.
- Incluir departamentos y modalidades con suficiente volumen cuando sea posible.
- Guardar semilla, filtros y fecha para reproducibilidad.

## Etiquetas de revisión

- `useful_alert`: la alerta ayuda a priorizar revisión humana.
- `clear_reason`: la explicación es comprensible y trazable.
- `paa_match_correct`: el match PAA parece correcto al contrastarlo.
- `comparable_useful`: los comparables ayudan a contextualizar.
- `review_decision`: `requiere_revision`, `no_requiere`, `incierto`.
- `human_action_suggested`: mantener, bajar, subir prioridad o pedir más datos.

## Acuerdo entre revisores

Cuando haya dos revisores, registrar acuerdo/desacuerdo por caso y resolver
discrepancias con una nota de consenso. No usar etiquetas acusatorias.

## Plantilla

Usar `validation/manual_review_sample.csv` como plantilla. Las filas SAMPLE deben
reemplazarse por filas reales solo cuando exista revisión humana trazable.

## Métricas esperadas

- `precision@20` sobre los 20 primeros casos revisados.
- `agreement_rate` entre revisores cuando haya doble revisión.
- `useful_explanation_rate` a partir de `clear_reason`.
- Tasa de `paa_match_correct` cuando aplique.
- Tasa de `comparable_useful` cuando aplique.

## Script de resumen

Cuando existan revisiones reales:

```bash
uv run --python 3.11 python -m src.evaluation.human_validation_summary
```

El script debe rechazar plantillas `SAMPLE` y filas sin `is_real_review=TRUE`.

## Reglas éticas

No registrar conclusiones de responsabilidad. Usar lenguaje de revisión humana,
trazabilidad y acción sugerida.

## Limitaciones

La muestra no reemplaza una auditoría. Sirve para estimar utilidad operativa,
claridad y estabilidad de la cola de revisión. Los resultados deben reportarse
con fecha, revisores, tamaño de muestra y criterios de selección.
