# TR/EN homepage notch, foundations, navigation and non-home isolation on public preview.
import json
from pathlib import Path
from urllib.parse import urlsplit

async def run(page):
    base = '{0.scheme}://{0.netloc}'.format(urlsplit(page.url))
    results = []
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
    async def check(name, action):
        try:
            detail = await action()
            results.append({'name': name, 'passed': True, 'detail': detail})
            print('PASS', name, json.dumps(detail))
        except Exception as error:
            results.append({'name': name, 'passed': False, 'error': str(error)})
            print('FAIL', name, str(error))
    async def origin():
        await page.evaluate("window.scrollTo({top:0,behavior:'instant'})")
        await page.wait_for_timeout(400)
    async def video_progress():
        await page.wait_for_function("document.querySelector('[data-testid=\"intro-video\"]').readyState >= 3", timeout=15000)
        first = await page.get_by_test_id('intro-video').evaluate('(v)=>({time:v.currentTime,paused:v.paused,error:v.error?.code,source:v.currentSrc})')
        await page.wait_for_timeout(700)
        second = await page.get_by_test_id('intro-video').evaluate('(v)=>({time:v.currentTime,paused:v.paused,error:v.error?.code})')
        assert not second['paused'] and not second['error'] and second['time'] != first['time'], (first,second)
        return {'first':first,'second':second}
    for width,height in [(1920,1080),(390,844)]:
        await page.set_viewport_size({'width':width,'height':height})
        for lang in ['tr','en']:
            label = f'{lang}-{width}'
            await page.emulate_media(reduced_motion='no-preference')
            await page.goto(f'{base}/{lang}/index.html',wait_until='domcontentloaded')
            await page.evaluate("localStorage.setItem('nova_cookie_notice_dismissed','1')")
            await page.reload(wait_until='domcontentloaded')
            await page.get_by_test_id('intro-video-hero').wait_for(state='visible')
            await page.wait_for_timeout(900)
            async def register():
                await page.get_by_test_id('header-control-3' if width==1920 else 'bottom-control-1').click(force=True)
                await page.wait_for_function("Math.abs(document.querySelector('#register').getBoundingClientRect().top)<2",timeout=20000)
                await page.wait_for_timeout(1000)
                rect = await page.locator('#register').bounding_box()
                assert abs(rect['y'])<2, rect
                return rect
            await check(label+' first register CTA',register)
            await origin()
            await check(label+' video initial',video_progress)
            initial = await page.evaluate("({hero:document.querySelector('.hero').getBoundingClientRect().top,content:document.querySelector('.home-scrollover-content').getBoundingClientRect().top})")
            async def boundary():
                hero_height = await page.get_by_test_id('intro-video-hero').evaluate('(e)=>e.getBoundingClientRect().height')
                await page.mouse.move(width//2,height//2)
                await page.mouse.wheel(0,hero_height-100)
                await page.wait_for_timeout(700)
                state = await page.evaluate("""() => {const h=document.querySelector('.hero'),c=document.querySelector('.home-scrollover-content');return {heroTop:h.getBoundingClientRect().top,contentTop:c.getBoundingClientRect().top,heroPosition:getComputedStyle(h).position,clip:getComputedStyle(c).clipPath,notchWidth:getComputedStyle(c).getPropertyValue('--scrollover-notch-width').trim(),notchHeight:getComputedStyle(c).getPropertyValue('--scrollover-notch-height').trim(),overflow:document.documentElement.scrollWidth-innerWidth};}""")
                assert state['heroTop']==0 and 95<state['contentTop']<105, state
                assert state['heroPosition']=='sticky' and state['overflow']==0, state
                nw,nh = ('20px','18px') if width==1920 else ('15px','14px')
                assert state['notchWidth']==nw and state['notchHeight']==nh and f'50% {nh}' in state['clip'] and nw in state['clip'],state
                await page.screenshot(path=f'/app/test_reports/nova73-{label}-boundary.jpeg',quality=40,full_page=False)
                return state
            await check(label+' native sticky notch boundary',boundary)
            await check(label+' video during boundary',video_progress)
            async def header():
                await page.mouse.wheel(0,140)
                await page.wait_for_timeout(600)
                state = await page.locator('#siteHeader').evaluate('(e)=>({transparent:e.classList.contains("transparent"),background:getComputedStyle(e).backgroundColor,color:getComputedStyle(e).color})')
                assert not state['transparent'] and state['background']=='rgba(11, 11, 11, 0.94)' and state['color']=='rgb(255, 255, 255)',state
                return state
            await check(label+' dark header over white content',header)
            async def reverse():
                await page.mouse.wheel(0,-3000)
                await page.wait_for_timeout(700)
                state = await page.evaluate("({y:scrollY,hero:document.querySelector('.hero').getBoundingClientRect().top,content:document.querySelector('.home-scrollover-content').getBoundingClientRect().top})")
                assert state['y']==0 and state['hero']==initial['hero'] and abs(state['content']-initial['content'])<1,state
                return state
            await check(label+' native reverse origin',reverse)
            await check(label+' video after reverse',video_progress)
            async def arrow():
                await page.get_by_test_id('hero-scroll-button').click(force=True)
                await page.wait_for_function("Math.abs(document.querySelector('#buildBeyondLiving').getBoundingClientRect().top)<2",timeout=10000)
                return await page.locator('#buildBeyondLiving').bounding_box()
            await check(label+' arrow navigation',arrow)
            async def foundations():
                section=page.get_by_test_id('nova-foundations-section')
                await section.scroll_into_view_if_needed()
                await page.wait_for_timeout(400)
                state=await section.evaluate("""e=>({previous:e.previousElementSibling.id,next:e.nextElementSibling.className,values:[...e.querySelectorAll('.nova-foundation-value')].map(x=>x.textContent.trim()),overflow:document.documentElement.scrollWidth-innerWidth,rect:e.getBoundingClientRect().toJSON()})""")
                assert state['previous']=='projects' and state['next']=='section-architects' and state['values']==['3','10','3'] and state['overflow']==0,state
                expected='NOVA YAKLAŞIMI' if lang=='tr' else 'THE NOVA APPROACH'
                assert await page.get_by_test_id('nova-foundations-kicker').inner_text()==expected
                assert len(await page.get_by_test_id('nova-foundations-title').inner_text())>30
                assert len(await page.get_by_test_id('nova-foundations-copy').inner_text())>100
                for testid in ['nova-foundation-current-projects','nova-foundation-completed-projects','nova-foundation-disciplines','nova-foundations-note']:
                    assert await page.get_by_test_id(testid).is_visible()
                await page.evaluate("window.scrollTo({top:document.querySelector('[data-testid=\"nova-foundations-section\"]').getBoundingClientRect().top+scrollY-125,behavior:'instant'})")
                await page.wait_for_timeout(200)
                await page.screenshot(path=f'/app/test_reports/nova73-{label}-section.jpeg',quality=40,full_page=False)
                return state
            await check(label+' localized section and metrics',foundations)
            async def portfolio():
                link=page.get_by_test_id('nova-foundations-portfolio-link')
                expected=f'{base}/{lang}/'+('projeler.html' if lang=='tr' else 'projects.html')
                assert await link.evaluate('(e)=>e.href')==expected
                await link.click(force=True)
                await page.wait_for_url(expected)
                assert await page.get_by_test_id('nova-foundations-section').count()==0
                assert await page.locator('.home-hero-scrollover,.home-scrollover-content').count()==0
                hero=page.locator('.pj-hero')
                assert await hero.count()==1
                assert await hero.evaluate('(e)=>getComputedStyle(e).position')!='sticky'
                return {'url':page.url,'title':await page.title()}
            await check(label+' portfolio CTA and page isolation',portfolio)
            async def reduced():
                await page.emulate_media(reduced_motion='reduce')
                await page.goto(f'{base}/{lang}/index.html',wait_until='domcontentloaded')
                await page.wait_for_timeout(600)
                assert await page.get_by_test_id('intro-video-hero').evaluate('(e)=>getComputedStyle(e).position')=='relative'
                await page.mouse.wheel(0,300)
                await page.wait_for_timeout(500)
                state=await page.get_by_test_id('intro-video-hero').evaluate('(e)=>({top:e.getBoundingClientRect().top,position:getComputedStyle(e).position})')
                assert state['top']<0,state
                return state
            await check(label+' reduced motion natural flow',reduced)
            error_text=await page.evaluate("""() => {const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));return errorElements.map(el => el.textContent).join(', ');}""")
            print(f'Found error message: {error_text}' if error_text else 'No error messages found on the page')
    await page.emulate_media(reduced_motion='no-preference')
    for lang in ['tr','en']:
        for filename in ['the-residences-east-west.html','the-apartments-tac.html','the-apartments-ana.html']:
            async def project():
                await page.goto(f'{base}/{lang}/{filename}',wait_until='domcontentloaded')
                assert await page.get_by_test_id('nova-foundations-section').count()==0
                assert await page.locator('.home-hero-scrollover,.home-scrollover-content').count()==0
                heroes=await page.locator('.hero,.ew-hero,.tac-hero,.ana-hero').evaluate_all('(es)=>es.map(e=>({class:e.className,position:getComputedStyle(e).position}))')
                assert heroes and all(e['position']!='sticky' for e in heroes),heroes
                return heroes
            await check(lang+' project isolation '+filename,project)
    print('CONSOLE/PAGE ERRORS',json.dumps(errors))
    Path('/app/test_reports/iter73_browser_results.json').write_text(json.dumps({'checks':results,'errors':errors},indent=2))
    print('TOTAL',sum(x['passed'] for x in results),'/',len(results))