# Demo Guide — ContratIA Abierta

La demo muestra priorización de revisión humana. No acusa, no sanciona y no
reemplaza auditoría jurídica o fiscal.

## Preparación

Ruta oficial académica:

```bash
make demo-full
make validate-final
```

Plus offline si Docker o puertos fallan:

```bash
make product-pipeline
make validate-product
make product-ui
```

Si Docker, OrbStack o puertos fallan, presentar la ruta lean y registrar el
bloqueador exacto en `docs/testing_evidence.md` y `docs/validation-summary.md`.

## Checklist antes de presentar

- `make lint` ejecutado.
- `make test` ejecutado.
- `validation/product_validation.json` revisado.
- Si aplica, `validation/final_validation.json` revisado.
- Abrir dashboard Dash en `http://localhost:8050`.
- Tener Streamlit `http://localhost:8501` como respaldo offline si aplica.
- Tener visible el disclaimer ético.
- Preparar un caso de `docs/demo-casebook.md`.

## Flujo de 2 minutos

1. Abrir dashboard Dash de Transparencia360.
2. Mostrar el primer viewport: “Qué revisar primero”, “Por qué” y “Qué acción
   humana sigue”.
3. Ir al ranking y ordenar por score de prioridad.
4. Seleccionar un proceso con confianza visible.
5. Explicar las tres razones principales.
6. Mostrar match PAA y comparables si existen.
7. Descargar CSV del ranking o HTML del proceso.
8. Cerrar con: “prioriza revisión humana con evidencia trazable”.

## Flujo de 5 minutos

1. Mostrar README y la tabla de dos rutas.
2. Abrir dashboard Dash y enseñar panorama.
3. Filtrar ranking por prioridad/confianza.
4. Abrir detalle ejecutivo.
5. Contrastar PAA, comparables y fuente SECOP.
6. Mostrar el reporte HTML descargable desde Dash.
7. Mostrar `docs/model-card.md` y `docs/ethics-note.md`.
8. Abrir health checks de los tres microservicios.
9. Cerrar con pendientes honestos: validación humana, UX real y despliegue público.

## Qué mostrar sí o sí

- Cola de revisión priorizada.
- Score de prioridad y `confidence_score`.
- Razones explicables.
- Fuente o evidencia trazable.
- Disclaimer ético.
- Estado honesto de validación humana.

## Qué hacer si falla Docker

1. No declarar éxito full-stack.
2. Ejecutar `make product-pipeline && make validate-product`.
3. Presentar Streamlit/FastAPI lean como respaldo, no como ruta oficial del curso.
4. Guardar el error exacto de Docker/puertos.
5. Explicar que la ruta académica exige servicios vivos y está validada por
   `validate-final` cuando la infraestructura está arriba.

## Qué NO decir ante el jurado

- No decir que el sistema prueba conductas.
- No prometer revisión automática suficiente.
- No presentar métricas humanas si no existen revisores reales.
- No vender embeddings neuronales: la ruta validada usa TF-IDF/coseno.
- No ocultar baja confianza o falta de comparables.

## Frase de cierre

ContratIA Abierta reduce miles de procesos a una cola priorizada, explicable y
auditable para revisión humana. El score de prioridad ayuda a decidir qué revisar
primero y qué evidencia contrastar.
