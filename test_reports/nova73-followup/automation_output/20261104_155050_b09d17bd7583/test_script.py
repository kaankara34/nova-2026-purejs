async def run_test(page, output_dir, page_url):
    import sys
    sys.path.insert(0,'/app/tests')
    from playwright_iter73_followup import run
    try:
        await run(page)
    except Exception as e:
        print('FAIL followup runner',str(e))
