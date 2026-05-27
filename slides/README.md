# Deck final - ContratIA Abierta

Esta carpeta contiene el deck final de 12 diapositivas para la sustentacion de
15 minutos del proyecto Transparencia360 / ContratIA Abierta.

## Entregables

- `contratia_abierta_deck.md`: fuente Markdown del deck.
- `contratia_abierta_speaker_notes.md`: notas de exposicion en espanol.
- `contratia_abierta_deck.pptx`: deck editable.
- `contratia_abierta_deck.pdf`: exportacion PDF.
- `contratia_abierta_beamer.pdf`: version LaTeX/Beamer optimizada para presentar.
- `latex/contratia_abierta_beamer.tex`: fuente LaTeX de la version Beamer.
- `assets/`: capturas reales del dashboard y diagramas generados desde el repo.

La carpeta `presentation/` mantiene una copia compatible:

- `presentation/slides.md`
- `presentation/speaker_notes.md`
- `presentation/export/slides.pptx`
- `presentation/export/slides.pdf`

## Regeneracion

Desde la raiz del repositorio:

```bash
make db-up
make etl-demo
make mongo-load
make api
make dashboard
uv run --python 3.11 python slides/scripts/generate_assets.py
/Users/thom/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node slides/scripts/capture_screenshots.mjs
/Users/thom/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node slides/scripts/build_deck.mjs
soffice --headless --convert-to pdf --outdir slides slides/contratia_abierta_deck.pptx
```

Version LaTeX/Beamer:

```bash
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=slides/latex/build slides/latex/contratia_abierta_beamer.tex
cp slides/latex/build/contratia_abierta_beamer.pdf slides/contratia_abierta_beamer.pdf
cp slides/contratia_abierta_beamer.pdf presentation/export/slides_latex.pdf
```

Verificacion visual:

```bash
pdftoppm -png -r 110 slides/contratia_abierta_beamer.pdf slides/latex/build/rendered/slide
```

Luego sincroniza la copia historica:

```bash
cp slides/contratia_abierta_deck.md presentation/slides.md
cp slides/contratia_abierta_speaker_notes.md presentation/speaker_notes.md
cp slides/contratia_abierta_deck.pptx presentation/export/slides.pptx
cp slides/contratia_abierta_deck.pdf presentation/export/slides.pdf
cp slides/assets/*.png presentation/assets/
```

## Evidencia usada

Las metricas salen de:

- `validation/final_validation.json`
- `validation/table_counts.csv`

Metricas usadas en el deck:

- 33 tablas PostgreSQL.
- 17.229 procesos en `procurement_process`.
- MongoDB con documentos en las colecciones requeridas.
- Health checks de contratos, prioridad y analitica en HTTP 200.
- 39 pruebas automatizadas pasando.

## Criterios de diseno

- Fondo claro, tipografia de sistema y acento azul institucional.
- Maximo 12 diapositivas.
- Texto visible reducido; detalles en notas.
- Capturas y diagramas reales del repositorio.
- Sin visuales genericos de IA, robots, cerebros, circuitos o promesas vagas.
- Lenguaje etico: priorizacion de revision humana, no prueba conductas indebidas.
