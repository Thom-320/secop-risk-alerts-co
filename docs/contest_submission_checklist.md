# Contest Submission Checklist

## Identidad

- [x] Repo público: https://github.com/Thom-320/secop-risk-alerts-co
- [x] Nombre de producto: ContratIA Abierta.
- [x] Frase ética visible: prioriza revisión humana con evidencia trazable.
- [x] README orientado a jurado (rutas duales, disclaimer, fuentes, scoring, límites).

## Demo

- [x] `make product-pipeline` ejecutado (sample mode; download mode disponible).
- [x] `make validate-product` con `validation/product_validation.json` (ok=true).
- [ ] Demo URL pública si está disponible.
- [ ] Video demo de 2 a 3 minutos.
- [x] Dashboard Streamlit revisado (lean route).
- [x] API read-only para demo pública (PUBLIC_READ_ONLY=true).

## Documentación

- [x] `docs/model-card.md` (19 secciones).
- [x] Data cards en `docs/data-cards/` (4 datasets).
- [x] `docs/crisp_ml.md`.
- [x] `docs/ethics-note.md`.
- [x] `docs/demo-guide.md`.
- [x] `docs/demo-casebook.md` (5 sample cases + comando reproducible).
- [x] `docs/validation-summary.md`.
- [x] `docs/deployment.md`.
- [x] `docs/fairness_territorial.md`.

## Validación

- [x] Validación automática documentada (`make validate-product`, `make validate-final`).
- [x] Estado de validación humana documentado (protocolo listo, resultados pendientes).
- [x] `docs/human_validation_results.md` actualizado solo con revisiones reales (pendiente).
- [x] `docs/usability_results.md` actualizado solo con 5 usuarios reales (pendiente).

## Concurso

- [ ] Registro en "Usos" si aplica.
- [ ] Captura o enlace del registro.
- [x] Licencia de código y condiciones de datos visibles (MIT, datos.gov.co abiertos).
- [x] No hay lenguaje acusatorio ni métricas fabricadas.
