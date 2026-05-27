import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const pptxgen = require("pptxgenjs");

const root = path.resolve(fileURLToPath(new URL("../..", import.meta.url)));
const assets = path.join(root, "slides", "assets");
const out = path.join(root, "slides", "contratia_abierta_deck.pptx");

const data = JSON.parse(fs.readFileSync(path.join(root, "validation", "final_validation.json"), "utf8"));
const evidence = data.evidence;
const countsCsv = fs.readFileSync(path.join(root, "validation", "table_counts.csv"), "utf8");
const tableRows = Object.fromEntries(
  countsCsv
    .trim()
    .split("\n")
    .slice(1)
    .map((line) => {
      const [name, rows] = line.split(",");
      return [name, Number(rows)];
    }),
);

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Transparencia360 / ContratIA Abierta";
pptx.company = "Universidad del Rosario";
pptx.subject = "Proyecto final de Ingenieria de Datos";
pptx.title = "ContratIA Abierta";
pptx.lang = "es-CO";
pptx.theme = {
  headFontFace: "Aptos Display",
  bodyFontFace: "Aptos",
  lang: "es-CO",
};
pptx.defineLayout({ name: "WIDE", width: 13.333, height: 7.5 });
pptx.layout = "WIDE";
pptx.margin = 0;

const C = {
  bg: "F8FAFC",
  ink: "263241",
  muted: "667085",
  line: "D9DEE8",
  accent: "275DA8",
  accentDark: "153E75",
  accentSoft: "EAF1FB",
  green: "2F8F64",
  amber: "B7791F",
  white: "FFFFFF",
};

function addText(slide, text, x, y, w, h, opts = {}) {
  slide.addText(text, {
    x,
    y,
    w,
    h,
    margin: 0.02,
    breakLine: false,
    fit: "shrink",
    fontFace: opts.fontFace || "Aptos",
    fontSize: opts.fontSize || 18,
    color: opts.color || C.ink,
    bold: opts.bold || false,
    valign: opts.valign || "mid",
    align: opts.align || "left",
    paraSpaceAfterPt: 0,
  });
}

function addHeader(slide, number, title, kicker = "Transparencia360") {
  slide.background = { color: C.bg };
  addText(slide, String(number).padStart(2, "0"), 0.55, 0.38, 0.45, 0.22, {
    fontSize: 8,
    color: C.accent,
    bold: true,
  });
  addText(slide, kicker.toUpperCase(), 1.05, 0.34, 2.9, 0.28, {
    fontSize: 8,
    color: C.muted,
    bold: true,
  });
  addText(slide, title, 0.55, 0.73, 9.3, 0.55, {
    fontSize: 25,
    bold: true,
  });
  slide.addShape(pptx.ShapeType.line, {
    x: 0.55,
    y: 1.36,
    w: 12.15,
    h: 0,
    line: { color: C.line, width: 1 },
  });
}

function addFooter(slide) {
  addText(slide, "Priorizacion de revision humana; no prueba conductas indebidas.", 0.55, 7.08, 7, 0.22, {
    fontSize: 8,
    color: C.muted,
  });
}

function addBadge(slide, text, x, y, w, color = C.accentSoft) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h: 0.34,
    rectRadius: 0.06,
    fill: { color },
    line: { color: color },
  });
  addText(slide, text, x + 0.12, y + 0.07, w - 0.24, 0.17, {
    fontSize: 8,
    color: C.accentDark,
    bold: true,
    align: "center",
  });
}

function addMetric(slide, label, value, x, y, w, color = C.accent) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h: 1.05,
    rectRadius: 0.08,
    fill: { color: C.white },
    line: { color: C.line, width: 1 },
  });
  addText(slide, value, x + 0.18, y + 0.14, w - 0.36, 0.36, {
    fontSize: 24,
    bold: true,
    color,
  });
  addText(slide, label, x + 0.18, y + 0.62, w - 0.36, 0.22, {
    fontSize: 9,
    color: C.muted,
  });
}

function image(slide, name, x, y, w, h) {
  slide.addImage({ path: path.join(assets, name), x, y, w, h });
}

