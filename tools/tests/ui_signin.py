import time

from common import setup_module, teardown_module
from selenium import webdriver
from selenium.webdriver.common.by import By


def test_signin(driver: webdriver.Firefox):
    start_time = time.time()

    signin_url = "http://localhost:8000/signin/"
    home_url = "http://localhost:8000/"

    driver.get(signin_url)

    # check if the user is redirected to the "http://localhost:8000/"
    # then click on logout button
    # again make sure that user is on "http://localhost:8000/login"
    if driver.current_url == home_url:
        driver.execute_script("document.getElementById('logout-button').click();")
        time.sleep(2)
        if driver.current_url != signin_url:
            raise AssertionError("User is not redirected to signin URL")

    # check the login page with some dummy data
    # if the user is redirected to the "http://localhost:8000/"
    # then the test passed
    username = driver.find_element(By.ID, "email")
    password = driver.find_element(By.ID, "password")
    submit = driver.find_element(By.CSS_SELECTOR, "#signin-form .submit-btn")

    username.send_keys("active_user@jitendra.me")
    password.send_keys("rootroot")
    submit.click()
    time.sleep(2)
    if driver.current_url != home_url:
        raise AssertionError("User is not redirected to home URL")

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
