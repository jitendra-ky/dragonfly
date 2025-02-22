import random
import time

from common import setup_module, teardown_module
from selenium import webdriver
from selenium.webdriver.common.by import By


def test_signup(driver: webdriver.Firefox):
    start_time = time.time()

    signup_url = "http://localhost:8000/signup/"
    home_url = "http://localhost:8000/"

    driver.get(signup_url)
    time.sleep(1)

    # check if the user is redirected to the "http://localhost:8000/"
    # then click on logout button
    # again make sure that user is on "http://localhost:8000/login"
    if driver.current_url == home_url:
        driver.find_element(By.ID, "logout-button").click()
        time.sleep(2)
        # change url to signup_url
        driver.get(signup_url)
        if not driver.current_url == signup_url:
            raise AssertionError("Failed to redirect to signup URL")

    # check the signup page with some dummy data
    fullname = driver.find_element(By.ID, "fullname")
    email = driver.find_element(By.ID, "email")
    password = driver.find_element(By.ID, "password")
    confirm_password = driver.find_element(By.ID, "confirm-password")
    submit = driver.find_element(By.CSS_SELECTOR, "#signup-form .submit-btn")

    fullname.send_keys("John Doe")
    email.send_keys(f"jk69854+test{random.randint(10000, 99999)}@gmail.com")
    password.send_keys("rootroot")
    confirm_password.send_keys("rootroot")
    submit.click()
    time.sleep(2)

    # check if OTP page is displayed
    otp_input = driver.find_element(By.ID, "otp")
    if otp_input is None:
        raise AssertionError("OTP input not found")

    # enter a random OTP and submit
    otp_input.send_keys("123456") # enter the wrong OTP
    otp_submit = driver.find_element(By.CSS_SELECTOR, "#otp-form .submit-btn")
    otp_submit.click()
    time.sleep(2)

    # check if the user is redirected to the home page
    if driver.current_url == home_url:
        raise AssertionError("User was redirected to the home page")

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"✓ signup test passed in {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    driver = setup_module()
    try:
        test_signup(driver)
    finally:
        teardown_module(driver)
