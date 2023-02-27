import time

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from config import Config


class WebDriver(webdriver.Chrome):
    def __init__(self, link, profile, window_rect=None):
        self.link = link
        self.profile = profile
        self.window_rect = window_rect
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument(f'--user-data-dir={profile}')
        self.service = Config.service

        if not self.window_rect:
            self.options.add_argument("--start-maximized")

        super().__init__(service=self.service, options=self.options)

        self.get(self.link)

    def get(self, url) -> 'WebDriver':
        if self.window_rect:
            self.set_window_rect(*self.window_rect)

        super().get(url)

        try:
            self.find_element(By.CSS_SELECTOR, ".CheckboxCaptcha-Button").click()

            while 'showcaptcha' in self.current_url:
                time.sleep(1)
        except NoSuchElementException:
            pass

        WebDriverWait(self, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'body')))

        return self
