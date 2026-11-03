async def run_test(page, output_dir, page_url):
    import json
    base=page.url.split('/tr/')[0]
    state='''() => { const h=document.querySelector('[data-testid="intro-video-hero"]'), c=document.querySelector('.home-scrollover-content'), v=document.querySelector('[data-testid="intro-video"]'); const hb=h.getBoundingClientRect(), cb=c.getBoundingClientRect(); return {position:getComputedStyle(h).position,heroTop:hb.top,height:hb.height,contentTop:cb.top,background:getComputedStyle(c).backgroundColor,scrollY,overflow:document.documentElement.scrollWidth>innerWidth,paused:v.paused,time:v.currentTime,ready:v.readyState,headerBottom:document.querySelector('#siteHeader').getBoundingClientRect().bottom,bottomTop:document.querySelector('#mobileBottomBar').getBoundingClientRect().top}; }'''
    errors=[]
    failures=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('response',lambda r:failures.append([r.status,r.url]) if '/media/' in r.url and r.status>=400 else None)
    for viewport,mode in [({'width':1920,'height':1080},'no-preference'),({'width':390,'height':844},'no-preference'),({'width':1920,'height':1080},'reduce')]:
        await page.set_viewport_size(viewport)
        await page.emulate_media(reduced_motion=mode)
        for lang in ['tr','en']:
            name=f'{lang}-{viewport["width"]}-{mode}'
            try:
                await page.goto(f'{base}/{lang}/index.html',wait_until='domcontentloaded')
                await page.get_by_test_id('intro-video-hero').wait_for(state='visible')
                await page.wait_for_timeout(2800)
                initial=await page.evaluate(state)
                assert initial['position']==('relative' if mode=='reduce' else 'sticky'),initial
                assert not initial['overflow'],initial
                await page.mouse.wheel(0,round(initial['height']*.6))
                await page.wait_for_timeout(1200)
                middle=await page.evaluate(state)
                assert abs(middle['contentTop']-(initial['contentTop']-middle['scrollY']))<2,middle
                assert middle['background']=='rgb(255, 255, 255)' and not middle['overflow'],middle
                assert abs(middle['heroTop']-(-middle['scrollY'] if mode=='reduce' else 0))<2,middle
                if mode!='reduce':
                    assert not initial['paused'] and not middle['paused'] and middle['time']>initial['time'],[initial,middle]
                if viewport['width']==390:
                    assert middle['headerBottom']<middle['bottomTop'],middle
                clickable=await page.get_by_test_id('header-control-1').evaluate('(b)=>{const r=b.getBoundingClientRect();return b.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height/2));}')
                assert clickable,'Header menu obstructed'
                if lang=='tr' and mode!='reduce':
                    if viewport['width']==390:
                        await page.screenshot(path='/app/test_reports/screenshots_iter71_home/automation_output/20261103_101518_905421a4ff22/mobile.jpeg', type="jpeg", quality=40, full_page=False)
                    else:
                        await page.screenshot(path='/app/test_reports/screenshots_iter71_home/automation_output/20261103_101518_905421a4ff22/desktop.jpeg', type="jpeg", quality=40, full_page=False)
                await page.get_by_test_id('header-control-1').click(force=True)
                await page.wait_for_timeout(700)
                assert await page.locator('#sideMenu').evaluate('(e)=>e.classList.contains("open")')
                await page.get_by_test_id('menu-control-1').click(force=True)
                await page.wait_for_timeout(700)
                await page.mouse.wheel(0,-2000)
                await page.wait_for_timeout(1100)
                restored=await page.evaluate(state)
                assert restored['scrollY']==0 and abs(restored['contentTop']-initial['contentTop'])<2,restored
                if mode!='reduce':
                    assert not restored['paused'] and restored['time']>middle['time'],restored
                print('PASS',name,json.dumps({'initial':initial,'middle':middle,'restored':restored}))
            except Exception as e:
                print('FAIL',name,str(e))
    error_text=await page.evaluate('''() => {const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));return errorElements.map(el => el.textContent).join(", ");}''')
    print(f'Found error message: {error_text}' if error_text else 'No error messages found on the page')
    print('PAGE ERRORS',errors,'FAILED MEDIA',failures)
