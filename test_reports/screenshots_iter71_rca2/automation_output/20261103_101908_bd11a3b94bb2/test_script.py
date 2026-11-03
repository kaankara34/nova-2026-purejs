async def run_test(page, output_dir, page_url):
    try:
        await page.set_viewport_size({'width':390,'height':844})
        await page.wait_for_timeout(2000)
        if await page.locator('#cookieBanner.show').count():
            await page.get_by_role('button',name='ANLADIM',exact=True).click(force=True)
            await page.wait_for_timeout(600)
        details='''()=>{const t=document.querySelector('#register');return {y:scrollY,top:t.getBoundingClientRect().top,absoluteTop:t.getBoundingClientRect().top+scrollY,htmlHeight:document.documentElement.scrollHeight,ancestors:[t.parentElement,t.parentElement.parentElement].map(a=>({class:a.className,top:a.getBoundingClientRect().top,height:a.getBoundingClientRect().height,scrollTop:a.scrollTop,overflow:getComputedStyle(a).overflowY}))}}'''
        print('BEFORE',await page.evaluate(details))
        await page.get_by_test_id('bottom-control-1').click(force=True)
        await page.wait_for_timeout(4500)
        print('FIRST CLICK',await page.evaluate(details))
        await page.get_by_test_id('bottom-control-1').click(force=True)
        await page.wait_for_timeout(2500)
        print('SECOND CLICK',await page.evaluate(details))
        await page.evaluate('window.scrollTo({top:0,behavior:"instant"})')
        await page.wait_for_timeout(400)
        await page.get_by_test_id('bottom-control-1').click(force=True)
        await page.wait_for_timeout(4500)
        print('WARM TOP CLICK',await page.evaluate(details))
        await page.set_viewport_size({'width':1920,'height':1080})
        await page.goto(page.url,wait_until='domcontentloaded')
        await page.wait_for_timeout(2000)
        await page.get_by_test_id('header-control-3').click(force=True)
        await page.wait_for_timeout(4500)
        print('DESKTOP REGISTER CLICK',await page.evaluate(details))
        print('PASS RCA probe complete')
    except Exception as e:
        print('FAIL RCA probe',str(e))
