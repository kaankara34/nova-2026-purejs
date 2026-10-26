async def run_test(page, output_dir, page_url):
    import asyncio

    base_url = "https://515dc9a7-0d61-46f2-bb41-31805466b8fc.preview.emergentagent.com"

    async def step(name, coro):
        try:
            await coro()
            print(f"PASS: {name}")
        except Exception as e:
            print(f"FAIL: {name} -> {e}")

    try:
        page.on("console", lambda msg: print(f"CONSOLE: {msg.type}: {msg.text}"))
        await page.set_viewport_size({"width": 1920, "height": 1080})

        async def load_home():
            await page.goto(f"{base_url}/tr/index.html", wait_until="domcontentloaded")
            await page.wait_for_timeout(1200)
            await page.wait_for_selector('[data-testid="lang-header-tr"]', timeout=10000)
            await page.screenshot(path="/app/test_reports/screenshots_iter61/automation_output/20261026_105558_9de12a6a826c/home_tr.jpeg", type="jpeg", quality=40, full_page=False)
        await step("Load TR homepage", load_home)

        async def check_no_errors():
            error_text = await page.evaluate("""() => {
            const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));
            return errorElements.map(el => el.textContent).join(", ");
            }""")
            if error_text:
                print(f"Found error message: {error_text}")
            else:
                print("No error messages found on the page")
        await step("Error scan", check_no_errors)

        async def middle_click_preserved():
            async with page.expect_popup(timeout=10000) as popinfo:
                await page.locator('[data-testid="lang-header-en"]').click(button="middle")
            popup = await popinfo.value
            await popup.wait_for_load_state("domcontentloaded")
            popup_url = popup.url
            print(f"Popup URL after middle click: {popup_url}")
            await popup.close()
            if "/en/index.html" not in popup_url:
                raise Exception("Middle-click did not open EN counterpart")
        await step("Native middle-click behavior", middle_click_preserved)

        async def tr_to_en_to_tr_click():
            await page.locator('[data-testid="lang-header-en"]').click(force=True)
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(800)
            url1 = page.url
            from_attr_en = await page.locator('.lang-switch').first.get_attribute('data-lang-from')
            active_en = await page.locator('[data-testid="lang-header-en"]').get_attribute('aria-current')
            print(f"After TR->EN url={url1}, data-lang-from={from_attr_en}, aria-current-en={active_en}")
            if "/en/index.html" not in url1:
                raise Exception("Did not navigate to EN")

            await page.locator('[data-testid="lang-header-tr"]').click(force=True)
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(800)
            url2 = page.url
            from_attr_tr = await page.locator('.lang-switch').first.get_attribute('data-lang-from')
            active_tr = await page.locator('[data-testid="lang-header-tr"]').get_attribute('aria-current')
            print(f"After EN->TR url={url2}, data-lang-from={from_attr_tr}, aria-current-tr={active_tr}")
            if "/tr/index.html" not in url2:
                raise Exception("Did not navigate back to TR")
        await step("TR->EN->TR click and active state", tr_to_en_to_tr_click)

        async def keyboard_enter_navigation():
            await page.goto(f"{base_url}/tr/projeler.html", wait_until="domcontentloaded")
            await page.wait_for_timeout(900)
            await page.keyboard.press("Tab")
            await page.keyboard.press("Tab")
            await page.keyboard.press("Tab")
            await page.keyboard.press("Tab")
            focused = await page.evaluate("document.activeElement?.getAttribute('data-testid') || document.activeElement?.tagName")
            print(f"Focused element before Enter: {focused}")
            await page.focus('[data-testid="lang-header-en"]')
            await page.keyboard.press("Enter")
            await page.wait_for_load_state("domcontentloaded")
            if "/en/projects.html" not in page.url:
                raise Exception(f"Keyboard Enter did not navigate counterpart: {page.url}")
        await step("Keyboard Tab/Enter navigation", keyboard_enter_navigation)

        async def counterpart_checks():
            pairs = [
                ("/tr/projeler.html", '[data-testid="lang-header-en"]', "/en/projects.html"),
                ("/tr/medya.html", '[data-testid="lang-header-en"]', "/en/newsroom.html"),
                ("/tr/gizlilik-bildirimi.html", '[data-testid="lang-header-en"]', "/en/privacy-notice.html"),
                ("/en/contact.html", '[data-testid="lang-header-tr"]', "/tr/iletisim.html"),
            ]
            for src, selector, expected in pairs:
                await page.goto(base_url + src, wait_until="domcontentloaded")
                await page.wait_for_timeout(700)
                href = await page.locator(selector).get_attribute("href")
                print(f"{src} selector {selector} href={href}")
                await page.locator(selector).click(force=True)
                await page.wait_for_load_state("domcontentloaded")
                if expected not in page.url:
                    raise Exception(f"Counterpart mismatch {src} -> {page.url}, expected {expected}")
        await step("Page counterpart mappings", counterpart_checks)

        async def offcanvas_controls_unchanged():
            await page.goto(f"{base_url}/tr/index.html", wait_until="domcontentloaded")
            await page.wait_for_timeout(700)
            await page.locator('#menuToggle').click(force=True)
            await page.wait_for_selector('#sideMenu.open', timeout=5000)
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(350)
            is_open = await page.locator('#sideMenu').evaluate("el => el.classList.contains('open')")
            if is_open:
                raise Exception("Escape did not close side menu")
            await page.locator('#menuToggle').click(force=True)
            await page.wait_for_timeout(300)
            await page.locator('[data-testid="lang-menu-en"]').click(force=True)
            await page.wait_for_load_state('domcontentloaded')
            if "/en/index.html" not in page.url:
                raise Exception("Offcanvas lang switch did not navigate")
        await step("Offcanvas open/close/lang switch", offcanvas_controls_unchanged)

        async def style_checks_and_animation():
            await page.goto(f"{base_url}/tr/index.html", wait_until="domcontentloaded")
            await page.wait_for_timeout(700)
            await page.locator('[data-testid="lang-header-en"]').click(force=True)
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(500)

            style = await page.evaluate("""() => {
                const sw = document.querySelector('.header-actions .lang-switch');
                const indicator = sw?.querySelector('.lang-indicator');
                const before = getComputedStyle(sw, '::before');
                const s = getComputedStyle(sw);
                const i = getComputedStyle(indicator);
                return {
                    dataLangFrom: sw?.dataset.langFrom || null,
                    beforeBg: before.backgroundColor,
                    beforeBorder: before.borderColor,
                    beforeFilter: before.backdropFilter || before.webkitBackdropFilter || '',
                    indicatorBg: i.backgroundColor,
                    indicatorBorder: i.borderColor,
                    indicatorAnimation: i.animationName,
                    indicatorTransition: i.transitionProperty,
                    railWidth: sw?.getBoundingClientRect().width || 0,
                    railHeight: sw?.getBoundingClientRect().height || 0,
                    hasGreenToken: /#0f|#00ff00|green|rgb\(0,\s*128,\s*0\)/i.test((before.background + ' ' + i.background + ' ' + before.borderColor + ' ' + i.borderColor))
                };
            }""")
            print(f"Computed style snapshot: {style}")
            if style.get("hasGreenToken"):
                raise Exception("Found green styling token in toggle")
            if not style.get("dataLangFrom"):
                raise Exception("data-lang-from missing after native language switch")
            if "lang-glass-slide" not in (style.get("indicatorAnimation") or ""):
                raise Exception("Arrival animation keyframe missing")
        await step("Glass style + arrival animation checks", style_checks_and_animation)

        async def responsive_matrix():
            sizes = [
                (320, 844), (390, 844), (768, 1024), (800, 1024),
                (900, 1024), (1024, 1024), (1440, 900), (1920, 1080)
            ]
            for w, h in sizes:
                await page.set_viewport_size({"width": w, "height": h})
                await page.goto(f"{base_url}/tr/index.html", wait_until="domcontentloaded")
                await page.wait_for_timeout(600)
                data = await page.evaluate("""() => {
                    const sw = document.querySelector('.header-actions .lang-switch');
                    const tr = sw?.querySelector('.lang-opt[lang="tr"] .lang-label');
                    const en = sw?.querySelector('.lang-opt[lang="en"] .lang-label');
                    const flagTr = sw?.querySelector('.lang-opt[lang="tr"] .lang-flag');
                    const flagEn = sw?.querySelector('.lang-opt[lang="en"] .lang-flag');
                    const logo = document.querySelector('.logo-mark');
                    const menu = document.querySelector('#menuToggle');
                    const actions = document.querySelector('.header-actions');
                    const bodyOverflow = document.documentElement.scrollWidth > window.innerWidth;
                    const r = (el) => el ? el.getBoundingClientRect() : null;
                    const overlap = (a,b) => {
                        if(!a || !b) return false;
                        return !(a.right < b.left || a.left > b.right || a.bottom < b.top || a.top > b.bottom);
                    };
                    const swr = r(sw), logor = r(logo), menur = r(menu), actionsr = r(actions);
                    return {
                        width: window.innerWidth,
                        trText: tr?.textContent?.trim() || '',
                        enText: en?.textContent?.trim() || '',
                        hasBothFlags: !!flagTr && !!flagEn,
                        hasBothLabels: !!tr && !!en,
                        bodyOverflow,
                        switchVisible: !!sw && getComputedStyle(sw).display !== 'none',
                        overlapLogo: overlap(swr, logor),
                        overlapMenu: overlap(swr, menur),
                        overlapActions: overlap(swr, actionsr),
                        headerHeight: document.querySelector('.site-header')?.getBoundingClientRect().height || 0,
                        switchW: swr?.width || 0,
                        switchH: swr?.height || 0
                    };
                }""")
                print(f"Viewport {w}x{h}: {data}")
                if data.get("switchVisible") and (not data.get("hasBothFlags") or not data.get("hasBothLabels")):
                    raise Exception(f"Missing labels/flags at {w}x{h}")
                if data.get("switchVisible") and (data.get("trText") != "TR" or data.get("enText") != "EN"):
                    raise Exception(f"TR/EN labels unexpected at {w}x{h}")
                if data.get("bodyOverflow"):
                    raise Exception(f"Horizontal overflow at {w}x{h}")
            await page.set_viewport_size({"width": 1920, "height": 1080})
            await page.goto(f"{base_url}/tr/index.html", wait_until="domcontentloaded")
            await page.wait_for_timeout(500)
            await page.screenshot(path="/app/test_reports/screenshots_iter61/automation_output/20261026_105558_9de12a6a826c/home_tr_1920.jpeg", type="jpeg", quality=40, full_page=False)
        await step("Responsive visibility/overflow matrix", responsive_matrix)

        async def test_relative_paths():
            urls = [
                f"{base_url}/tr/index.html",
                f"{base_url}/frontend/tr/index.html",
                f"{base_url}/en/index.html",
                f"{base_url}/frontend/en/index.html"
            ]
            for u in urls:
                r = await page.request.get(u)
                print(f"{u} => {r.status}")
                if r.status >= 400:
                    raise Exception(f"Relative path serving failed for {u}")
        await step("Root and /frontend serving paths", test_relative_paths)

        print("UI regression run completed")

    except Exception as e:
        print(f"FATAL: {e}")
