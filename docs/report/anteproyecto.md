# Anteproyecto

## Titulo

Transparencia360 / ContratIA Abierta: Sistema Poliglota de Priorizacion de Revision Contractual en Colombia.

## Cliente y necesidad

Cliente realista: veeduria ciudadana, oficina de transparencia o periodista de datos que debe priorizar revision humana sobre miles de procesos SECOP.

## Objetivo general

Disenar e implementar un sistema de ingenieria de datos que integre datos abiertos de contratacion publica para priorizar procesos que merecen revision humana.

## Alternativa seleccionada

Arquitectura poliglota con PostgreSQL como fuente relacional, MongoDB para documentos/eventos, microservicios FastAPI y dashboard Dash.

## Restricciones

- Usar 10.000+ registros.
- Incluir 15+ tablas.
- No afirmar deteccion de corrupcion.
- Mantener trazabilidad y pruebas reproducibles.
