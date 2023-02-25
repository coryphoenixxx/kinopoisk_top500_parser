from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class WebDriver(webdriver.Chrome):
    def __init__(self, profile, window_rect):
        self.profile = profile
        self.window_rect = window_rect
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument(f'--user-data-dir={profile}')
        # self.options.add_argument(f'--headless')
        self.service = Service(executable_path=ChromeDriverManager(path=r".\\drivers").install())
        super().__init__(service=self.service, options=self.options)

    def show(self):
        self.set_window_rect(*self.window_rect)
