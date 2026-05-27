# Presentacion final

Esta carpeta conserva la copia compatible del deck final generado en `slides/`.

- `slides.md`: fuente Markdown reflejada desde `slides/contratia_abierta_deck.md`.
- `speaker_notes.md`: notas reflejadas desde `slides/contratia_abierta_speaker_notes.md`.
- `assets/`: capturas reales y diagramas usados en el deck.
- `export/slides.pptx`: PowerPoint editable.
- `export/slides.pdf`: PDF listo para revisar o presentar.
- `export/slides_latex.pdf`: version LaTeX/Beamer para presentacion sobria.
- `html/contratia_abierta_interactive.html`: version HTML interactiva.
- `export/slides_interactive.pptx`: export editable generado desde el HTML.
- `export/slides_interactive.pdf`: PDF generado desde el HTML.

La fuente canonica esta en `slides/`. Para regenerar todo, usa:

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

Para la version LaTeX:

```bash
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=slides/latex/build slides/latex/contratia_abierta_beamer.tex
cp slides/latex/build/contratia_abierta_beamer.pdf slides/contratia_abierta_beamer.pdf
cp slides/contratia_abierta_beamer.pdf presentation/export/slides_latex.pdf
```

Para la version HTML interactiva:

```bash
open slides/html/contratia_abierta_interactive.html
/Users/thom/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node slides/html/export_interactive_deck.mjs
cp slides/html/contratia_abierta_interactive.html presentation/html/contratia_abierta_interactive.html
cp slides/html/export/contratia_abierta_interactive.pptx presentation/export/slides_interactive.pptx
cp slides/html/export/contratia_abierta_interactive.pdf presentation/export/slides_interactive.pdf
```
