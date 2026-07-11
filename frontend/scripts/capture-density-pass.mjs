import { chromium } from "playwright";
import { mkdirSync } from "node:fs";

const BASE = process.env.BASE_URL ?? "http://localhost:3021";
const OUT = "../docs/screenshots";

const pages = [
  { path: "/", name: "density-dashboard" },
  { path: "/financial-waste", name: "density-financial-waste" },
  { path: "/risk-management", name: "density-risk-management" },
  { path: "/business-simulation", name: "density-business-simulation" },
  { path: "/reports", name: "density-reports" },
  { path: "/data-management", name: "density-data-management" },
];

mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch();
const context = await browser.newContext({
  viewport: { width: 1920, height: 1080 },
  deviceScaleFactor: 1,
});
const page = await context.newPage();

for (const { path, name } of pages) {
  await page.goto(`${BASE}${path}`, { waitUntil: "networkidle" });
  await page.waitForTimeout(800);
  await page.screenshot({ path: `${OUT}/${name}.png`, fullPage: false });
  console.log(`captured ${name}`);
}

await browser.close();
