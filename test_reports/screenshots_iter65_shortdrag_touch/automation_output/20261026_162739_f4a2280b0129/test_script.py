async def run_test(page, output_dir, page_url):
    try:
        print('Step 1: Load EN page desktop')
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.goto('https://darg-clone-1.preview.emergentagent.com/en/index.html', wait_until='domcontentloaded')
        await page.wait_for_selector('[data-testid="lang-header-knob"]', timeout=8000)
        print('PASS: EN page loaded')

        print('Step 2: Short 8px drag from knob center should not navigate')
        knob = page.locator('[data-testid="lang-header-knob"]')
        kbox = await knob.bounding_box()
        if not kbox:
          raise Exception('Knob box missing')
        sx = kbox['x'] + kbox['width'] / 2
        sy = kbox['y'] + kbox['height'] / 2
        await page.mouse.move(sx, sy)
        await page.mouse.down()
        await page.mouse.move(sx - 8, sy)
        await page.mouse.up()
        await page.wait_for_timeout(700)
        short_url = page.url
        print(f'URL after knob short drag: {short_url}')
        if '/en/' not in short_url:
          raise Exception('Short knob drag navigated unexpectedly')
        print('PASS: Short drag cancel validated from knob center')

        print('Step 3: Touch drag tests via CDP at 390px')
        await page.set_viewport_size({"width": 390, "height": 844})
        await page.goto('https://darg-clone-1.preview.emergentagent.com/en/index.html', wait_until='domcontentloaded')
        await page.wait_for_selector('[data-testid="lang-header-toggle"]', timeout=8000)
        client = await page.context.new_cdp_session(page)
        await client.send('Emulation.setTouchEmulationEnabled', {'enabled': True, 'maxTouchPoints': 1})

        tknob = page.locator('[data-testid="lang-header-knob"]')
        tbox = await tknob.bounding_box()
        if not tbox:
          raise Exception('Touch knob box missing')
        cx = tbox['x'] + tbox['width'] / 2
        cy = tbox['y'] + tbox['height'] / 2

        await client.send('Input.dispatchTouchEvent', {
          'type': 'touchStart',
          'touchPoints': [{'x': cx, 'y': cy, 'radiusX': 2, 'radiusY': 2, 'force': 1, 'id': 1}]
        })
        await client.send('Input.dispatchTouchEvent', {
          'type': 'touchMove',
          'touchPoints': [{'x': cx - 14, 'y': cy, 'radiusX': 2, 'radiusY': 2, 'force': 1, 'id': 1}]
        })
        await page.wait_for_timeout(450)
        hold_url = page.url
        await client.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
        await page.wait_for_timeout(750)
        release_url = page.url
        print(f'Touch 14px hold/release URL: {hold_url} -> {release_url}')
        if '/en/' not in hold_url:
          raise Exception('Touch hold navigated before release')
        if '/tr/' not in release_url:
          raise Exception('Touch release 14px did not navigate to TR')
        print('PASS: Touch 14px drag commit works')

        await page.goto('https://darg-clone-1.preview.emergentagent.com/en/index.html', wait_until='domcontentloaded')
        await page.wait_for_selector('[data-testid="lang-header-knob"]', timeout=8000)
        tbox2 = await page.locator('[data-testid="lang-header-knob"]').bounding_box()
        sx2 = tbox2['x'] + tbox2['width'] / 2
        sy2 = tbox2['y'] + tbox2['height'] / 2
        await client.send('Input.dispatchTouchEvent', {
          'type': 'touchStart',
          'touchPoints': [{'x': sx2, 'y': sy2, 'radiusX': 2, 'radiusY': 2, 'force': 1, 'id': 1}]
        })
        await client.send('Input.dispatchTouchEvent', {
          'type': 'touchMove',
          'touchPoints': [{'x': sx2 - 8, 'y': sy2, 'radiusX': 2, 'radiusY': 2, 'force': 1, 'id': 1}]
        })
        await client.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
        await page.wait_for_timeout(750)
        short_touch_url = page.url
        print(f'Touch 8px short drag URL: {short_touch_url}')
        if '/en/' not in short_touch_url:
          raise Exception('Short touch 8px incorrectly navigated')
        print('PASS: Touch short drag returns/no nav')

        # Get error messages using specific selectors
        error_text = await page.evaluate("""() => {
        const errorElements = Array.from(document.querySelectorAll('.error, [class*=\"error\"], [id*=\"error\"]'));
        return errorElements.map(el => el.textContent).join(', ');
        }""")
        if error_text:
          print(f"Found error message: {error_text}")
        else:
          print("No error messages found on the page")

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
