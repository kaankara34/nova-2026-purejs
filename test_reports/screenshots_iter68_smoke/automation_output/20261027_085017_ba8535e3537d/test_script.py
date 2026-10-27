async def run_test(page, output_dir, page_url):
    try:
        await page.set_viewport_size({"width": 390, "height": 844})
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(1500)
        await page.screenshot(path="/app/test_reports/screenshots_iter68_smoke/automation_output/20261027_085017_ba8535e3537d/home_tr_390.jpeg", type="jpeg", quality=40, full_page=False)
        print("PASS: frontend loaded and screenshot captured")

        error_text = await page.evaluate("""() => {
        const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));
        return errorElements.map(el => el.textContent).join(", ");
        }""")
        if error_text:
            print(f"Found error message: {error_text}")
        else:
            print("No error messages found on the page")
    except Exception as e:
        print(f"FAIL: smoke load check failed: {e}")
