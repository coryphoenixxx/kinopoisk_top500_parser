import os
import time
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver

from dotenv import load_dotenv

load_dotenv()


class WebDriverMixin:
    """Инициализация WebDriver"""

    def __init__(self):
        pass


class Crawler(WebDriverMixin):
    def __init__(self):
        super().__init__()

    def start(self, params):
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument("--disable-plugins-discovery")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        service = Service(executable_path=ChromeDriverManager().install())

        user_data_dir = os.getenv('CHROME_USER_DATA_DIR') + fr"\{params['parent_dir']}"

        options.add_argument('--user-data-dir={}'.format(user_data_dir))
        options.add_argument('--profile-directory={}'.format(params["profile_dir"]))

        driver = webdriver.Chrome(service=service, options=options)
        driver.set_window_rect(*params["window_rect"])

        time.sleep(params['delay'])

        driver.get(params['link'])

        for _ in range(2):
            body = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'body')))
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(1)

        link_elems = driver.find_elements(By.CSS_SELECTOR, ".base-movie-main-info_link__YwtP1")

        result = [elem.get_attribute('href') for elem in link_elems]

        time.sleep(3)
        driver.quit()
        return result

