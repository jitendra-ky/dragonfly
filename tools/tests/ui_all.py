from common import setup_module, teardown_module
from ui_signin import test_signin, test_signin_with_google
from ui_signup import test_signup

driver = setup_module()

test_signin(driver)
test_signup(driver)
test_signin_with_google(driver)

teardown_module(driver)
