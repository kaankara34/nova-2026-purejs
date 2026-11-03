async def run_test(page, output_dir, page_url):
    base=page.url.split('/tr/')[0]
    for lang in ['tr','en']:
        try:
            await page.set_viewport_size({'width':1920,'height':1080})
            await page.goto(f'{base}/{lang}/index.html',wait_until='domcontentloaded')
            await page.wait_for_timeout(1800)
            await page.evaluate('window.scrollTo({top:1100,behavior:"instant"})')
            await page.wait_for_timeout(600)
            data=await page.locator('#siteHeader').evaluate('''h=>{const b=h.querySelector('[data-testid="header-control-1"]');return {headerBackground:getComputedStyle(h).backgroundColor,transparent:h.classList.contains('transparent'),menuColor:getComputedStyle(b.querySelector('span')).backgroundColor,contentTop:document.querySelector('.home-scrollover-content').getBoundingClientRect().top,contentBackground:getComputedStyle(document.querySelector('.home-scrollover-content')).backgroundColor,heroBottom:document.querySelector('.hero').getBoundingClientRect().bottom};}''')
            assert data['contentTop']<0,data
            print('HEADER COVER PROBE',lang,data)
            if data['transparent'] and data['headerBackground']=='rgba(0, 0, 0, 0)' and data['menuColor']=='rgb(255, 255, 255)':
                print('FAIL header contrast over white content',lang)
            else:
                print('PASS header contrast',lang)
        except Exception as e:
            print('FAIL header probe',lang,str(e))
