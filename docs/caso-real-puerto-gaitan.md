# Caso real: ¿nuestro sistema prioriza donde el control fiscal ya encontró irregularidades?

> Chequeo retrospectivo **ciego**. El modelo nunca vio casos de la Contraloría ni
> noticias. Pregunta: ¿las entidades con irregularidades públicas *vigentes*
> aparecen arriba en nuestra cola, o las tratamos como al resto?

## Caso positivo: Municipio de Puerto Gaitán (Meta)

### Lo que dice el registro público (Contraloría / Procuraduría)

Puerto Gaitán recibe una de las mayores asignaciones de regalías petroleras del
país. El control fiscal documentó irregularidades reiteradas:

- **Sistemas de tratamiento de agua**: hallazgos fiscales por más de **$14.735
  millones** solo en Puerto Gaitán Oriente; tanques de purificación de agua de
  más de **$270 millones cada uno** que no cumplieron su objetivo (Procuraduría /
  Contraloría).
- **Sistemas fotovoltaicos**: hallazgo fiscal de **$8.901 millones** por
  incumplimiento técnico y falta de mantenimiento (2025).
- **Regalías**: la Secretaría de Transparencia identificó indicadores de posibles
  hechos de corrupción en el manejo de recursos de regalías.

### Lo que hace nuestro sistema, sin esa información

| Métrica | Puerto Gaitán | Universo nacional |
| --- | ---: | ---: |
| Tasa de procesos en alta prioridad (score ≥ 70) | **1.56%** | 0.51% |
| Enriquecimiento | **3.1×** | 1.0× (línea base) |
| Score máximo de un proceso | **88** (top ~0.1%) | — |

El proceso de Puerto Gaitán con mayor score que marcamos es una
**"CONSTRUCCIÓN SISTEMAS DE ACUEDUCTO PARA LOS RESGUARDOS INDÍGENAS"** por
**$42.408 millones** (score 87). Es decir: el sistema, de forma independiente,
sube al top percentil un contrato de **agua/acueducto en Puerto Gaitán** — la
misma entidad y la misma categoría donde la Contraloría halló irregularidades.

**No afirmamos que ese contrato específico sea el sancionado.** Afirmamos que el
triage prioriza, sin etiqueta previa, contratos de la entidad y categoría que el
control fiscal ya señaló. Eso es exactamente lo que debe hacer una herramienta de
priorización: llevar al revisor humano primero a donde hay señal.

## El contraejemplo que da credibilidad: Gobernación de Casanare

Casanare es emblema nacional de corrupción: varios exgobernadores **condenados
por la Corte Suprema** y fallos fiscales de la Contraloría por **$9.842
millones**. Sería fácil esperar que nuestro sistema lo "marcara" — pero:

| Entidad | Enriquecimiento vs nacional |
| --- | ---: |
| Municipio de Puerto Gaitán | 3.1× |
| Departamento del Meta | 2.9× |
| **Gobernación de Casanare** | **1.0× (promedio)** |
| Alcaldía de Villavicencio | 0.7× (por debajo) |

La Gobernación de Casanare puntúa en el **promedio**. ¿Por qué? Porque los
escándalos condenados son de administraciones de hace **10+ años** (p. ej. la
biblioteca de Paz de Ariporo, inconclusa "hace 13 años"), mientras nuestros datos
son contratación **reciente (2024–2026)**, que estructuralmente no es anómala.

**Esto es una fortaleza, no una falla.** El sistema **no es una lista negra de
entidades por reputación**: es un detector de **procesos estructuralmente
atípicos**. Por eso sube Puerto Gaitán (irregularidades *vigentes* en agua) y no
sube Casanare por inercia histórica. Una herramienta que marcara "Casanare =
malo" sería injusta con la administración actual y sería ruido, no señal.

## Qué prueba y qué NO prueba este caso

**Prueba:**
- El triage no ordena humo: concentra prioridad donde hay irregularidad pública
  vigente y documentada (Puerto Gaitán, 3.1×).
- Discrimina por estructura del proceso actual, no por reputación de la entidad
  (Casanare en promedio).

**No prueba:**
- Que esos contratos específicos sean corruptos. Son señales de prioridad de
  revisión humana, no veredictos.
- Causalidad. Es corroboración retrospectiva a nivel entidad + categoría.

## Reproducible

```sql
WITH u AS (SELECT 100.0*sum((priority_score>=70)::int)/count(*) AS p FROM risk_assessment)
SELECT e.name,
       round((100.0*sum((ra.priority_score>=70)::int)/count(*))::numeric,2) AS pct_alta,
       round((100.0*sum((ra.priority_score>=70)::int)/count(*)/(SELECT p FROM u))::numeric,1) AS veces_vs_nacional
FROM public_entity e
JOIN procurement_process p ON p.entity_id = e.entity_id
JOIN risk_assessment ra ON ra.process_id = p.process_id
WHERE e.name IN ('MUNICIPIO DE PUERTO GAITAN','DEPARTAMENTO DEL META',
                 'GOBERNACION DEL CASANARE','ALCALDIA MUNICIPIO DE VILLAVICENCIO')
GROUP BY e.name ORDER BY veces_vs_nacional DESC;
```

## Fuentes públicas

- Contraloría / Procuraduría — irregularidades en contratación de agua y regalías,
  Puerto Gaitán (filtros de agua, sistemas fotovoltaicos).
- Corte Suprema de Justicia — condena a exgobernadores de Casanare por
  irregularidades en la contratación.
- Contraloría General — fallos fiscales por $9.842 millones, cuatro casos de
  impacto nacional en Casanare.
