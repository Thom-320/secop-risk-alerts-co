# Codex Final Contest Readiness Report

Fecha: 2026-05-27 (cierre final de contest readiness).

## Commit base

`dd50cd2` — Update overnight agent status.

## Archivos modificados (esta ronda)

| Archivo | Cambio |
|---|---|
| `src/scoring/semantic_similarity.py` | Añadido `SentenceTransformerProvider` con `CONTRATIA_USE_TRANSFORMER_EMBEDDINGS=1`. Fallback automático a TF-IDF si el modelo no carga. |
| `tests/test_scoring.py` | +4 tests para provider transformer (graceful fallback, env var, empty texts, import sin modelo). |
| `tests/test_final_project_static.py` | Añadidos `ethics-note.md` y `reproducibility.md` a required docs. Nuevo `test_contest_critical_docs_are_non_empty`. |
| `docs/model-card.md` | Actualizada sección 15: SentenceTransformer como opcional con fallback, sin claim inflado. |
| `docs/demo-casebook.md` | Añadido comando Python reproducible para generar casos reales desde ranking.parquet. |
| `docs/demo-guide.md` | Actualizada advertencia sobre embeddings: opcional con fallback, no vender sin medir. |
| `README.md` | Actualizada sección de scoring: SentenceTransformer opcional con `CONTRATIA_USE_TRANSFORMER_EMBEDDINGS=1`. |

## Comandos ejecutados

```bash
git clone https://github.com/Thom-320/secop-risk-alerts-co.git
make lint                          # All checks passed
make test                          # 71 passed
make demo-full                     # 13,999 PG rows, 33 tables, 5 Mongo collections, 4 services up
make validate-final                # ok=true, APIs 200, 36 docs presentes, 0 blockers
make product-pipeline              # 19,625 extract, 420 ranking rows (sample mode)
make validate-product              # ok=true, mode=product-lean
```

## Resultados

| Comando | Resultado |
|---|---|
| `make lint` | All checks passed. |
| `make test` | **71 passed**, 0 failed. (+5 tests esta ronda) |
| `make product-pipeline` | 19,625 extract → 420 ranking rows (sample mode). |
| `make validate-product` | `ok=true`, `mode=product-lean`, 420 ranking rows, 0 forbidden claims. |
| `make demo-full` | PostgreSQL 33 objetos, 13,999 procurement_process. MongoDB 5 colecciones. 4 microservicios up. |
| `make validate-final` | `ok=true`, APIs 200, 36 docs presentes, integration_blockers=[]. |

## Qué quedó listo

### P0 — Cerrado

1. **Dashboard export**: CSV descargable del ranking con filtro de score. HTML descargable del proceso detalle con proceso, entidad, score, confianza, razones, PAA, comparables, limitaciones y disclaimer ético. Verificado por `test_dash_has_downloadable_evidence_exports`.

2. **Demo casebook**: `docs/demo-casebook.md` con 5 casos SAMPLE y comando Python reproducible para generar casos reales desde `ranking.parquet`. Cada caso incluye selector reproducible, entidad, departamento, señales, acción humana sugerida y frase exacta para jurado.

3. **Demo guide**: `docs/demo-guide.md` con recorrido 2 min, recorrido 5 min, checklist pre-presentación, qué hacer si falla Docker, qué mostrar sí o sí, qué NO decir ante jurado.

4. **Model card**: `docs/model-card.md` con 19 secciones: objetivo, usuarios, usos permitidos/prohibidos, datasets, features, componentes del score, fórmula de `priority_score`, `confidence_score`, métricas, limitaciones, sesgos, mantenimiento.

5. **Data cards**: `docs/data-cards/` con 4 fichas (`secop-ii-procesos.md`, `secop-integrado.md`, `paa-detalle.md`, `control-fiscal.md`), cada una con ID, URL oficial, propósito, campos usados/descartados, riesgos de calidad, normalizaciones, uso en scoring, limitaciones, licencia.

6. **Ethics note**: `docs/ethics-note.md` con riesgos de daño reputacional, falsos positivos/negativos, sesgo territorial, sesgo por entidades pequeñas, uso responsable, disclaimers, interpretación de alertas, decisión final.

