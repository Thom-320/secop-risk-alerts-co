# AGENTS.md

## Convenciones del proyecto

- Lenguaje de producto: usar siempre **alerta**, **priorización de revisión**, **score de prioridad** y **revisión humana**.
- Nunca afirmar corrupción, fraude o responsabilidad individual.
- El MVP opera sobre alcance fijo:
  - 2025-2026
  - Overview nacional agregado
  - Detalle demo en Meta y Casanare
- La tabla principal sale de `p6dx-8zbt`.
- `rpmr-utcd` solo enriquece con enlaces de alta confianza.
- `9sue-ezhx` siempre es visible, pero su entrada al score depende de compuerta.
- `wasc-xi4h` es contexto visible y no entra al score.
- Los joins deben documentar supuestos, cobertura, cardinalidad y tasas de match.
- Si un dato no es verificable, debe quedar marcado como limitación.
- `confidence_score` es una salida visible del MVP y no una heuristica interna escondida.

## Stack base

- Python 3.11
- DuckDB + Parquet como columna vertebral
- Polars para ETL y tablas intermedias
- Pandas solo para compatibilidad puntual con scikit-learn o Streamlit
- Streamlit para demo
- FastAPI para endpoints del producto

## Comandos de validación

```bash
uv sync --python 3.11 --extra dev
uv run --python 3.11 python -m src.extract.secop_api
uv run --python 3.11 python -m src.transform.build_process_master
uv run --python 3.11 python -m src.scoring.score_processes
uv run --python 3.11 pytest
uv run --python 3.11 ruff check .
uv run --python 3.11 streamlit run src/app/streamlit_app.py
uv run --python 3.11 uvicorn src.api.main:app --reload
```

## Reglas de datos

- No inventar columnas.
- No asumir joins 1 a 1 sin comprobarlos.
- Mantener `id_del_proceso` como llave principal de la tabla base.
- Tratar `procesos_relacionados` del PAA como ancla de alta precision cuando exista, no como backbone universal del join.
- No congelar pesos del score ni meter el PAA al score sin pasar las compuertas de validacion.
