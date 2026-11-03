async def run_test(page, output_dir, page_url):
    base=page.url.split('/tr/')[0]
    errors=[]
    failed=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('response',lambda r:failed.append([r.status,r.url]) if '/media/' in r.url and r.status>=400 else None)
    await page.set_viewport_size({'width':1920,'height':1080})
    for lang,filename in [('tr','projeler.html'),('en','projects.html')]:
        try:
            await page.goto(f'{base}/{lang}/{filename}',wait_until='domcontentloaded')
            image=page.get_by_test_id('pj-card-bahar-residence').locator('img')
            await image.scroll_into_view_if_needed()
            await page.wait_for_function('''() => {const i=document.querySelector('[data-testid="pj-card-bahar-residence"] img');return i.complete && i.naturalWidth>0;}''')
            data=await image.evaluate('(i)=>({src:i.currentSrc,width:i.naturalWidth,complete:i.complete})')
            assert data['src'].endswith('/media/images/bahar-cover.jpg'),data
            assert await page.locator('.pj-hero').evaluate('(h)=>getComputedStyle(h).position')!='sticky'
            print('PASS Bahar',lang,data)
        except Exception as e:
            print('FAIL Bahar',lang,str(e))
    for lang in ['tr','en']:
        try:
            await page.goto(f'{base}/{lang}/the-residences-east-west.html',wait_until='domcontentloaded')
            await page.get_by_test_id('ew-tower-east').scroll_into_view_if_needed()
            await page.wait_for_timeout(1800)
            first=await page.locator('#ewPlansTrack > .ew-plans-slide:not([data-clone])').first.locator('img').evaluate('(i)=>({src:i.currentSrc,width:i.naturalWidth,complete:i.complete})')
            assert first['complete'] and first['width']>0 and first['src'].endswith('east-3plus1.webp'),first
            print('PASS initial plan',lang,first)
            assert await page.locator('.ew-hero').evaluate('(h)=>getComputedStyle(h).position')!='sticky'
            for tower in ['east','west']:
                await page.get_by_test_id(f'ew-tower-{tower}').click(force=True)
                await page.wait_for_timeout(500)
                for idx,suffix in enumerate(['3plus1','4plus1','duplex-lower','duplex-upper']):
                    try:
                        await page.get_by_test_id(f'ew-plan-tab-{idx}').click(force=True)
                        await page.wait_for_timeout(650)
                        image=page.locator('#ewPlansTrack > .ew-plans-slide:not([data-clone])').nth(idx).locator('img')
                        await page.wait_for_function('''idx=>{const i=document.querySelectorAll('#ewPlansTrack > .ew-plans-slide:not([data-clone]) img')[idx];return i.complete && i.naturalWidth>0;}''',arg=idx)
                        data=await image.evaluate('''i=>{const r=i.getBoundingClientRect(),v=document.querySelector('#ewPlansViewport').getBoundingClientRect();return {src:i.currentSrc,width:i.naturalWidth,visible:r.left<v.right && r.right>v.left};}''')
                        assert data['src'].endswith(f'/media/images/ew/plans/{tower}-{suffix}.webp') and data['visible'],data
                        assert 'active' in (await page.get_by_test_id(f'ew-plan-tab-{idx}').get_attribute('class'))
                        print('PASS plan',lang,tower,idx,data)
                    except Exception as e:
                        print('FAIL plan',lang,tower,idx,str(e))
            await page.evaluate('window.dispatchEvent(new PageTransitionEvent("pageshow",{persisted:true}))')
            await page.wait_for_timeout(650)
            last=await page.locator('#ewPlansTrack > .ew-plans-slide:not([data-clone])').nth(3).locator('img').evaluate('''i=>{const r=i.getBoundingClientRect(),v=document.querySelector('#ewPlansViewport').getBoundingClientRect();return {src:i.currentSrc,width:i.naturalWidth,visible:r.left<v.right && r.right>v.left};}''')
            assert last['visible'] and last['width']>0 and last['src'].endswith('west-duplex-upper.webp'),last
            print('PASS pageshow refresh',lang,last)
            await page.get_by_test_id('header-control-1').click(force=True)
            await page.wait_for_timeout(700)
            assert await page.locator('#sideMenu').evaluate('(e)=>e.classList.contains("open")')
            await page.get_by_test_id('menu-control-1').click(force=True)
            print('PASS non-home header',lang)
        except Exception as e:
            print('FAIL East West',lang,str(e))
    error_text=await page.evaluate('''() => {const errorElements = Array.from(document.querySelectorAll('.error, [class*="error"], [id*="error"]'));return errorElements.map(el => el.textContent).join(", ");}''')
    print(f'Found error message: {error_text}' if error_text else 'No error messages found on the page')
    print('PAGE ERRORS',errors,'FAILED MEDIA',failed)
    await page.screenshot(path='/app/test_reports/screenshots_iter71_projects/automation_output/20261103_101638_5d8be35714e8/plans.jpeg', type="jpeg", quality=40, full_page=False)
