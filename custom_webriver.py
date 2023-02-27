import time

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from config import config


class WebDriver(webdriver.Chrome):
    def __init__(self, url, presets):
        self.url = url
        self.profile, self.window_rect = presets.get()
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument(f'--user-data-dir={self.profile}')
        self.service = config.service

        if not self.window_rect:
            self.options.add_argument("--start-maximized")

        super().__init__(service=self.service, options=self.options)

        self._get(self.url)

        presets.put((self.profile, self.window_rect))

    def _get(self, url):
        if self.window_rect:
            self.set_window_rect(*self.window_rect)

        super().get(url)

        WebDriverWait(self, 1).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'body')))

        try:
            self.find_element(By.CSS_SELECTOR, ".CheckboxCaptcha-Button").click()
            while 'showcaptcha' in self.current_url:
                time.sleep(0.5)
        except NoSuchElementException:
            pass
