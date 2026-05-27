# ETL

El ETL tiene dos rutas:

- Online: Socrata/datos.gov.co con `APP_TOKEN_SOCRATA` opcional.
- Demo: Parquet local verificado, con 10.000+ procesos para no depender de una descarga
  pesada en cada ejecucion.

Comandos:

```bash
make extract-demo
make build
make score
make etl-demo
make mongo-load
```

La carga a PostgreSQL normaliza geografia, entidades, proveedores, modalidades, tipos,
PAA, contexto fiscal, scores, razones y comparables.
