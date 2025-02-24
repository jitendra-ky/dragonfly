import time

from common import setup_module, teardown_module
from ui_signin import test_signin, test_signin_with_google
from ui_signup import test_signup

t1 = time.time()
driver = setup_module()
t2 = time.time()
print(f"Setup time: {t2 - t1:.2f}s")

test_signin(driver)
test_signup(driver)
test_signin_with_google(driver)

teardown_module(driver)
