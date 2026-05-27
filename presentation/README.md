# Presentacion final

Esta carpeta conserva la copia compatible del deck final generado en `slides/`.

- `slides.md`: fuente Markdown reflejada desde `slides/contratia_abierta_deck.md`.
- `speaker_notes.md`: notas reflejadas desde `slides/contratia_abierta_speaker_notes.md`.
- `assets/`: capturas reales y diagramas usados en el deck.
- `export/slides.pptx`: PowerPoint editable.
- `export/slides.pdf`: PDF listo para revisar o presentar.

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
