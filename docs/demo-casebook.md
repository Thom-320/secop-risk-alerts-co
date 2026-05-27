# Demo Casebook — ContratIA Abierta

Los siguientes casos son SAMPLE para guiar el relato de la demo. No son evidencia real,
no son etiquetas humanas y no deben presentarse como resultados de validación.

## CASE-001 — Alta prioridad con confianza alta

- `sample_flag`: SAMPLE.
- Proceso: `SAMPLE-PROC-001`.
- Selector reproducible: ranking por `priority_score` descendente y `confidence_score >= 70`.
- Entidad: Alcaldía Demo Meta.
- Departamento: Meta.
- Score aproximado o criterio: alta prioridad con confianza suficiente.
- Señales a mostrar: score de prioridad alto, confianza suficiente y razones visibles.
- Acción humana sugerida: abrir fuente SECOP, revisar objeto, cuantía y soporte.
- Frase para jurado: “Este caso ilustra cómo la herramienta ordena capacidad humana limitada”.
- Nota de demo: usarlo para explicar que prioridad no equivale a conclusión.

## CASE-002 — Alta prioridad con confianza baja

- `sample_flag`: SAMPLE.
- Proceso: `SAMPLE-PROC-002`.
- Selector reproducible: ranking por `priority_score` alto y `confidence_score < 55`.
- Entidad: Entidad Demo Casanare.
- Departamento: Casanare.
- Score aproximado o criterio: prioridad alta con confianza baja.
- Señales a mostrar: score alto con soporte incompleto.
- Acción humana sugerida: validar calidad de datos antes de escalar.
- Frase para jurado: “Score y confianza se leen juntos; baja confianza pide validar datos”.
- Nota de demo: usarlo para diferenciar prioridad de confianza.

## CASE-003 — Match PAA fuerte

- `sample_flag`: SAMPLE.
- Proceso: `SAMPLE-PROC-003`.
- Selector reproducible: filtrar `paa_match_status=strong`.
- Entidad: Alcaldía Demo Meta.
- Departamento: Meta.
- Score aproximado o criterio: proceso con evidencia PAA visible.
- Señales a mostrar: item PAA, referencia asociada y valor plan-vs-ejecución.
- Acción humana sugerida: revisar coherencia entre planeación y proceso.
- Frase para jurado: “El PAA aporta trazabilidad de planeación, no una conclusión”.
- Nota de demo: el match PAA aporta contexto, no una inferencia acusatoria.

## CASE-004 — Comparables disponibles

- `sample_flag`: SAMPLE.
- Proceso: `SAMPLE-PROC-004`.
- Selector reproducible: seleccionar proceso con `semantic_comparable_count > 0`.
- Entidad: Gobernación Demo Casanare.
- Departamento: Casanare.
- Score aproximado o criterio: comparables disponibles para contraste.
- Señales a mostrar: procesos pares, similitud y diferencias de valor.
- Acción humana sugerida: comparar objeto, modalidad y cuantía.
- Frase para jurado: “Los comparables ayudan a contrastar, no deciden por el revisor”.
- Nota de demo: comparables ayudan a contextualizar, no deciden por el humano.

## CASE-005 — Cola territorial

- `sample_flag`: SAMPLE.
- Proceso: `SAMPLE-PROC-005`.
- Selector reproducible: filtro territorial Meta/Casanare.
- Entidad: Entidad Territorial Demo.
- Departamento: Meta/Casanare.
- Score aproximado o criterio: caso para mostrar segmentación territorial.
- Señales a mostrar: filtro territorial, score, confianza y cobertura.
- Acción humana sugerida: armar una muestra territorial de revisión.
- Frase para jurado: “La comparación territorial siempre debe mostrar volumen y confianza”.
- Nota de demo: comparar territorios exige mostrar volumen y soporte de datos.
