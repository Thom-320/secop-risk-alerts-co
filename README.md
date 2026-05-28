# ContratIA Abierta

**ContratIA Abierta** es un sistema de **ingeniería de datos** que prioriza la
revisión humana de la contratación pública colombiana usando datos abiertos de
SECOP.

El sistema no acusa, no prueba corrupción y no reemplaza auditoría jurídica o fiscal; prioriza revisión humana con evidencia trazable.

La idea central es convertir datos abiertos de contratación pública en una cola
explicable: qué revisar primero, por qué, y qué acción humana sigue. La
herramienta produce alertas explicables y reportes de apoyo; nunca declara
responsabilidad individual ni conclusiones jurídicas.

## Arquitectura única (una sola lane)

Hay **una sola arquitectura oficial** de extremo a extremo:

```
Socrata API → ETL (Polars + Parquet) → PostgreSQL + MongoDB
            → FastAPI ×3 (contracts · risk · analytics) → Dash (DECIDIR/ENTENDER/CONFIAR)
```

| Componente | Detalle |
| --- | --- |
| **Comando** | `make demo-full && make validate-final` |
| **UI** | Dash `dashboard/dash_app.py` — zonas DECIDIR / ENTENDER / CONFIAR |
| **API** | Microservicios FastAPI `services/*` (puertos 8001/8002/8003) |
| **Storage** | PostgreSQL (33 objetos, fuente de verdad) + MongoDB (evidencia/eventos) |
| **Evidencia** | 90.431 procesos scoreados (Meta + Casanare), validación AGR 2.5×, caso real Puerto Gaitán 3.1× |

> Nota: `src/app/streamlit_app.py` y `src/api/main.py` (ruta lean Parquet) quedan
> como **fallback offline interno deprecado**, no como un segundo producto. El
> pipeline de scoring (`src/scoring`, `src/features`) es compartido por ambas
> rutas; la lane oficial es el stack full descrito arriba.

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
