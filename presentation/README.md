# Presentacion final

Esta carpeta conserva una copia legible del deck final generado en `slides/`.

- `slides.md`: fuente Markdown reflejada desde `slides/contratia_abierta_deck.md`.
- `speaker_notes.md`: notas reflejadas desde `slides/contratia_abierta_speaker_notes.md`.
- `assets/`: capturas reales y diagramas usados en el deck.
- `html/contratia_abierta_interactive.html`: version HTML interactiva.

La fuente canonica esta en `slides/`. Para regenerar todo, usa:

```bash
make db-up
make etl-demo
make mongo-load
make services-up
npm install
npm run slides:assets
npm run slides:capture
npm run slides:build
soffice --headless --convert-to pdf --outdir slides slides/contratia_abierta_deck.pptx
```

Para la version LaTeX:

```bash
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=slides/latex/build slides/latex/contratia_abierta_beamer.tex
```

Para la version HTML interactiva:

```bash
open slides/html/contratia_abierta_interactive.html
npm run slides:html
cp slides/html/contratia_abierta_interactive.html presentation/html/contratia_abierta_interactive.html
```

Los binarios exportados se regeneran localmente y no hacen parte de la rama
publica del portfolio.
