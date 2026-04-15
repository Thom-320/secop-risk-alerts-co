# CRISP-ML(Q)

## Objetivo analítico

Construir un sistema mínimo de priorización que ordene contratos y proveedores por alerta de riesgo explicable para revisión humana.

## Éxito del MVP

- Pipeline ejecutable con datos reales del API oficial
- Score 0-100 interpretable
- Explicación legible por contrato y proveedor
- Demo navegable en Streamlit

## Datos

- Fuente principal: SECOP II contratos electrónicos
- Fuentes auxiliares: procesos, adiciones, ubicaciones, PIDA y SECOP Integrado
- Alcance: 2025-2026, tres subredes de salud en Bogotá

## Preparación de datos

- Extracción paginada por Socrata
- Snapshots crudos en Parquet
- Normalización de tipos y fechas
- Consolidación por contrato
- Documentación de inconsistencias de llaves

## Features

- `ratio_adiciones`
- `n_adiciones`
- `share_proveedor_en_entidad`
- `recurrencia_entidad_proveedor`
- `metrica_valor_plazo`
- `data_quality_flags`

## Modelado

- Reglas explícitas con pesos fijos
- IsolationForest como complemento no supervisado
- LOF solo para benchmark opcional

## Evaluación

- Tests unitarios sobre features y scoring
- Smoke test de unicidad de `id_contrato`
- Revisión manual de top alertas en la app

## Riesgos operativos

- Límites del API o throttling
- Cambios en esquema del portal de datos
- Matches incompletos entre contratos, procesos y adiciones

## Consideraciones éticas

- No inferir culpabilidad
- No usar el score como verdad única
- Mantener trazabilidad de las alertas y explicar límites de calidad de datos

