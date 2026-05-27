# Modelo NoSQL

MongoDB guarda informacion documental y eventos que no son la fuente relacional de
verdad:

- snapshots crudos de procesos;
- logs de ingesta;
- auditorias de joins;
- snapshots de reportes;
- eventos de uso del dashboard.

La carga demo escribe las colecciones validadas y sus aliases academicos. Si MongoDB no
esta disponible, el bloqueo queda documentado por `make validate-final`.
