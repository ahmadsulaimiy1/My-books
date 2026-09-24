// Loads an HTML file at print size and prints the bounding boxes (in mm) of [data-measure] elements.
// Usage: node measure.js <input.html> <width_mm> <height_mm>
const path = require('path');
const { chromium } = require('playwright');
(async () => {
  const [input, wmm, hmm] = process.argv.slice(2);
  const pxPerMm = 96 / 25.4;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: Math.round(wmm * pxPerMm), height: Math.round(hmm * pxPerMm) } });
  await page.goto('file://' + path.resolve(input), { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  await page.emulateMedia({ media: 'print' });
  const boxes = await page.evaluate((k) => {
    const out = {};
    for (const el of document.querySelectorAll('[data-measure]')) {
      // measure the glyphs, not the padded background box
      let b;
      if (el instanceof SVGElement) { b = el.getBoundingClientRect(); }
      else { const r = document.createRange(); r.selectNodeContents(el); b = r.getBoundingClientRect(); }
      out[el.dataset.measure] = [b.left / k, b.top / k, b.right / k, b.bottom / k];
    }
    return out;
  }, pxPerMm);
  console.log(JSON.stringify(boxes));
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
