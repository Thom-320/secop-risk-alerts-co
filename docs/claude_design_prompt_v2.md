# Iteración 2 — Respuesta y nuevo brief para Claude Design

> **Para Thom:** copia y pega el bloque debajo al chat de Claude Design donde ya está trabajando. No necesitas adjuntar archivos nuevos — ya tiene todo. Solo este mensaje.

---

## RESPUESTA + REDIRECCIÓN

Gracias por la primera versión. Tomo las decisiones que reportaste:

- **Cifras de orden de magnitud en slide 3**: déjalas con asterisco visible: `≈ 900K` con nota a pie *"Estimación orden-de-magnitud SECOP nacional anual; cifra exacta por confirmar con Colombia Compra Eficiente."*. No invento más.
- **Demo doble (17.229 snapshot vs 13.999 real)**: perfecto que lo aclares en slide 13. Mantén ambos.
- **SVG inline en arquitectura**: bien, mejor que Mermaid para imprimir.
- **Equipo en slide 16**: déjalo como **"Thomas Chisica · Ingeniería de Datos · Universidad del Rosario"**.
- **Slide casebook**: sí, añade. **Insértalo como slide 12** desplazando el resto. Necesito ver 3-5 casos reales con score, razones, comparables. Si no tienes los datos exactos, márcalos con `proceso_demo_01`, `proceso_demo_02` y déjame inyectarlos después.

---

## Lo que NO está funcionando: se ve aburrido

Las slides están **demasiado planas y apagadas**. Cumplen la cuadrícula del brief pero parecen plantilla corporativa de consultora. **Eso no es lo que queremos.**

Lee este reset con cuidado:

### El nuevo norte estético

Esto no es Stripe ni McKinsey. Es **una herramienta cívica seria con personalidad editorial**, hecha por un estudiante de Universidad del Rosario que sabe de qué habla. Referencias visuales reales:

- **The Pudding** (the-pudding.com) — periodismo de datos con dirección de arte fuerte.
- **Pentagram case studies** — densas, asimétricas, tipografía protagonista.
- **MIT Technology Review** — gráficos con dirección, no genéricos.
- **Bloomberg Graphics** — datos densos pero respirados, color usado con intención.
- **Wired Italia / Internazionale** — editorial dense pero no aburrido.

**No** queremos:
- Gradient buttons púrpura-rosa de SaaS 2024.
- Glassmorphism, neumorphism, neon glow, cyberpunk. Eso ya lo dije.
- Hero con foto de stock de gente sonriendo.
- Iconos de Heroicons everywhere.

**Sí** queremos:
- **Una decisión tipográfica fuerte**: combinar un serif editorial (Source Serif Pro, GT Sectra, Newsreader, Tiempos, Domaine) para titulares y eyebrows con Inter para cuerpo. **Un serif bien usado solo** cambia toda la sensación de "AI-generated" a "diseñado por alguien".
- **Layouts asimétricos**: no toda slide tiene que tener el mismo top-band + título centrado. Slides 1, 8, 12 y 16 pueden romper la cuadrícula con un titular que ocupe 60% del ancho, una marca de paginación en mono que cuelga, un número grande que sale del bloque, etc.
- **Color usado con confianza**: en slides clave (1, 4, 8, 12, 16) un bloque grande de navy o coral cubriendo 40-50% del slide. No tengas miedo del color sólido. Hoy se siente todo blanco con acentos tímidos.
- **Tipografía data-driven**: cuando muestres `17.229`, déjalo enorme (96-128px), peso 900, tabular nums, alineado a la izquierda con el contexto pegado abajo en small caps. Que el número sea el héroe del slide, no un footnote.
- **Reglas y filetes editoriales**: líneas finas dividiendo bloques (1px hairline en navy oscuro), no cards-con-borde everywhere. Card excesiva = corporate boring.
- **Notas marginales**: en algunas slides, deja columna lateral derecha de ~80px con anotaciones en mono pequeño tipo "v3 · 27.05.2026" o "datos: p6dx-8zbt · snapshot 24m". Eso da el feel "documento técnico real", no "deck genérico".
- **Diagramas con personalidad**: el ERD y la arquitectura no tienen que ser Mermaid genérico ni cajas redondeadas iguales. Pueden tener líneas dibujadas con grosor variable, nodos que rompen el ancho, una pieza destacada en coral mientras el resto está en navy con opacidad reducida. **Jerarquía visual en el diagrama.**
- **Mockups del producto**: en lugar de capturas embedded planas, encuádralos en un mockup de browser sutil (barra de pestañas vacía, dot rojo/amarillo/verde) — eso aterriza que es un producto real.
- **Un toque de imperfección humana**: una nota a mano en una slide (SVG con `font-family: 'Caveat', cursive` o similar) que diga algo como *"← este es el caso del demo"*. Una. Solo una. Pero cambia todo.

### Sistema de diseño revisado (sobre tu primera versión)

**Tipografía nueva:**
```
@import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,wght@0,400;0,600;0,800;1,400&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&family=Caveat:wght@500&display=swap');

--font-display: 'Newsreader', Georgia, serif;     /* títulos y números grandes */
--font-sans: 'Inter', system-ui, sans-serif;       /* cuerpo y UI */
--font-mono: 'JetBrains Mono', SF Mono, monospace; /* IDs, código, anotaciones */
--font-hand: 'Caveat', cursive;                    /* solo para 1 anotación humana */
```

