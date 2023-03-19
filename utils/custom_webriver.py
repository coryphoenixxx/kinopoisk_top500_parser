import time
from typing import Optional

from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from config import config


class WebDriver(webdriver.Chrome):
    def __init__(
            self,
            preset: tuple[str, str, tuple[int, int]],
            js: bool = False,
            images: bool = False,
            incognito: bool = False,
            restore_default: bool = False,
            captcha_result: bool = False,
    ):
        """
        :param preset: параметры вебдрайвера
        :param js: нужен ли включенный javascript
        :param images: нужно ли отображение картинок
        :param incognito: нужен ли режим инкогнито
        :param restore_default: флаг для восстановления дефолтный настроек вебдрайвера (без js и картинок)
        :param captcha_result: нужно ли подтверждение решенной капчи
        """

        self._preset = preset
        self._js = js
        self._images = images
        self._incognito = incognito
        self._captcha_result = captcha_result
        self._counter = 0
        self._restore_default = restore_default

        driver_dir, user_data_dir, window_rect = preset
        self.service = Service(executable_path=ChromeDriverManager(path=driver_dir).install())

        self.options = webdriver.ChromeOptions()

        self.options.add_argument("--disable-infobars")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument(f'--user-data-dir={user_data_dir}')
        self.options.add_argument('--profile-directory=Default')

        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_experimental_option("prefs", {
            'profile.managed_default_content_settings.javascript': 1 if js else 2,
            'profile.managed_default_content_settings.images': 1 if images else 2,
        })

        if incognito:
            self.options.add_argument("--incognito")

        if not window_rect:
            self.options.add_argument("--start-maximized")

        super().__init__(service=self.service, options=self.options)
        if window_rect:
            self.set_window_rect(*window_rect)

    def get(self, url, expected_selector='body') -> Optional[bool]:
        """
        Перегруженный метод get() ведрайвера

        :param url: Урл, по которому делаем запрос
        :param expected_selector: Селектор элемента, который ожидаем увидеть на странице
        :return:
        """

        super().get(url)

        # Держать вебдрайвер с выключенными картинками и javascript по дефолту для ускорения скрапинга
        if 'showcaptcha' not in self.current_url and self._restore_default is True:
            self._restart(url, expected_selector)

        self._counter += 1
        if self._counter > config.scrape_limit_count:
            time.sleep(config.scrape_limit_sleep)
            self._counter = 0

        # Если появляется капча, то перезагрузить вебдрайвер с вкл. js и отображением картинок
        if 'showcaptcha' in self.current_url and self._incognito is False:
            if self._images is False or self._js is False:
                self._restart(url, expected_selector, js=True, images=True, restore_default=True)

            try:
                captcha_btn = self.find_element(By.CSS_SELECTOR, '.CheckboxCaptcha-Button')
                captcha_btn.click()
            except NoSuchElementException:
                pass

            while 'showcaptcha' in self.current_url:
                time.sleep(0.5)
            if self._captcha_result:
                return True

        # Иногда кинопоиск запрашивает аутентификацию по SSO, чтобы ее пройти —
        # перезапустить вебдрайвер с вкл. js
        if 'sso' in self.current_url and self._js is False:
            self._restart(url, expected_selector, js=True, images=False, restore_default=True)

        try:
            self.find_element(By.CLASS_NAME, 'error-page')
        except NoSuchElementException:
            try:
                WebDriverWait(self, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, expected_selector)))
            except TimeoutException:
                self.get(url, expected_selector)

    def _restart(self, url, expected_selector, js=False, images=False, restore_default=False):
        """Перезапуск вебдрайвера с новыми параметрами"""

        self.close()
        self.__init__(preset=self._preset, js=js, images=images, restore_default=restore_default)
        self.get(url, expected_selector)
