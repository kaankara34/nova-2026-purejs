async def run_test(page, output_dir, page_url):
    try:
        hero_paths = [
            '/en/index.html','/tr/index.html',
            '/en/mercan-bosphorus.html','/tr/mercan-bosphorus.html',
            '/en/marti-residence.html','/tr/marti-residence.html',
            '/en/bahar-residence.html','/tr/bahar-residence.html',
            '/en/the-residences-east-west.html','/tr/the-residences-east-west.html',
            '/en/the-apartments-ana.html','/tr/the-apartments-ana.html'
        ]

        base = 'https://darg-clone-1.preview.emergentagent.com'
        await page.set_viewport_size({"width": 1920, "height": 1080})
        print('STEP 1: Starting hero lifecycle sweep (Chromium runner)')

        for path in hero_paths:
            url = f"{base}{path}"
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=20000)
                await page.wait_for_timeout(700)
                v = page.locator('video[data-hero-video]').first
                if await v.count() == 0:
                    print(f"HERO {path}: no data-hero-video element")
                    continue
                t1 = await v.evaluate('el => el.currentTime')
                await page.wait_for_timeout(1800)
                t2 = await v.evaluate('el => el.currentTime')
                progressed = (t2 - t1) > 0.15

                await v.evaluate('el => el.pause()')
                p1 = await v.evaluate('el => ({paused: el.paused, t: el.currentTime})')
                await page.evaluate("window.dispatchEvent(new Event('blur'))")
                await page.evaluate("window.dispatchEvent(new Event('focus'))")
                await page.evaluate("window.dispatchEvent(new PageTransitionEvent('pagehide', {persisted: true}))")
                await page.evaluate("window.dispatchEvent(new PageTransitionEvent('pageshow', {persisted: true}))")
                await page.wait_for_timeout(500)
                p2 = await v.evaluate('el => ({paused: el.paused, t: el.currentTime})')
                pause_persist = p1['paused'] and p2['paused'] and abs(p2['t'] - p1['t']) < 0.2

                await page.evaluate("document.querySelector('video[data-hero-video]')?.dispatchEvent(new Event('nova:hero-resume'))")
                await page.wait_for_timeout(1100)
                p3 = await v.evaluate('el => ({paused: el.paused, t: el.currentTime})')
                resumed = (not p3['paused']) and (p3['t'] >= p2['t'])

                print(f"HERO {path}: progress={progressed} ({t1:.2f}->{t2:.2f}) pause_persist={pause_persist} resume={resumed}")
            except Exception as per_page_error:
                print(f"HERO {path}: ERROR {str(per_page_error)}")

        print('STEP 2: Checking mobile menu language switch hide behavior across breakpoints')
        for w in [320, 390, 768, 1024, 1100, 1440, 1920]:
            h = 844 if w <= 1100 else 1080
            await page.set_viewport_size({"width": w, "height": h})
            await page.goto(f"{base}/en/index.html", wait_until='domcontentloaded', timeout=20000)
            await page.wait_for_timeout(650)
            await page.click('#menuToggle', force=True)
            await page.wait_for_timeout(350)

            state = await page.evaluate("""() => {
                const header = document.querySelector('[data-testid="lang-switch"]');
                const menu = document.querySelector('[data-testid="lang-switch-menu"]');
                const read = (el) => {
                  if (!el) return null;
                  const s = getComputedStyle(el);
                  const r = el.getBoundingClientRect();
                  return {display: s.display, visibility: s.visibility, pointerEvents: s.pointerEvents, width: r.width, height: r.height};
                };
                return {open: document.body.classList.contains('nova-menu-open'), header: read(header), menu: read(menu)};
            }""")

            if w <= 1100:
                ok = bool(state['open'] and state['header'] and state['menu'] and state['header']['display'] == 'none' and state['menu']['display'] == 'none')
            else:
                ok = bool(state['open'] and state['header'] and state['header']['display'] != 'none')

            print(f"MENU width={w}: ok={ok} state={state}")
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(260)

        print('STEP 3: EastWest border animation lifecycle check')
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.goto(f"{base}/en/index.html", wait_until='domcontentloaded', timeout=20000)
        await page.wait_for_selector('#eastWestFeature', timeout=12000)
        await page.evaluate("document.getElementById('eastWestFeature').scrollIntoView({block:'center'})")
        await page.wait_for_timeout(1000)

        t1 = await page.evaluate("""() => Array.from(document.querySelectorAll('.ew-progress-active')).map(el => {
            const a = el.getAnimations()[0]; return a ? Number(a.currentTime || 0) : 0;
        })""")
        await page.wait_for_timeout(1000)
        t2 = await page.evaluate("""() => Array.from(document.querySelectorAll('.ew-progress-active')).map(el => {
            const a = el.getAnimations()[0]; return a ? Number(a.currentTime || 0) : 0;
        })""")
        progressed = any((b - a) > 80 for a, b in zip(t1, t2))

        await page.evaluate('window.scrollTo(0, 0)')
        await page.wait_for_timeout(900)
        o1 = await page.evaluate("""() => Array.from(document.querySelectorAll('.ew-progress-active')).map(el => {
            const a = el.getAnimations()[0]; return a ? Number(a.currentTime || 0) : 0;
        })""")
        await page.wait_for_timeout(900)
        o2 = await page.evaluate("""() => Array.from(document.querySelectorAll('.ew-progress-active')).map(el => {
            const a = el.getAnimations()[0]; return a ? Number(a.currentTime || 0) : 0;
        })""")
        paused_offscreen = all(abs(b - a) < 60 for a, b in zip(o1, o2))

        await page.evaluate("document.getElementById('eastWestFeature').scrollIntoView({block:'center'})")
        await page.wait_for_timeout(1000)
        r1 = await page.evaluate("""() => Array.from(document.querySelectorAll('.ew-progress-active')).map(el => {
            const a = el.getAnimations()[0]; return a ? Number(a.currentTime || 0) : 0;
        })""")
        await page.wait_for_timeout(1000)
        r2 = await page.evaluate("""() => Array.from(document.querySelectorAll('.ew-progress-active')).map(el => {
            const a = el.getAnimations()[0]; return a ? Number(a.currentTime || 0) : 0;
        })""")
        resumed = any((b - a) > 80 for a, b in zip(r1, r2))

        print(f"EW BORDER: progressed={progressed} paused_offscreen={paused_offscreen} resumed={resumed}")

        await page.screenshot(path='/app/test_reports/screenshots_iter66_deep/automation_output/20261026_171537_e20587afd1aa/final_state.jpeg', type="jpeg", quality=40, full_page=False)

        error_text = await page.evaluate("""() => {
        const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));
        return errorElements.map(el => el.textContent).join(", ");
        }""")
        if error_text:
            print(f"Found error message: {error_text}")
        else:
            print("No error messages found on the page")

        print('DEEP RUN RESULT: PASS')
    except Exception as e:
        print(f'DEEP RUN RESULT: FAIL - {str(e)}')
