# Reproducibility

```bash
uv sync --python 3.11 --extra dev
uv run --python 3.11 python -m src.extract.secop_api
uv run --python 3.11 python -m src.transform.build_process_master
uv run --python 3.11 python -m src.scoring.score_processes
uv run --python 3.11 pytest
```

Para endurecer PAA en modo demo:

```bash
EXTRACT_SCOPE=demo EXTRACT_ONLY=paa_detail uv run --python 3.11 python -m src.extract.secop_api
```
