async def run_test(page, output_dir, page_url):
    base=page.url.split('/tr/')[0]
    for lang in ['tr','en']:
        try:
            await page.set_viewport_size({'width':390,'height':800})
            await page.emulate_media(reduced_motion='no-preference')
            await page.goto(f'{base}/{lang}/index.html',wait_until='domcontentloaded')
            await page.wait_for_timeout(2000)
            if await page.locator('#cookieBanner.show').count():
                await page.get_by_role('button',name='ANLADIM' if lang=='tr' else 'GOT IT',exact=True).click(force=True)
                await page.wait_for_timeout(450)
            await page.get_by_test_id('hero-scroll-button').click(force=True)
            await page.wait_for_timeout(1200)
            y=await page.evaluate('scrollY')
            print('HERO ARROW',lang,'PASS' if y>100 else 'FAIL',{'scrollY':y,'targetExists':await page.locator('#liveAllIn').count()})
            await page.mouse.wheel(0,570)
            await page.wait_for_timeout(1000)
            middle=await page.evaluate('''()=>({heroTop:document.querySelector('[data-testid="intro-video-hero"]').getBoundingClientRect().top,contentTop:document.querySelector('.home-scrollover-content').getBoundingClientRect().top,overflow:document.documentElement.scrollWidth>innerWidth})''')
            assert middle['heroTop']==0 and not middle['overflow'],middle
            print('PASS 390x800 transition',lang,middle)
            await page.get_by_test_id('bottom-control-1').click(force=True)
            await page.wait_for_timeout(5500)
            position=await page.evaluate('''()=>({scrollY,targetTop:document.querySelector('#register').getBoundingClientRect().top,scrollHeight:document.documentElement.scrollHeight})''')
            print('BOTTOM CTA',lang,'PASS' if position['targetTop']<250 else 'FAIL',position)
            await page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
            await page.wait_for_timeout(1000)
            assert await page.get_by_test_id('intro-video').evaluate('(v)=>!v.paused')
            print('PASS deep reverse video',lang)
            await page.emulate_media(reduced_motion='reduce')
            await page.mouse.wheel(0,400)
            await page.wait_for_timeout(900)
            pos=await page.get_by_test_id('intro-video-hero').evaluate('(h)=>({position:getComputedStyle(h).position,top:h.getBoundingClientRect().top})')
            assert pos['position']=='relative' and pos['top']< -300,pos
            print('PASS mobile reduced motion',lang,pos)
        except Exception as e:
            print('FAIL followup',lang,str(e))
    error_text=await page.evaluate('''() => {const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));return errorElements.map(el => el.textContent).join(", ");}''')
    print(f'Found error message: {error_text}' if error_text else 'No error messages found on the page')
    await page.set_viewport_size({'width':390,'height':844})
