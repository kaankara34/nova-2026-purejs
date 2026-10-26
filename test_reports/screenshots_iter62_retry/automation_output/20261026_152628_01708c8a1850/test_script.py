async def run_test(page, output_dir, page_url):
    import asyncio

    page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))

    async def run_step(name, coro):
        try:
            await coro()
            print(f"PASS: {name}")
        except Exception as e:
            print(f"FAIL: {name} -> {e}")

    async def main():
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.goto("https://darg-clone-1.preview.emergentagent.com/tr/index.html", wait_until="domcontentloaded")
        await page.wait_for_selector('[data-testid="lang-header-toggle"]', timeout=12000)
        await page.wait_for_timeout(700)

        async def click_roundtrip():
            print("URL start:", page.url)
            await page.click('[data-testid="lang-header-toggle"]', force=True)
            await page.wait_for_timeout(350)
            await page.wait_for_url("**/en/**", timeout=9000)
            print("URL after first click:", page.url)

            await page.wait_for_timeout(500)
            await page.click('[data-testid="lang-header-toggle"]', force=True)
            await page.wait_for_timeout(350)
            await page.wait_for_url("**/tr/**", timeout=9000)
            print("URL after second click:", page.url)

        await run_step("Click roundtrip TR->EN->TR", click_roundtrip)

        async def keyboard_roundtrip():
            await page.goto("https://darg-clone-1.preview.emergentagent.com/tr/index.html", wait_until="domcontentloaded")
            await page.wait_for_selector('[data-testid="lang-header-toggle"]', timeout=12000)
            await page.wait_for_timeout(700)
            await page.focus('[data-testid="lang-header-toggle"]')
            await page.keyboard.press("Space")
            await page.wait_for_timeout(350)
            await page.wait_for_url("**/en/**", timeout=9000)
            print("URL after Space:", page.url)

            await page.wait_for_timeout(500)
            await page.focus('[data-testid="lang-header-toggle"]')
            await page.keyboard.press("ArrowLeft")
            await page.wait_for_timeout(350)
            await page.wait_for_url("**/tr/**", timeout=9000)
            print("URL after ArrowLeft:", page.url)

            await page.wait_for_timeout(500)
            await page.focus('[data-testid="lang-header-toggle"]')
            await page.keyboard.press("Enter")
            await page.wait_for_timeout(350)
            await page.wait_for_url("**/en/**", timeout=9000)
            print("URL after Enter:", page.url)

        await run_step("Keyboard roundtrip", keyboard_roundtrip)

        async def responsive_no_reload():
            widths = [320, 390, 768, 800, 900, 1024, 1440, 1920]
            await page.goto("https://darg-clone-1.preview.emergentagent.com/tr/index.html", wait_until="domcontentloaded")
            await page.wait_for_selector('[data-testid="lang-header-toggle"]', timeout=12000)
            for w in widths:
                h = 844 if w <= 390 else 1024 if w <= 900 else 1080
                await page.set_viewport_size({"width": w, "height": h})
                await page.wait_for_timeout(260)
                checks = await page.evaluate('''() => {
                    const t = document.querySelector('[data-testid="lang-header-toggle"]')?.getBoundingClientRect();
                    const tr = document.querySelector('[data-testid="lang-header-tr"]')?.getBoundingClientRect();
                    const en = document.querySelector('[data-testid="lang-header-en"]')?.getBoundingClientRect();
                    return {
                        overflow: document.documentElement.scrollWidth > window.innerWidth + 1,
                        t: t ? {w:t.width,h:t.height} : null,
                        tr: tr ? {w:tr.width,h:tr.height} : null,
                        en: en ? {w:en.width,h:en.height} : null,
                        vw: window.innerWidth
                    };
                }''')
                print(f"RESP {w}: {checks}")
                if checks["overflow"]:
                    raise Exception(f"Overflow at {w}")
                if not checks["t"] or checks["t"]["h"] < 44:
                    raise Exception(f"Toggle missing/height<44 at {w}")
                if 769 <= w <= 900:
                    if checks["t"]["w"] < 32:
                        raise Exception(f"Toggle width<32 at {w}")
                    if not checks["tr"] or not checks["en"] or checks["tr"]["w"] < 12 or checks["en"]["w"] < 12:
                        raise Exception(f"Labels width<12 at {w}")
                else:
                    if checks["t"]["w"] < 48:
                        raise Exception(f"Toggle width<48 at {w}")
                    if not checks["tr"] or not checks["en"] or checks["tr"]["w"] < 24 or checks["en"]["w"] < 24:
                        raise Exception(f"Labels width<24 at {w}")

        await run_step("Responsive checks without reload storm", responsive_no_reload)

    await main()
