async def run_test(page, output_dir, page_url):
    try:
        await page.set_viewport_size({"width": 1440, "height": 900})
        await page.goto("https://515dc9a7-0d61-46f2-bb41-31805466b8fc.preview.emergentagent.com/tr/index.html", wait_until="domcontentloaded")
        await page.wait_for_timeout(600)
        await page.keyboard.press("Tab")
        await page.keyboard.press("Tab")
        await page.keyboard.press("Tab")
        await page.keyboard.press("Tab")
        await page.keyboard.press("Tab")
        await page.focus('[data-testid="lang-header-en"]')
        await page.keyboard.press("Tab")
        await page.keyboard.press("Shift+Tab")
        state = await page.evaluate("""() => {
          const el = document.querySelector('[data-testid="lang-header-en"]');
          const st = getComputedStyle(el);
          return {
            focused: document.activeElement === el,
            outlineStyle: st.outlineStyle,
            outlineWidth: st.outlineWidth,
            ariaCurrentEn: el.getAttribute('aria-current'),
            ariaCurrentTr: document.querySelector('[data-testid="lang-header-tr"]').getAttribute('aria-current')
          };
        }""")
        print(f"Keyboard focus state: {state}")
    except Exception as e:
        print(f"FAIL: {e}")
