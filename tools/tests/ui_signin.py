import time

from common import setup_module, teardown_module
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


def test_signin(driver: webdriver.Firefox):
    start_time = time.time()

    signin_url = "http://localhost:8000/signin/"
    home_url = "http://localhost:8000/"

    driver.get(signin_url)
    time.sleep(1)

    # Clear localStorage to ensure clean state
    driver.execute_script("localStorage.clear();")

    # check the login page with valid credentials
    username = driver.find_element(By.ID, "email")
    password = driver.find_element(By.ID, "password")
    submit = driver.find_element(By.CSS_SELECTOR, "#signin-form .submit-btn")

    username.send_keys("active_user@jitendra.me")
    password.send_keys("rootroot")
    submit.click()

    # Wait for AJAX call to complete and JavaScript to redirect
    # The success message appears for 1 second before redirect
    time.sleep(2)

    # Wait for redirect to home page
    WebDriverWait(driver, 10).until(
        ec.url_to_be(home_url),
    )

    if driver.current_url != home_url:
        msg = (
            f"User is not redirected to home URL. "
            f"Current URL: {driver.current_url}"
        )
        raise AssertionError(msg)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"✓ signin test passed in {elapsed_time:.2f} seconds")

def test_signin_with_google(driver: webdriver.Firefox):
    pass

if __name__ == "__main__":
    driver = setup_module()
    try:
        test_signin(driver)
    finally:
        teardown_module(driver)
