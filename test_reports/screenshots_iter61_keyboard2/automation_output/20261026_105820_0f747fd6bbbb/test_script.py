async def run_test(page, output_dir, page_url):
    try:
        await page.set_viewport_size({"width": 1440, "height": 900})
        await page.goto("https://515dc9a7-0d61-46f2-bb41-31805466b8fc.preview.emergentagent.com/tr/projeler.html", wait_until="domcontentloaded")
        await page.wait_for_timeout(500)
        await page.locator('[data-testid="lang-header-en"]').press('Enter')
        await page.wait_for_timeout(800)
        print(f"URL after locator.press Enter: {page.url}")
    except Exception as e:
        print(f"FAIL: {e}")