function notes(slide, text) {
  slide.addNotes(text.split("\n").filter(Boolean));
}

function titleSlide() {
  const slide = pptx.addSlide();
  slide.background = { color: C.bg };
  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 0,
    w: 13.333,
    h: 0.18,
    fill: { color: C.accent },
    line: { color: C.accent },
  });
  addText(slide, "Transparencia360 / ContratIA Abierta", 0.75, 0.88, 11.8, 0.58, {
    fontSize: 29,
    bold: true,
  });
  addText(
    slide,
    "Sistema Poliglota de Priorizacion de Revision Contractual en Colombia",
    0.78,
    1.78,
    8.7,
    0.42,
    { fontSize: 17, color: C.muted },
  );
  addText(slide, "Ordenar miles de procesos SECOP para decidir que revisar primero.", 0.78, 2.75, 6.6, 0.45, {
    fontSize: 23,
    bold: true,
    color: C.accentDark,
  });
  addBadge(slide, "Revision humana", 0.78, 3.58, 1.65);
  addBadge(slide, "Datos abiertos", 2.62, 3.58, 1.55);
  addBadge(slide, "Trazabilidad", 4.35, 3.58, 1.35);
  image(slide, "architecture.png", 8.0, 2.05, 4.6, 2.59);
  addText(slide, "Ingenieria de Datos - Universidad del Rosario", 0.78, 6.55, 5.8, 0.22, {
    fontSize: 10,
    color: C.muted,
  });
  addFooter(slide);
  notes(
    slide,
    "Presentamos Transparencia360 / ContratIA Abierta, un sistema full-stack para priorizar revision humana de procesos de contratacion publica colombiana. La tesis es simple: los datos abiertos ya existen, pero revisarlos todos manualmente no es viable. El sistema ordena procesos para decidir que revisar primero y mantiene trazabilidad hacia las fuentes. Desde el inicio dejamos claro el limite: no prueba conductas indebidas, no reemplaza auditoria juridica o fiscal y no acusa a ninguna entidad o proveedor.",
  );
}

function problemSlide() {
  const slide = pptx.addSlide();
  addHeader(slide, 2, "Problema: volumen sin atencion suficiente");
  addText(slide, "No faltan datos de contratacion.", 0.75, 1.85, 3.5, 0.4, { fontSize: 22, bold: true });
  addText(slide, "Falta capacidad humana para revisarlos con prioridad, evidencia y trazabilidad.", 0.75, 2.42, 4.4, 0.68, {
    fontSize: 16,
    color: C.muted,
  });
  const boxes = [
    ["Miles de procesos", "SECOP / PAA / contexto"],
    ["Ranking explicable", "score + confianza + razones"],
    ["Revision humana", "decision documentada"],
  ];
  boxes.forEach(([a, b], i) => {
    const x = 6.1 + i * 2.25;
    slide.addShape(pptx.ShapeType.roundRect, {
      x,
      y: 2.22,
      w: 1.78,
      h: 1.25,
      rectRadius: 0.1,
      fill: { color: i === 1 ? C.accentSoft : C.white },
      line: { color: i === 1 ? C.accent : C.line, width: 1 },
    });
    addText(slide, a, x + 0.15, 2.48, 1.48, 0.22, { fontSize: 10, bold: true, align: "center" });
    addText(slide, b, x + 0.15, 2.83, 1.48, 0.28, { fontSize: 7.5, color: C.muted, align: "center" });
    if (i < 2) {
      slide.addShape(pptx.ShapeType.chevron, {
        x: x + 1.87,
        y: 2.63,
        w: 0.36,
        h: 0.42,
        fill: { color: C.accent },
        line: { color: C.accent },
      });
    }
  });
  addFooter(slide);
  notes(
    slide,
    "El problema no es la ausencia de datos. En Colombia existen fuentes abiertas como SECOP, PAA y otros datasets institucionales. El problema practico es que una veeduria, una oficina de control interno o un periodista de datos no puede revisar miles de procesos con el mismo nivel de detalle. La decision operativa es semanal y concreta: en que procesos invertir tiempo humano primero. Por eso el proyecto no intenta emitir veredictos; intenta transformar volumen y ruido en una cola explicable de revision.",
  );
}

