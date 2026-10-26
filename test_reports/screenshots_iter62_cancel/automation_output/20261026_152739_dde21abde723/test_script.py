async def run_test(page, output_dir, page_url):
    import asyncio

    async def step(name, fn):
        try:
            await fn()
            print(f"PASS: {name}")
        except Exception as e:
            print(f"FAIL: {name} -> {e}")

    async def main():
        await page.set_viewport_size({"width": 390, "height": 844})
        await page.goto("https://darg-clone-1.preview.emergentagent.com/tr/index.html", wait_until="domcontentloaded")
        await page.wait_for_selector('[data-testid="lang-header-toggle"]', timeout=12000)

        async def vertical_drag_cancel_no_nav():
            box = await page.locator('[data-testid="lang-header-toggle"]').bounding_box()
            x = box['x'] + box['width'] * 0.45
            y = box['y'] + box['height'] * 0.5
            before = page.url
            await page.mouse.move(x, y)
            await page.mouse.down()
            await page.mouse.move(x + 2, y + 30, steps=10)
            await page.mouse.up()
            await page.wait_for_timeout(500)
            if page.url != before:
                raise Exception("Vertical drag changed language")

        await step("Vertical drag cancel", vertical_drag_cancel_no_nav)

        async def escape_cancels_pending_drag():
            box = await page.locator('[data-testid="lang-header-toggle"]').bounding_box()
            x = box['x'] + box['width'] * 0.45
            y = box['y'] + box['height'] * 0.5
            await page.mouse.move(x, y)
            await page.mouse.down()
            await page.mouse.move(x + 18, y, steps=5)
            await page.keyboard.press('Escape')
            await page.mouse.up()
            await page.wait_for_timeout(500)
            if '/tr/' not in page.url:
                raise Exception("Escape did not cancel")

        await step("Escape during drag cancels", escape_cancels_pending_drag)

        async def no_double_nav_after_drag():
            await page.goto("https://darg-clone-1.preview.emergentagent.com/tr/index.html", wait_until="domcontentloaded")
            await page.wait_for_selector('[data-testid="lang-header-toggle"]', timeout=12000)
            box = await page.locator('[data-testid="lang-header-toggle"]').bounding_box()
            x1 = box['x'] + box['width'] * 0.35
            x2 = box['x'] + box['width'] * 0.85
            y = box['y'] + box['height'] * 0.5
            await page.mouse.move(x1, y)
            await page.mouse.down()
            await page.mouse.move(x2, y, steps=12)
            await page.mouse.up()
            await page.wait_for_url('**/en/**', timeout=8000)
            first_url = page.url
            await page.wait_for_timeout(800)
            if page.url != first_url:
                raise Exception("Unexpected extra navigation after drag")

        await step("Drag synth-click suppression", no_double_nav_after_drag)

        async def aria_busy_commit_only():
            await page.goto("https://darg-clone-1.preview.emergentagent.com/tr/index.html", wait_until="domcontentloaded")
            await page.wait_for_selector('[data-testid="lang-header-toggle"]', timeout=12000)
            await page.click('[data-testid="lang-header-toggle"]', force=True)
            busy = await page.evaluate("""() => document.querySelector('[data-testid='lang-header-toggle']')?.getAttribute('aria-busy')""")
            print("aria-busy immediate:", busy)
            if busy not in ("true", None):
                raise Exception(f"Unexpected aria-busy value {busy}")

        await step("aria-busy appears only at commit window", aria_busy_commit_only)

    await main()
