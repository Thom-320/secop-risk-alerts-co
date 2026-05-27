# Demo Casebook — ContratIA Abierta

## Casos reales para demo (modo sample)

Los siguientes casos provienen de los datos generados en modo sample
(`PRODUCT_SOURCE_MODE=sample`). Los scores en modo sample son bajos porque los
fixtures no contienen la variabilidad real de contratos SECOP.

Para generar casos con datos abiertos reales:

```bash
make product-pipeline PRODUCT_SOURCE_MODE=download
make validate-product
```

Luego ejecutar el script de generación:

```bash
uv run --python 3.11 python - <<'PY'
import pandas as pd
from pathlib import Path

marts = Path("data/marts") if Path("data/marts").exists() else Path("data/sample/product_marts")
ranking = pd.read_parquet(marts / "ranking.parquet")
comparables = pd.read_parquet(marts / "comparables.parquet")

cols = ["process_key","entity_name","department","modality","base_price",
        "priority_score","confidence_score","paa_match_status",
        "semantic_comparable_count","reasons"]

print("=== Top 5 by priority_score ===")
top5 = ranking.nlargest(5, "priority_score")
for _, row in top5.iterrows():
    print(f"\n{row['process_key']} | {row['entity_name']} | {row['department']}")
    print(f"  Score: {row['priority_score']} | Conf: {row['confidence_score']}")
    print(f"  Modality: {row['modality']} | PAA: {row['paa_match_status']} | Comps: {row['semantic_comparable_count']}")
    print(f"  Reasons: {row['reasons']}")

print("\n=== PAA strong matches (if any) ===")
paa = ranking[ranking["paa_match_status"] == "strong"].nlargest(3, "paa_match_confidence")
for _, row in paa.iterrows():
    print(f"\n{row['process_key']} | PAA conf: {row['paa_match_confidence']}")

print("\n=== Score distribution ===")
print(ranking["priority_score"].describe())
print(f"High priority (>=70): {len(ranking[ranking['priority_score'] >= 70])}")
print(f"With comparables: {len(ranking[ranking['semantic_comparable_count'] > 0])}")
PY
```

---

## CASE-001 — Top score con comparables (sample)

- `sample_flag`: SAMPLE (datos generados, no SECOP real).
- Proceso: `CO1.REQ.10348855`.
- Entidad: Gobernación del Casanare.
- Departamento: Casanare.
- Score: 41 | Confianza: 70 | Comparables: 5.
- Señales a mostrar: score de prioridad relativo más alto, 5 comparables, duración atípica.
- Acción humana sugerida: abrir fuente SECOP, revisar objeto, cuantía y soporte documental.
- Frase para jurado: "Este caso ilustra cómo la herramienta ordena capacidad humana limitada con evidencia trazable".
- Nota de demo: los scores en sample mode son bajos porque los fixtures no contienen variabilidad real de contratos. Con `PRODUCT_SOURCE_MODE=download` los scores reflejan datos abiertos reales.

## CASE-002 — ICBF con confianza alta (sample)

- `sample_flag`: SAMPLE.
- Proceso: `CO1.REQ.10351469`.
- Entidad: ICBF Regional Meta.
- Departamento: Meta.
- Score: 37 | Confianza: 85 | Comparables: 5.
- Señales a mostrar: confianza alta (85) con score moderado, 5 comparables.
- Acción humana sugerida: revisar si el score refleja adecuadamente la prioridad operativa de este tipo de entidad.
- Frase para jurado: "Confianza alta con score moderado indica buen soporte de datos; el revisor decide si escala".
- Nota de demo: ICBF es una entidad nacional con presencia regional; útil para mostrar variedad institucional.

## CASE-003 — Monto atípico con duración (sample)

- `sample_flag`: SAMPLE.
- Proceso: `CO1.REQ.10388129`.
- Entidad: Alcaldía Municipio de Puerto López.
- Departamento: Meta.
- Score: 37 | Confianza: 70 | Comparables: 5.
- Señales a mostrar: monto atípico (2.00x mediana) y duración atípica (1.98x mediana).
- Acción humana sugerida: contrastar objeto contractual y modalidad con pares del mismo departamento.
- Frase para jurado: "Dos señales simultáneas de atipicidad suben la prioridad, pero siempre requieren contraste humano con la fuente".
- Nota de demo: las entidades municipales pequeñas pueden tener comparables menos estables; revisar `confidence_score` siempre.

## CASE-004 — Cola territorial Meta (sample)

- `sample_flag`: SAMPLE.
- Proceso: `CO1.REQ.10374235`.
- Entidad: DMORI.
- Departamento: Meta.
- Score: 38 | Confianza: 70 | Comparables: 5.
- Señales a mostrar: filtro departamental Meta, duración atípica, 5 comparables locales.
- Acción humana sugerida: armar una muestra territorial de revisión para Meta.
- Frase para jurado: "La comparación territorial siempre debe mostrar volumen y confianza, no solo score".
- Nota de demo: 420 procesos en Meta/Casanare en sample mode; el filtro territorial ayuda a segmentar revisiones.

## CASE-005 — Confianza baja vs score (sample)

- `sample_flag`: SAMPLE.
- Proceso: `CO1.REQ.10368194`.
- Entidad: varias entidades demo.
- Departamento: Meta/Casanare.
- Score: 29 | Confianza: 45.
- Señales a mostrar: score moderado con confianza baja, pocos comparables o datos insuficientes.
- Acción humana sugerida: validar calidad de datos antes de decidir si escala.
- Frase para jurado: "Score y confianza se leen juntos; confianza baja pide validar datos antes de cualquier acción".
- Nota de demo: usar este caso para mostrar que no todas las alertas son automáticas y que el sistema pide validación cuando los datos son insuficientes.

---

## Nota sobre sample mode vs datos reales

Los casos arriba usan datos generados (`PRODUCT_SOURCE_MODE=sample`). Los scores
son bajos (media 8.7, máximo 41) porque los fixtures no contienen la variabilidad
real de contratos SECOP (competencia, montos, modalidades diversas). Para la demo
de concurso se recomienda ejecutar:

```bash
make product-pipeline PRODUCT_SOURCE_MODE=download
make validate-product
```

Y regenerar los casos con el script Python de arriba. Los scores con datos reales
típicamente tienen distribución más amplia (0-100) con señales de competencia,
valor relativo, modalidad y PAA reales.
