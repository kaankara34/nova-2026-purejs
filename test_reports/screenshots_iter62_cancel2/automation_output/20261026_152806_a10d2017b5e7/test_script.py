async def run_test(page, output_dir, page_url):
    import asyncio

    async def run():
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.goto("https://darg-clone-1.preview.emergentagent.com/tr/index.html", wait_until="domcontentloaded")
        await page.wait_for_selector('[data-testid="lang-header-toggle"]', timeout=12000)

        try:
            box = await page.locator('[data-testid="lang-header-toggle"]').bounding_box()
            x1 = box['x'] + box['width'] * 0.35
            x2 = box['x'] + box['width'] * 0.85
            y = box['y'] + box['height'] * 0.5
            await page.mouse.move(x1, y)
            await page.mouse.down()
            await page.mouse.move(x2, y, steps=12)
            await page.mouse.up()
            await page.wait_for_url('**/en/**', timeout=9000)
            first_url = page.url
            await page.wait_for_timeout(1000)
            print('URL after drag and settle:', page.url)
            if page.url != first_url:
                raise Exception('Second navigation happened')
            print('PASS: drag synth-click suppression verified')
        except Exception as e:
            print(f'FAIL: drag synth-click suppression -> {e}')

        try:
            await page.goto("https://darg-clone-1.preview.emergentagent.com/tr/index.html", wait_until="domcontentloaded")
            await page.wait_for_selector('[data-testid="lang-header-toggle"]', timeout=12000)
            await page.click('[data-testid="lang-header-toggle"]', force=True)
            busy = await page.evaluate("""() => document.querySelector('[data-testid=\"lang-header-toggle\"]')?.getAttribute('aria-busy')""")
            print('aria-busy immediate:', busy)
            print('PASS: aria-busy probe executed')
        except Exception as e:
            print(f'FAIL: aria-busy probe -> {e}')

        try:
            error_text = await page.evaluate("""() => {
    const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));
    return errorElements.map(el => el.textContent).join(", ");
    }""")
            if error_text:
                print(f"Found error message: {error_text}")
            else:
                print("No error messages found on the page")
        except Exception as e:
            print(f"FAIL: error scan -> {e}")

    await run()
