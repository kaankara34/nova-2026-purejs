async def run_test(page, output_dir, page_url):
    import asyncio

    page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))

    async def run_step(name, coro):
        try:
            await coro()
            print(f"PASS: {name}")
            return True
        except Exception as e:
            print(f"FAIL: {name} -> {e}")
            return False

    async def main():
        await page.set_viewport_size({"width": 1920, "height": 1080})

        async def goto_tr():
            await page.goto("https://darg-clone-1.preview.emergentagent.com/tr/index.html", wait_until="domcontentloaded")
            await page.wait_for_timeout(500)
            await page.wait_for_selector('[data-testid="lang-header-toggle"]', timeout=10000)

        await run_step("Load TR homepage", goto_tr)

        async def visual_checks():
            knob = page.locator('[data-testid="lang-header-knob"]')
            rail = page.locator('[data-testid="lang-header-rail"]')
            tr_label = page.locator('[data-testid="lang-header-tr"]')
            en_label = page.locator('[data-testid="lang-header-en"]')

            kb = await knob.bounding_box()
            rb = await rail.bounding_box()
            trb = await tr_label.bounding_box()
            enb = await en_label.bounding_box()
            if not all([kb, rb, trb, enb]):
                raise Exception("Missing bounding boxes")

            if abs(kb["width"] - kb["height"]) > 0.8:
                raise Exception(f"Knob not circular enough: w={kb['width']} h={kb['height']}")

            if trb["x"] + trb["width"] >= rb["x"]:
                raise Exception("TR label is not fully outside left side")
            if enb["x"] <= rb["x"] + rb["width"]:
                raise Exception("EN label is not fully outside right side")

            indicator_count = await page.locator('.lang-indicator').count()
            if indicator_count != 0:
                raise Exception(f"Found deprecated .lang-indicator count={indicator_count}")

            styles = await page.evaluate('''() => {
                const rail = document.querySelector('[data-testid="lang-header-rail"]');
                const knob = document.querySelector('[data-testid="lang-header-knob"]');
                const trFlag = document.querySelector('[data-testid="lang-header-flag-tr"]');
                const enFlag = document.querySelector('[data-testid="lang-header-flag-en"]');
                const sw = document.querySelector('[data-testid="lang-switch"]');
                const rs = getComputedStyle(rail);
                const ks = getComputedStyle(knob);
                const trs = getComputedStyle(trFlag);
                const ens = getComputedStyle(enFlag);
                return {
                    railBg: rs.backgroundColor,
                    railImg: rs.backgroundImage,
                    knobBg: ks.backgroundColor,
                    knobImg: ks.backgroundImage,
                    trOpacity: trs.opacity,
                    enOpacity: ens.opacity,
                    lang: sw?.dataset.language || null
                };
            }''')
            print(f"STYLE SNAPSHOT: {styles}")

            if "79, 107, 87" in (styles.get("railBg") or "") or "79, 107, 87" in (styles.get("knobBg") or ""):
                raise Exception("Toggle uses green tint")

            if styles.get("lang") == "tr":
                if float(styles.get("trOpacity", "0")) < 0.9 or float(styles.get("enOpacity", "0")) > 0.1:
                    raise Exception("TR state flag visibility mismatch")

        await run_step("Visual structure: circular knob, external labels, no segmented indicator", visual_checks)

        async def aria_check_tr():
            toggle = page.locator('[data-testid="lang-header-toggle"]')
            role = await toggle.get_attribute("role")
            checked = await toggle.get_attribute("aria-checked")
            if role != "switch":
                raise Exception(f"role is {role}")
            if checked != "false":
                raise Exception(f"TR state aria-checked expected false got {checked}")

        await run_step("ARIA role/switch TR state", aria_check_tr)

        async def click_toggle_to_en_and_back():
            expected_en = await page.evaluate('''() => new URL(document.querySelector('[data-testid="lang-header-en"]').getAttribute('href'), location.href).href''')
            await page.click('[data-testid="lang-header-toggle"]', force=True)
            await page.wait_for_url("**/en/**", timeout=6000)
            if not page.url.startswith(expected_en.split("#")[0].split("?")[0]):
                print(f"INFO: expected EN base {expected_en}, got {page.url}")

            expected_tr = await page.evaluate('''() => new URL(document.querySelector('[data-testid="lang-header-tr"]').getAttribute('href'), location.href).href''')
            await page.click('[data-testid="lang-header-toggle"]', force=True)
            await page.wait_for_url("**/tr/**", timeout=6000)
            if not page.url.startswith(expected_tr.split("#")[0].split("?")[0]):
                print(f"INFO: expected TR base {expected_tr}, got {page.url}")

        await run_step("Center toggle click TR->EN->TR", click_toggle_to_en_and_back)

        async def drag_commit_release_only():
            await goto_tr()
            toggle = page.locator('[data-testid="lang-header-toggle"]')
            box = await toggle.bounding_box()
            if not box:
                raise Exception("No toggle box")
            start_x = box["x"] + box["width"] * 0.35
            end_x = box["x"] + box["width"] * 0.85
            y = box["y"] + box["height"] * 0.5

            before = page.url
            await page.mouse.move(start_x, y)
            await page.mouse.down()
            await page.mouse.move(end_x, y, steps=12)
            await page.wait_for_timeout(350)
            during = page.url
            if during != before:
                raise Exception("Navigated before mouseup")
            await page.mouse.up()
            await page.wait_for_url("**/en/**", timeout=7000)

        await run_step("Mouse drag follows, navigates only on release", drag_commit_release_only)

        async def partial_drag_snaps_back():
            await goto_tr()
            toggle = page.locator('[data-testid="lang-header-toggle"]')
            box = await toggle.bounding_box()
            start_x = box["x"] + box["width"] * 0.4
            y = box["y"] + box["height"] * 0.5
            await page.mouse.move(start_x, y)
            await page.mouse.down()
            await page.mouse.move(start_x + 6, y, steps=5)
            await page.mouse.up()
            await page.wait_for_timeout(550)
            if "/tr/" not in page.url:
                raise Exception(f"Unexpected navigation for partial drag: {page.url}")

        await run_step("Partial drag under midpoint snaps back, no navigation", partial_drag_snaps_back)

        async def drag_out_and_back_no_nav():
            await goto_tr()
            toggle = page.locator('[data-testid="lang-header-toggle"]')
            box = await toggle.bounding_box()
            start_x = box["x"] + box["width"] * 0.38
            y = box["y"] + box["height"] * 0.5
            await page.mouse.move(start_x, y)
            await page.mouse.down()
            await page.mouse.move(start_x + 24, y, steps=8)
            await page.mouse.move(start_x + 2, y, steps=8)
            await page.mouse.up()
            await page.wait_for_timeout(550)
            if "/tr/" not in page.url:
                raise Exception(f"Unexpected navigation after drag back: {page.url}")

        await run_step("Drag out then back cancels commit", drag_out_and_back_no_nav)

        async def right_click_no_change():
            await goto_tr()
            before = page.url
            await page.click('[data-testid="lang-header-toggle"]', button='right', force=True)
            await page.wait_for_timeout(400)
            if page.url != before:
                raise Exception("Right click changed language")

        await run_step("Non-primary/right click does not toggle", right_click_no_change)

        async def keyboard_checks():
            await goto_tr()
            await page.focus('[data-testid="lang-header-toggle"]')
            await page.keyboard.press("Space")
            await page.wait_for_url("**/en/**", timeout=6000)

            await page.focus('[data-testid="lang-header-toggle"]')
            await page.keyboard.press("ArrowLeft")
            await page.wait_for_url("**/tr/**", timeout=6000)

            await page.focus('[data-testid="lang-header-toggle"]')
            await page.keyboard.press("Enter")
            await page.wait_for_url("**/en/**", timeout=6000)

            checked = await page.locator('[data-testid="lang-header-toggle"]').get_attribute("aria-checked")
            if checked != "true":
                raise Exception(f"EN state aria-checked expected true got {checked}")

        await run_step("Keyboard Space/Enter/Arrow toggles", keyboard_checks)

        async def pageshow_back_forward_reset():
            await goto_tr()
            await page.click('[data-testid="lang-header-toggle"]', force=True)
            await page.wait_for_url("**/en/**", timeout=6000)
            await page.go_back(wait_until="domcontentloaded")
            await page.wait_for_timeout(500)
            checked = await page.locator('[data-testid="lang-header-toggle"]').get_attribute("aria-checked")
            if checked != "false":
                raise Exception(f"After back expected TR checked=false got {checked}")

        await run_step("Back/forward pageshow state reset", pageshow_back_forward_reset)

        async def reduced_motion_check():
            await page.emulate_media(reduced_motion="reduce")
            await goto_tr()
            dur = await page.evaluate('''() => getComputedStyle(document.querySelector('[data-testid="lang-header-knob"]')).transitionDuration''')
            if "0s" not in dur:
                raise Exception(f"Expected reduced-motion transition 0s, got {dur}")
            await page.emulate_media(reduced_motion="no-preference")

        await run_step("Reduced motion disables transition", reduced_motion_check)

        async def offcanvas_switch_presence():
            await goto_tr()
            await page.click('#menuToggle', force=True)
            await page.wait_for_timeout(300)
            await page.wait_for_selector('[data-testid="lang-menu-toggle"]', timeout=5000)
            menu_box = await page.locator('[data-testid="lang-menu-toggle"]').bounding_box()
            if not menu_box:
                raise Exception("Menu toggle not visible")

        await run_step("Offcanvas menu language switch present", offcanvas_switch_presence)

        async def ctrl_click_anchor_does_not_navigate_current_tab():
            await goto_tr()
            before = page.url
            await page.keyboard.down("Control")
            await page.click('[data-testid="lang-header-en"]', force=True)
            await page.keyboard.up("Control")
            await page.wait_for_timeout(400)
            if page.url != before:
                raise Exception("Ctrl-click navigated current tab")

        await run_step("Modifier-click keeps current tab behavior", ctrl_click_anchor_does_not_navigate_current_tab)

        async def representative_pages_and_query_hash_behavior():
            pages = [
                "tr/the-residences-east-west.html?src=qa#hero",
                "tr/medya.html?src=qa#top",
                "tr/gizlilik-bildirimi.html?src=qa#p1",
            ]
            for rel in pages:
                await page.goto(f"https://darg-clone-1.preview.emergentagent.com/{rel}", wait_until="domcontentloaded")
                await page.wait_for_selector('[data-testid="lang-header-en"]', timeout=8000)
                expected_en = await page.evaluate('''() => new URL(document.querySelector('[data-testid="lang-header-en"]').getAttribute('href'), location.href).href''')
                await page.click('[data-testid="lang-header-en"]', force=True)
                await page.wait_for_url("**/en/**", timeout=7000)
                if page.url.split("#")[0] != expected_en.split("#")[0]:
                    raise Exception(f"Did not navigate to anchor href target. expected={expected_en}, got={page.url}")
                await page.go_back(wait_until="domcontentloaded")
                await page.wait_for_timeout(300)

        await run_step("Project/newsroom/legal pages preserve existing anchor targets", representative_pages_and_query_hash_behavior)

        async def responsive_visibility_overflow_and_hitareas():
            widths = [320, 390, 768, 800, 900, 1024, 1440, 1920]
            for w in widths:
                h = 844 if w <= 390 else 1024 if w <= 900 else 1080
                await page.set_viewport_size({"width": w, "height": h})
                await goto_tr()
                checks = await page.evaluate('''() => {
                    const sw = document.querySelector('[data-testid="lang-switch"]');
                    const toggle = document.querySelector('[data-testid="lang-header-toggle"]');
                    const tr = document.querySelector('[data-testid="lang-header-tr"]');
                    const en = document.querySelector('[data-testid="lang-header-en"]');
                    const rail = document.querySelector('[data-testid="lang-header-rail"]');
                    const rect = el => el ? el.getBoundingClientRect() : null;
                    return {
                        overflow: document.documentElement.scrollWidth > window.innerWidth + 1,
                        sw: rect(sw),
                        toggle: rect(toggle),
                        tr: rect(tr),
                        en: rect(en),
                        rail: rect(rail),
                        viewport: { w: window.innerWidth, h: window.innerHeight }
                    };
                }''')
                if checks["overflow"]:
                    raise Exception(f"Horizontal overflow at width {w}")
                for key in ["sw", "toggle", "tr", "en", "rail"]:
                    if not checks[key]:
                        raise Exception(f"Missing {key} at width {w}")
                    r = checks[key]
                    if r["right"] < 0 or r["left"] > w or r["bottom"] < 0:
                        raise Exception(f"{key} not visible at width {w}")

                tw = checks["toggle"]["width"]
                th = checks["toggle"]["height"]
                trw = checks["tr"]["width"]
                trh = checks["tr"]["height"]
                enw = checks["en"]["width"]
                enh = checks["en"]["height"]

                if 769 <= w <= 900:
                    if tw < 32 or th < 44:
                        raise Exception(f"Narrow-tablet hit area too small at {w}: {tw}x{th}")
                    if trw < 12 or enw < 12 or trh < 44 or enh < 44:
                        raise Exception(f"Narrow-tablet label area too small at {w}: TR {trw}x{trh}, EN {enw}x{enh}")
                else:
                    if tw < 48 or th < 44:
                        raise Exception(f"Desktop/mobile hit area too small at {w}: {tw}x{th}")
                    if trw < 24 or enw < 24 or trh < 44 or enh < 44:
                        raise Exception(f"Label area too small at {w}: TR {trw}x{trh}, EN {enw}x{enh}")

        await run_step("Responsive visibility + overflow + target sizes", responsive_visibility_overflow_and_hitareas)

        async def touch_swipe_mobile():
            await page.set_viewport_size({"width": 390, "height": 844})
            await goto_tr()

            # Use Chrome DevTools Protocol for real touch events.
            cdp = await page.context.new_cdp_session(page)
            await cdp.send("Emulation.setTouchEmulationEnabled", {"enabled": True, "maxTouchPoints": 2})

            box = await page.locator('[data-testid="lang-header-toggle"]').bounding_box()
            if not box:
                raise Exception("No toggle for touch")
            y = box["y"] + box["height"] * 0.5
            x1 = box["x"] + box["width"] * 0.35
            x2 = box["x"] + box["width"] * 0.85

            before = page.url
            await cdp.send("Input.dispatchTouchEvent", {
                "type": "touchStart",
                "touchPoints": [{"x": x1, "y": y, "radiusX": 4, "radiusY": 4, "id": 1}],
            })
            await cdp.send("Input.dispatchTouchEvent", {
                "type": "touchMove",
                "touchPoints": [{"x": x2, "y": y, "radiusX": 4, "radiusY": 4, "id": 1}],
            })
            await page.wait_for_timeout(250)
            if page.url != before:
                raise Exception("Touch moved caused navigation before release")
            await cdp.send("Input.dispatchTouchEvent", {
                "type": "touchEnd",
                "touchPoints": [],
            })
            await page.wait_for_url("**/en/**", timeout=7000)

        await run_step("Real touch swipe commits on release", touch_swipe_mobile)

        async def final_error_scan():
            error_text = await page.evaluate("""() => {
    const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));
    return errorElements.map(el => el.textContent).join(", ");
    }""")
            if error_text:
                print(f"Found error message: {error_text}")
            else:
                print("No error messages found on the page")

        await run_step("Final page error scan", final_error_scan)

        await page.screenshot(path="/app/test_reports/screenshots_iter62/automation_output/20261026_152458_9eb8202330bd/lang_toggle_final.jpeg", type="jpeg", quality=40, full_page=False)

    await main()
