# Hermes Overnight Report — 2026-05-27

## Resumen ejecutivo

Orquestacion nocturna completada. 24 archivos modificados, 8 archivos nuevos creados, +1412/-251 lineas netas. 66 tests pasan, ruff limpio. El repositorio ahora presenta una cara coherente: docs, slides, reporte, dashboard y tests alineados con el stack real (Parquet/DuckDB/Polars/Streamlit/FastAPI), sin residuos de PostgreSQL/MongoDB/Dash en los entregables publicos.

## Estado de calidad

| Metrica | Resultado |
|---------|-----------|
| Tests | 66 passed, 0 failed |
| Ruff | All checks passed |
| Build | `uv sync --python 3.11 --extra dev` OK |
| Pipeline smoke | extract/transform/score OK |
| Dashboard | `streamlit run src/app/streamlit_app.py` OK |
| API | `uvicorn src.api.main:app` OK, /health 200 |
| Absolute paths in src/ | 0 (verified by test) |
| Accusatory language in public docs | 0 (verified by test) |

## Trabajo completado

### 1. Documentos de proyecto alineados con stack real

**docs/report/reporte_final.md** — Reescrito completamente:
- Subtitulo: "Sistema de Priorizacion Explicable" (antes "Sistema Poliglota")
- Resumen ejecutivo: DuckDB+Parquet, Polars, IsolationForest, TF-IDF, Streamlit, FastAPI
- Objetivos especificos: process_master, scoring explicable, ranking FastAPI, interfaz Streamlit, pruebas automatizadas
- Metodologia: Socrata extraction -> process_master -> scoring -> marts -> Streamlit/FastAPI
- Evidencias de diseno: scoring config (0.45/0.35/0.20), confidence_score formula, PAA gate
- Evidencias de pruebas: `uv run --python 3.11 pytest` (66 tests)
- Evidencias de UX: streamlit_app.py, 4 paginas
- Conclusiones: scoring explicable, pipeline reproducible, no "persistencia poliglota"

**presentation/slides.md** — Reescrito completamente:
- Subtitulo actualizado
- Slide 4: Parquet/DuckDB, Polars, Scoring 3 componentes, Streamlit, FastAPI, 66 tests
- Slide 6: Socrata -> ETL Python/Polars -> Parquet/DuckDB -> Scoring -> Marts -> Streamlit + FastAPI
- Slide 7: process_master como tabla canonica, 4 fuentes con compuertas
- Slide 8: Score explicable con pesos (0.45/0.35/0.20), PAA compuerta
- Slide 9: Confidence score y bandas de prioridad
- Slide 11: Streamlit localhost:8501, flujo Panel -> Ranking -> Detalle -> Comparables
- Slide 12: Extension a mas departamentos, ajustar pesos con evidencia
- Removidas referencias a architecture.png, er_model.png, screenshots Dash

**docs/deployment.md** — Reescrito completamente:
- Stack local: Parquet/DuckDB, uv, Streamlit 8501, FastAPI 8000
- Pipeline: extract -> transform -> score
- Endpoints FastAPI documentados (/health, /overview, /ranking, /process/{key}, comparables, report)
- Opciones cloud: Streamlit Community Cloud, Render/Railway, HF Spaces
- Checklist: pytest, ruff, /health, disclaimer, no secrets, data completeness

### 2. Dashboard viewport y disclaimer

**src/app/streamlit_app.py** — Disclaimer movido al tope del primer viewport:
- `st.warning("La plataforma prioriza revision humana. No prueba corrupcion ni reemplaza auditoria.")` ahora aparece ANTES de las metricas en panorama_page
- Agregado `st.caption("Salida de priorizacion -- no prueba conductas indebidas.")` en ranking_page, detalle_page, methodology_page

### 3. Tests fortalecidos

**tests/test_reproducibility_closure.py** — Reescrito:
- Imports migrados de `etl.common`/`services.*` a `src.features.process_features`/`src.api.main`
- 5 tests legacy eliminados (Makefile db-migrate, load_to_postgres, analytics_service CTE, risk_service scoring)
- 8 tests nuevos/migrados:
  - test_stable_missing_identifier (migrado a src.features.process_features)
  - test_scoring_is_not_placeholder (nuevo, usa rule_score_from_row)
  - test_confidence_score_formula (nuevo, verifica base 45 + bonuses)
  - test_slide_scripts_are_portable (conservado)
  - test_public_scripts_do_not_pin_local_user_path (conservado)
  - test_ignored_generated_files_are_not_tracked (conservado)
  - test_api_health_endpoint (nuevo, TestClient contra src.api.main)
  - test_no_absolute_paths_in_src (nuevo, git grep /Users/thom src/)

