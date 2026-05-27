# Seguridad y roles

La demo local usa credenciales de desarrollo definidas en `.env.example` y
`docker-compose.yml`. Para despliegue publico deben reemplazarse por secretos del
proveedor de hosting.

## Roles PostgreSQL

`sql/007_security_roles.sql` crea perfiles de menor privilegio:

- `contratia_analyst_readonly`: `SELECT` sobre vistas analiticas.
- `contratia_reviewer`: `SELECT` sobre vistas e `INSERT/UPDATE` sobre `human_review`.
- `contratia_admin`: privilegios administrativos sobre tablas y secuencias del esquema.

## Superficie de API

Los endpoints de lectura se pueden exponer en una demo publica. Los endpoints de revision
humana deben protegerse con autenticacion o mantenerse en demo local si hay despliegue
publico. Ningun endpoint debe presentar el score como prueba de conducta indebida.
