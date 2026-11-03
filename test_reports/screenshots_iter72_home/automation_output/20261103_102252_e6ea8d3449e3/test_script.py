async def run_test(page, output_dir, page_url):
    import importlib.util
    spec = importlib.util.spec_from_file_location('home_regression','/app/tests/playwright_iter72_home.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    await module.run(page)