7. **Human validation**: Protocolo en `docs/human_validation_protocol.md` (40-100 casos, mezcla top/bajo score, rúbrica, dos revisores, métricas). Resultados en `docs/human_validation_results.md` marcados PENDIENTE. Plantilla en `validation/manual_review_sample.csv` con `sample_flag=SAMPLE` y `is_real_review=FALSE`.

8. **Validation summary**: `docs/validation-summary.md` separa validado automáticamente, validado manualmente, pendiente, bloqueadores, comandos de evidencia.

9. **Fairness territorial**: `docs/fairness_territorial.md` explica sesgo por entidades pequeñas, `confidence_score`, métricas por departamento, comandos SQL para calcular.

10. **Deployment doc**: `docs/deployment.md` con modo local, opciones cloud, variables de entorno, puertos, modo read-only, endpoints protegidos, `PUBLIC_READ_ONLY=true`.

11. **IA semántica honesta**: `src/scoring/semantic_similarity.py` con protocolo `SimilarityProvider`, `TfidfSimilarityProvider` (default CI), `SentenceTransformerProvider` opcional vía `CONTRATIA_USE_TRANSFORMER_EMBEDDINGS=1`. Fallback automático a TF-IDF. Modelo: `paraphrase-multilingual-MiniLM-L12-v2`. Documentado en model-card y README sin claims inflados.

12. **CI y validadores**: `test_final_project_static.py` verifica existencia de todos los docs requeridos (ethics-note.md, reproducibility.md, model-card.md, data-cards/*, demo-casebook.md, etc.) y no-emptiness de docs críticos. `test_scoring.py` cubre provider TF-IDF y graceful fallback del transformer.

13. **Seguridad**: `docs/security.md` documenta endpoints no públicos (`POST /reviews`, `POST /risk/recompute/{process_id}`). `deployment.md` advierte sobre `PUBLIC_READ_ONLY=true` para demos públicas.

14. **Slides**: `presentation/slides.md` limpio: no dice "detecta corrupción", no promete embeddings sin medir, incluye demo story. Verificado por `test_slide_sources_do_not_keep_stale_39_test_claim`.

### Product route (ContratIA Abierta)

- `make product-pipeline && make validate-product` reproducible.
- Dashboard con export CSV + HTML.
- Ranking con 420 filas demo.
- Streamlit/FastAPI como respaldo offline.

### Academic route (Transparencia360)

- `make demo-full && make validate-final` pasa con PostgreSQL, MongoDB, 3 microservicios, Dash.
- 33 objetos públicos, 13,999 filas procurement_process.
- 71 tests pasan.

## Qué sigue siendo tarea humana

- Encuesta UX con 5 usuarios reales (`docs/usability_results.md`).
- Validación humana de 40-100 procesos (`docs/human_validation_protocol.md`).
- Nombres, roles, director/docente, fecha exacta (`docs/report/reporte_final.md`).
- Despliegue público read-only (decisión + credenciales).
- Registro en "Usos" del portal datos.gov.co.
- Ejecutar `CONTRATIA_USE_TRANSFORMER_EMBEDDINGS=1` con modelo descargado y medir mejora sobre TF-IDF (si se quiere incluir en defensa).

No se fabricaron resultados UX, etiquetas humanas ni métricas no ejecutadas.

## Top 5 riesgos restantes

1. **Validación humana pendiente**: sin revisores reales, el protocolo es solo un documento. Impacto: contest jury puede penalizar.
2. **Encuesta UX pendiente**: sin 5 respuestas con `is_real_response=TRUE`, la sección UX es un placeholder honesto pero incompleto.
3. **Datos del equipo**: integrantes, roles, director/docente deben llenarse antes de entregar PDF final.
4. **Docker/OrbStack**: repetir `make demo-full && make validate-final` en la máquina de sustentación el mismo día. Los puertos alternos (55432, 27018) pueden chocar si hay otras instancias.
5. **SentenceTransformer opcional**: el proveedor está implementado pero no medido contra TF-IDF. Si se activa en demo, debe probarse primero que el modelo carga y que las métricas de similitud son razonables.
