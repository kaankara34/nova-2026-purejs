import asyncio
import os
import json
from pathlib import Path
from playwright.async_api import async_playwright


BASE = os.environ['REACT_APP_BACKEND_URL'].rstrip('/')
HERO_PATHS = [
    "/en/index.html",
    "/tr/index.html",
    "/en/mercan-bosphorus.html",
    "/tr/mercan-bosphorus.html",
    "/en/marti-residence.html",
    "/tr/marti-residence.html",
    "/en/bahar-residence.html",
    "/tr/bahar-residence.html",
    "/en/the-residences-east-west.html",
    "/tr/the-residences-east-west.html",
    "/en/the-apartments-ana.html",
    "/tr/the-apartments-ana.html",
]


async def check_hero_page(page, path, browser_name):
    url = f"{BASE}{path}"
    result = {
        "url": url,
        "loaded": False,
        "video_found": False,
        "progress_ok": False,
        "pause_persist_ok": False,
        "resume_ok": False,
        "notes": [],
    }
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(700)
        result["loaded"] = True

        video = page.locator("video[data-hero-video]").first
        if await video.count() == 0:
            result["notes"].append("no hero video element")
            return result
        result["video_found"] = True
        try:
            await page.wait_for_function("(() => { const v=document.querySelector('video[data-hero-video]'); return v && (v.readyState>=2 || v.error); })()", timeout=15000)
        except Exception:
            result["notes"].append("media readiness timeout")
        result["media_capability"] = await video.evaluate("v=>({mp4:v.canPlayType('video/mp4; codecs=\"avc1.640028\"'),webm:v.canPlayType('video/webm; codecs=\"vp9\"'),ready:v.readyState,network:v.networkState,src:v.currentSrc,error:v.error?{code:v.error.code,message:v.error.message}:null})")

        t1 = await video.evaluate("el => el.currentTime")
        await page.wait_for_timeout(2000)
        t2 = await video.evaluate("el => el.currentTime")
        if (t2 - t1) > 0.15:
            result["progress_ok"] = True
        else:
            result["notes"].append(f"no visible progress ({t1:.3f}->{t2:.3f}) - possible codec/autoplay/runtime limit")

        # User-intentional pause should persist across lifecycle events.
        await video.evaluate("el => el.pause()")
        await page.wait_for_timeout(100)
        p1 = await video.evaluate("el => ({paused: el.paused, t: el.currentTime})")
        await page.evaluate("window.dispatchEvent(new Event('blur'))")
        await page.evaluate("window.dispatchEvent(new Event('focus'))")
        await page.evaluate("window.dispatchEvent(new PageTransitionEvent('pagehide', {persisted: true}))")
        await page.evaluate("window.dispatchEvent(new PageTransitionEvent('pageshow', {persisted: true}))")
        await page.wait_for_timeout(700)
        p2 = await video.evaluate("el => ({paused: el.paused, t: el.currentTime})")
        if p1["paused"] and p2["paused"] and abs(p2["t"] - p1["t"]) < 0.2:
            result["pause_persist_ok"] = True
        else:
            result["notes"].append(f"pause persistence mismatch: before={p1}, after={p2}")

        await page.evaluate("document.querySelector('video[data-hero-video]')?.dispatchEvent(new Event('nova:hero-resume'))")
        await page.wait_for_timeout(1200)
        p3 = await video.evaluate("el => ({paused: el.paused, t: el.currentTime})")
        if (not p3["paused"]) and (p3["t"] >= p2["t"]):
            result["resume_ok"] = True
        else:
            result["notes"].append(f"resume event did not restore playback: {p3}")

    except Exception as exc:
        result["notes"].append(f"error: {exc}")
    return result


