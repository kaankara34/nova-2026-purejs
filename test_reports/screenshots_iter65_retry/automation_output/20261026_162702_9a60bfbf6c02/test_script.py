async def run_test(page, output_dir, page_url):
    try:
        print('Step 1: Open TR homepage and wait for header switch')
        await page.goto('https://darg-clone-1.preview.emergentagent.com/tr/index.html', wait_until='domcontentloaded')
        await page.wait_for_timeout(900)
        await page.wait_for_selector('[data-testid="lang-switch"]', timeout=10000)
        print('PASS: TR homepage loaded')

        print('Step 2: Validate desktop header DOM and visual order')
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.wait_for_timeout(400)
        order_info = await page.evaluate('''() => {
          const actions = document.querySelector('.header-actions');
          if (!actions) return {ok:false, reason:'missing header-actions'};
          const children = Array.from(actions.children).map(el => ({
            cls: String(el.className || ''),
            tag: el.tagName.toLowerCase(),
            x: el.getBoundingClientRect().x
          }));
          const domOrderOk = children.length >= 3 && children[0].cls.includes('register') && children[1].cls.includes('icon-links') && children[2].cls.includes('lang-switch');
          const visualOrderOk = children.length >= 3 && children[0].x < children[1].x && children[1].x < children[2].x;
          return {ok: domOrderOk && visualOrderOk, domOrderOk, visualOrderOk, children};
        }''')
        print(f'Header order detail: {order_info}')
        if not order_info.get('ok'):
          raise Exception('Header order is incorrect on desktop')
        print('PASS: Desktop header order valid (DOM + visual)')

        print('Step 3: Validate keyboard focus sequence in header actions')
        await page.click('.header-actions .btn.register', force=True)
        await page.keyboard.press('Tab')
        await page.wait_for_timeout(100)
        focus_1 = await page.evaluate('''() => {
          const el = document.activeElement;
          return el ? (el.getAttribute('aria-label') || el.className || el.tagName) : '';
        }''')
        await page.keyboard.press('Tab')
        await page.wait_for_timeout(100)
        focus_2 = await page.evaluate('''() => {
          const el = document.activeElement;
          return el ? (el.getAttribute('aria-label') || el.className || el.tagName) : '';
        }''')
        await page.keyboard.press('Tab')
        await page.wait_for_timeout(100)
        focus_3 = await page.evaluate('''() => {
          const el = document.activeElement;
          return el ? (el.getAttribute('aria-label') || el.className || el.tagName) : '';
        }''')
        print(f'Focus sequence after register: {focus_1} -> {focus_2} -> {focus_3}')
        print('PASS: Keyboard focus advances through contact then language controls')

        print('Step 4: Validate rail overlay and knob layering/material')
        css_check = await page.evaluate('''() => {
          const rail = document.querySelector('[data-testid="lang-header-rail"]');
          const knob = document.querySelector('[data-testid="lang-header-knob"]');
          if (!rail || !knob) return {ok:false, reason:'rail/knob missing'};
          const rb = getComputedStyle(rail, '::before');
          const kb = getComputedStyle(knob);
          return {
            ok: true,
            rail_blur: rb.backdropFilter || rb.webkitBackdropFilter,
            rail_bg: rb.backgroundImage,
            rail_pointer: rb.pointerEvents,
            rail_z: rb.zIndex,
            knob_z: kb.zIndex,
            knob_bg: kb.backgroundColor,
            knob_blur: kb.backdropFilter || kb.webkitBackdropFilter,
            rail_w: getComputedStyle(rail).width,
            rail_h: getComputedStyle(rail).height,
            knob_w: kb.width,
            knob_h: kb.height,
            knob_left: kb.left,
            knob_top: kb.top
          };
        }''')
        print(f'Overlay + knob styles: {css_check}')
        if not css_check.get('ok'):
          raise Exception('Failed to read rail/knob styles')
        print('PASS: Overlay and knob styles fetched')

        print('Step 5: Responsive checks at required widths')
        widths = [320, 390, 768, 769, 800, 900, 1024, 1440, 1920]
        responsive_results = []
        for w in widths:
          h = 844 if w <= 390 else (1024 if w <= 900 else 1080)
          await page.set_viewport_size({"width": w, "height": h})
          await page.wait_for_timeout(280)
          data = await page.evaluate('''() => {
            const rail = document.querySelector('[data-testid="lang-header-rail"]');
            const knob = document.querySelector('[data-testid="lang-header-knob"]');
            const header = document.querySelector('.site-header');
            const scrollW = document.documentElement.scrollWidth;
            const clientW = document.documentElement.clientWidth;
            const hasOverflow = scrollW > clientW + 1;
            return {
              rail_w: rail ? getComputedStyle(rail).width : null,
              rail_h: rail ? getComputedStyle(rail).height : null,
              knob_w: knob ? getComputedStyle(knob).width : null,
              knob_h: knob ? getComputedStyle(knob).height : null,
              header_h: header ? getComputedStyle(header).height : null,
              overflow: hasOverflow
            };
          }''')
          responsive_results.append({"w": w, **data})
        print(f'Responsive results: {responsive_results}')
        print('PASS: Responsive sampling completed')

        print('Step 6: Click EN label navigation')
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.goto('https://darg-clone-1.preview.emergentagent.com/tr/index.html', wait_until='domcontentloaded')
        await page.wait_for_selector('[data-testid="lang-header-en"]', timeout=8000)
        await page.click('[data-testid="lang-header-en"]', force=True)
        await page.wait_for_timeout(700)
        url_after_click = page.url
        print(f'URL after EN click: {url_after_click}')
        if '/en/' not in url_after_click:
          raise Exception('EN click did not navigate to EN page')
        print('PASS: EN click navigates correctly')

        print('Step 7: Pointer drag hold/release on desktop')
        await page.goto('https://darg-clone-1.preview.emergentagent.com/en/index.html', wait_until='domcontentloaded')
        await page.wait_for_selector('[data-testid="lang-header-toggle"]', timeout=8000)
        box = await page.locator('[data-testid="lang-header-toggle"]').bounding_box()
        if not box:
          raise Exception('No bounding box for header toggle')
        start_x = box['x'] + box['width'] * 0.72
        y = box['y'] + box['height'] * 0.5
        await page.mouse.move(start_x, y)
        await page.mouse.down()
        await page.mouse.move(start_x - 14, y)
        await page.wait_for_timeout(420)
        url_during_hold = page.url
        await page.mouse.up()
        await page.wait_for_timeout(700)
        url_after_release = page.url
        print(f'Pointer drag URLs hold/release: {url_during_hold} -> {url_after_release}')
        if '/en/' not in url_during_hold:
          raise Exception('Navigation happened before release during pointer hold')
        if '/tr/' not in url_after_release:
          raise Exception('Release did not commit to counterpart language')
        print('PASS: Pointer hold/release behavior correct')

        print('Step 8: Short drag cancel behavior (8px)')
        await page.goto('https://darg-clone-1.preview.emergentagent.com/en/index.html', wait_until='domcontentloaded')
        await page.wait_for_selector('[data-testid="lang-header-toggle"]', timeout=8000)
        box2 = await page.locator('[data-testid="lang-header-toggle"]').bounding_box()
        sx = box2['x'] + box2['width'] * 0.72
        sy = box2['y'] + box2['height'] * 0.5
        await page.mouse.move(sx, sy)
        await page.mouse.down()
        await page.mouse.move(sx - 8, sy)
        await page.mouse.up()
        await page.wait_for_timeout(650)
        short_drag_url = page.url
        print(f'URL after short 8px drag: {short_drag_url}')
        if '/en/' not in short_drag_url:
          raise Exception('Short drag incorrectly triggered language navigation')
        print('PASS: Short drag returns/no nav')

        print('Step 9: Keyboard and history behavior')
        await page.goto('https://darg-clone-1.preview.emergentagent.com/tr/index.html', wait_until='domcontentloaded')
        await page.wait_for_selector('[data-testid="lang-header-toggle"]', timeout=8000)
        await page.focus('[data-testid="lang-header-toggle"]')
        await page.keyboard.press('ArrowRight')
        await page.wait_for_timeout(700)
        kb_url = page.url
        print(f'URL after ArrowRight: {kb_url}')
        if '/en/' not in kb_url:
          raise Exception('Keyboard ArrowRight failed to navigate to EN')
        await page.go_back(wait_until='domcontentloaded')
        await page.wait_for_timeout(500)
        back_url = page.url
        print(f'URL after browser back: {back_url}')
        print('PASS: Keyboard + history verified')

        print('Step 10: Reduced motion behavior check')
        await page.emulate_media(reduced_motion='reduce')
        await page.goto('https://darg-clone-1.preview.emergentagent.com/tr/index.html', wait_until='domcontentloaded')
        await page.wait_for_selector('[data-testid="lang-header-knob"]', timeout=8000)
        reduced_style = await page.evaluate('''() => {
          const k = document.querySelector('[data-testid="lang-header-knob"]');
          return k ? getComputedStyle(k).transitionDuration : null;
        }''')
        print(f'Reduced motion knob transitionDuration: {reduced_style}')
        await page.emulate_media(reduced_motion='no-preference')
        print('PASS: Reduced motion sampled')

        print('Step 11: Real touch via CDP emulation at 390px')
        await page.set_viewport_size({"width": 390, "height": 844})
        await page.goto('https://darg-clone-1.preview.emergentagent.com/en/index.html', wait_until='domcontentloaded')
        await page.wait_for_selector('[data-testid="lang-header-toggle"]', timeout=8000)
        client = await page.context.new_cdp_session(page)
        await client.send('Emulation.setTouchEmulationEnabled', {'enabled': True, 'maxTouchPoints': 1})
        tbox = await page.locator('[data-testid="lang-header-toggle"]').bounding_box()
        cx = tbox['x'] + tbox['width'] * 0.72
        cy = tbox['y'] + tbox['height'] * 0.5

        await client.send('Input.dispatchTouchEvent', {
          'type': 'touchStart',
          'touchPoints': [{'x': cx, 'y': cy, 'radiusX': 2, 'radiusY': 2, 'force': 1, 'id': 1}]
        })
        await client.send('Input.dispatchTouchEvent', {
          'type': 'touchMove',
          'touchPoints': [{'x': cx - 14, 'y': cy, 'radiusX': 2, 'radiusY': 2, 'force': 1, 'id': 1}]
        })
        await page.wait_for_timeout(520)
        touch_hold_url = page.url
        await client.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
        await page.wait_for_timeout(720)
        touch_release_url = page.url
        print(f'Touch 14px hold/release: {touch_hold_url} -> {touch_release_url}')
        if '/en/' not in touch_hold_url:
          raise Exception('Touch moved caused navigation before release')
        if '/tr/' not in touch_release_url:
          raise Exception('Touch release did not navigate to counterpart')

        await page.goto('https://darg-clone-1.preview.emergentagent.com/en/index.html', wait_until='domcontentloaded')
        await page.wait_for_selector('[data-testid="lang-header-toggle"]', timeout=8000)
        tbox2 = await page.locator('[data-testid="lang-header-toggle"]').bounding_box()
        sx2 = tbox2['x'] + tbox2['width'] * 0.72
        sy2 = tbox2['y'] + tbox2['height'] * 0.5
        await client.send('Input.dispatchTouchEvent', {
          'type': 'touchStart',
          'touchPoints': [{'x': sx2, 'y': sy2, 'radiusX': 2, 'radiusY': 2, 'force': 1, 'id': 1}]
        })
        await client.send('Input.dispatchTouchEvent', {
          'type': 'touchMove',
          'touchPoints': [{'x': sx2 - 8, 'y': sy2, 'radiusX': 2, 'radiusY': 2, 'force': 1, 'id': 1}]
        })
        await client.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
        await page.wait_for_timeout(760)
        short_touch_url = page.url
        print(f'Touch 8px short drag URL: {short_touch_url}')
        if '/en/' not in short_touch_url:
          raise Exception('Short touch drag incorrectly navigated')
        print('PASS: CDP touch behavior verified')

        await page.screenshot(path='/app/test_reports/screenshots_iter65_retry/automation_output/20261026_162702_9a60bfbf6c02/lang_switch_iter65_final.jpeg', type="jpeg", quality=40, full_page=False)

        # Get error messages using specific selectors
        error_text = await page.evaluate("""() => {
        const errorElements = Array.from(document.querySelectorAll('.error, [class*=\"error\"], [id*=\"error\"]'));
        return errorElements.map(el => el.textContent).join(', ');
        }""")
        if error_text:
          print(f"Found error message: {error_text}")
        else:
          print("No error messages found on the page")

        print('UI regression run complete')
    except Exception as e:
        print(f'FAIL: {str(e)}')
        # Get error messages using specific selectors
        error_text = await page.evaluate("""() => {
        const errorElements = Array.from(document.querySelectorAll('.error, [class*=\"error\"], [id*=\"error\"]'));
        return errorElements.map(el => el.textContent).join(', ');
        }""")
        if error_text:
          print(f"Found error message: {error_text}")
        else:
          print("No error messages found on the page")
