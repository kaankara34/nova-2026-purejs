async def run_test(page, output_dir, page_url):
    try:
        await page.set_viewport_size({"width": 390, "height": 844})
        await page.wait_for_load_state("domcontentloaded")
        await page.locator('[data-testid="ew-feature-media"]').scroll_into_view_if_needed()
        await page.wait_for_timeout(800)

        def_js = """() => {
          const topEl = document.querySelector('.ew-progress-top');
          const rightEl = document.querySelector('.ew-progress-right');
          const glintEl = document.querySelector('.ew-progress-glint');
          const pick = el => {
            const a = el?.getAnimations?.()[0];
            return a ? {state: a.playState, time: Number(a.currentTime || 0)} : null;
          };
          return {top: pick(topEl), right: pick(rightEl), glint: pick(glintEl)};
        }"""

        a0 = await page.evaluate(def_js)
        await page.wait_for_timeout(5200)
        a1 = await page.evaluate(def_js)
        print(f"ANIM SNAP before/after 5s: {a0} -> {a1}")

        lifecycle = await page.evaluate("""async () => {
          const topEl = document.querySelector('.ew-progress-top');
          const anim = topEl?.getAnimations?.()[0];
          if (!anim) return {missing: true};
          const t1 = Number(anim.currentTime || 0);
          window.dispatchEvent(new PageTransitionEvent('pagehide', { persisted: true }));
          const pausedState = anim.playState;
          await new Promise(r => setTimeout(r, 400));
          window.dispatchEvent(new PageTransitionEvent('pageshow', { persisted: true }));
          await new Promise(r => setTimeout(r, 1200));
          const t2 = Number(anim.currentTime || 0);
          return {missing: false, t1, t2, pausedState, resumedState: anim.playState};
        }""")
        print(f"ANIM lifecycle: {lifecycle}")

        blur_recover = await page.evaluate("""async () => {
          const topEl = document.querySelector('.ew-progress-top');
          const anim = topEl?.getAnimations?.()[0];
          if (!anim) return {missing: true};
          const t1 = Number(anim.currentTime || 0);
          window.dispatchEvent(new Event('blur'));
          window.scrollBy(0, 220);
          await new Promise(r => setTimeout(r, 5200));
          window.scrollBy(0, -220);
          const t2 = Number(anim.currentTime || 0);
          return {missing: false, t1, t2, state: anim.playState};
        }""")
        print(f"ANIM blur+scroll recovery: {blur_recover}")

        error_text = await page.evaluate("""() => {
        const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));
        return errorElements.map(el => el.textContent).join(", ");
        }""")
        if error_text:
            print(f"Found error message: {error_text}")
        else:
            print("No error messages found on the page")
    except Exception as e:
        print(f"FAIL: animation probe failed: {e}")