async def check_mobile_menu_and_switch_visibility(page):
    widths = [320, 390, 768, 1024, 1100, 1440, 1920]
    rows = []
    for width in widths:
        height = 844 if width <= 1100 else 1080
        row = {"width": width, "ok": False, "notes": []}
        try:
            await page.set_viewport_size({"width": width, "height": height})
            await page.goto(f"{BASE}/en/index.html", wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(600)
            await page.click("#menuToggle", force=True)
            await page.wait_for_timeout(350)

            state = await page.evaluate(
                """() => {
                const header = document.querySelector('[data-testid="lang-switch"]');
                const menu = document.querySelector('[data-testid="lang-switch-menu"]');
                const hit = document.elementFromPoint(window.innerWidth - 24, 70);
                function read(el){
                    if(!el) return null;
                    const s = getComputedStyle(el);
                    const r = el.getBoundingClientRect();
                    return {
                        display: s.display,
                        visibility: s.visibility,
                        opacity: s.opacity,
                        pointerEvents: s.pointerEvents,
                        width: r.width,
                        height: r.height
                    };
                }
                return {
                    bodyMenuOpen: document.body.classList.contains('nova-menu-open'),
                    header: read(header),
                    menu: read(menu),
                    hitTag: hit ? hit.tagName : null,
                    hitClass: hit ? hit.className : null
                };
            }"""
            )

            if width <= 1100:
                cond = (
                    state.get("bodyMenuOpen")
                    and state.get("header")
                    and state["header"]["display"] == "none"
                    and state.get("menu")
                    and state["menu"]["display"] == "none"
                )
            else:
                cond = state.get("bodyMenuOpen") and state.get("header") and state["header"]["display"] != "none"

            row["ok"] = bool(cond)
            if not row["ok"]:
                row["notes"].append(f"state={state}")

            await page.keyboard.press("Escape")
            await page.wait_for_timeout(250)
        except Exception as exc:
            row["notes"].append(str(exc))
        rows.append(row)
    return rows


async def check_east_west_border(page):
    result = {"ok": False, "notes": []}
    try:
        await page.set_viewport_size({"width": 1920, "height": 1080})
        await page.goto(f"{BASE}/en/index.html", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_selector("#eastWestFeature", timeout=15000)
        await page.evaluate("document.getElementById('eastWestFeature').scrollIntoView({block:'center'})")
        await page.wait_for_timeout(1200)

        sample1 = await page.evaluate(
            """() => Array.from(document.querySelectorAll('.ew-progress-active')).map(el => {
                const anim = el.getAnimations()[0];
                return anim ? {state: anim.playState, t: Number(anim.currentTime||0)} : {state:'none', t:0};
            })"""
        )
        await page.wait_for_timeout(1200)
        sample2 = await page.evaluate(
            """() => Array.from(document.querySelectorAll('.ew-progress-active')).map(el => {
                const anim = el.getAnimations()[0];
                return anim ? {state: anim.playState, t: Number(anim.currentTime||0)} : {state:'none', t:0};
            })"""
        )
        progressed = any((b["t"] - a["t"]) > 80 for a, b in zip(sample1, sample2))

        await page.evaluate("window.scrollTo({top: 0, behavior: 'instant'})")
        await page.wait_for_timeout(900)
        off1 = await page.evaluate(
            """() => Array.from(document.querySelectorAll('.ew-progress-active')).map(el => {
                const anim = el.getAnimations()[0];
                return anim ? Number(anim.currentTime||0) : 0;
            })"""
        )
        await page.wait_for_timeout(900)
        off2 = await page.evaluate(
            """() => Array.from(document.querySelectorAll('.ew-progress-active')).map(el => {
                const anim = el.getAnimations()[0];
                return anim ? Number(anim.currentTime||0) : 0;
            })"""
        )
        mostly_paused = all(abs(b - a) < 60 for a, b in zip(off1, off2))

        await page.evaluate("document.getElementById('eastWestFeature').scrollIntoView({block:'center'})")
        await page.wait_for_timeout(1000)
        on1 = await page.evaluate(
            """() => Array.from(document.querySelectorAll('.ew-progress-active')).map(el => {
                const anim = el.getAnimations()[0];
                return anim ? Number(anim.currentTime||0) : 0;
            })"""
        )
        await page.wait_for_timeout(1000)
        on2 = await page.evaluate(
            """() => Array.from(document.querySelectorAll('.ew-progress-active')).map(el => {
                const anim = el.getAnimations()[0];
                return anim ? Number(anim.currentTime||0) : 0;
            })"""
        )
        resumed = any((b - a) > 80 for a, b in zip(on1, on2))

        result["ok"] = bool(progressed and mostly_paused and resumed)
        if not result["ok"]:
            result["notes"].append(
                f"progressed={progressed}, paused_offscreen={mostly_paused}, resumed={resumed}, sample1={sample1}, sample2={sample2}"
            )
    except Exception as exc:
        result["notes"].append(str(exc))
    return result


async def main():
    report = {"browsers": {}, "menu": None, "east_west": None}
    async with async_playwright() as p:
        for browser_name in ("chromium", "webkit"):
            browser_type = getattr(p, browser_name)
            try:
                browser = await browser_type.launch(headless=True)
            except Exception as exc:
                report["browsers"][browser_name] = {"available": False, "error": str(exc)}
                print(f"BROWSER {browser_name}: unavailable -> {exc}")
                continue

            context = await browser.new_context(viewport={"width": 1920, "height": 1080})
            page = await context.new_page()
            page.set_default_timeout(30000)

            hero_results = []
            for path in HERO_PATHS:
                hero_results.append(await check_hero_page(page, path, browser_name))

            report["browsers"][browser_name] = {
                "available": True,
                "hero_results": hero_results,
            }

            if browser_name == "chromium":
                report["menu"] = await check_mobile_menu_and_switch_visibility(page)
                report["east_west"] = await check_east_west_border(page)

            await context.close()
            await browser.close()

    print("=== ITER66 PLAYWRIGHT REPORT START ===")
    for browser_name, data in report["browsers"].items():
        if not data.get("available"):
            print(f"{browser_name}: unavailable ({data.get('error')})")
            continue
        ok_count = sum(1 for r in data["hero_results"] if r["video_found"] and r["progress_ok"])
        print(f"{browser_name}: hero progress pass {ok_count}/{len(data['hero_results'])}")
        for row in data["hero_results"]:
            if row["notes"]:
                print(f"  - {row['url']} :: {' | '.join(row['notes'])}")

    print("Menu checks:")
    for row in report.get("menu") or []:
        print(f"  - width={row['width']} ok={row['ok']} notes={row['notes']}")

    print(f"EastWest border check: {report.get('east_west')}")
    print("=== ITER66 PLAYWRIGHT REPORT END ===")
    Path('/app/test_reports/iter66_browser_followup.json').write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
