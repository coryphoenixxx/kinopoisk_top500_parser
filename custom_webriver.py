from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from config import config


class WebDriver(webdriver.Chrome):
    def __init__(self, preset, js=False, tease_captcha=False):
        self.user_data_dir, self.window_rect = preset

        self.options = webdriver.ChromeOptions()

        # self.options.add_argument('--headless')
        # self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        # self.options.add_argument(f'--user-agent={self.user_agent}')
        # self.options.add_argument('--disable-extensions')
        # self.options.add_argument("--no-sandbox")
        # self.options.add_argument('-–disable-gpu')
        # self.options.add_argument("--proxy-server='direct://'")
        # self.options.add_argument("--proxy-bypass-list=*")
        # self.options.add_argument("--disable-dev-shm-usage")
        # self.options.add_argument("--remote-debugging-port=9222")

        # prefs = {
        #     "profile.managed_default_content_settings.images": 1,
        #     "profile.default_content_setting_values.notifications": 2,
        #     "profile.managed_default_content_settings.stylesheets": 2,
        #     "profile.managed_default_content_settings.cookies": 1,
        #     "profile.managed_default_content_settings.javascript": 2,
        #     "profile.managed_default_content_settings.plugins": 2,
        #     "profile.managed_default_content_settings.popups": 2,
        #     "profile.managed_default_content_settings.geolocation": 1,
        #     "profile.managed_default_content_settings.media_stream": 2,
        # }
        #
        # self.options.add_experimental_option("prefs", prefs)

        self.options.add_experimental_option("prefs", {'profile.managed_default_content_settings.javascript': 2})
        if js:
            self.options.add_experimental_option("prefs", {'profile.managed_default_content_settings.javascript': 1})

        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument("--disable-infobars")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument(f'--user-data-dir={self.user_data_dir}')
        self.options.add_argument('--profile-directory=Default')

        if tease_captcha:
            self.options.add_argument("--incognito")

        if not self.window_rect:
            self.options.add_argument("--start-maximized")

        super().__init__(service=config.service, options=self.options)

        if self.window_rect:
            self.set_window_rect(*self.window_rect)

    def get(self, url, expected_selector='body'):
        super().get(url)

        WebDriverWait(self, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, expected_selector)))
