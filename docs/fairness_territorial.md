# Fairness Territorial

## Propósito del análisis

Evaluar si la priorización de revisión humana presenta diferencias territoriales que
puedan explicarse por cobertura, calidad documental o volumen de datos. El objetivo no
es igualar artificialmente scores, sino hacer visibles límites y soporte de datos.

## Variables de segmentación

- Departamento.
- Modalidad.
- Entidad.
- Monto o valor base.

## Métricas

- Proporción de alertas altas por departamento.
- Score promedio.
- Confianza promedio.
- Cobertura PAA.
- Procesos sin comparables.
- Volumen total de procesos por segmento.

## Riesgos de sesgo

- Subregistro o publicación incompleta.
- Diferencias de calidad documental entre entidades.
- Entidades con menos datos históricos.
- Modalidades difíciles de comparar.
- Departamentos con bajo volumen y comparables escasos.

## Resultados

Pendientes de cálculo con base local validada. No se fabrican métricas territoriales.

## Comandos para calcular métricas

Con servicios y PostgreSQL disponibles:

```bash
DATABASE_URL=postgresql://contratia:contratia@localhost:55432/contratia \
uv run --python 3.11 python - <<'PY'
import os
import psycopg
from psycopg.rows import dict_row

sql = """
SELECT department,
       count(*) AS processes,
       avg(priority_score)::float AS avg_priority_score,
       avg(confidence_score)::float AS avg_confidence_score,
       avg((priority_score >= 70)::int)::float AS high_priority_share,
       avg((process_reference IS NOT NULL)::int)::float AS process_reference_coverage
FROM v_ranking_processes
GROUP BY department
ORDER BY processes DESC;
"""

with psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row) as conn:
    with conn.cursor() as cur:
        cur.execute(sql)
        for row in cur.fetchall():
            print(dict(row))
PY
```

Para cobertura PAA y comparables, cruzar `v_plan_vs_execution` y
`semantic_comparable` por `process_id` y agrupar por departamento/modalidad.

## Política de presentación

Toda vista territorial debe mostrar volumen, score y confianza. Un territorio con score
alto y confianza baja debe presentarse como candidato a validación de datos, no como
conclusión.
