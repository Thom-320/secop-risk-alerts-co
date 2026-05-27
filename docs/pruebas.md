# Pruebas

Cobertura esperada:

- pruebas unitarias de features y scoring;
- pruebas de manifest y chunks;
- pruebas estaticas de SQL, constraints, triggers, CTE y window functions;
- pruebas de endpoints FastAPI;
- smoke test de Dash;
- guardrails de lenguaje;
- validacion final con PostgreSQL, MongoDB y APIs.

Comandos:

```bash
make test
make lint
make validate-final
```
