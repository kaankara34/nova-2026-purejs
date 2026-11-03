async def run_test(page, output_dir, page_url):
    try:
        await page.set_viewport_size({"width":1920,"height":1080})
        await page.get_by_test_id('intro-video-hero').wait_for(state='visible')
        await page.wait_for_timeout(2500)
        print('PASS homepage loaded', await page.title())
        await page.screenshot(path='/app/test_reports/screenshots_iter71_smoke/automation_output/20261103_101347_dbd4495a69da/home.jpeg', type="jpeg", quality=40, full_page=False)
    except Exception as e:
        print('FAIL homepage load', str(e))
