async def run_test(page, output_dir, page_url):
    try:
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(1200)
        print("D1 PASS: desktop page loaded")

        counts = await page.evaluate("""() => ({
          header: document.querySelectorAll('[data-testid="lang-switch"]').length,
          menu: document.querySelectorAll('#sideMenu .lang-switch').length
        })""")
        print(f"D2 INFO lang counts desktop: {counts}")

        await page.locator('[data-testid="ew-feature-media"]').scroll_into_view_if_needed()
        await page.wait_for_timeout(600)
        pre = await page.evaluate("""() => {
          const anim = document.querySelector('.ew-progress-top')?.getAnimations?.()[0];
          return anim ? {state: anim.playState, t: Number(anim.currentTime || 0)} : null;
        }""")
        print(f"D3 INFO pre-hover animation: {pre}")

        media = page.locator('[data-testid="ew-feature-media"]')
        box = await media.bounding_box()
        if box:
          await page.mouse.move(box['x'] + box['width']/2, box['y'] + box['height']/2)
          await page.wait_for_timeout(700)
          hovered = await page.evaluate("""() => {
            const anim = document.querySelector('.ew-progress-top')?.getAnimations?.()[0];
            return anim ? {state: anim.playState, t: Number(anim.currentTime || 0)} : null;
          }""")
          print(f"D4 INFO hover state: {hovered}")

          await page.mouse.move(box['x'] + box['width'] + 80, box['y'] + 10)
          await page.wait_for_timeout(800)
          resumed = await page.evaluate("""() => {
            const anim = document.querySelector('.ew-progress-top')?.getAnimations?.()[0];
            return anim ? {state: anim.playState, t: Number(anim.currentTime || 0)} : null;
          }""")
          print(f"D5 INFO post-leave state: {resumed}")
        else:
          print("D4 FAIL: could not get ew media box")

        await page.click('[data-testid="header-control-1"]', force=True)
        await page.wait_for_timeout(400)
        side_state = await page.evaluate("""() => ({
          open: !!document.getElementById('sideMenu')?.classList.contains('open'),
          headerDisplay: getComputedStyle(document.querySelector('[data-testid="lang-switch"]')).display
        })""")
        print(f"D6 INFO desktop side-menu state: {side_state}")

        await page.screenshot(path="/app/test_reports/screenshots_iter68_desktop/automation_output/20261027_085249_517291824134/desktop_state.jpeg", type="jpeg", quality=40, full_page=False)

        error_text = await page.evaluate("""() => {
        const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));
        return errorElements.map(el => el.textContent).join(", ");
        }""")
        if error_text:
            print(f"Found error message: {error_text}")
        else:
            print("No error messages found on the page")
    except Exception as e:
        print(f"FAIL: desktop checks failed: {e}")
