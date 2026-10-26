async def run_test(page, output_dir, page_url):
    import re

    page.on("console", lambda msg: print(f"CONSOLE: {msg.type}: {msg.text}"))

    try:
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(1200)
        print("Step 1 PASS: Loaded TR homepage")
    except Exception as e:
        print(f"Step 1 FAIL: {e}")

    try:
        lang_switch = page.get_by_test_id("lang-switch").first
        await lang_switch.wait_for(state="visible", timeout=8000)
        lang_toggle = lang_switch.locator('.lang-toggle').first
        lang_rail = lang_switch.locator('.lang-rail').first
        lang_knob = lang_switch.locator('.lang-knob').first
        print("Step 2 PASS: Located language switch elements")
    except Exception as e:
        print(f"Step 2 FAIL: {e}")

    try:
        metrics = await page.evaluate('''() => {
          const sw = document.querySelector('[data-testid="lang-switch"]');
          const rail = sw?.querySelector('.lang-rail');
          const knob = sw?.querySelector('.lang-knob');
          const railRect = rail?.getBoundingClientRect();
          const knobRect = knob?.getBoundingClientRect();
          const kStyle = knob ? getComputedStyle(knob) : null;
          const rStyle = rail ? getComputedStyle(rail) : null;
          return {
            rail_w: railRect?.width,
            rail_h: railRect?.height,
            knob_w: knobRect?.width,
            knob_h: knobRect?.height,
            knob_left: kStyle?.left,
            knob_top: kStyle?.top,
            knob_bg: kStyle?.backgroundColor,
            knob_bg_img: kStyle?.backgroundImage,
            knob_backdrop: kStyle?.backdropFilter || kStyle?.webkitBackdropFilter,
            rail_bg_img: rStyle?.backgroundImage,
            rail_bg_color: rStyle?.backgroundColor,
            travel_css: getComputedStyle(sw).getPropertyValue('--lang-travel').trim(),
          };
        }''')
        print(f"Desktop metrics: {metrics}")
        assert round(metrics['rail_w']) == 48, f"rail width expected 48 got {metrics['rail_w']}"
        assert round(metrics['rail_h']) == 26, f"rail height expected 26 got {metrics['rail_h']}"
        assert round(metrics['knob_w']) == 24, f"knob width expected 24 got {metrics['knob_w']}"
        assert round(metrics['knob_h']) == 24, f"knob height expected 24 got {metrics['knob_h']}"
        assert metrics['knob_left'] == '0px', f"knob left expected 0px got {metrics['knob_left']}"
        assert metrics['knob_top'] == '0px', f"knob top expected 0px got {metrics['knob_top']}"
        assert 'none' in (metrics['knob_backdrop'] or '').lower(), f"backdrop filter should be none, got {metrics['knob_backdrop']}"
        assert 'rgba(236, 236, 236, 1)' in (metrics['knob_bg'] or '') or 'rgb(236, 236, 236)' in (metrics['knob_bg'] or ''), f"unexpected knob base color: {metrics['knob_bg']}"
        print("Step 3 PASS: Desktop geometry/material checks passed")
    except Exception as e:
        print(f"Step 3 FAIL: {e}")

    try:
        before_url = page.url
        rail_box = await lang_rail.bounding_box()
        start_x = rail_box['x'] + 8
        y = rail_box['y'] + rail_box['height'] / 2

        await page.mouse.move(start_x, y)
        await page.mouse.down()
        await page.mouse.move(start_x + 11, y, steps=5)
        await page.wait_for_timeout(180)

        drag_mid = await page.evaluate('''() => {
          const knob = document.querySelector('[data-testid="lang-switch"] .lang-knob');
          const tr = getComputedStyle(knob).transform;
          if (!tr || tr === 'none') return 0;
          const m = tr.match(/matrix\(([^)]+)\)/);
          if (!m) return 0;
          const vals = m[1].split(',').map(v => parseFloat(v.trim()));
          return vals.length >= 6 ? vals[4] : 0;
        }''')
        print(f"Observed mid-drag translateX: {drag_mid}")
        assert abs(drag_mid - 11) <= 2.5, f"drag not ~1:1 expected ~11 got {drag_mid}"
        assert page.url == before_url, "URL changed during held drag"

        await page.mouse.up()
        await page.wait_for_timeout(900)
        assert '/en/' in page.url, f"Expected navigation to EN after release, got {page.url}"
        print("Step 4 PASS: Drag preview and release commit behavior passed")
    except Exception as e:
        print(f"Step 4 FAIL: {e}")

    try:
        en_switch = page.get_by_test_id("lang-switch").first
        en_rail = en_switch.locator('.lang-rail').first
        en_knob = en_switch.locator('.lang-knob').first

        en_metrics = await page.evaluate('''() => {
          const sw = document.querySelector('[data-testid="lang-switch"]');
          const rail = sw?.querySelector('.lang-rail');
          const knob = sw?.querySelector('.lang-knob');
          const r = getComputedStyle(rail);
          const k = getComputedStyle(knob);
          return {
            rail_img: r.backgroundImage,
            rail_color: r.backgroundColor,
            knob_transform: k.transform
          }
        }''')
        print(f"EN metrics: {en_metrics}")

        rail_box_en = await en_rail.bounding_box()
        sx = rail_box_en['x'] + rail_box_en['width'] - 8
        sy = rail_box_en['y'] + rail_box_en['height'] / 2
        await page.mouse.move(sx, sy)
        await page.mouse.down()
        await page.mouse.move(sx - 3, sy, steps=3)
        await page.mouse.up()
        await page.wait_for_timeout(900)
        assert '/en/' in page.url, "Short drag near EN should remain EN (nearest endpoint)"
        print("Step 5 PASS: Short drag nearest-end behavior passed")
    except Exception as e:
        print(f"Step 5 FAIL: {e}")

    try:
        # Click TR label to navigate back
        tr_link = page.locator('[data-testid="lang-switch"] .lang-opt[lang="tr"]').first
        await tr_link.click(force=True)
        await page.wait_for_timeout(1100)
        assert '/tr/' in page.url, f"Expected back to TR via click, got {page.url}"

        # Keyboard navigation to EN should work
        tr_toggle = page.locator('[data-testid="lang-switch"] .lang-toggle').first
        await tr_toggle.focus()
        await page.keyboard.press('ArrowRight')
        await page.wait_for_timeout(1000)
        assert '/en/' in page.url, f"Expected EN via keyboard ArrowRight, got {page.url}"

        print("Step 6 PASS: Click and keyboard behaviors passed")
    except Exception as e:
        print(f"Step 6 FAIL: {e}")

    try:
        # Narrow tablet dimensions check
        await page.goto('https://darg-clone-1.preview.emergentagent.com/tr/index.html', wait_until='domcontentloaded')
        await page.set_viewport_size({"width": 800, "height": 1024})
        await page.wait_for_timeout(1000)
        tab_metrics = await page.evaluate('''() => {
          const sw = document.querySelector('[data-testid="lang-switch"]');
          const rail = sw?.querySelector('.lang-rail');
          const knob = sw?.querySelector('.lang-knob');
          const railRect = rail?.getBoundingClientRect();
          const knobRect = knob?.getBoundingClientRect();
          const travel = getComputedStyle(sw).getPropertyValue('--lang-travel').trim();
          return {
            rail_w: railRect?.width,
            rail_h: railRect?.height,
            knob_w: knobRect?.width,
            knob_h: knobRect?.height,
            travel
          };
        }''')
        print(f"Narrow tablet metrics: {tab_metrics}")
        assert round(tab_metrics['rail_w']) == 32, f"tablet rail width expected 32 got {tab_metrics['rail_w']}"
        assert round(tab_metrics['rail_h']) == 20, f"tablet rail height expected 20 got {tab_metrics['rail_h']}"
        assert round(tab_metrics['knob_w']) == 18, f"tablet knob width expected 18 got {tab_metrics['knob_w']}"
        assert round(tab_metrics['knob_h']) == 18, f"tablet knob height expected 18 got {tab_metrics['knob_h']}"
        print("Step 7 PASS: Narrow tablet geometry passed")
    except Exception as e:
        print(f"Step 7 FAIL: {e}")

    try:
        await page.screenshot(path='/app/test_reports/screenshots_iter64/automation_output/20261026_155853_5a6111af548b/lang_toggle_800.jpeg', type="jpeg", quality=40, full_page=False)
        print('Step 8 PASS: Captured verification screenshot')
    except Exception as e:
        print(f"Step 8 FAIL: {e}")

    try:
        # Get error messages using specific selectors
        error_text = await page.evaluate("""() => {
        const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));
        return errorElements.map(el => el.textContent).join(", ");
        }""")
        if error_text:
            print(f"Found error message: {error_text}")
        else:
            print("No error messages found on the page")
    except Exception as e:
        print(f"Error while checking error selectors: {e}")
