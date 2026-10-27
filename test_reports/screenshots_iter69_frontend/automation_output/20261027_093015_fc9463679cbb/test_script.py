async def run_test(page, output_dir, page_url):
    try:
        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))

        # Step 1: TR home mobile news count should be 3
        await page.set_viewport_size({"width": 390, "height": 844})
        await page.goto("https://darg-clone-1.preview.emergentagent.com/tr/index.html", wait_until="domcontentloaded")
        await page.wait_for_timeout(1200)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.78)")
        await page.wait_for_timeout(4500)

        tr_mobile_cards = await page.locator('#newsHomeGrid [data-testid="news-card"]').count()
        print(f"TR mobile cards: {tr_mobile_cards}")

        req_count_before = await page.evaluate("""() => {
            return performance.getEntriesByType('resource')
              .map(e => e.name)
              .filter(n => n.includes('raw.githubusercontent.com/kaankara34/nova-news-feed')).length;
        }""")
        print(f"Feed request count before resize: {req_count_before}")

        # Step 2: resize to tablet/desktop threshold, should become 6 without reload
        await page.set_viewport_size({"width": 768, "height": 1024})
        await page.wait_for_timeout(1800)
        tr_tablet_cards = await page.locator('#newsHomeGrid [data-testid="news-card"]').count()
        print(f"TR tablet cards after resize: {tr_tablet_cards}")

        req_count_after_up = await page.evaluate("""() => {
            return performance.getEntriesByType('resource')
              .map(e => e.name)
              .filter(n => n.includes('raw.githubusercontent.com/kaankara34/nova-news-feed')).length;
        }""")
        print(f"Feed request count after upsize: {req_count_after_up}")

        # Step 3: resize back to mobile should return to 3
        await page.set_viewport_size({"width": 390, "height": 844})
        await page.wait_for_timeout(1800)
        tr_mobile_cards_back = await page.locator('#newsHomeGrid [data-testid="news-card"]').count()
        print(f"TR mobile cards after resize-back: {tr_mobile_cards_back}")

        # Step 4: EN home mobile check
        await page.goto("https://darg-clone-1.preview.emergentagent.com/en/index.html", wait_until="domcontentloaded")
        await page.wait_for_timeout(1200)
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight * 0.78)")
        await page.wait_for_timeout(4500)
        en_mobile_cards = await page.locator('#newsHomeGrid [data-testid="news-card"]').count()
        print(f"EN mobile cards: {en_mobile_cards}")

        # Step 5: TR EDSAA content and structure checks
        await page.goto("https://darg-clone-1.preview.emergentagent.com/tr/edsaa.html", wait_until="domcontentloaded")
        await page.wait_for_timeout(1200)

        h1_count = await page.locator('h1').count()
        h1_text = (await page.locator('[data-testid="edsaa-title"]').text_content() or '').strip()
        desc_text = (await page.locator('[data-testid="edsaa-description"]').text_content() or '').strip()
        has_register_form = await page.locator('[data-testid="contact-register-form"]').count()

        print(f"EDSAA TR h1 count: {h1_count}")
        print(f"EDSAA TR h1 text: {h1_text}")
        print(f"EDSAA TR description: {desc_text}")
        print(f"EDSAA TR register form count: {has_register_form}")

        # Step 6: Side menu should include EDSAA item under NOVA KONUT
        await page.click('[data-testid="header-control-1"]', force=True)
        await page.wait_for_timeout(400)
        await page.click('[data-testid="menu-control-3"]', force=True)
        await page.wait_for_timeout(500)

        edsaa_menu_item_count = await page.locator('[data-testid="menu-link-edsaa"]').count()
        fallback_subitem_count = await page.locator('#sideMenu .submenu[data-id="nova-konut"] a[href="edsaa.html"]').count()
        print(f"EDSAA menu-link-edsaa count: {edsaa_menu_item_count}")
        print(f"EDSAA fallback submenu href count: {fallback_subitem_count}")

        # Step 7: language switch TR->EN should stay on EDSAA
        await page.click('[data-testid="menu-control-1"]', force=True)
        await page.wait_for_timeout(400)
        await page.click('[data-testid="lang-header-en"]', force=True)
        await page.wait_for_timeout(1500)
        print(f"Current URL after TR->EN switch: {page.url}")

        # Step 8: Scrollbar style check
        scrollbar_style = await page.evaluate("""() => {
          const cs = getComputedStyle(document.documentElement);
          return {
            scrollbarWidth: cs.scrollbarWidth || null,
            scrollbarColor: cs.scrollbarColor || null
          };
        }""")
        print(f"Scrollbar styles: {scrollbar_style}")

        await page.screenshot(path="/app/test_reports/screenshots_iter69_frontend/automation_output/20261027_093015_fc9463679cbb/edsaa_state.jpeg", type="jpeg", quality=40, full_page=False)

        # Error detection block (required)
        error_text = await page.evaluate("""() => {
        const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));
        return errorElements.map(el => el.textContent).join(", ");
        }""")
        if error_text:
            print(f"Found error message: {error_text}")
        else:
            print("No error messages found on the page")

        print("Frontend verification script completed")

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
