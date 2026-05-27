# Deck LaTeX Beamer

Esta carpeta contiene una version LaTeX/Beamer del deck final de ContratIA
Abierta. Mantiene la misma narrativa de 12 diapositivas, pero prioriza
tipografia consistente, control preciso de layout y salida PDF nativa.

## Compilar

Desde la raiz del repositorio:

```bash
latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=slides/latex/build slides/latex/contratia_abierta_beamer.tex
cp slides/latex/build/contratia_abierta_beamer.pdf slides/contratia_abierta_beamer.pdf
cp slides/contratia_abierta_beamer.pdf presentation/export/slides_latex.pdf
```

## Verificacion visual

```bash
pdftoppm -png -r 120 slides/contratia_abierta_beamer.pdf slides/latex/build/rendered/slide
```

Revisar las paginas renderizadas antes de presentar. El deck usa capturas reales
de `slides/assets/` y metricas de la validacion ya documentada.

## Criterios

- 12 diapositivas, 16:9.
- Fondo claro, acento institucional sobrio y tipografia sans.
- Pocas palabras por slide, detalles en notas de exposicion existentes.
- Sin imagenes genericas de IA ni lenguaje acusatorio.
- Disclaimer etico visible en todas las diapositivas.
