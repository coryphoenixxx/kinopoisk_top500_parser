from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
# options.add_argument('--headless')
options.add_argument('--disable-dev-shm-usage')
options.add_experimental_option("excludeSwitches", ["enable-automation"])


