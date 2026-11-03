"""Homepage sticky layering, reverse scroll, video continuity and reduced-motion regression."""
import asyncio
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from playwright.async_api import async_playwright

STATE = """() => {
 const h=document.querySelector('[data-testid="intro-video-hero"]'), c=document.querySelector('.home-scrollover-content'), v=document.querySelector('[data-testid="intro-video"]');
 const hb=h.getBoundingClientRect(), cb=c.getBoundingClientRect();
 return {position:getComputedStyle(h).position,heroTop:hb.top,height:hb.height,contentTop:cb.top,background:getComputedStyle(c).backgroundColor,
 scrollY,overflow:document.documentElement.scrollWidth>innerWidth,paused:v.paused,time:v.currentTime,ready:v.readyState,
 headerBottom:document.querySelector('#siteHeader').getBoundingClientRect().bottom,bottomTop:document.querySelector('#mobileBottomBar').getBoundingClientRect().top};
}"""


async def run(page, base):
    errors, media_failures, results = [], [], []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('response', lambda r: media_failures.append([r.status, r.url]) if '/media/' in r.url and r.status >= 400 else None)
    for viewport, mode in [({'width':1920,'height':1080},'no-preference'), ({'width':390,'height':844},'no-preference'), ({'width':1920,'height':1080},'reduce')]:
        await page.set_viewport_size(viewport)
        await page.emulate_media(reduced_motion=mode)
        for lang in ['tr','en']:
            name=f'{lang}-{viewport["width"]}-{mode}'
            try:
                await page.goto(f'{base}/{lang}/index.html', wait_until='domcontentloaded')
                await page.get_by_test_id('intro-video-hero').wait_for(state='visible')
                await page.wait_for_timeout(2800)
                initial=await page.evaluate(STATE)
                assert initial['position']==('relative' if mode=='reduce' else 'sticky'), initial
                assert not initial['overflow'], initial
                await page.mouse.wheel(0, round(initial['height']*.6))
                await page.wait_for_timeout(1200)
                middle=await page.evaluate(STATE)
                assert abs(middle['contentTop']-(initial['contentTop']-middle['scrollY']))<2, middle
                assert middle['background']=='rgb(255, 255, 255)' and not middle['overflow'], middle
                assert abs(middle['heroTop']-(-middle['scrollY'] if mode=='reduce' else 0))<2, middle
                if mode!='reduce':
                    assert not initial['paused'] and not middle['paused'] and middle['time']>initial['time'], [initial,middle]
                if viewport['width']==390:
                    assert middle['headerBottom']<middle['bottomTop'], middle
                clickable=await page.get_by_test_id('header-control-1').evaluate('(b)=>{const r=b.getBoundingClientRect();return b.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height/2));}')
                assert clickable, 'Header menu obstructed'
                if lang=='tr' and mode!='reduce':
                    await page.screenshot(path=f'/app/test_reports/screenshots_iter71_home/scroll_{viewport["width"]}.jpeg',quality=40,full_page=False)
                await page.get_by_test_id('header-control-1').click(force=True)
                await page.wait_for_timeout(700)
                assert await page.locator('#sideMenu').evaluate('(e)=>e.classList.contains("open")')
                await page.get_by_test_id('menu-control-1').click(force=True)
                await page.wait_for_timeout(700)
                await page.mouse.wheel(0,-2000)
                await page.wait_for_timeout(1100)
                restored=await page.evaluate(STATE)
                assert restored['scrollY']==0 and abs(restored['contentTop']-initial['contentTop'])<2, restored
                if mode!='reduce':
                    assert not restored['paused'] and restored['time']>middle['time'], restored
                results.append({'case':name,'pass':True,'initial':initial,'middle':middle,'restored':restored})
                print('PASS',name,json.dumps(results[-1]))
            except Exception as e:
                results.append({'case':name,'pass':False,'error':str(e)})
                print('FAIL',name,str(e))
    error_text=await page.evaluate("""() => {const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));return errorElements.map(el => el.textContent).join(", ");}""")
    print(f'Found error message: {error_text}' if error_text else 'No error messages found on the page')
    print('PAGE ERRORS',errors,'FAILED MEDIA',media_failures)
    return {'results':results,'page_errors':errors,'failed_media':media_failures}


async def main():
    load_dotenv('/app/frontend/.env')
    Path('/app/test_reports/screenshots_iter71_home').mkdir(parents=True,exist_ok=True)
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True)
        page=await browser.new_page()
        result=await run(page,os.environ['REACT_APP_BACKEND_URL'].rstrip('/'))
        Path('/app/test_reports/iter71_home_results.json').write_text(json.dumps(result,indent=2))
        await browser.close()

if __name__=='__main__':
    asyncio.run(main())