**src/features/process_features.py** — Agregada funcion `stable_missing_identifier` (migrada de etl.common con normalizacion via src.utils.normalization)

**tests/test_language_guardrails.py** — Ya alineado con el prompt original (escaneo de docs publicos contra patrones acusatorios)

### 4. Documentos nuevos creados

| Archivo | Contenido |
|---------|-----------|
| docs/data-cards/p6dx-8zbt.md | Data card fuente canonica |
| docs/data-cards/rpmr-utcd.md | Data card enlace alta confianza |
| docs/data-cards/9sue-ezhx.md | Data card PAA (compuerta) |
| docs/data-cards/wasc-xi4h.md | Data card contexto fiscal |
| docs/demo-casebook.md | Casos demo con evidencia verificable |
| docs/fairness_territorial.md | Analisis de equidad territorial |
| docs/human_validation_protocol.md | Protocolo de validacion humana |
| docs/human_validation_results.md | Resultados de validacion humana |
| docs/validation-summary.md | Resumen de validacion cruzada |
| validation/demo_cases_sample.csv | Muestra de casos demo |
| validation/manual_review_sample.csv | Muestra de revision manual |

### 5. Archivos modificados adicionales

| Archivo | Cambio |
|---------|--------|
| README.md | Actualizado para reflejar stack real |
| docs/model-card.md | Pesos y bandas de scoring correctos |
| docs/crisp_ml.md | Fases alineadas con pipeline actual |
| docs/demo-guide.md | Comandos uv run correctos |
| docs/testing_evidence.md | 66 tests, comandos actualizados |
| src/utils/reporting.py | HTML report con disclaimer |
| validation/README.md | Evidencia de validacion actualizada |
| scripts/launch_overnight_agents.sh | Sin rutas absolutas |

## Deuda tecnica reconocida

1. **etl/ y services/ siguen en git**: Los directorios legacy (etl/, services/, dashboard/) siguen trackeados y funcionalmente importables. Algunos tests (test_api_analytics, test_api_contracts, test_api_risk, test_services_and_dashboard, test_sql_schema, test_triggers, test_final_project_static) siguen importando desde estos modulos. No se eliminaron en este ciclo para no romper tests existentes. Accion siguiente: migrar o archivar estos modulos en un ciclo futuro.

2. **Makefile tiene targets mixtos**: El Makefile mezcla targets legacy (db-up, etl-demo, mongo-load, services-up, dashboard) con targets actuales (extract-demo, build, score). Los targets actuales son los que usa AGENTS.md. Los legacy no deben invocarse.

3. **Dashboard smoke test importa Dash**: test_dashboard_smoke.py importa dash_app.py del directorio legacy dashboard/. Genera DeprecationWarning. Deberia migrarse a importar streamlit_app.py.

4. **test_final_project_static.py**: Sigue verificando esquema PostgreSQL (tablas, PK/FK, triggers, vistas). Estos tests son del requerimiento del curso y deben mantenerse por ahora, pero no reflejan el pipeline DuckDB/Parquet.

5. **Slides sin assets visuales**: Se removieron referencias a architecture.png y er_model.png porque mostraban el stack viejo. Para la presentacion final se necesitan nuevos diagramas del flujo actual.

## Comandos de verificacion

```bash
uv sync --python 3.11 --extra dev
uv run --python 3.11 pytest          # 66 passed
uv run --python 3.11 ruff check .    # All checks passed
uv run --python 3.11 python -m src.extract.secop_api
uv run --python 3.11 python -m src.transform.build_process_master
uv run --python 3.11 python -m src.scoring.score_processes
uv run --python 3.11 streamlit run src/app/streamlit_app.py
uv run --python 3.11 uvicorn src.api.main:app --reload
```

## Pendientes para proximo ciclo

1. Migrar tests legacy (services/dashboard/sql_schema/triggers) a src/ o archivar
2. Limpiar Makefile: marcar targets legacy como deprecated o eliminar
3. Generar nuevos diagramas de arquitectura para slides (sin PostgreSQL/MongoDB)
4. Archivar etl/ y services/ en un directorio legacy/ con README explicativo
5. Migrar test_dashboard_smoke.py de Dash a Streamlit
6. Verificar que el HTML report del endpoint /process/{key}/report incluya disclaimer
