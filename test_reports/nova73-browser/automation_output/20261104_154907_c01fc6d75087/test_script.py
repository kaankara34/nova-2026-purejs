async def run_test(page, output_dir, page_url):
    import sys
    sys.path.insert(0,'/app/tests')
    from playwright_iter73_nova import run
    try:
        await run(page)
    except Exception as e:
        print('FAIL test runner',str(e))
