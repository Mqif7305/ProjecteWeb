from splinter.browser import Browser

def before_all(context):
    context.browser = Browser('firefox', headless=True)
    # Alternatively, use `firefox` and headless=False to see the browser while testing

def after_all(context):
    context.browser.quit()
    context.browser = None