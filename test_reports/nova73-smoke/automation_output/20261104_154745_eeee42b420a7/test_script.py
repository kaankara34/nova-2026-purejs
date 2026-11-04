async def run_test(page, output_dir, page_url):
    try:
        await page.set_viewport_size({"width":1920,"height":1080})
        await page.get_by_test_id('intro-video-hero').wait_for(state='visible')
        await page.wait_for_timeout(2000)
        await page.screenshot(path='/app/test_reports/nova73-smoke/automation_output/20261104_154745_eeee42b420a7/nova73-smoke.jpeg', type="jpeg", quality=40, full_page=False)
        print('PASS homepage loads', await page.title())
    except Exception as e:
        print('FAIL homepage loads', str(e))
