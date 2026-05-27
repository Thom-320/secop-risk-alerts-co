import fs from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require(
  require.resolve("playwright", {
    paths: ["/Users/thom/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules"],
  }),
);

const root = path.resolve(fileURLToPath(new URL("../..", import.meta.url)));
const assets = path.join(root, "slides", "assets");
await fs.mkdir(assets, { recursive: true });

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 950 }, deviceScaleFactor: 1 });

async function shot(name) {
  await page.screenshot({ path: path.join(assets, name), fullPage: false });
}

await page.goto("http://127.0.0.1:8050", { waitUntil: "networkidle", timeout: 60000 });
await shot("screenshot_dashboard_home.png");

await page.getByText("Ranking", { exact: true }).click();
await page.waitForTimeout(1000);
await shot("screenshot_ranking.png");

await page.getByText("Detalle", { exact: true }).click();
await page.waitForTimeout(1000);
await shot("screenshot_process_detail.png");

await browser.close();
