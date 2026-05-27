import fs from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);
const nodeModules = "/Users/thom/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules";
const { chromium } = require(require.resolve("playwright", { paths: [nodeModules] }));
const pptxgen = require(require.resolve("pptxgenjs", { paths: [nodeModules] }));

const root = path.resolve(fileURLToPath(new URL("../..", import.meta.url)));
const htmlPath = path.join(root, "slides", "html", "contratia_abierta_interactive.html");
const outDir = path.join(root, "slides", "html", "export");
const shotDir = path.join(outDir, "frames");
const pptxPath = path.join(outDir, "contratia_abierta_interactive.pptx");
const pdfPath = path.join(outDir, "contratia_abierta_interactive.pdf");

await fs.mkdir(shotDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 1 });
const fileUrl = pathToFileURL(htmlPath).href;

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Transparencia360 / ContratIA Abierta";
pptx.subject = "Interactive HTML deck export";
pptx.title = "ContratIA Abierta interactive deck";
pptx.defineLayout({ name: "WIDE", width: 13.333, height: 7.5 });
pptx.layout = "WIDE";

for (let i = 1; i <= 12; i += 1) {
  await page.goto(`${fileUrl}?slide=${i}`, { waitUntil: "networkidle" });
  await page.addStyleTag({
    content: ".controls,.progress,.help,.notes-panel{display:none!important}",
  });
  await page.waitForTimeout(120);
  const framePath = path.join(shotDir, `slide-${String(i).padStart(2, "0")}.png`);
  await page.locator(".stage").screenshot({ path: framePath });
  const slide = pptx.addSlide();
  slide.background = { color: "F8FAFC" };
  slide.addImage({ path: framePath, x: 0, y: 0, w: 13.333, h: 7.5 });
}

await page.goto(`${fileUrl}?slide=1`, { waitUntil: "networkidle" });
await page.pdf({
  path: pdfPath,
  printBackground: true,
  width: "16in",
  height: "9in",
  margin: { top: "0in", right: "0in", bottom: "0in", left: "0in" },
});

await browser.close();
await pptx.writeFile({ fileName: pptxPath });

console.log(JSON.stringify({ pptxPath, pdfPath, frames: 12 }, null, 2));
