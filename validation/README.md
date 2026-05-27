# Evidencia de validacion

Los archivos `*.json` y `*.csv` de esta carpeta son generados por el pipeline y no se
versionan. Se regeneran con:

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
