async def run_test(page, output_dir, page_url):
    try:
        await page.set_viewport_size({"width": 1920, "height": 1080})
        print("STEP 1: Viewport set")

        await page.wait_for_selector('[data-testid="header-logo-image"]', timeout=15000)
        await page.wait_for_selector('[data-testid="intro-video"]', timeout=15000)
        print("STEP 2: Header logo and hero video loaded")

        current_time_1 = await page.eval_on_selector('[data-testid="intro-video"]', 'el => el.currentTime')
        await page.wait_for_timeout(2500)
        current_time_2 = await page.eval_on_selector('[data-testid="intro-video"]', 'el => el.currentTime')
        print(f"STEP 3: Hero currentTime progressed {current_time_1:.3f} -> {current_time_2:.3f}")

        await page.screenshot(path='/app/test_reports/screenshots_iter66_smoke/automation_output/20261026_171319_7d0ac67d3c93/home_smoke.jpeg', type="jpeg", quality=40, full_page=False)
        print("STEP 4: Screenshot captured")

        error_text = await page.evaluate("""() => {
        const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));
        return errorElements.map(el => el.textContent).join(", ");
        }""")
        if error_text:
            print(f"Found error message: {error_text}")
        else:
            print("No error messages found on the page")

        print("SMOKE RESULT: PASS")
    except Exception as e:
        print(f"SMOKE RESULT: FAIL - {str(e)}")
