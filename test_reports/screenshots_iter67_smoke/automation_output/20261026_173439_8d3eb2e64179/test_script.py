async def run_test(page, output_dir, page_url):
    try:
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.wait_for_timeout(300)
        await page.wait_for_load_state("domcontentloaded", timeout=15000)
        print("PASS: homepage domcontentloaded")

        await page.wait_for_selector('[data-testid="lang-switch"]', timeout=10000)
        print("PASS: lang switch visible")

        await page.screenshot(path="/app/test_reports/screenshots_iter67_smoke/automation_output/20261026_173439_8d3eb2e64179/home_smoke.jpeg", type="jpeg", quality=40, full_page=False)
        print("PASS: smoke screenshot captured")

        error_text = await page.evaluate("""() => {
        const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));
        return errorElements.map(el => el.textContent).join(", ");
        }""")
        if error_text:
            print(f"Found error message: {error_text}")
        else:
            print("No error messages found on the page")
    except Exception as e:
        print(f"FAIL: smoke check failed: {str(e)}")