function stakeholderSlide() {
  const slide = pptx.addSlide();
  addHeader(slide, 3, "Stakeholder y decision");
  const personas = [
    ["Veeduria ciudadana", "seguimiento al gasto publico"],
    ["Control interno", "focalizar revision institucional"],
    ["Periodista de datos", "priorizar investigacion verificable"],
  ];
  personas.forEach(([title, desc], i) => {
    const x = 0.8 + i * 4.0;
    slide.addShape(pptx.ShapeType.roundRect, {
      x,
      y: 2.0,
      w: 3.35,
      h: 1.45,
      rectRadius: 0.08,
      fill: { color: C.white },
      line: { color: C.line, width: 1 },
    });
    addText(slide, title, x + 0.22, 2.28, 2.9, 0.26, { fontSize: 15, bold: true, color: C.accentDark });
    addText(slide, desc, x + 0.22, 2.76, 2.75, 0.28, { fontSize: 10, color: C.muted });
  });
  addText(slide, "Decision semanal", 0.8, 4.3, 2.4, 0.3, { fontSize: 18, bold: true });
  addText(slide, "Que procesos revisar primero, con que razones y con que confianza.", 3.1, 4.26, 7.2, 0.42, {
    fontSize: 19,
    color: C.accentDark,
    bold: true,
  });
  addFooter(slide);
  notes(
    slide,
    "El stakeholder esta definido como una organizacion con requerimientos reales: veeduria ciudadana, oficina de transparencia, control interno o periodismo de datos. Todos comparten una restriccion: tienen capacidad limitada y necesitan justificar por que revisan un caso antes que otro. La salida del sistema es un ranking con razones, comparables y confianza. Eso permite discutir una decision de priorizacion, no una acusacion automatica.",
  );
}

function requirementsSlide() {
  const slide = pptx.addSlide();
  addHeader(slide, 4, "Mapa de requisitos del curso");
  const items = [
    ["PostgreSQL", `${evidence.postgres_table_count} tablas publicas`],
    ["MongoDB", "5 colecciones con documentos"],
    ["FastAPI", "3 servicios health 200"],
    ["Dash", "interfaz oficial"],
    ["ETL", `${evidence.procurement_process_rows.toLocaleString("es-CO")} procesos demo`],
    ["SQL avanzado", "triggers, CTE, windows"],
    ["Pruebas", "66 pytest pasan"],
    ["Docs", `${evidence.required_docs_present} archivos requeridos`],
  ];
  items.forEach(([a, b], i) => {
    const x = 0.85 + (i % 4) * 3.05;
    const y = 1.95 + Math.floor(i / 4) * 1.45;
    slide.addShape(pptx.ShapeType.roundRect, {
      x,
      y,
      w: 2.55,
      h: 0.92,
      rectRadius: 0.08,
      fill: { color: C.white },
      line: { color: C.line, width: 1 },
    });
    addText(slide, a, x + 0.17, y + 0.15, 2.15, 0.2, { fontSize: 12, bold: true, color: C.accentDark });
    addText(slide, b, x + 0.17, y + 0.49, 2.15, 0.18, { fontSize: 8.5, color: C.muted });
  });
  addFooter(slide);
  notes(
    slide,
    "La guia de clase pedia una solucion de ingenieria de datos, no solo un dashboard. Por eso el proyecto se cerro con PostgreSQL como base relacional principal, MongoDB como soporte documental y de eventos, tres microservicios FastAPI, una interfaz oficial en Dash, ETL reproducible y SQL avanzado. La validacion final reporta 27 tablas relacionales y 33 objetos publicos, 17.229 procesos en la carga demo, colecciones Mongo con documentos, health checks en 200 y la suite automatizada no integral pasando.",
  );
}

