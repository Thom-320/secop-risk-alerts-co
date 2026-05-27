# Human Validation Results

Estado: pendiente.

Este archivo no contiene resultados reales. No se fabrican etiquetas humanas,
precisión operacional ni conclusiones de validación. La evidencia se diligenciará
solo después de ejecutar `docs/human_validation_protocol.md` con revisores reales.

## Tabla esperada

| Campo | Descripción |
| --- | --- |
| `review_id` | Identificador de revisión |
| `process_id` | Proceso revisado |
| `process_key` | Llave del proceso |
| `priority_band` | Banda del score de prioridad |
| `confidence_score` | Soporte de datos |
| `alert_usefulness` | Útil, dudosa o no útil |
| `explanation_clarity` | Puntaje 1-5 |
| `paa_match_quality` | Puntaje 1-5 o no aplica |
| `comparables_quality` | Puntaje 1-5 o no aplica |
| `human_action_suggested` | Acción sugerida por el revisor |
| `reviewer_agreement` | Acuerdo entre revisores si aplica |
| `is_real_review` | Debe ser TRUE para evidencia real |

## Cómo se diligenciará

1. Seleccionar 40 a 100 procesos con mezcla de prioridad alta, media, baja y controles.
2. Entregar a revisores una ficha por proceso.
3. Registrar utilidad, claridad, PAA, comparables y acción humana sugerida.
4. Consolidar resultados sin datos personales sensibles.
5. Actualizar este archivo con conteos reales, fecha, método y responsable.
