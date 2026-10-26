async def run_test(page, output_dir, page_url):
    try:
        await page.set_viewport_size({"width": 1440, "height": 900})
        await page.goto("https://515dc9a7-0d61-46f2-bb41-31805466b8fc.preview.emergentagent.com/tr/projeler.html", wait_until="domcontentloaded")
        await page.wait_for_timeout(700)
        await page.focus('[data-testid="lang-header-en"]')
        await page.keyboard.press("Enter")
        await page.wait_for_load_state("domcontentloaded")
        print(f"URL after focused Enter: {page.url}")
    except Exception as e:
        print(f"FAIL: {e}")
