async def run_test(page, output_dir, page_url):
    await page.set_viewport_size({"width": 1920, "height": 1080})
    try:
        await page.wait_for_selector('[data-testid="lang-header-knob"]', timeout=15000)
        await page.wait_for_timeout(300)
        knob = await page.evaluate('''() => {
          const k = document.querySelector('[data-testid="lang-header-knob"]');
          const s = getComputedStyle(k);
          return { border: s.border, shadow: s.boxShadow, bg: s.backgroundColor };
        }''')
        print(f"EN knob style: {knob}")
        await page.screenshot(path='/app/test_reports/screenshots_iter63_en/automation_output/20261026_154329_efd5bbdd6f97/lang_toggle_en_final.jpeg', type="jpeg", quality=40, full_page=False)
        print('EN screenshot done')
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
        print(f"Error: {str(e)}")
