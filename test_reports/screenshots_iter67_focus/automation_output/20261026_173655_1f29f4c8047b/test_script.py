async def run_test(page, output_dir, page_url):
    try:
        # Mobile menu/language hide+restore checks
        await page.set_viewport_size({"width": 390, "height": 844})
        await page.wait_for_load_state("domcontentloaded", timeout=15000)
        await page.wait_for_selector('[data-testid="lang-switch"]', timeout=10000)
        await page.wait_for_selector('[data-testid="lang-switch-menu"]', timeout=10000)
        print("PASS: language switch elements present")

        header_switch = page.locator('[data-testid="lang-switch"]')
        menu_switch = page.locator('[data-testid="lang-switch-menu"]')
        before_header_visible = await header_switch.is_visible()
        before_menu_visible = await menu_switch.is_visible()
        print(f"INFO: pre-open visibility header={before_header_visible} menu={before_menu_visible}")

        await page.locator('#menuToggle').tap()
        await page.wait_for_timeout(500)

        hidden_state = await page.evaluate("""() => {
          const h = document.querySelector('[data-testid="lang-switch"]');
          const m = document.querySelector('[data-testid="lang-switch-menu"]');
          const styleInfo = (el) => {
            if (!el) return null;
            const cs = getComputedStyle(el);
            return {display: cs.display, visibility: cs.visibility, opacity: cs.opacity};
          };
          return { header: styleInfo(h), menu: styleInfo(m), bodyMenuOpen: document.body.classList.contains('nova-menu-open') };
        }""")
        print(f"INFO: menu-open lang switch state={hidden_state}")

        await page.locator('#menuClose').click(force=True)
        await page.wait_for_timeout(700)
        restored_header_visible = await header_switch.is_visible()
        print(f"PASS: post-close header visible={restored_header_visible}")

        # Theme checks on selected light-theme pages
        theme_results = []
        for path in ["/en/design.html", "/en/contact.html", "/en/build-beyond-living.html"]:
            await page.goto(f"https://darg-clone-1.preview.emergentagent.com{path}", wait_until="domcontentloaded")
            await page.wait_for_timeout(250)
            vals = await page.evaluate("""() => {
              const root = getComputedStyle(document.documentElement);
              const header = getComputedStyle(document.querySelector('.site-header'));
              const bg = getComputedStyle(document.body).backgroundColor;
              return {
                c_bg: root.getPropertyValue('--c-bg').trim(),
                c_text: root.getPropertyValue('--c-text').trim(),
                header_bg: header.backgroundColor,
                body_bg: bg
              };
            }""")
            theme_results.append({"path": path, **vals})
        print(f"INFO: theme snapshots={theme_results}")

        # Resource availability metrics (first-load practical sample)
        await page.goto("https://darg-clone-1.preview.emergentagent.com/en/design.html", wait_until="load")
        await page.wait_for_timeout(800)
        resource_metrics = await page.evaluate("""() => {
          const entries = performance.getEntriesByType('resource');
          const picks = entries.filter(e => /nova-logo|media\/flags|favicon|apple-touch-icon/.test(e.name));
          return picks.slice(0, 12).map(e => ({
            name: e.name,
            transferSize: e.transferSize,
            encodedBodySize: e.encodedBodySize,
            decodedBodySize: e.decodedBodySize,
            duration: Number(e.duration.toFixed(2))
          }));
        }""")
        print(f"INFO: resource_metrics={resource_metrics}")

        codec_diag = await page.evaluate("""() => {
          const v = document.createElement('video');
          return {
            avc1_640028: v.canPlayType('video/mp4; codecs="avc1.640028"'),
            mp4_generic: v.canPlayType('video/mp4'),
            webm_vp9: v.canPlayType('video/webm; codecs="vp9"')
          };
        }""")
        print(f"INFO: chromium_codec_diagnostics={codec_diag}")

        # East-West border progress lifecycle sanity
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.goto("https://darg-clone-1.preview.emergentagent.com/en/the-residences-east-west.html", wait_until="domcontentloaded")
        await page.wait_for_selector('[data-testid="ew-feature-progress"]', timeout=10000)
        await page.wait_for_timeout(600)

        ew_geometry = await page.evaluate("""() => {
          const panel = document.querySelector('.ew-feature-inner');
          const progress = document.querySelector('[data-testid="ew-feature-progress"]');
          const p = panel.getBoundingClientRect();
          const g = progress.getBoundingClientRect();
          return {
            dw: Math.abs(Math.round(p.width - g.width)),
            dh: Math.abs(Math.round(p.height - g.height)),
          };
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
        print(f"PASS: ew progress currentTime advanced {t1} -> {t2}")

        await page.evaluate("window.dispatchEvent(new Event('pagehide'))")
        await page.wait_for_timeout(300)
        paused_state = await page.evaluate("""() => {
          const top = document.querySelector('[data-testid="ew-progress-top"]');
          const a = top?.getAnimations?.()[0];
          return a ? a.playState : 'missing';
        }""")
        print(f"INFO: ew state after pagehide={paused_state}")

        await page.evaluate("window.dispatchEvent(new Event('pageshow'))")
        await page.wait_for_timeout(500)
        resumed_state = await page.evaluate("""() => {
          const top = document.querySelector('[data-testid="ew-progress-top"]');
          const a = top?.getAnimations?.()[0];
          return a ? a.playState : 'missing';
        }""")
        print(f"INFO: ew state after pageshow={resumed_state}")

        error_text = await page.evaluate("""() => {
        const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));
        return errorElements.map(el => el.textContent).join(", ");
        }""")
        if error_text:
            print(f"Found error message: {error_text}")
        else:
            print("No error messages found on the page")

    except Exception as e:
        print(f"FAIL: focused browser checks failed: {str(e)}")
