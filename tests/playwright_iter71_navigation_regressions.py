"""Reproduce unresolved hero-arrow, transparent-header and first contact-jump regressions."""
import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright


async def run(page, base):
    for lang in ['tr', 'en']:
        await page.set_viewport_size({'width':390,'height':844})
        await page.goto(f'{base}/{lang}/index.html',wait_until='domcontentloaded')
        await page.wait_for_timeout(2000)
        if await page.locator('#cookieBanner.show').count():
            await page.get_by_role('button',name='ANLADIM' if lang=='tr' else 'GOT IT',exact=True).click(force=True)
            await page.wait_for_timeout(600)
        try:
            await page.get_by_test_id('hero-scroll-button').click(force=True)
            await page.wait_for_timeout(1200)
            assert await page.evaluate('scrollY')>100,'Hero arrow does not scroll; #liveAllIn target missing'
            print('PASS hero arrow',lang)
        except Exception as e:
            print('FAIL hero arrow',lang,str(e))
        try:
            await page.get_by_test_id('bottom-control-1').click(force=True)
            await page.wait_for_timeout(5500)
            data=await page.evaluate('''()=>({y:scrollY,targetTop:document.querySelector('#register').getBoundingClientRect().top})''')
            assert data['targetTop']<250,data
            print('PASS first contact jump',lang,data)
        except Exception as e:
            print('FAIL first contact jump',lang,str(e))
        try:
            await page.evaluate('window.scrollTo({top:1100,behavior:"instant"})')
            await page.wait_for_timeout(500)
            data=await page.locator('#siteHeader').evaluate('''h=>({background:getComputedStyle(h).backgroundColor,transparent:h.classList.contains('transparent'),contentTop:document.querySelector('.home-scrollover-content').getBoundingClientRect().top})''')
            assert data['background']!='rgba(0, 0, 0, 0)',data
            print('PASS solid header over content',lang,data)
        except Exception as e:
            print('FAIL solid header over content',lang,str(e))


async def main():
    load_dotenv('/app/frontend/.env')
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True)
        await run(await browser.new_page(),os.environ['REACT_APP_BACKEND_URL'].rstrip('/'))
        await browser.close()

if __name__=='__main__':
    asyncio.run(main())