async def run_test(page, output_dir, page_url):
    try:
        viewports = [
            {"width": 390, "height": 844},
            {"width": 768, "height": 1024},
            {"width": 1024, "height": 1080},
            {"width": 1440, "height": 1080},
            {"width": 1920, "height": 1080},
        ]

        for idx, vp in enumerate(viewports):
            await page.set_viewport_size(vp)
            await page.goto('https://darg-clone-1.preview.emergentagent.com/tr/edsaa.html', wait_until='domcontentloaded')
            await page.wait_for_timeout(800)

            title_ok = await page.locator('[data-testid="edsaa-title"]').is_visible()
            render_ok = await page.locator('[data-testid="edsaa-render"]').is_visible()
            print(f"Viewport {vp['width']}x{vp['height']} title:{title_ok} render:{render_ok}")

            overflow = await page.evaluate("""() => {
                const root = document.documentElement;
                return root.scrollWidth > root.clientWidth + 1;
            }""")
            print(f"Viewport {vp['width']} overflow_x: {overflow}")

            lang_tr = await page.locator('[data-testid="lang-header-tr"]').get_attribute('href')
            lang_en = await page.locator('[data-testid="lang-header-en"]').get_attribute('href')
            print(f"Viewport {vp['width']} lang hrefs: TR={lang_tr}, EN={lang_en}")

            if idx == 0:
                await page.screenshot(path='/app/test_reports/screenshots_iter70_responsive/automation_output/20261027_093914_c31174fbf526/edsaa_390.jpeg', type="jpeg", quality=40, full_page=False)
            if idx == 4:
                await page.screenshot(path='/app/test_reports/screenshots_iter70_responsive/automation_output/20261027_093914_c31174fbf526/edsaa_1920.jpeg', type="jpeg", quality=40, full_page=False)

        await page.set_viewport_size({"width": 390, "height": 844})
        await page.goto('https://darg-clone-1.preview.emergentagent.com/tr/edsaa.html', wait_until='domcontentloaded')
        await page.wait_for_timeout(600)
        await page.click('[data-testid="header-control-1"]', force=True)
        await page.wait_for_timeout(500)
        await page.click('[data-testid="menu-control-3"]', force=True)
        await page.wait_for_timeout(500)
        await page.click('#sideMenu .submenu[data-id="nova-konut"] a[href="edsaa.html"]', force=True)
        await page.wait_for_timeout(800)
        print(f"After mobile menu click URL: {page.url}")

        error_text = await page.evaluate("""() => {
        const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));
        return errorElements.map(el => el.textContent).join(", ");
        }""")
        if error_text:
            print(f"Found error message: {error_text}")
        else:
            print("No error messages found on the page")

        print('Responsive sanity pass completed')
    except Exception as e:
        print(f"Responsive sanity pass failed: {str(e)}")
