# Deck — ContratIA Abierta

Deck único y canónico para la sustentación. Diseño editorial (HTML), 19 slides,
con la evidencia real del proyecto (validación AGR 2.46×, caso Puerto Gaitán 3.1×,
90.431 procesos reales, embeddings funcionando).

## Entregable canónico (lo único que necesitas)

- **`html/contratia_abierta.html`** — el deck. Ábrelo en Chrome y navega con `←/→`.
- **`html/deck-stage.js`** — componente de navegación (debe estar junto al HTML).
- **`contratia_abierta.pdf`** — exportación PDF (19 páginas, una por slide).

Guion de sustentación técnico y detallado: **`docs/pitch_tecnico.md`**.

## Cómo presentar

1. Abre `html/contratia_abierta.html` en Chrome (se ve mejor en vivo, fuentes
   cargadas, navegación con flechas y pantalla completa).
2. Ten el dashboard vivo en otra pestaña: `make demo-full` → `http://localhost:8050`.
3. Sigue `docs/pitch_tecnico.md` slide por slide.

## Regenerar el PDF desde el HTML

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --virtual-time-budget=20000 \
  --run-all-compositor-stages-before-draw --no-pdf-header-footer \
  --print-to-pdf=slides/contratia_abierta.pdf \
  "file://$PWD/slides/html/contratia_abierta.html"
```

El deck usa `@media print` (una slide por página A4 horizontal) vía `deck-stage.js`.

## Estructura

```
slides/
├── html/
│   ├── contratia_abierta.html   ← deck canónico
│   └── deck-stage.js            ← navegación + print
├── contratia_abierta.pdf        ← export PDF
├── assets/                      ← screenshots reales + diagramas
├── scripts/generate_assets.py   ← regenera diagramas
├── PROMPT.md · INSTRUCCIONES.md  ← brief de generación
└── archive/                     ← versiones anteriores (pptx, beamer, etc.) — no usar
```

## Evidencia usada en el deck

- 90.431 procesos reales scoreados (Meta + Casanare).
- 33 objetos PostgreSQL · 5 colecciones MongoDB · 3 APIs FastAPI · 71 tests.
- Validación AGR (control fiscal) 2.46× de enriquecimiento — prueba ciega.
- Caso real Puerto Gaitán 3.1× + contraejemplo honesto Casanare 1.0×.
- Embeddings MiniLM multilingüe funcionando (sim 0.61 vs 0.14).

## Criterios de diseño

- Editorial: Newsreader serif + Inter + JetBrains Mono. Navy / coral / teal.
- Lenguaje ético: prioriza revisión humana, no prueba conductas indebidas.
- Sin visuales genéricos de IA. Esquemas y datos reales del repositorio.
