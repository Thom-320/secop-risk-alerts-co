# Evidencia de validacion

Los archivos `*.json` y `*.csv` generados por el pipeline no se versionan. Se
regeneran con:

```bash
make etl-demo
make mongo-load
make validate-final
```

Archivos esperados:

- `load_summary.json`
- `table_counts.csv`
- `mongo_summary.json`
- `final_validation.json`

Excepciones versionables:

- `demo_cases_sample.csv`: casos de demostracion marcados como `SAMPLE`.
- `manual_review_sample.csv`: plantilla de validacion humana marcada como `SAMPLE`.

Estas excepciones no son resultados reales ni etiquetas humanas.
