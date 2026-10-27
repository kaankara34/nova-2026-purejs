async def run_test(page, output_dir, page_url):
    try:
        await page.set_viewport_size({"width": 1920, "height": 1080})
        print("Step 1: Viewport set")

        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(1200)
        print("Step 2: Page loaded")

        title_visible = await page.locator('[data-testid="edsaa-title"]').is_visible()
        print(f"Step 3: EDSAA title visible: {title_visible}")

        await page.click('[data-testid="header-control-1"]', force=True)
        await page.wait_for_timeout(500)
        print("Step 4: Opened menu")

        nova_btn = page.locator('[data-testid="menu-control-3"]').first
        await nova_btn.click(force=True)
        await page.wait_for_timeout(500)
        print("Step 5: Opened NOVA submenu")

        edsaa_count = await page.locator('#sideMenu .submenu[data-id="nova-konut"] a[href="edsaa.html"]').count()
        print(f"Step 6: EDSAA link count in NOVA submenu: {edsaa_count}")

        active_page_count = await page.locator('#sideMenu .submenu[data-id="nova-konut"] a[href="edsaa.html"][aria-current="page"]').count()
        print(f"Step 7: EDSAA active aria-current links: {active_page_count}")

        has_register = await page.locator('#register').count()
        print(f"Step 8: #register sections found: {has_register}")

        await page.screenshot(path='/app/test_reports/screenshots_iter70_frontend_smoke/automation_output/20261027_093634_b6f200d227f1/edsaa_menu_state.jpeg', type="jpeg", quality=40, full_page=False)
        print("Step 9: Captured screenshot")

        error_text = await page.evaluate("""() => {
        const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));
        return errorElements.map(el => el.textContent).join(", ");
        }""")
        if error_text:
            print(f"Found error message: {error_text}")
        else:
            print("No error messages found on the page")

        print("UI smoke completed successfully")
    except Exception as e:
        print(f"UI smoke failed: {str(e)}")
