import geckodriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


def setup_module():
    geckodriver_autoinstaller.install()
    firefox_options = Options()
    firefox_options.headless = True
    firefox_options.add_argument("--width=1920")
    firefox_options.add_argument("--height=1080")
    return webdriver.Firefox(options=firefox_options)

def teardown_module(driver: webdriver.Firefox):
    driver.quit()
