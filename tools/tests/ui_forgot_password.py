import time

from common import setup_module, teardown_module
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


def test_forgot_password(driver: webdriver.Firefox):
    start_time = time.time()

    forgot_password_url = "http://localhost:8000/forgot-password/"

    driver.get(forgot_password_url)
    time.sleep(1)

    # check the forgot password page with some dummy data
    email = driver.find_element(By.ID, "email")
    submit = driver.find_element(By.CSS_SELECTOR, "#forgot-password-form .submit-btn")

    email.send_keys("active_user@jitendra.me")
    submit.click()
    time.sleep(5)

    # check if OTP input is displayed
    otp_input = WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.ID, "otp")),
    )
    if otp_input is None:
        raise AssertionError("OTP input not found")

    # enter a random OTP and new password, then submit
    otp_input.send_keys("000000")  # enter the wrong OTP
    new_password = driver.find_element(By.ID, "new-password")
    new_password.send_keys("newpassword123")
    otp_submit = driver.find_element(By.CSS_SELECTOR, "#reset-password-form .submit-btn")
    otp_submit.click()
    time.sleep(2)

    # Wait for error message to appear with text
    error_message = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, ".error-message")),
    )

    # Verify error message has text content
    WebDriverWait(driver, 5).until(
        lambda _d: len(error_message.text.strip()) > 0,
    )

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"✓ forgot password test passed in {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    driver = setup_module()
    try:
        test_forgot_password(driver)
    finally:
        teardown_module(driver)
