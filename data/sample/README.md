# Datos sample

Esta carpeta queda reservada para fixtures pequenos y publicables. Los datos reales de
demo se conservan localmente bajo `data/raw`, `data/interim`, `data/marts` y
`data/legacy_raw`, pero esas rutas estan ignoradas por Git para evitar subir archivos
pesados.

Para reconstruir la demo local:

```bash
make etl-demo
make mongo-load
```
