from selenium import webdriver

from config import Config


class WebDriver(webdriver.Chrome):
    def __init__(self, profile, window_rect=None):
        self.profile = profile
        self.window_rect = window_rect
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument(f'--user-data-dir={profile}')
        self.service = Config.service
        super().__init__(service=self.service, options=self.options)

    def get(self, url) -> 'WebDriver':
        self.set_window_rect(*self.window_rect)
        super().get(url)
        return self