function sourcesSlide() {
  const slide = pptx.addSlide();
  addHeader(slide, 5, "Datos oficiales y volumen de demo");
  const sources = [
    ["p6dx-8zbt", "SECOP II Procesos", "unidad analitica"],
    ["rpmr-utcd", "SECOP Integrado", "contexto ejecucion"],
    ["9sue-ezhx", "PAA Detalle", "planeacion"],
    ["wasc-xi4h", "Control fiscal", "contexto visible"],
  ];
  sources.forEach(([id, name, use], i) => {
    const y = 1.78 + i * 0.72;
    addText(slide, id, 0.85, y, 1.2, 0.18, { fontSize: 9, color: C.accent, bold: true });
    addText(slide, name, 2.1, y - 0.02, 3.3, 0.22, { fontSize: 12, bold: true });
    addText(slide, use, 5.55, y, 2.7, 0.18, { fontSize: 9, color: C.muted });
  });
  addMetric(slide, "procesos", tableRows.procurement_process.toLocaleString("es-CO"), 8.65, 1.75, 1.75);
  addMetric(slide, "razones", tableRows.risk_reason.toLocaleString("es-CO"), 10.6, 1.75, 1.75, C.green);
  addMetric(slide, "PAA items", tableRows.paa_item.toLocaleString("es-CO"), 8.65, 3.05, 1.75, C.amber);
  addMetric(slide, "auditoria", tableRows.audit_log.toLocaleString("es-CO"), 10.6, 3.05, 1.75, C.accentDark);
  addFooter(slide);
  notes(
    slide,
    "Las fuentes son datasets oficiales abiertos. SECOP II Procesos aporta la unidad analitica principal: el proceso contractual. SECOP Integrado y PAA permiten contexto de ejecucion y planeacion. El dataset de vigilancia o control fiscal se usa como contexto visible, no como determinante de responsabilidad. La demo carga mas de 10.000 registros, concretamente 17.229 procesos, y deja conteos en validation/table_counts.csv para que el profesor pueda verificar el volumen.",
  );
}

function imageSlide(n, title, img, caption, note) {
  const slide = pptx.addSlide();
  addHeader(slide, n, title);
  image(slide, img, 0.85, 1.66, 11.65, 5.05);
  addText(slide, caption, 0.95, 6.68, 10.7, 0.24, { fontSize: 10, color: C.muted });
  addFooter(slide);
  notes(slide, note);
}

function noSqlSlide() {
  const slide = pptx.addSlide();
  addHeader(slide, 8, "NoSQL y auditoria documental");
  const collections = [
    ["raw_process_snapshots", evidence.mongo_counts.raw_process_snapshots],
    ["etl_run_logs", evidence.mongo_counts.etl_run_logs],
    ["risk_event_logs", evidence.mongo_counts.risk_event_logs],
    ["report_snapshots", evidence.mongo_counts.report_snapshots],
    ["user_action_logs", evidence.mongo_counts.user_action_logs],
  ];
  collections.forEach(([name, count], i) => {
    const y = 1.82 + i * 0.72;
    addText(slide, name, 1.05, y, 3.4, 0.2, { fontSize: 14, bold: true, color: C.accentDark });
    addText(slide, `${count} documento(s)`, 4.72, y, 1.6, 0.2, { fontSize: 10, color: C.muted });
    slide.addShape(pptx.ShapeType.line, { x: 1.0, y: y + 0.36, w: 5.2, h: 0, line: { color: C.line, width: 0.75 } });
  });
  addText(slide, "MongoDB guarda evidencia flexible sin deformar el modelo relacional.", 7.2, 2.28, 4.35, 0.64, {
    fontSize: 22,
    bold: true,
    color: C.accentDark,
  });
  addText(slide, "Snapshots, logs, reportes y acciones se consultan como documentos trazables.", 7.22, 3.25, 4.1, 0.42, {
    fontSize: 13,
    color: C.muted,
  });
  addFooter(slide);
  notes(
    slide,
    "MongoDB no reemplaza a PostgreSQL. Se usa para datos con forma documental o historica: snapshots crudos, logs de ETL, eventos de prioridad, reportes generados y acciones de dashboard. Esto permite conservar evidencia flexible sin deformar el modelo relacional. En la validacion, las colecciones requeridas existen y tienen documentos. La idea es que un auditor pueda reconstruir de donde salio una vista o un reporte sin depender solamente de tablas normalizadas.",
  );
}

