from behave import *

use_step_matcher("parse")

@given('Exists a user "{username}" with password "{password}"')
def step_impl(context, username, password):
    from django.contrib.auth.models import User
    User.objects.create_user(username=username, email='user@example.com', password=password)

@given('I login as user "{username}" with password "{password}"')
def step_impl(context, username, password):
    context.browser.visit(context.get_url('/accounts/login/?next=/myrestaurants/'))
    form = context.browser.find_by_id('login-form')
    context.browser.fill('username', username)
    context.browser.fill('password', password)
    form.find_by_value('login').first.click()
    assert context.browser.is_text_present('User: ' + username)

@then("I'm redirected to the login form")
def step_impl(context):
    wait = WebDriverWait(context.browser.driver, 3)
    login_form = wait.until(
        visibility_of_element_located((By.ID, "login-form"))
    )
    # context.browser.driver.save_screenshot("debug_redirect.png")
    assert context.browser.url.startswith(context.get_url('login'))