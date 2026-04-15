# Master Brief

## Problema

Las veedurías ciudadanas, oficinas de control interno y periodistas de datos enfrentan un costo alto para vigilar contratación pública. El volumen de contratos supera la capacidad de revisión manual y obliga a priorizar.

## Usuario

- Veedurías ciudadanas
- Oficinas de control interno
- Periodistas de datos

## Decisión pública habilitada

Priorizar qué contratos y proveedores revisar primero cada semana con base en alertas objetivas y explicables.

## Datasets

- `jbjy-vk9h`: base contractual principal
- `p6dx-8zbt`: contexto del proceso de contratación
- `cb9c-h8sn`: trazabilidad de adiciones y modificaciones
- `gra4-pcp2`: ubicación de ejecución
- `wmwy-ixwz`: contexto PIDA y alineación con apertura de datos
- `rpmr-utcd`: QA y benchmark auxiliar

## Señales iniciales

1. Adiciones atípicas
2. Concentración de proveedores por entidad
3. Valor/plazo desproporcionado
4. Recurrencia entidad-proveedor

## Metodología

- Alcance reducido a tres entidades del sector salud en Bogotá para 2025-2026.
- Construcción de una tabla base canónica por contrato con `id_contrato` como llave principal.
- Scoring híbrido:
  - Reglas explícitas con pesos fijos
  - IsolationForest como señal no supervisada complementaria
- Explicación textual por contrato y proveedor.

## Diferenciación frente a visores genéricos de SECOP

- Prioriza revisión en lugar de solo listar contratos.
- Resume señales accionables por contrato y proveedor.
- Explica por qué un caso sube en prioridad.
- Integra varias fuentes SECOP II con una tabla analítica simple.

## Riesgos y límites

- Los joins entre tablas SECOP II tienen inconsistencias y no siempre son completos.
- `cb9c-h8sn` no trae monto de adición estructurado.
- El sistema no prueba irregularidad ni reemplaza auditoría.

## Definición explícita de tabla base

- Llave principal: `id_contrato`
- Tabla principal: `jbjy-vk9h`
- Enriquecimientos:
  - `p6dx-8zbt` vía `proceso_de_compra = id_del_portafolio`
  - `cb9c-h8sn` vía `id_contrato`
  - `gra4-pcp2` vía `id_contrato`

## Columnas finales principales

- Identificación: `id_contrato`, `proceso_de_compra`, `nombre_entidad`, `codigo_entidad`
- Proveedor: `documento_proveedor`, `codigo_proveedor`, `proveedor_adjudicado`, `supplier_key`
- Contrato: fechas, valor, objeto, tipo, modalidad, sector, URL
- Proceso: duración declarada, unidad, valor adjudicación, estado
- Adiciones: `dias_adicionados`, `n_adiciones`, `n_modificaciones`
- Ubicación: `ubicacion_ejecucion`, `n_ubicaciones`, `flag_multiple_ubicaciones`

## Columnas descartadas

Se descartan columnas bancarias, nombres de ordenadores de gasto, supervisores y otros campos sensibles o irrelevantes para la primera versión del score.

## Supuestos de join

- `jbjy.proceso_de_compra` corresponde operativamente a `p6dx.id_del_portafolio` en este alcance.
- Cuando existen múltiples filas del mismo portafolio en `p6dx`, se prioriza:
  1. `adjudicado = Si`
  2. `estado_del_procedimiento = Seleccionado`
  3. Mayor fecha de actualización/publicación

## Limitaciones conocidas

- Habrá contratos sin match de proceso o ubicación.
- Puede haber más de una ubicación por contrato.
- El parseo de monto desde texto libre en adiciones es opcional y parcial.