function sqlSlide() {
  const slide = pptx.addSlide();
  addHeader(slide, 9, "SQL engineering visible");
  const cards = [
    ["Triggers", "audit_log, historial, updated_at"],
    ["Window functions", "concentracion y outliers"],
    ["CTE recursiva", "jerarquia territorial"],
    ["Transacciones", "score + evento atomico"],
  ];
  cards.forEach(([a, b], i) => {
    const x = 0.9 + (i % 2) * 5.85;
    const y = 1.95 + Math.floor(i / 2) * 1.55;
    slide.addShape(pptx.ShapeType.roundRect, {
      x,
      y,
      w: 4.85,
      h: 1.0,
      rectRadius: 0.08,
      fill: { color: C.white },
      line: { color: C.line, width: 1 },
    });
    addText(slide, a, x + 0.24, y + 0.18, 2.2, 0.22, { fontSize: 15, bold: true, color: C.accentDark });
    addText(slide, b, x + 0.24, y + 0.55, 3.6, 0.2, { fontSize: 10, color: C.muted });
  });
  addText(slide, "No es solo almacenamiento: hay integridad, trazabilidad y consultas analiticas reproducibles.", 1.0, 5.55, 10.9, 0.4, {
    fontSize: 18,
    bold: true,
  });
  addFooter(slide);
  notes(
    slide,
    "La solucion incluye piezas concretas del temario. Hay triggers de auditoria que escriben cambios en audit_log, historial de estado para procesos, validacion de score y mantenimiento de updated_at. Las vistas usan window functions para ranking, concentracion proveedor-entidad y outliers por grupo par. Tambien hay CTE recursiva para jerarquia territorial. El archivo de transacciones muestra como registrar score y evento asociado de forma atomica.",
  );
}

function scoringSlide() {
  const slide = pptx.addSlide();
  addHeader(slide, 10, "Score explicable, no veredicto");
  const parts = [
    ["Reglas", "senales auditables"],
    ["Pares", "desviacion contextual"],
    ["Anomalia", "apoyo interpretable"],
    ["Confianza", "calidad y cobertura"],
    ["Razones", "texto trazable"],
  ];
  parts.forEach(([a, b], i) => {
    const x = 0.85 + i * 2.42;
    slide.addShape(pptx.ShapeType.roundRect, {
      x,
      y: 2.08,
      w: 1.9,
      h: 1.3,
      rectRadius: 0.1,
      fill: { color: i === 0 ? C.accentSoft : C.white },
      line: { color: i === 0 ? C.accent : C.line, width: 1 },
    });
    addText(slide, a, x + 0.16, 2.36, 1.55, 0.24, { fontSize: 13, bold: true, align: "center", color: C.accentDark });
    addText(slide, b, x + 0.16, 2.78, 1.55, 0.18, { fontSize: 8.5, color: C.muted, align: "center" });
  });
  addText(slide, "Salida: score de prioridad + confianza + razones + comparables.", 1.05, 4.55, 9.8, 0.36, {
    fontSize: 20,
    bold: true,
  });
  addFooter(slide);
  notes(
    slide,
    "El score sigue una filosofia rules-first. Combina reglas claras, desviacion frente a procesos pares, componente de anomalia como apoyo y una medida de confianza. Cada evaluacion genera razones auditables. Si la calidad de datos es baja, la confianza baja. Si hay comparables cercanos, se muestran como referencia. Lo clave es que el score ordena revision humana; no determina responsabilidad, no sanciona y no sustituye criterio experto.",
  );
}

