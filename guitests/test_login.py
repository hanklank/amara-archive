from utils.factories import *

from .pages.login import LoginPage

def check_user_logged_in(driver, correct_user):
    user_menu = driver.find_element_by_id('user-menu')
    assert user_menu.get_attribute('data-username') == correct_user.username

def test_login(driver, base_url):
    user = UserFactory(username='test_login_user', password='password')
    page = LoginPage(driver, base_url)
    page.username_field().send_keys("test_login_user")
    page.password_field().send_keys("password")
    page.signin_button().click()
    check_user_logged_in(driver, user)
