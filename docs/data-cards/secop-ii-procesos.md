# Data Card — SECOP II Procesos de Contratación

## 1. Dataset

SECOP II Procesos de Contratación.

## 2. ID en datos.gov.co

`p6dx-8zbt`.

URL oficial: `https://www.datos.gov.co/resource/p6dx-8zbt`.

## 3. Entidad fuente

Colombia Compra Eficiente / datos.gov.co.

## 4. Uso dentro del sistema

Tabla principal de procesos contractuales. Alimenta ranking, detalle, features base,
comparables y trazabilidad hacia la fuente primaria.

## 5. Granularidad

Una fila representa un proceso SECOP II publicado.

## 6. Campos usados

Identificador del proceso, referencia, entidad, departamento, modalidad, objeto,
descripción, fechas, estado, valor base, proveedor cuando existe y conteos de respuesta
cuando están disponibles.

Campos descartados: metadatos administrativos no usados en la demo, campos
duplicados y campos sin cobertura suficiente para features estables.

## 7. Llaves de enlace

`id_del_proceso`, referencia normalizada del proceso, entidad normalizada y campos de
proceso relacionados cuando otra fuente los trae.

## 8. Problemas de calidad esperados

Nulos, cambios de esquema, valores faltantes, entidades con nombres variables, procesos
sin proveedor, campos textuales cortos y diferencias entre proceso publicado y contrato
final.

## 9. Transformaciones aplicadas

Normalización de nombres y llaves, coerción de montos, selección de periodo demo,
deduplicación por proceso, derivación de features interpretables y carga a PostgreSQL.

## 10. Riesgos de sesgo

Entidades con mejor documentación pueden tener confianza mayor. Departamentos con menos
procesos pueden tener menos comparables y métricas más inestables.

## 11. Qué NO se infiere desde este dataset

No se infiere conducta indebida, responsabilidad fiscal, responsabilidad jurídica ni
conclusiones sobre personas, entidades o proveedores.

## 12. Estado en el MVP

Fuente base obligatoria y activa. Si no se carga, no hay cola de revisión confiable.
Condiciones de uso: dataset abierto de datos.gov.co; conservar atribución a la
fuente oficial y revisar licencia vigente antes de redistribuir datos completos.