function demoSlide() {
  const slide = pptx.addSlide();
  addHeader(slide, 11, "Demo: flujo de revision");
  image(slide, "screenshot_dashboard_home.png", 0.75, 1.65, 3.8, 2.51);
  image(slide, "screenshot_ranking.png", 4.75, 1.65, 3.8, 2.51);
  image(slide, "screenshot_process_detail.png", 8.75, 1.65, 3.8, 2.51);
  addText(slide, "1 Panorama", 0.82, 4.45, 2.0, 0.22, { fontSize: 13, bold: true, color: C.accentDark });
  addText(slide, "2 Ranking", 4.82, 4.45, 2.0, 0.22, { fontSize: 13, bold: true, color: C.accentDark });
  addText(slide, "3 Detalle y comparables", 8.82, 4.45, 2.8, 0.22, { fontSize: 13, bold: true, color: C.accentDark });
  addText(slide, "El usuario entiende el universo, filtra candidatos y revisa evidencia trazable.", 1.0, 5.7, 10.7, 0.34, {
    fontSize: 17,
    bold: true,
  });
  addFooter(slide);
  notes(
    slide,
    "La demo empieza en Panorama con conteos, cobertura y distribucion por departamento. Luego pasa a Ranking, donde se filtra por score y se revisan procesos priorizados. Despues entra a Detalle de proceso, que muestra explicacion, entidad, modalidad, score, confianza y comparables. El flujo esperado para el usuario es: primero entender el universo, segundo escoger un candidato, tercero revisar evidencia y cuarto decidir si abre una revision humana.",
  );
}

function closingSlide() {
  const slide = pptx.addSlide();
  addHeader(slide, 12, "Validacion, limites y siguiente paso");
  image(slide, "validation_summary.png", 0.85, 1.72, 5.9, 3.32);
  addText(slide, "Validacion final: ok", 7.35, 1.9, 3.9, 0.4, { fontSize: 23, bold: true, color: C.green });
  addText(slide, "Limites: datos ruidosos, joins imperfectos, requiere revision humana.", 7.37, 2.7, 4.1, 0.48, {
    fontSize: 14,
    color: C.muted,
  });
  addText(slide, "Siguiente: encuesta real con 5 usuarios y piloto controlado.", 7.37, 3.55, 4.1, 0.48, {
    fontSize: 16,
    bold: true,
    color: C.accentDark,
  });
  addFooter(slide);
  notes(
    slide,
    "La validacion final cruza los criterios academicos: tablas, filas, Mongo, APIs, tests, docs y README. Quedan limites honestos: los datos abiertos pueden ser ruidosos, los joins entre fuentes no son perfectos y la herramienta requiere revision humana. El siguiente paso humano es aplicar la encuesta real con 5 usuarios, incorporar retroalimentacion y, si hay stakeholder disponible, ejecutar un piloto controlado. El aporte del proyecto es convertir datos masivos en una cola trazable de revision.",
  );
}

titleSlide();
problemSlide();
stakeholderSlide();
requirementsSlide();
sourcesSlide();
imageSlide(
  6,
  "Arquitectura de extremo a extremo",
  "architecture.png",
  "Socrata -> ETL -> PostgreSQL + MongoDB -> FastAPI -> Dash.",
  "La arquitectura separa ingestion, persistencia, servicios y presentacion. Socrata alimenta el ETL. Parquet queda como cache o fallback local. PostgreSQL conserva el modelo normalizado y es la fuente de verdad. MongoDB almacena snapshots, logs y eventos que encajan mejor como documentos. Encima hay servicios FastAPI separados para contratos, prioridad y analitica. Dash consume esos datos y presenta el flujo de demo. Esta separacion permite probar cada capa.",
);
imageSlide(
  7,
  "Modelo relacional como fuente de verdad",
  "er_model.png",
  "27 tablas relacionales con PK/FK, constraints e indices; 33 objetos publicos incluyendo vistas.",
  "El modelo relacional supera el minimo de 15 tablas y llega a 27 tablas relacionales y 33 objetos publicos en la validacion local. Agrupa ingesta, geografia, entidades, proveedores, procesos, PAA, contexto fiscal, score, razones, comparables, auditoria y revision humana. La parte importante no es solo contar tablas: hay llaves primarias, foraneas, restricciones de score y confianza, indices utiles y vistas analiticas. PostgreSQL se usa para garantizar integridad, no solo como deposito.",
);
noSqlSlide();
sqlSlide();
scoringSlide();
demoSlide();
closingSlide();

await pptx.writeFile({ fileName: out });
console.log(out);
