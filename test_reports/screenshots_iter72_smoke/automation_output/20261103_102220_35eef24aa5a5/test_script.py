async def run_test(page, output_dir, page_url):
    await page.set_viewport_size({"width":1920,"height":1080})
    try:
        await page.get_by_test_id('intro-video-hero').wait_for()
        await page.wait_for_timeout(1500)
        print('PASS homepage loads', await page.title())
        await page.screenshot(path='/app/test_reports/screenshots_iter72_smoke/automation_output/20261103_102220_35eef24aa5a5/home.jpeg', type="jpeg", quality=40, full_page=False)
    except Exception as e:
        print('FAIL homepage',str(e))
