# Demo Casebook — ContratIA Abierta

## Casos reales para demo

Los siguientes casos provienen de datos abiertos reales de SECOP II (scope: Meta
y Casanare). Los scores de prioridad son calculados sobre datos reales, no
generados.

Para regenerar con datos actuales:

```bash
make product-pipeline PRODUCT_SOURCE_MODE=download
make validate-product
```

Luego ejecutar para ver casos frescos:

```bash
uv run --python 3.11 python - <<'PY'
import pandas as pd; from pathlib import Path
r = pd.read_parquet(Path("data/marts") / "ranking.parquet")
top5 = r.nlargest(5, "priority_score")
for _, row in top5.iterrows():
    print(f"{row['process_key']} | {row['entity_name']} | Score: {row['priority_score']}")
PY
```

---

## CASE-001 — Top score con señales múltiples (REAL)

- `process_key`: `CO1.REQ.9381735`
- `entidad`: Red Salud Casanare E.S.E.
- `departamento`: Casanare
- `score`: 53 | `confianza`: 85
- `razones principales`: monto atípico (427x mediana), duración atípica (6.86x mediana), señal débil de alineación plan vs ejecución
- `comparables`: 5 disponibles
- `PAA`: sin match directo
- **Qué mostrar en pantalla**: score con múltiples señales simultáneas, confianza alta, 5 comparables.
- **Qué acción humana sigue**: contrastar objeto contractual, cuantía y modalidad contra fuente SECOP. Verificar si el monto atípico se explica por naturaleza del contrato.
- **Frase para jurado**: "Tres señales simultáneas suben la prioridad, pero siempre requieren contraste humano con la fuente primaria".
- **⚠️ Recuerda**: esto es priorización de revisión, no prueba conducta indebida.

## CASE-002 — Monto extremadamente atípico (REAL)

- `process_key`: `CO1.REQ.8496410`
- `entidad`: Empresa de Servicios Públicos de Granada E.S.P.
- `departamento`: Meta
- `score`: 53 | `confianza`: 70
- `razones principales`: monto atípico (9230x mediana), duración atípica (7.00x), señal débil de alineación plan vs ejecución
- `comparables`: 5 disponibles
- `PAA`: sin match directo
- **Qué mostrar en pantalla**: monto extremadamente atípico con confianza media, 5 comparables.
- **Qué acción humana sigue**: revisar si el monto extremo es por tipo de contrato (obra, concesión) o si requiere revisión adicional de adjudicación.
- **Frase para jurado**: "Montos extremos frente a pares suben la prioridad; el revisor decide si el tipo de contrato explica la diferencia".
- **⚠️ Recuerda**: esto es priorización de revisión, no prueba conducta indebida.

## CASE-003 — Entidad municipal con PAA fuerte (REAL)

- `process_key`: Top match con `paa_match_status=strong` (filtrar en ranking).
- `entidad`: variable según datos.
- `departamento`: Meta o Casanare.
- `selector reproducible`: `ranking[ranking["paa_match_status"] == "strong"].nlargest(1, "paa_match_confidence")`.
- **Qué mostrar en pantalla**: item PAA asociado, similitud semántica, confianza del match, comparación plan-vs-ejecución.
- **Qué acción humana sigue**: revisar coherencia entre el item planeado en PAA y el proceso contractual ejecutado.
- **Frase para jurado**: "El match PAA aporta trazabilidad de planeación; no es una conclusión, es evidencia para el revisor".
- **⚠️ Recuerda**: el PAA visible es contexto de planeación, no inferencia acusatoria.

## CASE-004 — Confianza máxima (100/100) con score moderado (REAL)

- `process_key`: `CO1.REQ.9589534`
- `entidad`: Empresa Social del Estado del Departamento del Meta E.S.E.
- `departamento`: Meta
- `score`: 15 | `confianza`: 100
- `razones principales`: sin señales fuertes visibles, todos los datos presentes.
- `comparables`: 5 disponibles
- `PAA`: sin match
- **Qué mostrar en pantalla**: confianza perfecta con score bajo — el sistema dice "datos completos, no hay señales de prioridad urgente".
- **Qué acción humana sigue**: no escalar. Confianza alta y score bajo = proceso con datos completos que no presenta atipicidades. Ideal para mostrar que el sistema también dice "no revisar".
- **Frase para jurado**: "Confianza 100 y score 15: el sistema prioriza bien. Datos completos sin señales de atipicidad; no todo es alerta".
- **⚠️ Recuerda**: mostrar que el sistema también sabe callarse es tan importante como mostrar que prioriza.

## CASE-005 — Cola territorial Meta (REAL)

- `selector reproducible`: `ranking[ranking["department"] == "Meta"].nlargest(1, "priority_score")`.
- `entidades destacadas en Meta`: Alcaldía de Aguazul, CACOM-2, SUBRECURSOS FONAM, Empresas Públicas Granada, ICBF Regional Meta.
- `volumen`: 3,527 procesos totales en Meta y Casanare.
- **Qué mostrar en pantalla**: filtro departamental, distribución de scores, cobertura PAA por departamento.
- **Qué acción humana sigue**: armar una muestra territorial de revisión priorizada, comparar Meta vs Casanare en score medio y confianza media.
- **Frase para jurado**: "La comparación territorial exige mostrar volumen y confianza, no solo score. Territorios con menos datos pueden tener métricas menos estables".
- **⚠️ Recuerda**: `docs/fairness_territorial.md` explica los límites de comparación entre departamentos.

---

## Datos de esta corrida

- **Fuente**: SECOP II Procesos de Contratación (`p6dx-8zbt`) + SECOP Integrado (`rpmr-utcd`) + PAA (`9sue-ezhx`) + control fiscal (`wasc-xi4h`).
- **Alcance**: Meta y Casanare (demo scope).
- **Total ranking**: 3,527 procesos puntuados.
- **PAA strong matches**: 139 procesos con match de planeación fuerte.
- **Comparables**: 17,605 pares proceso-proceso.
- **Score medio**: 8.4 | **Score máximo**: 53 | **Confianza media**: 75.
- **Generado**: 2026-05-27 con `PRODUCT_SOURCE_MODE=download`.

La distribución de scores con datos de solo dos departamentos es naturalmente
baja en scores extremos. Con el dataset nacional completo se esperan scores más
altos y distribuciones más amplias.
