# Prompt para Claude (Design / Artifact) — Rediseño del dashboard ContratIA Abierta

Copia y pega el bloque debajo en una conversación nueva de Claude.ai. Adjunta también, si quieres, capturas del dashboard actual (`slides/assets/screenshot_dashboard_home.png`, `screenshot_ranking.png`, `screenshot_process_detail.png`) para que tenga referencia visual del estado actual.

---

## PROMPT PARA CLAUDE

Eres un diseñador senior de producto trabajando en una herramienta cívica seria. Necesito que rediseñes el dashboard de **ContratIA Abierta** como un artifact HTML/Tailwind funcional de una sola página (mock interactivo de alta fidelidad, sin backend).

### Contexto del producto

ContratIA Abierta es una herramienta de IA explicable que **prioriza la revisión humana** de procesos de contratación pública en Colombia. **No detecta corrupción.** Ordena miles de procesos de SECOP en una cola priorizada y auditable para que oficinas de control interno, veedurías y periodistas decidan qué revisar primero, con evidencia trazable.

- Usuario primario: **oficina de control interno / transparencia territorial**.
- Datos: SECOP II (procesos), SECOP Integrado (contratos), Plan Anual de Adquisiciones, contexto fiscal AGR.
- Demo: 17.229 procesos cargados, scope Meta y Casanare (Orinoquía).

### Tesis ética (no negociable, debe verse en la UI)

- **Nunca** lenguaje acusatorio. No "fraude", "corrupción", "irregularidad".
- Score = "prioridad de revisión", no "riesgo de delito".
- Disclaimer visible siempre: *"Esta herramienta prioriza revisión humana. No prueba corrupción ni responsabilidad jurídica."*
- Cada alerta muestra razones, comparables, confianza y fuente.

### Vistas (5 pestañas)

1. **Panorama** — KPIs + qué revisar primero esta semana.
2. **Ranking** — tabla priorizada filtrable, exportable a CSV.
3. **Detalle del proceso** — ficha ejecutiva con score, razones, comparables, alineación PAA.
4. **Concentración** — análisis por entidad/proveedor (presentado como evidencia, NO como ranking acusatorio).
5. **Metodología & Ética** — cómo se calcula el score, límites, model card.

### Datos para poblar el mock (ejemplo)

```
KPIs:
- 17.229 procesos analizados
- 12,4% en alta prioridad (score ≥ 70)
- 67% match PAA fuerte (confianza ≥ 0.75)
- 423 entidades · 2.156 proveedores

Top candidato de la semana:
- Proceso: META-2025-CD-0421
- Entidad: Gobernación del Meta
- Score: 87.4 / Confianza: 0.81
- Razones: (1) Valor 3.2× sobre la mediana de comparables; (2) Match PAA débil (0.42); (3) Modalidad atípica para la categoría.

Ranking (5 filas de ejemplo): mezcla scores 90/82/74/61/47 con razones distintas.
```

### Lenguaje de diseño

- **Paleta**: navy profundo `#103A5C` (primario), coral cálido `#E35A4B` (acento/llamadas a atención), teal `#1F827C` (positivos), sand `#F5EAD2` (advertencias suaves), off-white `#FAFAF7` canvas, slate `#5A6478` muted.
- **Tipografía**: Inter (sans). Display semibold/extrabold para titulares; tabular-nums en todo lo numérico; mono (`SF Mono`/`ui-monospace`) para IDs de proceso, códigos de dataset, hashes.
- **Densidad**: respira. Cards con radio `12-16px`, sombras suaves (no neón, no glassmorphism barato), borde sutil `1px` y separación generosa `24-32px`.
- **Jerarquía**: eyebrow uppercase coral 11px → título 26-30px ink → cuerpo 14-15px muted. Una sola sombra dramática reservada para el bloque "Qué revisar primero".
- **Iconografía**: lucide o heroicons. Minimalista, no más de 2 por sección.
- **Charts**: paleta secuencial navy → coral; tabular labels; sin 3D, sin pie charts; barras horizontales para rankings, distribuciones con histogramas.

### Patrones específicos que SÍ quiero

- **Hero del Panorama**: bloque destacado "QUÉ REVISAR PRIMERO ESTA SEMANA" con el top candidato grande, sus 3 razones, score pill y CTA "Abrir detalle".
- **Score pill**: badge redondeado con tier de color (verde 0–20 típico / navy 21–40 leve / ámbar 41–70 notable / coral 71–100 alta prioridad).
- **Tira de decisión**: 3 cards horizontales — "¿Qué?" / "¿Por qué?" / "¿Qué sigue?" — debajo del hero.
- **Disclaimer ético persistente**: barra superior amarilla-pastel con borde izquierdo coral, siempre visible.
- **Detalle del proceso**: layout dos columnas — izquierda evidencia (razones numeradas, comparables, alineación PAA con barras); derecha metadatos + botón "Exportar ficha ejecutiva PDF" y "Registrar revisión humana".
- **Tabla de ranking**: zebra sutil, sort/filter visibles, hover con tint navy soft, columna de score con pill, link "Ver detalle".
- **Footer**: créditos, repo, licencia MIT, link a la model card.

### Patrones que NO quiero

- Glassmorphism / blur exagerado.
- Gradientes saturados arcoíris.
- Pie charts / donuts decorativos.
- Iconos grandes de personas/lupa/banderas como decoración.
- "Riesgo de corrupción" en cualquier texto.
- Rojo intenso como color dominante (lectura acusatoria).
- Mapas decorativos sin función.
- Animaciones de scroll-parallax.

### Entregable

Un **único artifact HTML** (Tailwind CDN ok) con las 5 vistas como pestañas funcionales (cambio de tab por JS vanilla), datos mock embebidos, todo el texto en **español de Colombia**. Que se vea como una herramienta seria de gobierno, no un dashboard de fintech.

### Tono del texto

Directo, profesional, ético. Ejemplos:
- "Estos 20 procesos suben primero a la cola de revisión esta semana."
- "Razones explicables, no acusaciones."
- "Cada alerta requiere contraste con la fuente primaria antes de cualquier decisión."

Empieza con la vista **Panorama**. Hazla impecable. Después construye Ranking → Detalle → Concentración → Metodología.
