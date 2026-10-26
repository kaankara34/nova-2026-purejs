async def run_test(page, output_dir, page_url):
    try:
        await page.set_viewport_size({"width": 320, "height": 844})
        await page.goto("https://515dc9a7-0d61-46f2-bb41-31805466b8fc.preview.emergentagent.com/tr/index.html", wait_until="domcontentloaded")
        await page.wait_for_timeout(800)
        await page.screenshot(path="/app/test_reports/screenshots_iter61_mobile/automation_output/20261026_105746_58ab2f1306ea/tr_320_header.jpeg", type="jpeg", quality=40, full_page=False)
        print("PASS: captured 320 screenshot")
    except Exception as e:
        print(f"FAIL: {e}")
