// Renders the assembled HTML to PDF with Chromium (Playwright).
// Usage: node render.js <input.html> <output.pdf>
// Set CHROMIUM_PATH to use a specific Chromium executable.
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const [input, output] = process.argv.slice(2);
  const exe = process.env.CHROMIUM_PATH;
  const browser = await chromium.launch(exe ? { executablePath: exe } : {});
  const page = await browser.newPage();
  page.setDefaultTimeout(0);
  await page.goto('file://' + path.resolve(input), { waitUntil: 'load', timeout: 0 });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);
  await page.pdf({ path: output, preferCSSPageSize: true, printBackground: true, outline: true, tagged: true });
  await browser.close();
})().catch((err) => { console.error(err); process.exit(1); });
