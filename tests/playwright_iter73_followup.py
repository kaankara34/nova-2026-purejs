# Mobile visible-content clearance and desktop project-page isolation.
from urllib.parse import urlsplit

async def run(page):
    base='{0.scheme}://{0.netloc}'.format(urlsplit(page.url))
    for lang in ['tr','en']:
        await page.set_viewport_size({'width':390,'height':844})
        await page.goto(f'{base}/{lang}/index.html',wait_until='domcontentloaded')
        await page.evaluate("localStorage.setItem('nova_cookie_notice_dismissed','1')")
        await page.reload(wait_until='domcontentloaded')
        for testid in ['nova-foundations-portfolio-link','nova-foundation-current-projects','nova-foundation-completed-projects','nova-foundation-disciplines']:
            try:
                target=page.get_by_test_id(testid)
                await target.evaluate("e=>window.scrollTo({top:e.getBoundingClientRect().top+scrollY-innerHeight/2+e.getBoundingClientRect().height/2,behavior:'instant'})")
                await page.wait_for_timeout(400)
                state=await target.evaluate("""e=>{const r=e.getBoundingClientRect(),h=document.querySelector('#siteHeader').getBoundingClientRect(),b=document.querySelector('#mobileBottomBar').getBoundingClientRect(),hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return {top:r.top,bottom:r.bottom,headerBottom:h.bottom,barTop:b.top,clear:e.contains(hit),overflow:document.documentElement.scrollWidth-innerWidth};}""")
                assert state['top']>state['headerBottom'] and state['bottom']<state['barTop'] and state['clear'] and state['overflow']==0,state
                print('PASS mobile clearance',lang,testid,state)
                if testid=='nova-foundation-disciplines':
                    await page.screenshot(path=f'/app/test_reports/nova73-{lang}-mobile-metrics.jpeg',quality=40,full_page=False)
            except Exception as e:
                print('FAIL mobile clearance',lang,testid,str(e))
        await page.set_viewport_size({'width':1920,'height':1080})
        for filename in ['the-residences-east-west.html','the-apartments-tac.html','the-apartments-ana.html']:
            try:
                await page.goto(f'{base}/{lang}/{filename}',wait_until='domcontentloaded')
                assert await page.get_by_test_id('nova-foundations-section').count()==0
                assert await page.locator('.home-hero-scrollover,.home-scrollover-content').count()==0
                state=await page.locator('.ew-hero,.tac-hero,.ana-hero').evaluate_all('(es)=>es.map(e=>getComputedStyle(e).position)')
                assert state and all(x=='relative' for x in state),state
                print('PASS desktop project isolation',lang,filename,state)
            except Exception as e:
                print('FAIL desktop project isolation',lang,filename,str(e))