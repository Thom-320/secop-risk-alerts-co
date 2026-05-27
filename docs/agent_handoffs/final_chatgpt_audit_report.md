# Final Codex Audit Report — secop-risk-alerts-co

Fecha: 2026-05-27 10:30 COT.
Agente: Codex (ChatGPT Pro $100/mo).
Scope: Auditoría final de cierre del repositorio para entrega ID + concurso.

## Comandos ejecutados

```bash
git status --short --branch
find . -maxdepth 3 -type f | sort
make lint
make test
make product-pipeline PRODUCT_SOURCE_MODE=sample
make validate-product
make academic-demo
make validate-academic
make validate-final
```

## Resultados

| Comando | Resultado | Detalle |
| --- | --- | --- |
| `make lint` | ✅ PASS | All checks passed (ruff) |
| `make test` | ✅ PASS | 66 passed, 0 failed, 2 deprecation warnings (dash_table) |
| `make product-pipeline` | ✅ PASS | 19625 procesos, 420 ranking, 2080 comparables |
| `make validate-product` | ✅ PASS | `ok=true`, 0 blockers, 0 forbidden language |
| `make academic-demo` | ✅ PASS | PostgreSQL+MongoDB+servicios+Dash up |
| `make validate-academic` | ✅ PASS | `ok=true`, 33 public objects, 13999 rows, APIs 200 |
| `make validate-final` | ✅ PASS | Product + academic both ok=true |

## Archivos modificados en esta auditoría

1. `presentation/slides.md` — Corregidos pesos de scoring (de 3 componentes genéricos a 6 señales reales).
2. `docs/testing_evidence.md` — Actualizado con resultados frescos de esta ronda.

## Archivos creados en rondas anteriores (untracked, ready for commit)

- `docs/product_route.md`
- `docs/academic_route.md`
- `docs/contest_submission_checklist.md`
- `docs/class_submission_checklist.md`
- `docs/demo-casebook.md`
- `docs/deployment.md`
- `docs/fairness_territorial.md`
- `docs/human_validation_protocol.md`
- `docs/human_validation_results.md`
- `docs/validation-summary.md`
- `docs/data-cards/secop-ii-procesos.md`
- `docs/data-cards/secop-integrado.md`
- `docs/data-cards/paa-detalle.md`
- `docs/data-cards/control-fiscal.md`
- `docs/audit/final_repo_audit.md`
- `docs/agent_handoffs/final_chatgpt_audit_report.md`
- `etl/validate_product.py`
- `src/evaluation/human_validation_summary.py`
- `src/scoring/semantic_similarity.py`
- `validation/demo_cases_sample.csv`
- `validation/manual_review_sample.csv`

## Estado de las rutas

### Product route (ContratIA Abierta)

| Item | Estado |
| --- | --- |
| Pipeline | `make product-pipeline` ✅ |
| Validación | `make validate-product` → ok=true ✅ |
| UI/API | `make product-ui` / `make product-api` ✅ |
| README | Ruta dual clara ✅ |
| Model card | 19 secciones completas ✅ |
| Data cards | 4 datasets documentados ✅ |
| Demo guide | Flujo 2 y 5 minutos ✅ |
| Demo casebook | 5 casos SAMPLE ✅ |
| Language guard | Sin violaciones de lenguaje prohibido ✅ |
| CSV export | Botón en UI ✅ |

### Academic route (Transparencia360)

| Item | Estado |
| --- | --- |
| PostgreSQL | 33 objetos públicos, 13999 procesos ✅ |
| MongoDB | 5/5 colecciones con documentos ✅ |
| Microservicios | contracts, risk, analytics → 200 ✅ |
| Dash | Dashboard funcional ✅ |
| SQL avanzado | Triggers, vistas, CTE recursiva, window functions, transactions ✅ |
| Seguridad | `007_security_roles.sql` en schema ✅ |
| `PUBLIC_READ_ONLY` | Bloquea POST mutables ✅ |
| Scoring | Determinístico, 6 componentes con pesos documentados ✅ |
| Validación | `make validate-academic` → ok=true ✅ |

## Pendientes humanos (no automatizables)

1. **Encuesta UX con 5 usuarios reales** — `docs/usability_results.md` tiene tabla vacía.
2. **Validación manual de 40-100 procesos** — Protocolo listo en `docs/human_validation_protocol.md`.
3. **Nombres, roles, director/docente, fecha exacta** — Placeholder `[COMPLETAR POR EL EQUIPO]` en reportes.
4. **URL pública de despliegue** — `docs/deployment.md` describe recomendaciones sin implementar.
5. **Registro en "Usos"** — No hecho.

## Bloqueadores resueltos

- Ninguno. Todas las validaciones automáticas pasan.

## Top 5 mejoras restantes (ordenadas por impacto)

1. Encuesta UX real con 5 usuarios — cambia el claim de "demo" a "validado con usuarios".
2. Validación humana real de 40-100 procesos — da métricas de utilidad operativa.
3. Completar datos de equipo y fecha en reportes — requisito de entrega.
4. Despliegue público read-only — visibilidad para concurso.
5. Evaluar `sentence-transformers` como mejora opcional documentada (no como requisito).

## Notas

- No se fabricaron resultados UX ni humanos.
- No se usó lenguaje acusatorio en ninguna superficie pública.
- El repositorio está limpio de `.DS_Store`, `__pycache__`, `.venv` y `.pytest_cache`.
- Los archivos overnight (`docs/agent_handoffs/`) son artefactos de auditoría, no de entrega.
- Las diapositivas (`slides/`, `presentation/`) están alineadas con la evidencia real (66 pruebas, 6 componentes de scoring, 33 objetos PostgreSQL).
