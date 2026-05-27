# Data Card — Resultado de ejecución del plan de vigilancia/control fiscal

## 1. Dataset

Resultado de ejecución del plan de vigilancia/control fiscal.

## 2. ID en datos.gov.co

`wasc-xi4h`.

URL oficial: `https://www.datos.gov.co/resource/wasc-xi4h`.

## 3. Entidad fuente

Datos Abiertos Colombia / entidades de control fiscal según publicación en datos.gov.co.

## 4. Uso dentro del sistema

Contexto institucional agregado para el dashboard y la ficha de revisión. No alimenta
el score de prioridad del MVP.

## 5. Granularidad

Resultado o registro de vigilancia/control fiscal, usualmente a nivel de sujeto o
entidad auditada, no a nivel de proceso contractual individual.

## 6. Campos usados

Sujeto auditado, entidad, vigencia, tipo de actuación, resultado agregado y valores
cuando están disponibles.

Campos descartados: campos sin enlace territorial o temporal suficiente, metadatos
no usados en visualización y atributos que puedan inducir interpretaciones fuera de
contexto.

## 7. Llaves de enlace

Nombre de entidad/sujeto normalizado y campos territoriales cuando existen. El enlace
es agregado por entidad, no por proceso.

## 8. Problemas de calidad esperados

Nombres no coincidentes, cobertura parcial, diferencias temporales, falta de vínculo a
proceso SECOP específico y variabilidad entre entidades reportantes.

## 9. Transformaciones aplicadas

Normalización de nombres, agregación por sujeto/entidad, carga documental y exposición
como contexto visible.

## 10. Riesgos de sesgo

Entidades con mayor vigilancia o mejor reporte pueden aparecer con más contexto. Menor
presencia en el dataset no significa menor necesidad de revisión.

## 11. Qué NO se infiere desde este dataset

No se infiere responsabilidad, conducta indebida ni prioridad automática
de un proceso específico.

## 12. Estado en el MVP

Activo como contexto visible. No modifica `priority_score` ni `confidence_score`.
Condiciones de uso: dataset abierto de datos.gov.co; conservar atribución a la
fuente oficial y revisar licencia vigente antes de redistribuir datos completos.
