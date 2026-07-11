import { chromium } from "playwright";
import { mkdirSync } from "node:fs";

const OUT = "../docs/screenshots";
mkdirSync(OUT, { recursive: true });

let browser;
try {
  browser = await chromium.launch({ channel: "chrome" });
} catch {
  browser = await chromium.launch();
}

const context = await browser.newContext({
  viewport: { width: 1920, height: 1080 },
  deviceScaleFactor: 1,
});
const page = await context.newPage();
await page.goto("http://localhost:3000/", { waitUntil: "networkidle" });
await page.waitForTimeout(1000);
await page.screenshot({
  path: `${OUT}/dashboard-viewport-1920x1080.png`,
  fullPage: false,
});
console.log("captured dashboard viewport");
await browser.close();
