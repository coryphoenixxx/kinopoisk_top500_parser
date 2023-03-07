from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from config import config


class WebDriver(webdriver.Chrome):
    def __init__(self, preset, js=False, tease_captcha=False):
        self.preset = preset
        self.user_data_dir, self.window_rect = preset
        self.js = js
        self.options = webdriver.ChromeOptions()

        self.options.add_argument("--disable-infobars")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument(f'--user-data-dir={self.user_data_dir}')
        self.options.add_argument('--profile-directory=Default')

        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_experimental_option("prefs", {
            'profile.managed_default_content_settings.javascript': 2,
            'profile.managed_default_content_settings.images': 2})
        if js is True:
            self.options.add_experimental_option("prefs", {
                'profile.managed_default_content_settings.javascript': 1,
                'profile.managed_default_content_settings.images': 1})

        if tease_captcha:
            self.options.add_argument("--incognito")

        if not self.window_rect:
            self.options.add_argument("--start-maximized")

        super().__init__(service=config.service, options=self.options)

        if self.window_rect:
            self.set_window_rect(*self.window_rect)

    def get(self, url, expected_selector='body'):
        super().get(url)

        try:
            if self.js is False and 'sso' in self.current_url:
                raise SSOException
        except SSOException:
            self.close()
            self.__init__(preset=self.preset, js=True)
            self.get(url, expected_selector=expected_selector)

        try:
            self.find_element(By.CLASS_NAME, 'error-page')
        except NoSuchElementException:
            WebDriverWait(self, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, expected_selector)))


class SSOException(Exception):
    pass
