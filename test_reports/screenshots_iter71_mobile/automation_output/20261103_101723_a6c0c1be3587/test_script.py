async def run_test(page, output_dir, page_url):
    base=page.url.split('/tr/')[0]
    for lang in ['tr','en']:
        try:
            await page.set_viewport_size({'width':390,'height':800})
            await page.emulate_media(reduced_motion='no-preference')
            await page.goto(f'{base}/{lang}/index.html',wait_until='domcontentloaded')
            await page.wait_for_timeout(1800)
            cookie=page.get_by_role('button',name='ANLADIM' if lang=='tr' else 'GOT IT',exact=True)
            if await cookie.is_visible():
                await cookie.click(force=True)
                await page.wait_for_timeout(450)
            initial=await page.get_by_test_id('intro-video-hero').bounding_box()
            await page.mouse.wheel(0,570)
            await page.wait_for_timeout(1000)
            data=await page.evaluate('''()=>{const h=document.querySelector('[data-testid="intro-video-hero"]'),c=document.querySelector('.home-scrollover-content'),b=document.querySelector('[data-testid="bottom-control-1"]'),r=b.getBoundingClientRect();return {heroTop:h.getBoundingClientRect().top,contentTop:c.getBoundingClientRect().top,overflow:document.documentElement.scrollWidth>innerWidth,bottomHit:b.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height/2)),headerBottom:document.querySelector('#siteHeader').getBoundingClientRect().bottom,bottomTop:document.querySelector('#mobileBottomBar').getBoundingClientRect().top};}''')
            assert abs(data['heroTop'])<2 and abs(data['contentTop']-(initial['height']-570))<2 and not data['overflow'] and data['bottomHit'] and data['headerBottom']<data['bottomTop'],data
            print('PASS mobile 390x800 transition and bottom-bar hit test',lang,data)
            await page.mouse.wheel(0,250)
            await page.wait_for_timeout(800)
            cover=await page.evaluate('''()=>{const c=document.querySelector('.home-scrollover-content'),hit=document.elementFromPoint(innerWidth/2,innerHeight/2);return {contentTop:c.getBoundingClientRect().top,coverHit:c.contains(hit),videoPaused:document.querySelector('[data-testid="intro-video"]').paused};}''')
            assert cover['contentTop']<0 and cover['coverHit'],cover
            print('PASS full opaque content cover',lang,cover)
            await page.get_by_test_id('bottom-control-1').click(force=True)
            await page.wait_for_timeout(2200)
            register=await page.locator('#register').bounding_box()
            assert register['y']<250 and register['y']+register['height']>0,register
            print('PASS bottom-bar navigation',lang,register)
            await page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
            await page.wait_for_timeout(1000)
            assert await page.get_by_test_id('intro-video').evaluate('(v)=>!v.paused')
            print('PASS video after deep reverse',lang)
            await page.emulate_media(reduced_motion='reduce')
            await page.wait_for_timeout(300)
            assert await page.get_by_test_id('intro-video-hero').evaluate('(h)=>getComputedStyle(h).position')=='relative'
            await page.mouse.wheel(0,400)
            await page.wait_for_timeout(700)
            top=await page.get_by_test_id('intro-video-hero').evaluate('(h)=>h.getBoundingClientRect().top')
            assert top< -300,top
            print('PASS mobile reduced-motion natural flow',lang,top)
        except Exception as e:
            print('FAIL supplemental mobile',lang,str(e))
    error_text=await page.evaluate('''() => {const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));return errorElements.map(el => el.textContent).join(", ");}''')
    print(f'Found error message: {error_text}' if error_text else 'No error messages found on the page')
    await page.set_viewport_size({'width':390,'height':844})
