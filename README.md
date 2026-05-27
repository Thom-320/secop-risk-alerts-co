# ContratIA Abierta / Transparencia360

**Transparencia360** es el proyecto unificado para Ingeniería de Datos.
**ContratIA Abierta** es el nombre de producto/demo de la misma solución, no un
fork separado.

El sistema no acusa, no prueba corrupción y no reemplaza auditoría jurídica o fiscal; prioriza revisión humana con evidencia trazable.

La idea central es convertir datos abiertos de contratación pública en una cola
explicable: qué revisar primero, por qué, y qué acción humana sigue. La
herramienta produce alertas explicables y reportes de apoyo; nunca declara
responsabilidad individual ni conclusiones jurídicas.

## Ruta oficial de entrega

| Modo | Comando | UI | API | Storage | Evidencia |
| --- | --- | --- | --- | --- | --- |
| **Demo de concurso (ContratIA Abierta)** | `make product-pipeline && make validate-product` | Dash `dashboard/dash_app.py` | FastAPI lean `src/api/main.py` | Parquet/DuckDB | Ruta liviana, reproducible sin Docker, export CSV+HTML |
| **Evidencia de ingeniería (Transparencia360)** | `make demo-full && make validate-final` | Dash `dashboard/dash_app.py` | Microservicios FastAPI `services/*` | PostgreSQL + MongoDB | 13.999 procesos, 33 objetos PG, 5 colecciones Mongo, APIs 200 |

La demo de concurso usa la ruta lean de ContratIA Abierta. El stack full-stack
académico queda como evidencia de ingeniería avanzada. No son equivalentes; el
jurado debe mirar primero la ruta de concurso.

## Fuentes de datos

- `p6dx-8zbt`: SECOP II Procesos de Contratación.
- `rpmr-utcd`: SECOP Integrado.
- `9sue-ezhx`: SECOP II Plan Anual de Adquisiciones Detalle.
- `wasc-xi4h`: ejecución/control fiscal como contexto visible.

El contexto fiscal se muestra como evidencia contextual y no como etiqueta del
modelo. La ausencia o presencia de contexto fiscal no prueba conducta indebida.

## Quickstart oficial académico full-stack

Instalar dependencias:

```bash
uv sync --python 3.11 --extra dev
```

Levantar la ruta completa:

```bash
make demo-full
make validate-final
```

Comandos equivalentes por etapa:

```bash
make academic-db-up
make academic-db-schema
make academic-etl
make academic-services-up
make validate-final
```

Endpoints locales:

- Contracts service: `http://localhost:8001/health`
- Risk service: `http://localhost:8002/health`
- Analytics service: `http://localhost:8003/health`
- Dash académico: `http://localhost:8050`

`validate-final` exige PostgreSQL, MongoDB y servicios vivos. Si Docker,
OrbStack o los puertos no están disponibles, el JSON marca bloqueadores de
integración y no declara éxito falso.

## Plus offline / producto lean

Generar artefactos de producto. Por defecto usa fixtures versionables de muestra
para evitar descargas completas de Socrata en CI o clones limpios:

```bash
make product-pipeline
make product-ui
make product-api
```

Usar fuentes Socrata reales cuando se quiera reconstruir con datos abiertos
actuales:

```bash
make product-pipeline PRODUCT_SOURCE_MODE=download
```

Endpoints locales:

- Streamlit producto: `http://localhost:8501`
- FastAPI producto: `http://localhost:8000`
- Health producto: `http://localhost:8000/health`

Validación del producto lean:

```bash
make validate-product
```

`validate-product` no requiere PostgreSQL, MongoDB ni Docker. Si faltan marts,
el reporte indicará: `Ejecute make product-pipeline`.

## Targets legacy

Los targets antiguos se conservan como alias para no romper flujos previos:

- `make db-up` -> `make academic-db-up`
- `make db-schema` -> `make academic-db-schema`
- `make db-migrate` -> `make academic-db-schema`
- `make etl-demo` -> `make academic-etl`
- `make services-up` -> `make academic-services-up`
- `make demo-full` -> `make academic-demo`
- `make validate-final` -> `make product-pipeline` + `make validate-product` + `make validate-academic`

## Scoring

El score combina señales interpretables:

- componente de anomalía;
- desviación frente a pares comparables;
- reglas explícitas;
- confianza de datos;
- razones visibles.

La similitud textual usa NLP clásico con TF-IDF y coseno para matching
PAA/proceso y comparables. La dependencia `sentence-transformers` está disponible
como proveedor opcional (`CONTRATIA_USE_TRANSFORMER_EMBEDDINGS=1`), con fallback
automático a TF-IDF si el modelo no está disponible. CI y validaciones locales
usan TF-IDF por defecto para evitar descargas pesadas.

## Evidencia y límites

Documentos principales:

- `docs/product_route.md`
- `docs/academic_route.md`
- `docs/model-card.md`
- `docs/ethics-note.md`
- `docs/demo-guide.md`
- `docs/demo-casebook.md`
- `docs/validation-summary.md`
- `docs/human_validation_protocol.md`
- `docs/human_validation_results.md`
- `docs/deployment.md`

Pendientes humanos que no se fabrican:

- encuesta UX con 5 usuarios reales;
- validación manual con revisores;
- URL pública de despliegue;
- registro en “Usos” si aplica al concurso.

## Calidad

```bash
make lint
make test
make demo-full
make validate-final
# opcional:
make product-pipeline && make validate-product
```

## Licencia

Código bajo MIT. Los datos provienen de fuentes abiertas oficiales de Colombia y
conservan sus condiciones de uso originales.
