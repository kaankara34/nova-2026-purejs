async def run_test(page, output_dir, page_url):
    try:
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.wait_for_load_state("domcontentloaded", timeout=15000)
        await page.wait_for_selector('[data-testid="ew-feature-media"]', timeout=10000)
        await page.wait_for_selector('[data-testid="ew-feature-progress"]', timeout=10000)
        await page.wait_for_timeout(800)

        ew_geometry = await page.evaluate("""() => {
          const panel = document.querySelector('.ew-feature-inner');
          const progress = document.querySelector('[data-testid="ew-feature-progress"]');
          const p = panel.getBoundingClientRect();
          const g = progress.getBoundingClientRect();
          return {dw: Math.abs(Math.round(p.width - g.width)), dh: Math.abs(Math.round(p.height - g.height))};
        }""")
        print(f"INFO: ew_geometry_diff={ew_geometry}")

        t1 = await page.evaluate("""() => {
          const top = document.querySelector('[data-testid="ew-progress-top"]');
          const a = top?.getAnimations?.()[0];
          return a ? Number(a.currentTime || 0) : -1;
        }""")
        await page.wait_for_timeout(1200)
        t2 = await page.evaluate("""() => {
          const top = document.querySelector('[data-testid="ew-progress-top"]');
          const a = top?.getAnimations?.()[0];
          return a ? Number(a.currentTime || 0) : -1;
        }""")
        print(f"INFO: ew progress currentTime {t1} -> {t2}")

        await page.evaluate("window.dispatchEvent(new Event('pagehide'))")
        await page.wait_for_timeout(250)
        paused_state = await page.evaluate("""() => {
          const a = document.querySelector('[data-testid="ew-progress-top"]')?.getAnimations?.()[0];
          return a ? a.playState : 'missing';
        }""")
        await page.evaluate("window.dispatchEvent(new Event('pageshow'))")
        await page.wait_for_timeout(500)
        resumed_state = await page.evaluate("""() => {
          const a = document.querySelector('[data-testid="ew-progress-top"]')?.getAnimations?.()[0];
          return a ? a.playState : 'missing';
        }""")
        print(f"INFO: ew lifecycle playState pagehide={paused_state} pageshow={resumed_state}")

        error_text = await page.evaluate("""() => {
        const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));
        return errorElements.map(el => el.textContent).join(", ");
        }""")
        if error_text:
            print(f"Found error message: {error_text}")
        else:
            print("No error messages found on the page")
    except Exception as e:
        print(f"FAIL: ew checks failed: {str(e)}")
