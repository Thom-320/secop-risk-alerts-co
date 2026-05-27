# Ethics Note

## Principio operativo

ContratIA Abierta y Transparencia360 priorizan revisión humana. Una alerta
explicable significa: “este proceso merece ser mirado antes con esta evidencia”.
No significa sanción, responsabilidad ni conclusión jurídica o fiscal.

## Riesgos de daño

- Daño reputacional si un score se presenta fuera de contexto.
- Falsos positivos por datos incompletos, campos mal diligenciados o comparables
  insuficientes.
- Falsos negativos cuando la fuente abierta no contiene señales observables.
- Sesgo territorial si departamentos con pocos procesos tienen menos pares.
- Sesgo contra entidades pequeñas si su baja cobertura documental reduce la
  confianza o limita comparables.

## Uso responsable

- Mantener visible el disclaimer en README, UI, reportes y diapositivas.
- Usar lenguaje de “priorización de revisión humana” y “alerta explicable”.
- Revisar fuente SECOP y documentos primarios antes de cualquier decisión.
- Registrar decisiones humanas cuando se use la herramienta en una revisión real.
- Separar claramente evidencia automática de juicio experto.

## Interpretación de alertas

Una alerta debe leerse como una pregunta operacional:

1. ¿Por qué aparece arriba en la cola?
2. ¿Qué datos soportan la señal?
3. ¿Qué fuente primaria debe abrir el revisor?
4. ¿La confianza es suficiente o primero hay que validar datos?
5. ¿La acción humana es mantener, bajar, subir prioridad o pedir más información?

## Decisión final

La decisión final debe tomarla una persona o equipo competente según el contexto:
control interno, auditoría, veeduría, periodismo de datos o academia. El sistema
solo organiza evidencia pública y trazable para apoyar esa revisión.

## Datos sensibles

El MVP usa datos abiertos de contratación pública. Aun así, los reportes deben
evitar lenguaje acusatorio, datos personales innecesarios y rankings públicos de
personas. En despliegues públicos se recomienda `PUBLIC_READ_ONLY=true`.

## Control fiscal

`wasc-xi4h` se usa como contexto visible. No es etiqueta de entrenamiento, no
convierte un proceso en caso confirmado y no debe interpretarse sin revisar el
alcance temporal y territorial del dato.
