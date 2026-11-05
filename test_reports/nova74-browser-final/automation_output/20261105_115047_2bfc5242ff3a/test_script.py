async def run_test(page, output_dir, page_url):
    import importlib.util
    spec = importlib.util.spec_from_file_location('iter74', '/app/tests/playwright_iter74_static.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        await module.run(page)
    except Exception as e:
        print('FAIL test execution', str(e))
