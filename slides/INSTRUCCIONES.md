# Cómo usar este paquete

## Paso a paso

1. Abre [claude.ai](https://claude.ai) en una conversación nueva (selecciona el modelo más reciente — Opus o Sonnet 4.x).
2. **Sube TODOS los archivos del paquete primero** (arrastra y suelta al chat):
   - Todos los `.md` dentro de `docs/` y `docs/data-cards/`
   - Todos los `.png` dentro de `assets/`
3. **Después** de subir los archivos, pega el contenido completo de `PROMPT.md` como tu primer mensaje.
4. Espera el artifact. Si el primer slide se ve flojo, pide: "Slide 1 todavía no se siente CTO-tier. Hazlo más sobrio: menos chips, más jerarquía, regla coral más visible."
5. Cuando todas las slides estén listas:
   - En el artifact, pulsa Cmd+S para guardar el HTML.
   - Abre el HTML en Chrome.
   - Cmd+P → "Guardar como PDF" → orientación **Horizontal**, márgenes **Ninguno**, "Gráficos de fondo" activado.

## Si Claude Design tira un artifact que no se exporta bien a PDF

Pídele:

> "El export a PDF está cortando contenido. Implementa `@media print` así:
> ```css
> @media print {
>   @page { size: A4 landscape; margin: 0; }
>   body { background: white; }
>   .nav, .progress, .counter { display: none !important; }
>   .slide { page-break-after: always; width: 297mm; height: 210mm; transform: scale(0.92); transform-origin: top left; }
> }
> ```
> Y verifica con vista previa de impresión que cada slide ocupa exactamente una página A4 horizontal."

## Contenido del paquete

```
PROMPT.md                     ← el brief para pegar en el chat
INSTRUCCIONES.md              ← este archivo
docs/
  README.md                   ← tesis y comandos
  arquitectura.md             ← stack técnico detallado
  model-card.md               ← score, pesos, límites
  testing_evidence.md         ← métricas duras de validación
  ethics-note.md              ← disclaimers no negociables
  data-cards/
    secop-ii-procesos.md      ← ficha p6dx-8zbt
    secop-integrado.md        ← ficha rpmr-utcd
    paa-detalle.md            ← ficha 9sue-ezhx
    control-fiscal.md         ← ficha wasc-xi4h
assets/
  architecture.png            ← diagrama existente (referencia)
  er_model.png                ← ERD existente (referencia)
  screenshot_dashboard_home.png
  screenshot_ranking.png
  screenshot_process_detail.png
  validation_summary.png      ← gráfico de validación
```

## Recomendación final

Para máxima calidad, abre claude.ai con **Claude Opus 4.x**. El artifact debería tomar 1-2 turnos. Si Claude te entrega algo decorativo (con glassmorphism, gradientes saturados, íconos grandes), córtalo de raíz citando el bloque "REGLAS DE PROHIBICIÓN" del PROMPT.
