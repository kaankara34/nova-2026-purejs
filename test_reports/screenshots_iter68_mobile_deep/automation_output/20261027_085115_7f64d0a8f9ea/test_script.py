async def run_test(page, output_dir, page_url):
    try:
        await page.set_viewport_size({"width": 390, "height": 844})
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(1500)
        print("STEP1 PASS: page loaded at 390x844")

        await page.wait_for_selector('[data-testid="ew-feature-media"]', timeout=10000)
        await page.locator('[data-testid="ew-feature-media"]').scroll_into_view_if_needed()
        await page.wait_for_timeout(500)
        print("STEP2 PASS: scrolled to East-West feature")

        ew_static = await page.evaluate("""() => {
          const section = document.getElementById('eastWestFeature');
          const progress = section?.querySelector('.ew-progress');
          const top = section?.querySelector('.ew-progress-top');
          const glint = section?.querySelector('.ew-progress-glint');
          const slideCount = section?.querySelectorAll('[data-ew-slide]').length || 0;
          const runningAnims = (section?.querySelectorAll('.ew-progress, .ew-progress-active, .ew-progress-glint') || []).length;
          const lineH = top ? getComputedStyle(top).height : null;
          const glintW = glint ? getComputedStyle(glint).width : null;
          const glintH = glint ? getComputedStyle(glint).height : null;
          return {hasSection: !!section, hasProgress: !!progress, slideCount, runningAnims, lineH, glintW, glintH};
        }""")
        print(f"STEP3 INFO: ew_static={ew_static}")

        timeline = []
        for i in range(7):
            snap = await page.evaluate("""() => {
              const section = document.getElementById('eastWestFeature');
              const media = document.getElementById('ewFeatureMedia');
              const active = media ? Array.from(media.querySelectorAll('[data-ew-slide]')).findIndex(s => s.classList.contains('is-active')) : -1;
              const anim = section ? section.getAnimations().find(a => a.effect?.target?.classList?.contains('ew-progress-top')) : null;
              return {
                t: Date.now(),
                active,
                animTime: anim ? Number(anim.currentTime || 0) : null,
                animState: anim ? anim.playState : 'missing'
              };
            }""")
            timeline.append(snap)
            print(f"STEP4 SAMPLE {i}: {snap}")
            if i < 6:
                await page.wait_for_timeout(5200)

        blur_before_after = await page.evaluate("""async () => {
          const section = document.getElementById('eastWestFeature');
          const getAnim = () => section?.getAnimations().find(a => a.effect?.target?.classList?.contains('ew-progress-top'));
          const before = getAnim() ? Number(getAnim().currentTime || 0) : null;
          window.dispatchEvent(new Event('blur'));
          window.scrollBy(0, 140);
          await new Promise(r => setTimeout(r, 6200));
          window.scrollBy(0, -140);
          const after = getAnim() ? Number(getAnim().currentTime || 0) : null;
          return {before, after};
        }""")
        print(f"STEP5 INFO blur+scroll progression: {blur_before_after}")

        recover_state = await page.evaluate("""async () => {
          const section = document.getElementById('eastWestFeature');
          const getAnim = () => section?.getAnimations().find(a => a.effect?.target?.classList?.contains('ew-progress-top'));
          section?.getAnimations().forEach(a => a.pause());
          const pausedState = getAnim() ? getAnim().playState : 'missing';
          window.dispatchEvent(new Event('scroll'));
          window.dispatchEvent(new Event('focus'));
          await new Promise(r => setTimeout(r, 1800));
          const resumed = getAnim() ? getAnim().playState : 'missing';
          return {pausedState, resumed};
        }""")
        print(f"STEP6 INFO forced-pause recovery: {recover_state}")

        page_lifecycle = await page.evaluate("""async () => {
          const section = document.getElementById('eastWestFeature');
          const getAnim = () => section?.getAnimations().find(a => a.effect?.target?.classList?.contains('ew-progress-top'));
          const pre = getAnim() ? getAnim().playState : 'missing';
          window.dispatchEvent(new PageTransitionEvent('pagehide', { persisted: true }));
          const during = getAnim() ? getAnim().playState : 'missing';
          window.dispatchEvent(new PageTransitionEvent('pageshow', { persisted: true }));
          await new Promise(r => setTimeout(r, 1200));
          const post = getAnim() ? getAnim().playState : 'missing';
          return {pre, during, post};
        }""")
        print(f"STEP7 INFO pagehide/pageshow: {page_lifecycle}")

        lang_counts = await page.evaluate("""() => {
          const header = document.querySelectorAll('[data-testid="lang-switch"]').length;
          const menu = document.querySelectorAll('#sideMenu .lang-switch').length;
          return {header, menu};
        }""")
        print(f"STEP8 INFO initial lang-switch counts: {lang_counts}")

        await page.click('[data-testid="header-control-1"]', force=True)
        await page.wait_for_timeout(500)
        menu_open_state = await page.evaluate("""() => {
          const side = document.getElementById('sideMenu');
          const headerSwitch = document.querySelector('[data-testid="lang-switch"]');
          const style = headerSwitch ? getComputedStyle(headerSwitch) : null;
          return {
            sideOpen: !!(side && side.classList.contains('open')),
            headerDisplay: style ? style.display : null,
            headerVisibility: style ? style.visibility : null,
            menuLangCount: document.querySelectorAll('#sideMenu .lang-switch').length
          };
        }""")
        print(f"STEP9 INFO menu-open lang state: {menu_open_state}")

        await page.click('[data-testid="menu-control-1"]', force=True)
        await page.wait_for_timeout(400)
        menu_close_state = await page.evaluate("""() => {
          const side = document.getElementById('sideMenu');
          const headerSwitch = document.querySelector('[data-testid="lang-switch"]');
          const style = headerSwitch ? getComputedStyle(headerSwitch) : null;
          return {
            sideOpen: !!(side && side.classList.contains('open')),
            headerDisplay: style ? style.display : null,
            headerVisibility: style ? style.visibility : null
          };
        }""")
        print(f"STEP10 INFO menu-close lang state: {menu_close_state}")

        try:
            cdp = await page.context.new_cdp_session(page)
            await cdp.send('Emulation.setTouchEmulationEnabled', {'enabled': True, 'maxTouchPoints': 5})
            box = await page.locator('[data-testid="header-control-1"]').bounding_box()
            if box:
                x = box['x'] + box['width'] / 2
                y = box['y'] + box['height'] / 2
                await cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': x, 'y': y}]})
                await cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
                await page.wait_for_timeout(500)
                cdp_menu = await page.evaluate("""() => !!document.getElementById('sideMenu')?.classList.contains('open')""")
                print(f"STEP11 PASS: CDP touch dispatched, side menu open={cdp_menu}")
            else:
                print("STEP11 FAIL: menu toggle bounding box missing")
        except Exception as cdp_error:
            print(f"STEP11 FAIL: CDP touch emulation unavailable: {cdp_error}")

        await page.screenshot(path="/app/test_reports/screenshots_iter68_mobile_deep/automation_output/20261027_085115_7f64d0a8f9ea/final_state.jpeg", type="jpeg", quality=40, full_page=False)

        error_text = await page.evaluate("""() => {
        const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));
        return errorElements.map(el => el.textContent).join(", ");
        }""")
        if error_text:
            print(f"Found error message: {error_text}")
        else:
            print("No error messages found on the page")

        print("STEP12 PASS: deep mobile lifecycle checks completed")
    except Exception as e:
        print(f"FAIL: deep mobile lifecycle test failed: {e}")
