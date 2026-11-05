async def run_test(page, output_dir, page_url):
    await page.set_viewport_size({"width": 1920, "height": 1080})
    try:
        await page.get_by_test_id('intro-video-hero').wait_for(state='visible')
        await page.wait_for_timeout(1800)
        print('PASS frontend loads; title:', await page.title())
        print('VIDEO', await page.get_by_test_id('intro-video').evaluate('(v)=>({ready:v.readyState,width:v.videoWidth,error:v.error&&v.error.message,src:v.currentSrc})'))
        await page.screenshot(path='/app/test_reports/nova74-smoke/automation_output/20261105_114851_0c0c749415d7/home.jpeg', type="jpeg", quality=40, full_page=False)
    except Exception as e:
        print('FAIL smoke', str(e))
