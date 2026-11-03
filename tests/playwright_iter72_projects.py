# Reuse all tower/unit and Bahar regressions; verify unaffected non-home header/layout.
async def run(page):
    import importlib.util
    base = page.url.split('/tr/')[0].split('/en/')[0]
    spec = importlib.util.spec_from_file_location('prior_projects','/app/tests/playwright_iter71_projects.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = await module.run(page,base)
    print('PROJECT RESULTS',result)
    for width,height in [(1920,1080),(390,844)]:
        await page.set_viewport_size({'width':width,'height':height})
        for lang,filename in [('tr','projeler.html'),('en','projects.html')]:
            try:
                await page.goto(f'{base}/{lang}/{filename}',wait_until='load')
                assert await page.locator('.home-hero-scrollover').count()==0
                assert await page.locator('#siteHeader').evaluate('(h)=>h.classList.contains("transparent")')
                await page.mouse.wheel(0,900)
                await page.wait_for_timeout(1000)
                state = await page.evaluate('''() => {const h=document.querySelector('#siteHeader');return {transparent:h.classList.contains('transparent'),bg:getComputedStyle(h).backgroundColor,overflow:document.documentElement.scrollWidth-innerWidth,heroPosition:getComputedStyle(document.querySelector('.pj-hero')).position};}''')
                assert not state['transparent'] and state['overflow']==0 and state['heroPosition']!='sticky',state
                await page.get_by_test_id('pj-card-bahar-residence').scroll_into_view_if_needed()
                await page.wait_for_function('''() => {const i=document.querySelector('[data-testid="pj-card-bahar-residence"] img');return i.complete && i.naturalWidth>0;}''')
                print('PASS non-home header/layout/Bahar',lang,width,state)
                await page.get_by_test_id('header-control-1').click(force=True)
                await page.wait_for_timeout(650)
                assert await page.locator('#sideMenu').evaluate('(e)=>e.classList.contains("open")')
                await page.get_by_test_id('menu-control-1').click(force=True)
                await page.wait_for_timeout(650)
                assert not await page.locator('#sideMenu').evaluate('(e)=>e.classList.contains("open")')
                print('PASS non-home menu',lang,width)
            except Exception as e:
                print('FAIL non-home',lang,width,str(e))