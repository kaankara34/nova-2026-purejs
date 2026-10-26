async def run_test(page, output_dir, page_url):
    try:
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.wait_for_load_state('domcontentloaded')
        await page.wait_for_timeout(1000)

        knob = page.locator('[data-testid="lang-switch"] .lang-knob').first
        await knob.screenshot(path='/app/test_reports/screenshots_iter64_pixels/knob_tr.png')
        print('Saved TR knob screenshot')

        en_link = page.locator('[data-testid="lang-switch"] .lang-opt[lang="en"]').first
        await en_link.click(force=True)
        await page.wait_for_timeout(1000)

        knob_en = page.locator('[data-testid="lang-switch"] .lang-knob').first
        await knob_en.screenshot(path='/app/test_reports/screenshots_iter64_pixels/knob_en.png')
        print('Saved EN knob screenshot')

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
        print(f"Pixel capture flow error: {e}")
