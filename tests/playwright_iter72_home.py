# Homepage scroll-over, header, arrow and first-click register regression checks.
async def run(page):
    base = page.url.split('/tr/')[0].split('/en/')[0]
    failures = []
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    await page.add_init_script("localStorage.removeItem('nova-news-feed:tr'); localStorage.removeItem('nova-news-feed:en'); localStorage.setItem('nova_cookie_notice_dismissed','1');")
    for width, height in [(1920,1080),(390,844)]:
        await page.set_viewport_size({'width':width,'height':height})
        for lang in ['tr','en']:
            label = f'{lang}-{width}'
            try:
                await page.goto(f'{base}/{lang}/index.html', wait_until='load')
                await page.get_by_test_id('intro-video').wait_for()
                await page.wait_for_function("!document.querySelector('#heroVideo').paused && document.querySelector('#heroVideo').currentTime > 0", timeout=15000)
                initial = await page.evaluate("({y:scrollY,content:document.querySelector('.home-scrollover-content').getBoundingClientRect().top,transparent:document.querySelector('#siteHeader').classList.contains('transparent')})")
                assert initial['y'] == 0 and initial['transparent'], initial
                print('PASS top transparent',label,initial)
                await page.mouse.wheel(0, initial['content']-40)
                await page.wait_for_timeout(1000)
                geometry = await page.evaluate("""() => {const hero=document.querySelector('#top'),content=document.querySelector('.home-scrollover-content'),header=document.querySelector('#siteHeader'),v=document.querySelector('#heroVideo');return {y:scrollY,hero:hero.getBoundingClientRect().top,content:content.getBoundingClientRect().top,header:header.getBoundingClientRect().bottom,transparent:header.classList.contains('transparent'),bg:getComputedStyle(header).backgroundColor,color:getComputedStyle(header).color,paused:v.paused,time:v.currentTime,overflow:document.documentElement.scrollWidth-innerWidth,snap:getComputedStyle(document.documentElement).scrollSnapType};}""")
                assert abs(geometry['hero']) < 1 and geometry['content'] <= geometry['header'], geometry
                assert not geometry['transparent'] and geometry['bg']=='rgba(11, 11, 11, 0.94)', geometry
                assert geometry['color']=='rgb(255, 255, 255)' and geometry['overflow']==0 and geometry['snap']=='none', geometry
                assert not geometry['paused'], geometry
                await page.wait_for_timeout(500)
                assert await page.get_by_test_id('intro-video').evaluate('(v)=>v.currentTime') > geometry['time']
                print('PASS sticky/header/native/video',label,geometry)
                if label=='tr-1920':
                    await page.screenshot(path='/app/test_reports/screenshots_iter72_home/header.jpeg',quality=40,full_page=False)
                await page.mouse.wheel(0,-geometry['y'])
                await page.wait_for_timeout(1000)
                assert await page.evaluate('scrollY')==0
                assert abs(await page.locator('.home-scrollover-content').evaluate('(e)=>e.getBoundingClientRect().top')-initial['content'])<1
                print('PASS reverse restores origin',label)
                await page.get_by_test_id('hero-scroll-button').click(force=True)
                await page.wait_for_timeout(1500)
                arrow = await page.locator('#buildBeyondLiving').evaluate('(e)=>({y:scrollY,top:e.getBoundingClientRect().top})')
                assert arrow['y']>0 and abs(arrow['top'])<2, arrow
                print('PASS hero arrow target',label,arrow)
            except Exception as e:
                failures.append(label+':'+str(e))
                print('FAIL',label,str(e))
            try:
                await page.goto(f'{base}/{lang}/index.html',wait_until='load')
                await page.wait_for_function('!!window.NovaNewsHome')
                assert await page.get_by_test_id('news-home-grid').get_attribute('aria-busy')=='true'
                await page.get_by_test_id('header-control-3' if width==1920 else 'bottom-control-1').click(force=True)
                await page.wait_for_function("document.querySelector('#newsHomeGrid').getAttribute('aria-busy')==='false'",timeout=15000)
                await page.wait_for_timeout(5000)
                register = await page.locator('#register').evaluate('(e)=>({top:e.getBoundingClientRect().top,y:scrollY,cards:document.querySelectorAll("#newsHomeGrid .news-card").length})')
                assert abs(register['top'])<=110 and register['cards']==(6 if width==1920 else 3), register
                await page.wait_for_timeout(1000)
                assert abs(await page.locator('#register').evaluate('(e)=>e.getBoundingClientRect().top')-register['top'])<2
                print('PASS fresh first-click CTA and stable layout',label,register)
                if label=='tr-390':
                    await page.screenshot(path='/app/test_reports/screenshots_iter72_home/mobile-register.jpeg',quality=40,full_page=False)
            except Exception as e:
                failures.append('CTA '+label+':'+str(e))
                print('FAIL CTA',label,str(e))
    await page.emulate_media(reduced_motion='reduce')
    for lang in ['tr','en']:
        try:
            await page.goto(f'{base}/{lang}/index.html',wait_until='load')
            assert await page.get_by_test_id('intro-video-hero').evaluate('(e)=>getComputedStyle(e).position')=='relative'
            await page.mouse.wheel(0,250)
            await page.wait_for_timeout(500)
            assert await page.get_by_test_id('intro-video-hero').evaluate('(e)=>e.getBoundingClientRect().top')<0
            print('PASS reduced-motion natural flow',lang)
        except Exception as e:
            failures.append('reduced '+lang+':'+str(e))
            print('FAIL reduced motion',lang,str(e))
    error_text = await page.evaluate("""() => {const errorElements=Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));return errorElements.map(el=>el.textContent).join(', ');}""")
    print(f'Found error message: {error_text}' if error_text else 'No error messages found on the page')
    print('PAGE ERRORS',errors,'FAILURES',failures)