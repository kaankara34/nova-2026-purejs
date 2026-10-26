async def run_test(page, output_dir, page_url):
    page.on("console", lambda msg: print(f"CONSOLE: {msg.type}: {msg.text}"))

    try:
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(1200)
        print(f"Step A PASS: loaded {page.url}")
    except Exception as e:
        print(f"Step A FAIL: {e}")

    try:
        rail = page.locator('[data-testid="lang-switch"] .lang-rail').first
        await rail.wait_for(state='visible', timeout=8000)
        box = await rail.bounding_box()
        y = box['y'] + box['height']/2

        # Return gesture from EN: move left then back right and release near EN
        start_x = box['x'] + box['width'] - 7
        await page.mouse.move(start_x, y)
        await page.mouse.down()
        await page.mouse.move(start_x - 9, y, steps=4)  # exceed drag threshold
        await page.mouse.move(start_x - 2, y, steps=3)  # return close to EN end
        await page.mouse.up()
        await page.wait_for_timeout(900)
        assert '/en/' in page.url, f"Expected stay EN after return gesture near EN end, got {page.url}"
        print("Step B PASS: return gesture commits nearest endpoint correctly")
    except Exception as e:
        print(f"Step B FAIL: {e}")

    try:
        # Commit-to-TR via drag beyond midpoint
        rail = page.locator('[data-testid="lang-switch"] .lang-rail').first
        box = await rail.bounding_box()
        y = box['y'] + box['height']/2
        start_x = box['x'] + box['width'] - 6
        await page.mouse.move(start_x, y)
        await page.mouse.down()
        await page.mouse.move(start_x - 14, y, steps=5)
        await page.mouse.up()
        await page.wait_for_timeout(1000)
        assert '/tr/' in page.url, f"Expected TR after drag past midpoint, got {page.url}"
        print("Step C PASS: drag release past midpoint navigates")
    except Exception as e:
        print(f"Step C FAIL: {e}")

    try:
        # Touch-style drag test on TR -> EN
        await page.goto('https://darg-clone-1.preview.emergentagent.com/tr/index.html', wait_until='domcontentloaded')
        await page.set_viewport_size({"width": 390, "height": 844})
        await page.wait_for_timeout(900)

        rail = page.locator('[data-testid="lang-switch"] .lang-rail').first
        box = await rail.bounding_box()
        y = box['y'] + box['height']/2
        sx = box['x'] + 6

        await page.touchscreen.tap(sx, y)
        await page.wait_for_timeout(800)
        assert '/en/' in page.url, f"Expected EN via touch tap, got {page.url}"
        print("Step D PASS: touch interaction navigates")
    except Exception as e:
        print(f"Step D FAIL: {e}")

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
