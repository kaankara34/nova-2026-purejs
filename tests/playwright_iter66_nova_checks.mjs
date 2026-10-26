import { chromium, webkit } from 'playwright';

const BASE = 'https://darg-clone-1.preview.emergentagent.com';
const HERO_PATHS = [
  '/en/index.html',
  '/tr/index.html',
  '/en/mercan-bosphorus.html',
  '/tr/mercan-bosphorus.html',
  '/en/marti-residence.html',
  '/tr/marti-residence.html',
  '/en/bahar-residence.html',
  '/tr/bahar-residence.html',
  '/en/the-residences-east-west.html',
  '/tr/the-residences-east-west.html',
  '/en/the-apartments-ana.html',
  '/tr/the-apartments-ana.html'
];

async function checkHeroPage(page, path) {
  const url = `${BASE}${path}`;
  const row = { url, loaded: false, videoFound: false, progressOk: false, pausePersistOk: false, resumeOk: false, notes: [] };
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(700);
    row.loaded = true;

    const video = page.locator('video[data-hero-video]').first();
    if (await video.count() === 0) {
      row.notes.push('no hero video element');
      return row;
    }
    row.videoFound = true;

    const t1 = await video.evaluate(el => el.currentTime);
    await page.waitForTimeout(2000);
    const t2 = await video.evaluate(el => el.currentTime);
    if ((t2 - t1) > 0.15) row.progressOk = true;
    else row.notes.push(`no visible progress (${t1.toFixed(3)}->${t2.toFixed(3)})`);

    await video.evaluate(el => el.pause());
    const p1 = await video.evaluate(el => ({ paused: el.paused, t: el.currentTime }));
    await page.evaluate(() => window.dispatchEvent(new Event('blur')));
    await page.evaluate(() => window.dispatchEvent(new Event('focus')));
    await page.evaluate(() => window.dispatchEvent(new PageTransitionEvent('pagehide', { persisted: true })));
    await page.evaluate(() => window.dispatchEvent(new PageTransitionEvent('pageshow', { persisted: true })));
    await page.waitForTimeout(700);
    const p2 = await video.evaluate(el => ({ paused: el.paused, t: el.currentTime }));
    if (p1.paused && p2.paused && Math.abs(p2.t - p1.t) < 0.2) row.pausePersistOk = true;
    else row.notes.push(`pause persistence mismatch before=${JSON.stringify(p1)} after=${JSON.stringify(p2)}`);

    await page.evaluate(() => document.querySelector('video[data-hero-video]')?.dispatchEvent(new Event('nova:hero-resume')));
    await page.waitForTimeout(1200);
    const p3 = await video.evaluate(el => ({ paused: el.paused, t: el.currentTime }));
    if (!p3.paused && p3.t >= p2.t) row.resumeOk = true;
    else row.notes.push(`resume mismatch ${JSON.stringify(p3)}`);
  } catch (e) {
    row.notes.push(String(e));
  }
  return row;
}

async function checkMenu(page) {
  const widths = [320, 390, 768, 1024, 1100, 1440, 1920];
  const out = [];
  for (const width of widths) {
    const row = { width, ok: false, notes: [] };
    try {
      await page.setViewportSize({ width, height: width <= 1100 ? 844 : 1080 });
      await page.goto(`${BASE}/en/index.html`, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(600);
      await page.click('#menuToggle', { force: true });
      await page.waitForTimeout(350);

      const state = await page.evaluate(() => {
        const header = document.querySelector('[data-testid="lang-switch"]');
        const menu = document.querySelector('[data-testid="lang-switch-menu"]');
        const read = el => {
          if (!el) return null;
          const s = getComputedStyle(el);
          return { display: s.display, visibility: s.visibility, opacity: s.opacity, pointerEvents: s.pointerEvents };
        };
        return { bodyOpen: document.body.classList.contains('nova-menu-open'), header: read(header), menu: read(menu) };
      });

      if (width <= 1100) {
        row.ok = Boolean(state.bodyOpen && state.header && state.menu && state.header.display === 'none' && state.menu.display === 'none');
      } else {
        row.ok = Boolean(state.bodyOpen && state.header && state.header.display !== 'none');
      }
      if (!row.ok) row.notes.push(JSON.stringify(state));

      await page.keyboard.press('Escape');
      await page.waitForTimeout(250);
    } catch (e) {
      row.notes.push(String(e));
    }
    out.push(row);
  }
  return out;
}

async function checkEastWest(page) {
  const out = { ok: false, notes: [] };
  try {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto(`${BASE}/en/index.html`, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForSelector('#eastWestFeature', { timeout: 15000 });
    await page.evaluate(() => document.getElementById('eastWestFeature')?.scrollIntoView({ block: 'center' }));
    await page.waitForTimeout(1200);

    const t1 = await page.evaluate(() => Array.from(document.querySelectorAll('.ew-progress-active')).map(el => el.getAnimations()[0]?.currentTime ?? 0));
    await page.waitForTimeout(1000);
    const t2 = await page.evaluate(() => Array.from(document.querySelectorAll('.ew-progress-active')).map(el => el.getAnimations()[0]?.currentTime ?? 0));
    const progressed = t1.some((x, i) => (t2[i] - x) > 80);

    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(1000);
    const o1 = await page.evaluate(() => Array.from(document.querySelectorAll('.ew-progress-active')).map(el => el.getAnimations()[0]?.currentTime ?? 0));
    await page.waitForTimeout(900);
    const o2 = await page.evaluate(() => Array.from(document.querySelectorAll('.ew-progress-active')).map(el => el.getAnimations()[0]?.currentTime ?? 0));
    const paused = o1.every((x, i) => Math.abs(o2[i] - x) < 60);

    await page.evaluate(() => document.getElementById('eastWestFeature')?.scrollIntoView({ block: 'center' }));
    await page.waitForTimeout(1000);
    const r1 = await page.evaluate(() => Array.from(document.querySelectorAll('.ew-progress-active')).map(el => el.getAnimations()[0]?.currentTime ?? 0));
    await page.waitForTimeout(1000);
    const r2 = await page.evaluate(() => Array.from(document.querySelectorAll('.ew-progress-active')).map(el => el.getAnimations()[0]?.currentTime ?? 0));
    const resumed = r1.some((x, i) => (r2[i] - x) > 80);

    out.ok = progressed && paused && resumed;
    if (!out.ok) out.notes.push(`progressed=${progressed} paused=${paused} resumed=${resumed}`);
  } catch (e) {
    out.notes.push(String(e));
  }
  return out;
}

async function runBrowser(name, browserType) {
  const report = { available: false, error: null, hero: [] };
  let browser;
  try {
    browser = await browserType.launch({ headless: true });
    report.available = true;
  } catch (e) {
    report.error = String(e);
    return report;
  }

  const context = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
  const page = await context.newPage();
  page.setDefaultTimeout(30000);

  for (const path of HERO_PATHS) {
    report.hero.push(await checkHeroPage(page, path));
  }

  if (name === 'chromium') {
    report.menu = await checkMenu(page);
    report.eastWest = await checkEastWest(page);
  }

  await context.close();
  await browser.close();
  return report;
}

const finalReport = {
  chromium: await runBrowser('chromium', chromium),
  webkit: await runBrowser('webkit', webkit)
};

console.log('=== ITER66 NODE PLAYWRIGHT REPORT START ===');
console.log(JSON.stringify(finalReport, null, 2));
console.log('=== ITER66 NODE PLAYWRIGHT REPORT END ===');
