import os
import time
from typing import List
from bs4 import BeautifulSoup
from selenium.common import InvalidSessionIdException
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver

# from chrome_config import options
from utils import Navigator
from movies_list import movie_lst
from fake_useragent import UserAgent
import undetected_chromedriver as uc
from dotenv import load_dotenv
from contextlib import suppress

from selenium import webdriver
from selenium_stealth import stealth

ua = UserAgent()
from random import randint

load_dotenv()


class WebDriverMixin:
    """Инициализация WebDriver"""

    def __init__(self):
        pass
        # options = uc.ChromeOptions()
        # options.user_data_dir = os.getenv("CHROME_PROFILE_PATH")
        # options.add_argument('--no-sandbox')
        # options.add_argument("--disable-blink-features=AutomationControlled")
        # options.add_argument('--disable-dev-shm-usage')
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # options.add_experimental_option('useAutomationExtension', False)
        # options.add_argument(f'--user-agent={ua.random}')
        # self.service = Service(executable_path=ChromeDriverManager().install())
        # self.driver.set_window_size(1920, 1080)


class Crawler(WebDriverMixin):
    def __init__(self):
        self.base_url = "https://www.kinopoisk.ru/lists/movies/top500/?page="
        super().__init__()

    def start(self, p):
        check_url = "https://intoli.com/blog/not-possible-to-block-chrome-headless/chrome-headless-test.html"
        kinopoisk_url = "https://www.kinopoisk.ru/lists/movies/top500"
        bot_url = "https://bot.sannysoft.com/"
        # self.driver.get("https://nowsecure.nl")

        # options = uc.ChromeOptions()
        # options.add_argument("--headless")
        # driver = uc.Chrome()
        # driver.user_data_dir = os.getenv("CHROME_PROFILE_PATH")

        options = webdriver.ChromeOptions()

        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        options.add_argument(f'--user-agent={user_agent}')

        time.sleep(randint(1, 20))
        driver = webdriver.Chrome(options=options)

        driver.set_window_rect(p[2], p[3], p[0] // 2, p[1] // 2)

        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )

        with suppress(InvalidSessionIdException, OSError):
            driver.get(kinopoisk_url)
            time.sleep(60)
        driver.quit()
