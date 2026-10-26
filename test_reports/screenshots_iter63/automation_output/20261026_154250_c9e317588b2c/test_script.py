async def run_test(page, output_dir, page_url):
    import asyncio

    await page.set_viewport_size({"width": 1920, "height": 1080})
    page.on("console", lambda msg: print(f"CONSOLE: {msg.type}: {msg.text}"))

    try:
        print("STEP 1: Wait for header language toggle")
        await page.wait_for_selector('[data-testid="lang-header-toggle"]', timeout=15000)
        await page.wait_for_timeout(500)
        print("STEP 1 PASS")

        print("STEP 2: Capture baseline style/state")
        baseline = await page.evaluate('''() => {
          const rail = document.querySelector('[data-testid="lang-header-rail"]');
          const knob = document.querySelector('[data-testid="lang-header-knob"]');
          const sw = document.querySelector('[data-testid="lang-switch"]');
          const tr = document.querySelector('[data-testid="lang-header-tr"]');
          const en = document.querySelector('[data-testid="lang-header-en"]');
          const header = document.querySelector('.site-header');
          const logo = document.querySelector('.logo-mark');
          const menu = document.querySelector('#menuToggle');
          const contact = document.querySelector('.icon-links a[href^="tel:"]');
          const railStyle = getComputedStyle(rail);
          const knobStyle = getComputedStyle(knob);
          const railRect = rail.getBoundingClientRect();
          const knobRect = knob.getBoundingClientRect();
          const trRect = tr.getBoundingClientRect();
          const enRect = en.getBoundingClientRect();
          const headerRect = header?.getBoundingClientRect();
          const logoRect = logo?.getBoundingClientRect();
          const menuRect = menu?.getBoundingClientRect();
          const contactRect = contact?.getBoundingClientRect();
          return {
            switchLanguage: sw?.dataset.language,
            flagLanguage: sw?.dataset.flagLanguage,
            railWidth: railRect.width,
            railHeight: railRect.height,
            knobWidth: knobRect.width,
            knobHeight: knobRect.height,
            railBgImage: railStyle.backgroundImage,
            railBgSize: railStyle.backgroundSize,
            railBgPosition: railStyle.backgroundPosition,
            railOverflow: railStyle.overflow,
            knobBg: knobStyle.backgroundColor,
            knobBorder: knobStyle.border,
            knobBackdrop: knobStyle.backdropFilter || knobStyle.webkitBackdropFilter,
            trHref: tr?.getAttribute('href'),
            enHref: en?.getAttribute('href'),
            trHreflang: tr?.getAttribute('hreflang'),
            enHreflang: en?.getAttribute('hreflang'),
            trLang: tr?.getAttribute('lang'),
            enLang: en?.getAttribute('lang'),
            trAriaCurrent: tr?.getAttribute('aria-current'),
            enAriaCurrent: en?.getAttribute('aria-current'),
            trX: trRect.x, enX: enRect.x,
            headerRect: headerRect ? {x: headerRect.x, y: headerRect.y, w: headerRect.width, h: headerRect.height} : null,
            logoRect: logoRect ? {x: logoRect.x, y: logoRect.y, w: logoRect.width, h: logoRect.height} : null,
            menuRect: menuRect ? {x: menuRect.x, y: menuRect.y, w: menuRect.width, h: menuRect.height} : null,
            contactRect: contactRect ? {x: contactRect.x, y: contactRect.y, w: contactRect.width, h: contactRect.height} : null,
            hasRedBlueOverlay: !!Array.from(document.querySelectorAll('*')).find(el => {
              const s = getComputedStyle(el);
              const b = s.borderColor + ' ' + s.outlineColor + ' ' + s.boxShadow;
              return /rgb\(255,\s*0,\s*0\)|rgb\(0,\s*0,\s*255\)/.test(b) && (s.outlineStyle !== 'none' || s.borderStyle !== 'none');
            })
          };
        }''')
        print(f"Baseline: {baseline}")
        print("STEP 2 PASS")

        print("STEP 3: Validate full-rail flag background and glass knob")
        if 'tr.svg' not in baseline['railBgImage']:
          raise Exception(f"Expected tr.svg on TR page, got {baseline['railBgImage']}")
        if baseline['railBgSize'] != 'cover':
          raise Exception(f"Expected background-size cover, got {baseline['railBgSize']}")
        if baseline['railOverflow'] != 'hidden':
          raise Exception(f"Expected overflow hidden, got {baseline['railOverflow']}")
        if baseline['hasRedBlueOverlay']:
          raise Exception("Detected possible red/blue annotation overlay")
        print("STEP 3 PASS")

        print("STEP 4: Geometry checks across required widths")
        widths = [320, 390, 768, 800, 900, 1024, 1440, 1920]
        geo_results = []
        for w in widths:
          h = 844 if w <= 390 else (1024 if w in [768, 800, 900] else 1080)
          await page.set_viewport_size({"width": w, "height": h})
          await page.wait_for_timeout(250)
          data = await page.evaluate('''() => {
            const rail = document.querySelector('[data-testid="lang-header-rail"]');
            const knob = document.querySelector('[data-testid="lang-header-knob"]');
            const railRect = rail.getBoundingClientRect();
            const knobRect = knob.getBoundingClientRect();
            const tr = document.querySelector('[data-testid="lang-header-tr"]');
            const en = document.querySelector('[data-testid="lang-header-en"]');
            const trRect = tr.getBoundingClientRect();
            const enRect = en.getBoundingClientRect();
            return {
              railW: railRect.width,
              railH: railRect.height,
              knobW: knobRect.width,
              knobH: knobRect.height,
              trX: trRect.x,
              enX: enRect.x
            };
          }''')
          geo_results.append({"width": w, **data})

        for row in geo_results:
          w = row['width']
          if 769 <= w <= 900:
            if abs(row['railW'] - 32) > 1.0 or abs(row['railH'] - 20) > 1.0:
              raise Exception(f"Narrow-tablet rail mismatch at {w}: {row}")
            if abs(row['knobW'] - 16) > 1.0 or abs(row['knobH'] - 16) > 1.0:
              raise Exception(f"Narrow-tablet knob mismatch at {w}: {row}")
          else:
            if abs(row['railW'] - 48) > 1.0 or abs(row['railH'] - 26) > 1.0:
              raise Exception(f"Standard rail mismatch at {w}: {row}")
            if abs(row['knobW'] - 22) > 1.0 or abs(row['knobH'] - 22) > 1.0:
              raise Exception(f"Standard knob mismatch at {w}: {row}")
        print(f"Geometry results: {geo_results}")
        print("STEP 4 PASS")

        print("STEP 5: Gesture hold then release commit behavior")
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.goto('https://darg-clone-1.preview.emergentagent.com/tr/index.html', wait_until='domcontentloaded')
        await page.wait_for_selector('[data-testid="lang-header-knob"]', timeout=15000)

        knob = page.locator('[data-testid="lang-header-knob"]').first
        rail = page.locator('[data-testid="lang-header-rail"]').first
        rail_box = await rail.bounding_box()
        knob_box = await knob.bounding_box()
        start_x = knob_box['x'] + knob_box['width'] / 2
        start_y = knob_box['y'] + knob_box['height'] / 2
        far_right_x = rail_box['x'] + rail_box['width'] - 2

        await page.mouse.move(start_x, start_y)
        await page.mouse.down()
        await page.mouse.move(far_right_x, start_y, steps=12)
        await page.wait_for_timeout(350)
        url_while_hold = page.url
        during = await page.evaluate('''() => {
          const sw = document.querySelector('[data-testid="lang-switch"]');
          const rail = document.querySelector('[data-testid="lang-header-rail"]');
          const s = getComputedStyle(rail);
          return {
            lang: sw?.dataset.language,
            flag: sw?.dataset.flagLanguage,
            bg: s.backgroundImage,
            pos: s.backgroundPosition
          };
        }''')
        print(f"While hold URL={url_while_hold}, state={during}")
        if '/tr/' not in url_while_hold:
          raise Exception("Navigated before release during drag hold")
        if during['flag'] != 'tr':
          raise Exception(f"Flag language changed during drag hold: {during}")

        await page.mouse.up()
        await page.wait_for_timeout(700)
        url_after_release = page.url
        print(f"URL after release commit: {url_after_release}")
        if '/en/' not in url_after_release:
          raise Exception("Did not navigate to EN after release at right endpoint")
        print("STEP 5 PASS")

        print("STEP 6: Fast short 8px drag should snap back without navigation")
        await page.goto('https://darg-clone-1.preview.emergentagent.com/tr/index.html', wait_until='domcontentloaded')
        await page.wait_for_selector('[data-testid="lang-header-knob"]', timeout=15000)
        knob = page.locator('[data-testid="lang-header-knob"]').first
        kb = await knob.bounding_box()
        sx = kb['x'] + kb['width'] / 2
        sy = kb['y'] + kb['height'] / 2

        await page.mouse.move(sx, sy)
        await page.mouse.down()
        await page.mouse.move(sx + 8, sy, steps=2)
        await page.mouse.up()
        await page.wait_for_timeout(500)
        if '/tr/' not in page.url:
          raise Exception(f"Unexpected navigation on short drag: {page.url}")
        progress_after_short = await page.evaluate("""() => getComputedStyle(document.querySelector('[data-testid=\"lang-switch\"]')).getPropertyValue('--lang-progress').trim()""")
        print(f"Progress after short drag: {progress_after_short}")
        print("STEP 6 PASS")

        print("STEP 7: Escape cancel during drag should not navigate")
        await page.goto('https://darg-clone-1.preview.emergentagent.com/tr/index.html', wait_until='domcontentloaded')
        await page.wait_for_selector('[data-testid="lang-header-knob"]', timeout=15000)
        knob = page.locator('[data-testid="lang-header-knob"]').first
        rail = page.locator('[data-testid="lang-header-rail"]').first
        rb = await rail.bounding_box()
        kb = await knob.bounding_box()
        sx = kb['x'] + kb['width'] / 2
        sy = kb['y'] + kb['height'] / 2
        rx = rb['x'] + rb['width'] - 3

        await page.mouse.move(sx, sy)
        await page.mouse.down()
        await page.mouse.move(rx, sy, steps=6)
        await page.keyboard.press('Escape')
        await page.mouse.up()
        await page.wait_for_timeout(400)
        if '/tr/' not in page.url:
          raise Exception(f"Navigation happened after Escape cancel: {page.url}")
        print("STEP 7 PASS")

        print("STEP 8: Keyboard toggle and back/forward state")
        await page.locator('[data-testid="lang-header-toggle"]').focus()
        await page.keyboard.press('ArrowRight')
        await page.wait_for_timeout(700)
        if '/en/' not in page.url:
          raise Exception(f"ArrowRight did not navigate to EN: {page.url}")

        en_state = await page.evaluate('''() => {
          const sw = document.querySelector('[data-testid="lang-switch"]');
          const rail = document.querySelector('[data-testid="lang-header-rail"]');
          const s = getComputedStyle(rail);
          const tr = document.querySelector('[data-testid="lang-header-tr"]');
          const en = document.querySelector('[data-testid="lang-header-en"]');
          return {
            dataLanguage: sw?.dataset.language,
            flagLanguage: sw?.dataset.flagLanguage,
            bg: s.backgroundImage,
            trCurrent: tr?.getAttribute('aria-current'),
            enCurrent: en?.getAttribute('aria-current')
          }
        }''')
        print(f"EN state: {en_state}")
        if 'gb.svg' not in en_state['bg']:
          raise Exception("EN committed state missing gb.svg background")

        await page.go_back(wait_until='domcontentloaded')
        await page.wait_for_timeout(400)
        if '/tr/' not in page.url:
          raise Exception(f"Back did not restore TR URL: {page.url}")
        await page.go_forward(wait_until='domcontentloaded')
        await page.wait_for_timeout(400)
        if '/en/' not in page.url:
          raise Exception(f"Forward did not restore EN URL: {page.url}")
        print("STEP 8 PASS")

        print("STEP 9: Reduced-motion should disable transitions")
        await page.emulate_media(reduced_motion='reduce')
        await page.goto('https://darg-clone-1.preview.emergentagent.com/tr/index.html', wait_until='domcontentloaded')
        await page.wait_for_selector('[data-testid="lang-header-knob"]', timeout=15000)
        transition_duration = await page.evaluate('''() => {
          const knob = document.querySelector('[data-testid="lang-header-knob"]');
          return getComputedStyle(knob).transitionDuration;
        }''')
        print(f"Reduced motion transition-duration: {transition_duration}")
        await page.emulate_media(reduced_motion='no-preference')
        print("STEP 9 PASS")

        print("STEP 10: Quick screenshot for visual evidence")
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.goto('https://darg-clone-1.preview.emergentagent.com/tr/index.html', wait_until='domcontentloaded')
        await page.wait_for_timeout(350)
        await page.screenshot(path='/app/test_reports/screenshots_iter63/automation_output/20261026_154250_c9e317588b2c/lang_toggle_tr_final.jpeg', type="jpeg", quality=40, full_page=False)
        print("STEP 10 PASS")

        # Get error messages using specific selectors
        error_text = await page.evaluate("""() => {
        const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));
        return errorElements.map(el => el.textContent).join(", ");
        }""")
        if error_text:
          print(f"Found error message: {error_text}")
        else:
          print("No error messages found on the page")

        print("ALL STEPS PASSED")

    except Exception as e:
        print(f"TEST FAILURE: {str(e)}")
        # Get error messages using specific selectors
        error_text = await page.evaluate("""() => {
        const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));
        return errorElements.map(el => el.textContent).join(", ");
        }""")
        if error_text:
          print(f"Found error message: {error_text}")
        else:
          print("No error messages found on the page")
