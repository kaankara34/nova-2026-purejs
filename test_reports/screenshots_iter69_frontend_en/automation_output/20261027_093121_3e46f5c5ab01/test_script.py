async def run_test(page, output_dir, page_url):
    try:
        await page.set_viewport_size({"width": 390, "height": 844})
        await page.goto("https://darg-clone-1.preview.emergentagent.com/en/index.html", wait_until="domcontentloaded")
        await page.wait_for_timeout(1200)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.78)")
        await page.wait_for_timeout(4200)

        en_mobile = await page.locator('#newsHomeGrid [data-testid="news-card"]').count()
        print(f"EN mobile cards: {en_mobile}")

        await page.set_viewport_size({"width": 768, "height": 1024})
        await page.wait_for_timeout(1500)
        en_tablet = await page.locator('#newsHomeGrid [data-testid="news-card"]').count()
        print(f"EN tablet cards: {en_tablet}")

        await page.goto("https://darg-clone-1.preview.emergentagent.com/en/edsaa", wait_until="domcontentloaded")
        await page.wait_for_timeout(1200)
        print(f"EN extensionless EDSAA URL result: {page.url}")

        error_text = await page.evaluate("""() => {
        const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));
        return errorElements.map(el => el.textContent).join(", ");
        }""")
        if error_text:
            print(f"Found error message: {error_text}")
        else:
            print("No error messages found on the page")

    except Exception as e:
        print(f"Script failed: {str(e)}")
        error_text = await page.evaluate("""() => {
        const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));
        return errorElements.map(el => el.textContent).join(", ");
        }""")
        if error_text:
            print(f"Found error message: {error_text}")
        else:
            print("No error messages found on the page")
