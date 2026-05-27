# Deck HTML interactivo

Version web interactiva de la presentacion final de ContratIA Abierta.

## Abrir

Desde la raiz del repositorio:

```bash
open slides/html/contratia_abierta_interactive.html
```

Controles:

- Flechas izquierda/derecha: navegar.
- Barra espaciadora: avanzar.
- `N`: mostrar u ocultar notas del expositor.
- `F`: pantalla completa.

## Exportar

El HTML incluye estilos de impresion. En navegador, usar imprimir y guardar como
PDF si se quiere una salida directa.

Tambien hay un exportador reproducible a PPTX y PDF basado en Playwright:

```bash
/Users/thom/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node slides/html/export_interactive_deck.mjs
```

Salidas:

- `slides/html/export/contratia_abierta_interactive.pptx`
- `slides/html/export/contratia_abierta_interactive.pdf`
- `slides/html/export/frames/slide-XX.png`

La copia compatible para entrega queda en:

- `presentation/html/contratia_abierta_interactive.html`
- `presentation/export/slides_interactive.pptx`
- `presentation/export/slides_interactive.pdf`

## Verificacion visual

El exportador genera `frames/slide-XX.png`, que permiten revisar todas las
diapositivas como imagenes reales renderizadas por Chromium. Para crear una hoja
de contacto local:

```bash
python3 - <<'PY'
from pathlib import Path
from PIL import Image, ImageDraw
frames = sorted(Path("slides/html/export/frames").glob("slide-*.png"))
thumbs = []
for idx, path in enumerate(frames, 1):
    img = Image.open(path).convert("RGB")
    img.thumbnail((360, 203))
    canvas = Image.new("RGB", (380, 245), (248, 250, 252))
    canvas.paste(img, (10, 10))
    ImageDraw.Draw(canvas).text((10, 220), f"HTML slide {idx}", fill=(38, 50, 65))
    thumbs.append(canvas)
out = Image.new("RGB", (1140, 980), (248, 250, 252))
for idx, thumb in enumerate(thumbs):
    out.paste(thumb, ((idx % 3) * 380, (idx // 3) * 245))
out.save("slides/html/export/contact_sheet.png")
PY
```

## Criterios

- Contenido visible en espanol.
- Sin visuales genericos de IA.
- Metricas reales de `validation/`.
- Capturas reales de `slides/assets/`.
- Lenguaje etico: priorizacion de revision humana, no prueba conductas indebidas.
