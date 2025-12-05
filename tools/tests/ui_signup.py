import time

from common import setup_module, teardown_module
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


def test_signup(driver: webdriver.Firefox):
    start_time = time.time()

    signup_url = "http://localhost:8000/signup/"

    # Clear localStorage to ensure clean state
    driver.execute_script("localStorage.clear();")

    driver.get(signup_url)
    time.sleep(1)

    # Wait for signup form to be visible (in case JavaScript tries to redirect)
    fullname = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.ID, "fullname")),
    )
    email = driver.find_element(By.ID, "email")
    password = driver.find_element(By.ID, "password")
    confirm_password = driver.find_element(By.ID, "confirm-password")
    submit = driver.find_element(By.CSS_SELECTOR, "#signup-form .submit-btn")

    fullname.send_keys("John Doe")
    email.send_keys("unregistered@jitendra.me")
    password.send_keys("rootroot")
    confirm_password.send_keys("rootroot")
    submit.click()

    # Wait for AJAX call and OTP form to appear (JavaScript hides signup and shows OTP form)
    time.sleep(2)

    # Wait for OTP input to be visible
    otp_input = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.ID, "otp")),
    )

    if otp_input is None:
        raise AssertionError("OTP input not found")

    # enter a random OTP and submit
    otp_input.send_keys("123456") # enter the wrong OTP
    otp_submit = driver.find_element(By.CSS_SELECTOR, "#otp-form .submit-btn")
    otp_submit.click()
    time.sleep(2)

    # check if wrong OTP error message is displayed
    error_message = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, "#otp-form .error-message")),
    )
    if error_message is None:
        raise AssertionError("Error message not found")

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"✓ signup test passed in {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    driver = setup_module()
    try:
        test_signup(driver)
    finally:
        teardown_module(driver)
