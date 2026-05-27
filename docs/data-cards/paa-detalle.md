# Data Card — SECOP II Plan Anual de Adquisiciones Detalle

## 1. Dataset

SECOP II Plan Anual de Adquisiciones Detalle.

## 2. ID en datos.gov.co

`9sue-ezhx`.

URL oficial: `https://www.datos.gov.co/resource/9sue-ezhx`.

## 3. Entidad fuente

Colombia Compra Eficiente / datos.gov.co.

## 4. Uso dentro del sistema

Contexto plan-vs-ejecución. Permite mostrar si un proceso tiene item PAA asociado y
qué tan trazable es la relación con la planeación.

## 5. Granularidad

Una fila representa un item del Plan Anual de Adquisiciones.

## 6. Campos usados

Descripción, entidad, valor estimado, modalidad prevista, fechas, duración, vigencia y
`procesos_relacionados` cuando está poblado.

Campos descartados: metadatos de versión no usados en el score, campos con baja
cobertura para el MVP y columnas redundantes frente a entidad/plan/proceso.

## 7. Llaves de enlace

Referencia normalizada de `procesos_relacionados`, entidad normalizada y claves de
proceso cuando existen. El enlace exacto por `procesos_relacionados` se trata como
ancla de alta precisión.

## 8. Problemas de calidad esperados

Descripciones ambiguas, items sin proceso relacionado, actualizaciones del plan,
referencias parciales y posibles relaciones muchos-a-muchos.

## 9. Transformaciones aplicadas

Normalización de referencias, extracción de posibles procesos relacionados, cálculo de
confianza de match, clasificación de estado del match y carga para vistas analíticas.

## 10. Riesgos de sesgo

Entidades que diligencian mejor el PAA pueden mostrar mayor cobertura. La ausencia de
match puede reflejar datos incompletos, no necesariamente un problema del proceso.

## 11. Qué NO se infiere desde este dataset

No se infiere incumplimiento de planeación ni irregularidad. El match PAA es contexto
para revisión humana.

## 12. Estado en el MVP

Visible siempre como contexto. Solo afecta scoring si supera compuertas explícitas de
cobertura/confianza.
Condiciones de uso: dataset abierto de datos.gov.co; conservar atribución a la
fuente oficial y revisar licencia vigente antes de redistribuir datos completos.