**Paleta — mantén los hex pero AUMENTA los bloques sólidos:**
- Slide 1 y 16: fondo navy completo (`#0B1E33`). Hoy se siente tímido.
- Slide 4 (arquitectura): fondo blanco con un bloque coral 35% ancho a la izquierda funcionando como "etiqueta" vertical con el número de slide grande.
- Slide 8 (score): fondo `--code-bg` (`#0E1B2E`) para todo el slide. La fórmula del score en una slide oscura con la matemática brillando en blanco/cloud le da peso técnico. Igual que un paper.
- Slide 12 (casebook): cada caso es una "fila editorial" con número grande a la izquierda en serif (`01`, `02`, `03`) y la evidencia a la derecha. Como índice de revista.

**Escala tipográfica nueva — sube todo dos pasos en hero slides:**
```
hero-display:  96-128px (números héroe, titulares slide 1/16)
display:       64-80px  (títulos editoriales)
title-l:       36-44px  (h2)
title-m:       24-28px  (h3)
body-l:        18px     (cuerpo principal en slides hero)
body:          14-15px  (cuerpo estándar)
caption:       11-12px  (notas, mono)
micro:         9-10px   (paginación, footer)
```

**Detalles de oficio:**
- `font-feature-settings: "cv11", "ss01", "ss03", "ss07"` para Inter (cifras alternativas con verdadera tabular y `1` con serifa).
- En el serif (Newsreader), activa `font-style: italic` SOLO en eyebrows y captions. Italic en serif es una herramienta editorial que se siente cara cuando se usa con tacto.
- En tablas y números, `font-variant-numeric: tabular-nums slashed-zero`.
- Espaciado: deja respiro entre el bloque hero y el cuerpo. No llenes todo.
- **Hairlines de 0.5px**, no 1px. Filete editorial fino.

### Cambios slide por slide

**Slide 1 (portada):**
- Fondo navy completo `#0B1E33`.
- Banda izquierda coral de 6px de ancho subiendo TODA la altura.
- Eyebrow arriba a la izquierda en italic serif blanco-cloud, NO uppercase.
- Titular **ContratIA Abierta** en serif `Newsreader` 900, 128px, color `#F5EAD2` (sand) — no blanco frío. Color cálido sobre navy = autoridad editorial.
- Línea debajo en Inter regular 22px, color cloud: "IA explicable para priorizar la revisión humana de la contratación pública en Colombia."
- A la derecha o abajo derecha, un bloque mono pequeño con metadata vertical: `v3 · concurso datos al ecosistema · 27.05.2026 · meta + casanare`.
- En la parte inferior, una sola línea italic serif sand: *"No emite juicios de corrupción. Ordena qué revisar primero, con evidencia trazable."*

**Slide 4 (arquitectura):**
- Layout split 35/65.
- Bloque coral 35% ancho a la izquierda con un `04` enorme (serif 200px) en blanco, y el título "Arquitectura" en serif 48px abajo.
- 65% derecho: el SVG de arquitectura, pero con **una pieza destacada**: el `Score Engine` en navy con outline coral grueso, todo lo demás en navy claro/medio. Que se vea cuál es el corazón del sistema.

**Slide 5 (ERD):**
- Mismo tratamiento split, pero invertido (bloque a la derecha).
- ERD con **`risk_assessment` y `paa_process_match`** en coral; el resto en navy. Esos dos son los componentes que ningún otro proyecto del concurso va a tener.

**Slide 8 (score):**
- Fondo `#0E1B2E` (code-bg).
- Eyebrow coral pequeña.
- Fórmula del score **enorme** en monospace blanco (`score = round(100 · σ(Σ wᵢ · sᵢ))`), 60-72px.
- Debajo, los 4 componentes como bloques pequeños con su barra de color, en grid 2×2 o 4×1.
- Tira de interpretación inferior con los 4 rangos — cada uno con su color como bloque sólido completo (no card con borde).

**Slide 12 (casebook NUEVO):**
- Headline en serif: "Casos del demo".
- 5 filas editoriales. Cada una:
  - Número grande izquierda (`01` en serif 72px, navy)
  - Nombre del proceso en mono medium 14px
  - Score en pill grande con color de tier
  - 1 frase razón en italic serif 18px
  - Confianza en mono pequeño a la derecha
- Hairline 0.5px entre filas. Sin cards.

**Slide 16 (cierre):**
- Fondo navy completo.
- Titular ENORME en serif italic, color sand: *"Una revisión imposible se convierte en una cola auditable."*
- Abajo, tres bloques de metadata en mono pequeño, alineados al pie: equipo · repo · contacto.
- Esquina inferior derecha: una sola anotación en `font-hand` (Caveat), color coral, ligeramente rotada: *"gracias por leer hasta acá ✶"*. Una. Sola.

---

### Reglas que NO cambian del primer brief

- Cero lenguaje acusatorio. El sistema **emite juicios de prioridad de revisión**, no de corrupción.
- Cero stock photos. Cero glassmorphism. Cero pie charts.
- Datos reales del repo. No inventes números.
- Export limpio a PDF A4 horizontal con `@media print` correcto.
- 16 slides (ahora 17 con el casebook insertado como 12).

### Lo que cambia: ya NO tan austero

Tienes permiso explícito para:
- Usar serif editorial en titulares.
- Bloques grandes de color sólido (navy o coral cubriendo media slide).
- Números héroe de 128px.
- Una anotación a mano (`Caveat`) en una sola slide.
- Layouts asimétricos en slides clave.
- Mockup de browser frame alrededor de los screenshots del dashboard.

Devuélveme la portada (slide 1), la slide 4 (arquitectura split coral) y la slide 8 (score sobre fondo oscuro) primero. Si esas tres se sienten editoriales en lugar de plantilla, sigo con el resto. Si todavía se sienten apagadas, te digo qué subir más.

Va.
