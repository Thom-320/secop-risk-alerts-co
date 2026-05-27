# Codex Final Contest Readiness Report

Fecha: 2026-05-27 (ronda de cierre final).

## Commit base

`dd50cd2` — Update overnight agent status.

## Archivos modificados (esta ronda)

| Archivo | Cambio |
|---|---|
| `src/extract/secop_api.py` | `write_sample_product_sources()` prefiere parquet generado (20k) sobre fixture CSV (3). Dedup `id_del_proceso`. Fallback `fecha_de_publicacion_del`. |
| `.gitignore` | Corregido patrón que chocaba con archivos overnight. Agregado `.streamlit/`. |
| `docs/testing_evidence.md` | Actualizado con resultados frescos (ranking 420, 13,999 filas PG). |
| `docs/agent_handoffs/final_chatgpt_audit_report.md` | Actualizado con resultados de segunda ronda. |
| `docs/audit/final_repo_audit.md` | Creado con estado final del repo. |
| `docs/agent_handoffs/codex_final_contest_readiness_report.md` | Este archivo, actualizado. |

## Comandos ejecutados

```bash
make lint
make test
make product-pipeline
make validate-product
make demo-full
make validate-final
```

## Resultados

| Comando | Resultado |
|---|---|
| `make lint` | All checks passed. |
| `make test` | 66 passed, 0 failed. |
| `make product-pipeline` | 19,625 extract → 420 ranking rows (sample mode). |
| `make validate-product` | `ok=true`, `mode=product-lean`, 420 ranking rows, 0 forbidden claims. |
| `make demo-full` | PostgreSQL 33 objetos, 13,999 procurement_process. MongoDB 5 colecciones. |
| `make validate-final` | `ok=true`, APIs 200, 36 docs presentes. |

## Qué quedó listo

- **Product route (ContratIA Abierta)**: `make product-pipeline && make validate-product` reproducible. Dashboard con export CSV + HTML. Ranking con 420 filas demo.
- **Academic route (Transparencia360)**: `make demo-full && make validate-final` pasa con PostgreSQL, MongoDB, 3 microservicios, Dash. 33 objetos públicos, 13,999 filas.
- **Documentación**: model card (19 secciones), data cards (4), demo guide (2+5 min), demo casebook (5 SAMPLE), human validation protocol, ethics note, fairness territorial, deployment, validation summary, product/academic routes, contest/class checklists.
- **Pruebas**: 66 tests cubren docs requeridos, schema SQL, triggers, views, scoring, API, dashboard, language guardrails, sample markers, slides consistency.
- **Seguridad**: `PUBLIC_READ_ONLY=true` bloquea POST mutables. Docs de endpoints protegidos en security.md y deployment.md.
- **Ética**: Todas las superficies públicas usan lenguaje de priorización/revisión humana. Prohibido "detectar corrupción", "fraude probado", etc. Verificado por `test_language_guardrails.py` y `validate_product.py`.
- **Semántica**: TF-IDF honesto. Embeddings neuronales documentados como opt-in futuro, no como claim validado.

## Qué sigue siendo tarea humana

- Encuesta UX con 5 usuarios reales (`docs/usability_results.md`).
- Validación humana de 40-100 procesos (`docs/human_validation_protocol.md`).
- Nombres, roles, director/docente, fecha exacta (`docs/report/reporte_final.md`).
- Despliegue público read-only (decisión + credenciales).
- Registro en "Usos" del portal datos.gov.co.

No se fabricaron resultados UX, etiquetas humanas ni métricas no ejecutadas.

## Top 5 riesgos restantes

1. **Validación humana pendiente**: sin revisores reales, el protocolo es solo un documento. Impacto: contest jury puede penalizar.
2. **Encuesta UX pendiente**: sin 5 respuestas con `is_real_response=TRUE`, la sección UX es un placeholder honesto pero incompleto.
3. **Datos del equipo**: integrantes, roles, director/docente deben llenarse antes de entregar PDF final.
4. **Docker/OrbStack**: repetir `make demo-full && make validate-final` en la máquina de sustentación el mismo día.
5. **IA semántica avanzada**: no prometer embeddings si no se ejecutan y miden. La ruta validada es TF-IDF.
