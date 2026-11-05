"""Public-preview static navigation/media review; no submissions or API mocking."""
async def run(page):
    from urllib.parse import urlsplit
    base = urlsplit(page.url)
    origin = base.scheme + '://' + base.netloc
    errors, console_errors, failed_http = [], [], []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda m: console_errors.append(m.text) if m.type == 'error' else None)
    page.on('response', lambda r: failed_http.append([r.status, r.url]) if r.status >= 400 else None)
    paths = ['tr/index.html', 'en/index.html', 'tr/projeler.html', 'en/projects.html',
             'tr/the-residences-east-west.html', 'en/the-residences-east-west.html']
    passed = 0
    for width, height in [(1920, 1080), (390, 844)]:
        await page.set_viewport_size({'width': width, 'height': height})
        for path in paths:
            try:
                response = await page.goto(origin + '/' + path, wait_until='domcontentloaded')
                await page.get_by_test_id('header-control-1').wait_for(state='visible')
                await page.wait_for_timeout(1200)
                assert response.status == 200
                assert await page.locator('html').get_attribute('lang') == path[:2]
                overflow = await page.evaluate('Math.max(document.documentElement.scrollWidth,document.body.scrollWidth)-innerWidth')
                assert overflow <= 1, f'overflow={overflow}'
                assert await page.get_by_test_id('header-logo-image').evaluate('(i)=>i.complete&&i.naturalWidth>0')
                if path.endswith('/index.html'):
                    await page.wait_for_function('document.querySelector("[data-testid=intro-video]").readyState>=2')
                    video = await page.get_by_test_id('intro-video').evaluate('(v)=>({width:v.videoWidth,error:v.error&&v.error.message,ready:v.readyState})')
                    assert video['width'] > 0 and not video['error']
                    print('PASS hero', path, width, video)
                    await page.screenshot(path=f'/app/test_reports/nova74-browser/{path[:2]}-{width}.jpeg', quality=40, full_page=False)
                await page.get_by_test_id('header-control-1').click(force=True)
                await page.wait_for_function('document.getElementById("sideMenu").classList.contains("open")')
                await page.wait_for_timeout(650)
                await page.get_by_test_id('menu-control-1').click(force=True)
                await page.wait_for_function('!document.getElementById("sideMenu").classList.contains("open")')
                print('PASS page/media/menu/overflow', width, path)
                passed += 1
            except Exception as e:
                print('FAIL', width, path, str(e))
    for lang, portfolio in [('tr','projeler.html'), ('en','projects.html')]:
        try:
            await page.goto(origin + '/' + lang + '/index.html', wait_until='domcontentloaded')
            await page.get_by_test_id('header-control-1').click(force=True)
            await page.wait_for_timeout(650)
            await page.get_by_test_id('menu-link-portfolio').click(force=True)
            await page.wait_for_url('**/' + lang + '/' + portfolio)
            await page.get_by_test_id('header-control-2').click(force=True)
            await page.wait_for_url('**/' + lang + '/index.html#top')
            await page.get_by_test_id('ew-feature-cta').click(force=True)
            await page.wait_for_url('**/' + lang + '/the-residences-east-west.html')
            await page.get_by_test_id('lang-header-' + ('en' if lang == 'tr' else 'tr')).click(force=True)
            await page.wait_for_url('**/' + ('en' if lang == 'tr' else 'tr') + '/the-residences-east-west.html')
            print('PASS navigation workflow', lang)
            passed += 1
        except Exception as e:
            print('FAIL navigation', lang, str(e))
    error_text = await page.evaluate("""() => {
        const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));
        return errorElements.map(el => el.textContent).join(', ');
    }""")
    print(f'Found error message: {error_text}' if error_text else 'No error messages found on the page')
    print('RESULT', {'passed': passed, 'total': 14, 'page_errors': errors, 'console_errors': console_errors, 'http_errors': failed_http})