# Data Card — SECOP Integrado

## 1. Dataset

SECOP Integrado.

## 2. ID en datos.gov.co

`rpmr-utcd`.

URL oficial: `https://www.datos.gov.co/resource/rpmr-utcd`.

## 3. Entidad fuente

Colombia Compra Eficiente / datos.gov.co.

## 4. Uso dentro del sistema

Enriquecimiento de contratos, proveedores y valores cuando existe enlace confiable con
procesos SECOP II.

## 5. Granularidad

Registro contractual integrado. Puede haber varios registros asociados a un proceso.

## 6. Campos usados

Número o referencia contractual, identificador de proceso, entidad, contratista,
proveedor, valor, fechas y origen del registro.

Campos descartados: columnas operativas no necesarias para el enlace, campos
redundantes y atributos sin uso directo en scoring o trazabilidad.

## 7. Llaves de enlace

Identificador de proceso, referencia contractual normalizada, entidad normalizada y
campos de proveedor cuando están disponibles.

## 8. Problemas de calidad esperados

Duplicidad histórica, procesos sin contrato asociado, enlaces no 1:1, valores faltantes
y cambios de nombres entre fuentes.

## 9. Transformaciones aplicadas

Normalización de identificadores, control de duplicados, joins de alta confianza,
agregación para concentración secundaria y carga relacional/documental.

## 10. Riesgos de sesgo

La cobertura contractual puede variar por entidad, modalidad y momento de publicación.
Procesos sin enlace no deben interpretarse como casos de mayor prioridad por sí solos.

## 11. Qué NO se infiere desde este dataset

No se infiere que un proveedor, entidad o contrato tenga conducta indebida. El dataset
solo agrega contexto operativo y trazabilidad contractual.

## 12. Estado en el MVP

Activo como enriquecimiento. No reemplaza a `p6dx-8zbt` como fuente principal.
Condiciones de uso: dataset abierto de datos.gov.co; conservar atribución a la
fuente oficial y revisar licencia vigente antes de redistribuir datos completos.
