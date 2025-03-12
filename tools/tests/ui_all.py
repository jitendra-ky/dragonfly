import time

from common import setup_module, teardown_module
from ui_signin import test_signin, test_signin_with_google
from ui_signup import test_signup

t1 = time.time()
driver = setup_module()
t2 = time.time()
print(f"Setup time: {t2 - t1:.2f}s")
try:
    test_signin(driver)
    test_signup(driver)
    test_signin_with_google(driver)
except Exception as e:
    driver.save_screenshot(f"debug_screenshot_{time.time()}.png")
    raise AssertionError(e) from e
teardown_module(driver)
