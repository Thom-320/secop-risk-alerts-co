# AGENTS.md

## Convenciones del proyecto

- Lenguaje de producto: usar siempre **alerta de riesgo**, **priorización de revisión** y **revisión humana**.
- Nunca afirmar corrupción, fraude o responsabilidad individual.
- El MVP opera sobre alcance fijo:
  - 2025-2026
  - Tres subredes de salud en Bogotá
- La tabla principal sale de `jbjy-vk9h`.
- Los joins deben documentar supuestos y tasas de match.
- Si un dato no es verificable, debe quedar marcado como limitación.

## Stack base

- Python 3.11
- DuckDB + Parquet como columna vertebral
- Pandas solo para limpieza y compatibilidad puntual
- Streamlit para demo

## Comandos de validación

```bash
uv sync --python 3.11 --extra dev
uv run --python 3.11 python -m src.extract.secop_api
uv run --python 3.11 python -m src.transform.build_base_contracts
uv run --python 3.11 python -m src.scoring.score_contracts
uv run --python 3.11 pytest
uv run --python 3.11 ruff check .
uv run --python 3.11 streamlit run src/app/streamlit_app.py
```

## Reglas de datos

- No inventar columnas.
- No asumir joins 1 a 1 sin comprobarlos.
- Mantener `id_contrato` como llave principal de la tabla base.
- Tratar `cb9c-h8sn` como fuente de trazabilidad de adiciones y modificaciones, no como verdad completa de monto.

