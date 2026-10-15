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

// Windows Chromium calls LogonUser(user, ".", "") the first time a profile opens a tab, to learn
// whether the account has a blank password (password_manager_util_win.cc, CheckBlankPasswordWithPrefs).
// On a non-domain machine every call is a failed interactive logon (event 4625); Playwright's
// launch() makes a fresh temp profile per run, so a test suite that opens ten browsers in ten
// minutes locks the user's Windows account. Chromium skips the check when Local State already
// records a password-change time at or after the real one, so every profile is seeded with that
// record before Chromium starts. launchPersistentContext is used because launch() refuses a
// user-data-dir; the wrapper below keeps the Browser calls these scripts make.
const WIN_EPOCH_OFFSET_US = 11644473600n * 1000000n;          // 1601-01-01 to 1970-01-01, in µs
export function seedProfile(dir) {
  fs.mkdirSync(dir, { recursive: true });
  const future = BigInt(Date.now() + 100 * 365 * 86400 * 1000) * 1000n + WIN_EPOCH_OFFSET_US;
  const file = path.join(dir, 'Local State');
  let state = {};
  try { state = JSON.parse(fs.readFileSync(file, 'utf8')); } catch {}
  state.password_manager = { ...(state.password_manager || {}), os_password_blank: false, os_password_last_changed: String(future) };
  fs.writeFileSync(file, JSON.stringify(state));
  return dir;
}

// Launch Chromium on a seeded temp profile. Returns an object with the Browser calls the draw
// scripts use: newPage(opts), newContext(opts) -> { newPage, addInitScript, close }, close(), process().
// deviceScaleFactor is per launch (a persistent context fixes it); viewport, colorScheme and
// reducedMotion are applied per page.
export async function launchChromium(pw, { executablePath, args = [], headless = true, deviceScaleFactor = 1 } = {}) {
  const dir = seedProfile(fs.mkdtempSync(path.join(os.tmpdir(), 'draw-chromium-')));
  const ctx = await pw.chromium.launchPersistentContext(dir, {
    headless, args, deviceScaleFactor, ...(executablePath ? { executablePath } : {}),
  });
  const blank = ctx.pages();
  const apply = async (page, o = {}) => {
    if (o.deviceScaleFactor && o.deviceScaleFactor !== deviceScaleFactor) {
      throw new Error(`deviceScaleFactor ${o.deviceScaleFactor} differs from the launch value ${deviceScaleFactor}; pass it to launchChromium`);
    }
    if (o.viewport) await page.setViewportSize(o.viewport);
    if (o.colorScheme || o.reducedMotion) await page.emulateMedia({ colorScheme: o.colorScheme, reducedMotion: o.reducedMotion });
    return page;
  };
  const newPage = async (o) => {
    const page = await apply(await ctx.newPage(), o);
    for (const b of blank.splice(0)) await b.close().catch(() => {});
    return page;
  };
  return {
    newPage,
    newContext: async (o = {}) => ({
      newPage: (p = {}) => newPage({ ...o, ...p }),
      addInitScript: (script, arg) => ctx.addInitScript(script, arg),
      close: async () => {},
    }),
    process: () => (ctx.browser() && ctx.browser().process ? ctx.browser().process() : null),
    // A persistent context exposes no process handle, so a hung browser is found by its profile dir.
    kill: () => {
      if (WIN) {
        const ps = `Get-CimInstance Win32_Process -Filter "Name='chrome.exe'" | Where-Object { $_.CommandLine -like '*${path.basename(dir)}*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }`;
        spawnSync('powershell.exe', ['-NoProfile', '-NonInteractive', '-Command', ps], { stdio: 'ignore', timeout: 15000 });
      } else {
        spawnSync('pkill', ['-9', '-f', path.basename(dir)], { stdio: 'ignore', timeout: 8000 });
      }
      try { fs.rmSync(dir, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 }); } catch {}
    },
    close: async () => {
      try { await ctx.close(); } finally { try { fs.rmSync(dir, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 }); } catch {} }
    },
    userDataDir: dir,
  };
}

export function hasFfmpeg() {
  return spawnSync('ffmpeg', ['-version'], { encoding: 'utf8' }).status === 0;
}
