# Model Card — ContratIA Abierta

## 1. Nombre del sistema

ContratIA Abierta, dentro del paraguas académico Transparencia360.

## 2. Propósito

Priorizar revisión humana de procesos de contratación pública colombiana usando datos
abiertos oficiales. El sistema produce una cola ordenada, explicable y auditable para
decidir qué procesos revisar primero.

## 3. Usuarios previstos

- Oficinas de control interno.
- Veedurías ciudadanas.
- Periodistas de datos.
- Equipos académicos que evalúan ingeniería de datos reproducible.

## 4. Decisión que apoya

Apoya la decisión operativa de priorizar revisión humana: qué proceso abrir primero,
qué evidencia mirar y qué limitaciones de datos considerar antes de escalar una revisión.

## 5. Decisiones que NO debe tomar

No decide sanciones, responsabilidad fiscal, responsabilidad jurídica, conducta
individual ni conclusiones acusatorias. Tampoco reemplaza auditoría jurídica,
fiscal o disciplinaria.

## 6. Fuentes de datos

- `p6dx-8zbt`: SECOP II Procesos de Contratación.
- `rpmr-utcd`: SECOP Integrado.
- `9sue-ezhx`: SECOP II Plan Anual de Adquisiciones Detalle.
- `wasc-xi4h`: Resultado de ejecución del plan de vigilancia/control fiscal.

## 7. Unidad de análisis

La unidad de análisis es el proceso contractual. El sistema no usa como unidad de
decisión a personas naturales, funcionarios, proveedores ni entidades como sujetos de
acusación.

## 8. Features principales

- Valor base o adjudicado disponible.
- Modalidad de contratación.
- Departamento y entidad contratante.
- Conteo de respuestas u oferta competitiva cuando existe.
- Longitud/calidad mínima de descripción.
- Desviación frente a procesos pares.
- Concentración relativa de proveedor cuando hay enlace confiable.
- Match PAA visible como contexto y sujeto a compuerta antes de afectar el score.
- Comparables semánticos para contexto de revisión.

## 9. Método de scoring

El scoring visible es interpretable y basado en features observables: combina
competencia, percentil de valor, modalidad, planeación, concentración contextual y
calidad de descripción. En el pipeline analítico también existen señales de anomalía y
comparables textuales para contexto. La salida es un score de prioridad de 0 a 100,
no una probabilidad de responsabilidad ni una conclusión fiscal.

## 10. Componentes del score

- Competencia: menor número de respuestas aumenta prioridad de revisión.
- Valor relativo: procesos más altos frente a pares comparables suben en la cola.
- Modalidad: modalidades menos comparables o más sensibles aumentan prioridad.
- Planeación: ausencia de match PAA puede aumentar necesidad de revisar contexto.
- Concentración: participación recurrente de proveedor aumenta señal de revisión.
- Descripción: textos muy cortos reducen soporte y pueden aumentar necesidad de revisar.

## 11. Métrica de confianza

`confidence_score` mide soporte de datos disponible, no certeza del score. Sube cuando
hay descripción suficiente, valor, modalidad, respuesta/competencia observable y match
PAA. Un score de prioridad alto con confianza baja debe tratarse como solicitud de
validación de datos antes de cualquier conclusión operativa.

## 12. Validación automática existente

La validación automática cubre lint, pruebas unitarias/no integrales, estructura SQL,
constraints, triggers, endpoints, import del dashboard, documentos requeridos y
validación final de servicios cuando PostgreSQL, MongoDB y APIs están disponibles.
`docs/testing_evidence.md` registra el estado local más reciente.

## 13. Validación humana pendiente

Pendiente. No hay etiquetas humanas reales incorporadas al repositorio. El protocolo
propuesto revisa 40 a 100 procesos mezclando prioridad alta, media, baja y controles
aleatorios. Los resultados solo deben agregarse cuando existan revisores reales, fecha,
método de muestreo y responsable de consolidación.

## 14. Sesgos y riesgos

- Subregistro o mala calidad documental por entidad o territorio.
- Diferencias territoriales en cobertura PAA y comparables.
- Modalidades difíciles de comparar con pares suficientes.
- Entidades con pocos procesos pueden tener métricas inestables.
- Joins parciales entre SECOP, SECOP Integrado, PAA y control fiscal.

## 15. Limitaciones técnicas

- Los datos abiertos pueden cambiar de esquema o contener nulos.
- Los enlaces no se asumen 1:1.
- El contexto fiscal es agregado y no entra al score del MVP.
- La ruta por defecto y CI usa NLP clásico con TF-IDF/coseno; no captura toda
  equivalencia semántica.
- La dependencia `sentence-transformers` está disponible como proveedor opcional.
  Para activarlo: `CONTRATIA_USE_TRANSFORMER_EMBEDDINGS=1`. Si el modelo no está
  disponible, el sistema vuelve automáticamente a TF-IDF como fallback seguro.
  Esta ruta neuronal no es obligatoria y no se declara como claim validado si no
  se ejecuta y mide.
- El modo demo depende de datos locales o servicios Docker/host disponibles.

## 16. Uso permitido

Priorización de revisión humana, exploración analítica, docencia, trazabilidad de datos,
preparación de colas de revisión y generación de preguntas auditables.

## 17. Uso no permitido

Acusar, sancionar, etiquetar proveedores o entidades como responsables, automatizar
decisiones legales/fiscales o presentar el score como prueba de conducta indebida.

## 18. Monitoreo recomendado

Monitorear distribución de score por departamento, score promedio, confianza promedio,
cobertura PAA, procesos sin comparables, razones frecuentes, endpoints mutables y
eventos de revisión humana. En demo pública usar `PUBLIC_READ_ONLY=true`.

## 19. Cambios futuros

- Ejecutar validación humana real y encuesta UX con 5 usuarios.
- Calibrar pesos con retroalimentación de revisores.
- Mejorar resolución de entidades y proveedores.
- Evaluar embeddings semánticos opcionales solo si agregan valor verificable frente
  a TF-IDF y si pueden documentarse con métricas reales.
- Agregar despliegue público con modo lectura, autenticación y monitoreo.
