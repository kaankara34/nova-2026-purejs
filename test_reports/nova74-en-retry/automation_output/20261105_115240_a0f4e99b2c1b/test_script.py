async def run_test(page, output_dir, page_url):
    await page.set_viewport_size({'width':1920,'height':1080})
    try:
        await page.get_by_test_id('header-control-1').wait_for(state='visible', timeout=15000)
        await page.wait_for_function('document.querySelector("[data-testid=intro-video]").readyState>=2')
        assert await page.get_by_test_id('header-logo-image').evaluate('(i)=>i.complete&&i.naturalWidth>0')
        assert await page.evaluate('Math.max(document.documentElement.scrollWidth,document.body.scrollWidth)-innerWidth') <= 1
        await page.get_by_test_id('header-control-1').click(force=True)
        await page.wait_for_timeout(700)
        await page.get_by_test_id('menu-control-1').click(force=True)
        await page.wait_for_timeout(700)
        assert await page.evaluate('!document.getElementById("sideMenu").classList.contains("open")')
        await page.screenshot(path='/app/test_reports/nova74-en-retry/automation_output/20261105_115240_a0f4e99b2c1b/en-desktop.jpeg', type="jpeg", quality=40, full_page=False)
        print('PASS EN desktop retry: page/logo/hero/menu/overflow; title', await page.title())
    except Exception as e:
        print('FAIL EN desktop retry', str(e))
