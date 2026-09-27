// Frame-exact export of showreel/index.html.
//   node showreel/render.mjs                 -> all 900 frames (60fps x 15s) into showreel/frames/
//   node showreel/render.mjs --stills 1,2.2  -> PNG stills at those times into showreel/stills/
// Serve WFD-WEBSITE/ first:  npx http-server WFD-WEBSITE -p 8123 -s
import { createRequire } from 'node:module';
import { mkdirSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); } catch { ({ chromium } = require('/opt/node22/lib/node_modules/playwright')); }

const here = path.dirname(fileURLToPath(import.meta.url));
const URL = process.env.REEL_URL || 'http://localhost:8123/showreel/?render=1';
const FPS = 60, DUR = 15;
const stillsArg = process.argv.indexOf('--stills');

const browser = await chromium.launch({ args: ['--disable-web-security', '--force-color-profile=srgb'] });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
page.on('console', m => { if (m.type() === 'warning' || m.type() === 'error') console.log('[page]', m.text()); });
await page.goto(URL, { waitUntil: 'networkidle' });
await page.evaluate(() => window.__ready);

const shot = async (t, file, type) => {
  await page.evaluate(t => window.render(t), t);
  await page.screenshot({ path: file, type, ...(type === 'jpeg' ? { quality: 95 } : {}), clip: { x: 0, y: 0, width: 1920, height: 1080 } });
};

if (stillsArg > -1) {
  const dir = path.join(here, 'stills'); mkdirSync(dir, { recursive: true });
  for (const s of process.argv[stillsArg + 1].split(',')) await shot(+s, path.join(dir, `t${(+s).toFixed(2)}.png`), 'png');
} else {
  const dir = path.join(here, 'frames'); mkdirSync(dir, { recursive: true });
  for (let f = 0; f < FPS * DUR; f++) {
    await shot(f / FPS, path.join(dir, `f${String(f).padStart(4, '0')}.jpg`), 'jpeg');
    if (f % 60 === 0) console.log(`frame ${f}/${FPS * DUR}`);
  }
}
await browser.close();
