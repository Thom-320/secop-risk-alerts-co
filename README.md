# secop-risk-alerts-co

MVP inicial del proyecto **Sistema de Alertas Priorizadas de Riesgo Contractual** para el concurso **Datos al Ecosistema 2026: IA para Colombia**.

## Objetivo

Responder de forma práctica y explicable a la pregunta:

**¿Qué contratos y qué proveedores debería revisar primero esta semana una veeduría ciudadana u oficina de control interno, y por qué?**

El sistema **no detecta corrupción** ni hace afirmaciones judiciales. Produce **alertas de riesgo** para priorizar revisión humana.

## Usuario principal

- Veedurías ciudadanas
- Oficinas de control interno
- Periodistas de datos

## Alcance congelado del MVP

- Ventana temporal: **2025-2026**
- Cobertura: **3 entidades del sector salud en Bogotá**
  - SUBRED INTEGRADA DE SERVICIOS DE SALUD NORTE E.S.E. (OFICIAL)
  - SUBRED INTEGRADA DE SERVICIOS DE SALUD SUR E.S.E.**
  - SUBRED INTEGRADA DE SERVICIOS DE SALUD SUR OCCIDENTE ESE.

## Datasets usados

- `jbjy-vk9h`: SECOP II - Contratos Electrónicos
- `p6dx-8zbt`: SECOP II - Procesos de Contratación
- `cb9c-h8sn`: SECOP II - Adiciones
- `gra4-pcp2`: SECOP II - Ubicaciones ejecución contratos
- `wmwy-ixwz`: Vista Diagnóstico PIDA anticorrupción
- `rpmr-utcd`: SECOP Integrado, solo para QA y benchmark auxiliar

## Arquitectura simple

1. Extracción oficial desde Socrata con `httpx`
2. Snapshots crudos en Parquet dentro de `data/raw/`
3. Tabla base canónica a nivel contrato en `data/interim/base_contracts.parquet`
4. Features y score interpretable + anomalía en `data/marts/`
5. Visualización Streamlit en `src/app/streamlit_app.py`

## Instalación

```bash
uv sync --python 3.11 --extra dev
cp .env.example .env
```

`APP_TOKEN_SOCRATA` es opcional, pero recomendado para mayor estabilidad del API.

## Cómo correr el pipeline

```bash
uv run --python 3.11 python -m src.extract.secop_api
uv run --python 3.11 python -m src.transform.build_base_contracts
uv run --python 3.11 python -m src.scoring.score_contracts
```

## Cómo correr la app

```bash
uv run --python 3.11 streamlit run src/app/streamlit_app.py
```

## Cómo correr tests y lint

```bash
uv run --python 3.11 pytest
uv run --python 3.11 ruff check .
```

## Limitaciones clave

- `cb9c-h8sn` no publica monto de adición en columna estructurada; el MVP usa como señal principal el **ratio temporal** de adiciones y solo hace parseo monetario auxiliar cuando el texto lo permite.
- Los joins entre SECOP II no son perfectos. Para este MVP, el enriquecimiento de procesos usa la relación observada `jbjy.proceso_de_compra -> p6dx.id_del_portafolio`.
- El score es de **priorización de revisión**, no de confirmación de irregularidad.

