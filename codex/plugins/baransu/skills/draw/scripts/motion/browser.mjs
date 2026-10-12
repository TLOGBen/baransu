// browser.mjs — find Playwright and a Chromium it can launch, on Linux, macOS and Windows.
// Shared by render.mjs, grab.mjs and verify-page.mjs so one fix reaches all three.
//
// Playwright, in order: --playwright / $PLAYWRIGHT_MODULE (a path or a package name), a local
// install next to the working directory, the global npm root.
// Chromium, in order: $CHROME_PATH, then the newest chromium-<build> under $PLAYWRIGHT_BROWSERS_PATH
// and the per-OS Playwright cache. Any installed build works: an executablePath means Playwright
// does not insist on the exact build it was released with.
import { createRequire } from 'node:module';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const WIN = process.platform === 'win32';
// ESM import() needs a file:// URL for an absolute path on Windows (a bare "C:/..." is read as a URL scheme).
const asSpec = (p) => (path.isAbsolute(p) ? pathToFileURL(p).href : p);
const pick = (m) => (m && (m.chromium ? m : m.default?.chromium ? m.default : null));

export const INSTALL_HINT = [
  'Playwright or its Chromium is missing. Install once, then rerun:',
  '  npm i -g playwright && npx playwright install chromium',
  '  (or locally in the folder you run from: npm i -D playwright && npx playwright install chromium)',
  'ffmpeg (render.mjs and checks.sh need it):',
  WIN ? '  winget install --id Gyan.FFmpeg -e   (then open a new terminal)' : process.platform === 'darwin' ? '  brew install ffmpeg' : '  sudo apt-get install -y ffmpeg',
].join('\n');

export async function loadPlaywright(explicit) {
  const req = createRequire(path.join(process.cwd(), 'package.json'));
  for (const c of [explicit, process.env.PLAYWRIGHT_MODULE, 'playwright']) {
    if (!c) continue;
    try {
      const spec = c === 'playwright' ? req.resolve('playwright') : c;
      const m = pick(await import(asSpec(spec)));
      if (m) return m;
    } catch {}
  }
  const g = spawnSync('npm root -g', { encoding: 'utf8', shell: true }).stdout?.trim();   // npm is a .cmd on Windows: one command line through a shell
  if (g) {
    for (const f of ['index.mjs', 'index.js']) {
      try { const m = pick(await import(asSpec(path.join(g, 'playwright', f)))); if (m) return m; } catch {}
    }
  }
  return null;
}

function cacheRoots() {
  const home = os.homedir();
  const roots = [process.env.PLAYWRIGHT_BROWSERS_PATH];
  if (WIN) roots.push(path.join(process.env.LOCALAPPDATA || path.join(home, 'AppData', 'Local'), 'ms-playwright'));
  else if (process.platform === 'darwin') roots.push(path.join(home, 'Library', 'Caches', 'ms-playwright'));
  roots.push(path.join(home, '.cache', 'ms-playwright'));
  return roots.filter(Boolean);
}

const EXECUTABLES = [
  'chrome-linux/chrome', 'chrome-linux64/chrome',
  'chrome-mac/Chromium.app/Contents/MacOS/Chromium', 'chrome-mac-arm64/Chromium.app/Contents/MacOS/Chromium',
  'chrome-mac/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing',
  'chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing',
  'chrome-win64/chrome.exe', 'chrome-win/chrome.exe',
];

export function chromiumPath() {
  if (process.env.CHROME_PATH && fs.existsSync(process.env.CHROME_PATH)) return process.env.CHROME_PATH;
  for (const r of cacheRoots()) {
    if (!fs.existsSync(r)) continue;
    const dirs = fs.readdirSync(r).filter((n) => /^chromium-\d+$/.test(n)).sort((a, b) => b.split('-')[1] - a.split('-')[1]);
    for (const d of dirs) {
      for (const rel of EXECUTABLES) {
        const p = path.join(r, d, rel);
        if (fs.existsSync(p)) return p;
      }
    }
  }
  return undefined; // let Playwright use its own default
}

export function hasFfmpeg() {
  return spawnSync('ffmpeg', ['-version'], { encoding: 'utf8' }).status === 0;
}
