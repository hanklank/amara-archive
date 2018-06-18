from utils.factories import *

from .pages.login import LoginPage

def check_user_logged_in(driver, correct_user):
    user_menu = driver.get_element_by_id('user-menu')
    assert user.get_attribute('data-username') == correct_user.username

def test_login(driver, base_url, admin_user):
    print 'in test login'
    page = LoginPage(driver, base_url)
    page.username_field().send_keys("admin")
    page.password_field().send_keys("password")
    page.signin_button().click()
